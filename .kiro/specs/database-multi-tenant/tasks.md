# Implementation Plan - Database Multi-Tenant

## Task Overview

Este plano implementa a migração para PostgreSQL multi-tenant com Row-Level Security, dividido em tarefas incrementais e testáveis.

---

## 1. Setup PostgreSQL e Configuração Base

Criar estrutura de configuração e conexão básica com PostgreSQL.

- [ ] 1.1 Criar arquivo de configuração `config/database.yml` com ambientes dev/test/prod
  - Definir parâmetros: host, port, database, user, password, pool_size
  - Suportar substituição por variáveis de ambiente
  - _Requirements: 6.1, 6.2, 6.3_

- [ ] 1.2 Implementar `src/database/config.py` para carregar configurações
  - Classe `DatabaseConfig` com método `_load_config()`
  - Property `connection_string` para SQLAlchemy
  - Validação de campos obrigatórios
  - _Requirements: 6.4, 6.5_

- [ ] 1.3 Criar `src/database/connection.py` com connection pool
  - Classe `DatabaseConnection` com SQLAlchemy engine
  - Configurar pool: min=5, max=20, timeout=30s, recycle=300s
  - Método `get_session()` para obter sessões
  - _Requirements: 3.1, 3.2, 3.3, 3.4_

- [ ] 1.4 Adicionar dependências ao `requirements.txt`
  - psycopg2-binary>=2.9.0
  - SQLAlchemy>=2.0.0
  - alembic>=1.12.0
  - PyYAML>=6.0

---

## 2. Implementar Modelos SQLAlchemy

Criar modelos ORM para todas as entidades do sistema.

- [ ] 2.1 Criar `src/database/models.py` com modelo `Organization`
  - Campos: id, name, slug, plan, active, timestamps
  - Relacionamentos com Supplier, Product, User
  - _Requirements: 4.1, 4.3, 4.4_

- [ ] 2.2 Implementar modelo `Supplier` com relacionamentos
  - Campos: id, org_id, supplier_id, name, data_type, url, consent_*
  - Foreign key para Organization
  - Índice em org_id
  - _Requirements: 4.1, 4.3, 4.4_

- [ ] 2.3 Implementar modelo `Product` (products_unified)
  - Campos: id, org_id, supplier_id, name, brand, category, weight, unit
  - Campos de preço: price_base, price_margin, price_shipping, price_final
  - Campos de estoque: stock_available, stock_quantity
  - Metadata JSON, timestamps, soft delete
  - Índices: (org_id, name), (org_id, category), (org_id, supplier_id)
  - _Requirements: 4.1, 4.3, 4.4, 8.1, 8.2, 8.3_

- [ ] 2.4 Implementar modelos `User` e `AuditLog`
  - User: id, org_id, email, password_hash, role, active
  - AuditLog: id, org_id, timestamp, operation, entity_type, data_hash
  - Soft delete em User
  - _Requirements: 4.1, 4.4, 4.5_

- [ ] 2.5 Adicionar validações e constraints nos modelos
  - Campos obrigatórios (nullable=False)
  - Unique constraints onde necessário
  - Enums para campos categóricos (plan, role, data_type, unit)
  - _Requirements: 4.2_

---

## 3. Criar Scripts de Migration

Implementar migrations SQL versionadas para criar schema.

- [ ] 3.1 Criar `src/database/migrations/001_initial_schema.sql`
  - CREATE TABLE para: organizations, suppliers, products_unified, users, audit_logs
  - Definir primary keys, foreign keys, constraints
  - Criar índices de performance
  - Criar tabela schema_migrations
  - _Requirements: 7.1, 7.2, 8.1, 8.2, 8.3_

- [ ] 3.2 Criar `src/database/migrations/002_rls_policies.sql`
  - ENABLE ROW LEVEL SECURITY em tabelas multi-tenant
  - CREATE POLICY para isolamento por org_id
  - CREATE POLICY para INSERT com org_id automático
  - CREATE POLICY para admin bypass
  - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5_

- [ ] 3.3 Implementar `src/database/migration_runner.py`
  - Função `run_migrations()` que executa SQL files em ordem
  - Registrar versão em schema_migrations
  - Skip migrations já aplicadas
  - Suporte a rollback (futuro)
  - _Requirements: 7.2, 7.3, 7.4, 7.5_

- [ ] 3.4 Criar script `scripts/init_database.py` para setup inicial
  - Executar migrations
  - Criar organização padrão "Made in Natural"
  - Criar usuário admin inicial
  - Validar schema após migrations
  - _Requirements: 2.3, 7.5_

---

## 4. Implementar Context Manager para RLS

Criar sistema de contexto para injetar org_id nas queries.

- [ ] 4.1 Adicionar método `set_org_context()` em `DatabaseConnection`
  - Executar `SET app.current_org_id = {org_id}` na sessão
  - Executar `SET app.user_role = {role}` para admin bypass
  - _Requirements: 5.2, 5.5_

- [ ] 4.2 Criar context manager `with_org_context()` para uso simplificado
  - Decorator ou context manager que injeta org_id automaticamente
  - Exemplo: `with db.with_org_context(org_id=1): ...`
  - _Requirements: 5.2_

- [ ] 4.3 Implementar helper `get_current_org_id()` para obter contexto atual
  - Ler de sessão ou contexto de request
  - Lançar exceção se org_id não estiver definido
  - _Requirements: 1.5_

---

## 5. Migração de Dados JSON → PostgreSQL

Migrar dados existentes de arquivos JSON para o banco.

- [ ] 5.1 Criar `scripts/migrate_json_to_postgres.py` com função `migrate_suppliers()`
  - Ler `data/suppliers.json`
  - Criar registros Supplier no banco
  - Associar à organização padrão (org_id=1)
  - Preservar todos os metadados
  - _Requirements: 2.1, 2.4_

- [ ] 5.2 Implementar função `migrate_products()` no mesmo script
  - Ler `data/catalog/catalog_repository.json`
  - Criar registros Product no banco
  - Mapear supplier_id de string para FK do banco
  - Preservar metadata (hash, extraction_date, source_url)
  - _Requirements: 2.2, 2.4_

- [ ] 5.3 Adicionar tratamento de erros e rollback na migração
  - Try/except com rollback em caso de falha
  - Log detalhado de erros
  - Relatório de migração (quantos registros migrados)
  - _Requirements: 2.5_

- [ ] 5.4 Criar script de validação pós-migração
  - Comparar contagem de registros JSON vs PostgreSQL
  - Validar integridade de foreign keys
  - Verificar que todos os produtos têm supplier válido
  - _Requirements: 2.4_

---

## 6. Health Checks e Monitoramento

Implementar endpoints e scripts de monitoramento do banco.

- [ ] 6.1 Criar `src/database/health.py` com função `check_database_health()`
  - Testar conectividade com query simples
  - Retornar métricas: conexões ativas, tamanho do banco, última migration
  - Timeout de 1 segundo
  - _Requirements: 10.1, 10.2, 10.3_

- [ ] 6.2 Implementar endpoint `/health/database` (preparação para API)
  - Chamar `check_database_health()`
  - Retornar status 200 se OK, 503 se falha
  - Incluir métricas no response
  - _Requirements: 10.1, 10.4_

- [ ] 6.3 Adicionar logging de métricas do connection pool
  - Log de conexões ativas, tempo de espera, pool size
  - Integrar com sistema de compliance existente
  - _Requirements: 3.5_

---

## 7. Backup e Recovery

Implementar scripts de backup automático e restore.

- [ ] 7.1 Criar `scripts/backup_database.sh` com pg_dump
  - Executar pg_dump com compressão gzip
  - Salvar em `backups/addas_backup_YYYYMMDD.sql.gz`
  - Incluir timestamp no nome do arquivo
  - _Requirements: 9.1, 9.2_

- [ ] 7.2 Implementar rotação de backups (manter últimos 30 dias)
  - Script que remove backups com mais de 30 dias
  - Executar automaticamente após cada backup
  - _Requirements: 9.3_

- [ ] 7.3 Criar `scripts/restore_database.sh` para restore
  - Validar integridade do arquivo de backup
  - Confirmar antes de aplicar restore
  - Log de operação de restore
  - _Requirements: 9.4_

---

## 8. Atualizar Sistema Existente para Usar PostgreSQL

Adaptar código existente para usar banco ao invés de JSON.

- [ ] 8.1 Atualizar `CatalogManager` para usar PostgreSQL
  - Substituir leitura de JSON por queries SQLAlchemy
  - Métodos: `search_products()`, `get_statistics()`, `integrate_supplier()`
  - Manter interface pública inalterada
  - _Requirements: 1.1, 1.2, 1.3_

- [ ] 8.2 Atualizar `ProductTransformer` para salvar no banco
  - Após normalização, salvar em PostgreSQL ao invés de JSON
  - Usar transações para garantir atomicidade
  - _Requirements: 1.2, 1.3_

- [ ] 8.3 Atualizar `ComplianceLogger` para usar tabela audit_logs
  - Migrar de JSONL para PostgreSQL
  - Manter formato de log compatível
  - _Requirements: 1.2, 1.3_

- [ ] 8.4 Atualizar scripts de pipeline para usar banco
  - `run_all_pipelines.py`, `run_gramore_pipeline.py`, etc
  - Injetar org_id=1 (organização padrão)
  - _Requirements: 1.1, 1.2_

---

## 9. Documentação e Testes

Documentar mudanças e criar testes.

- [ ] 9.1 Atualizar `docs/ARCHITECTURE.md` com nova arquitetura de banco
  - Diagrama ER
  - Explicação de RLS
  - Fluxo de dados atualizado

- [ ] 9.2 Criar `docs/DATABASE.md` com guia de uso
  - Como executar migrations
  - Como fazer backup/restore
  - Como adicionar novos modelos
  - Troubleshooting comum

- [ ] 9.3 Atualizar `README.md` com instruções de setup do banco
  - Pré-requisitos: PostgreSQL 15+
  - Comandos de inicialização
  - Variáveis de ambiente necessárias

- [ ]* 9.4 Criar testes de integração para modelos
  - Testar CRUD de cada modelo
  - Testar isolamento RLS entre organizações
  - Testar connection pool sob carga

- [ ]* 9.5 Criar testes para migration
  - Testar migração completa JSON → PostgreSQL
  - Validar integridade de dados após migração
  - Testar rollback em caso de erro

---

## Ordem de Execução Recomendada

1. **Tasks 1.x:** Setup e configuração base
2. **Tasks 2.x:** Modelos SQLAlchemy
3. **Tasks 3.x:** Migrations SQL
4. **Tasks 4.x:** Context manager RLS
5. **Tasks 5.x:** Migração de dados
6. **Tasks 6.x:** Health checks
7. **Tasks 7.x:** Backup/restore
8. **Tasks 8.x:** Atualizar código existente
9. **Tasks 9.x:** Documentação e testes

## Notas Importantes

- Todas as tasks 1-8 são obrigatórias para funcionalidade completa
- Tasks 9.4 e 9.5 (testes) são opcionais mas recomendadas
- Cada task deve ser commitada individualmente
- Testar localmente antes de cada commit
- Manter compatibilidade com sistema JSON durante transição
