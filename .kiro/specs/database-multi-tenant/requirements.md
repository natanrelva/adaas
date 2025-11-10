# Requirements Document - Database Multi-Tenant

## Introduction

Migração do sistema de armazenamento baseado em arquivos JSON para PostgreSQL com suporte multi-tenant usando Row-Level Security (RLS). Esta mudança é fundamental para transformar o sistema monolítico em uma plataforma SaaS escalável.

## Glossary

- **System**: O sistema Made in Natural / Add'as Platform
- **Organization**: Entidade tenant que agrupa fornecedores, produtos e usuários
- **RLS (Row-Level Security)**: Mecanismo do PostgreSQL que filtra automaticamente linhas baseado em políticas
- **Migration**: Processo de transferência de dados de JSON para PostgreSQL
- **Connection Pool**: Pool de conexões reutilizáveis ao banco de dados

## Requirements

### Requirement 1: Multi-Tenant Database Schema

**User Story:** Como administrador da plataforma, quero que cada organização tenha seus dados isolados, para garantir segurança e privacidade entre tenants.

#### Acceptance Criteria

1. WHEN uma organização é criada, THE System SHALL criar um registro na tabela `organizations` com ID único
2. WHEN dados são inseridos, THE System SHALL associar automaticamente o `org_id` do contexto atual
3. WHILE um usuário está autenticado, THE System SHALL filtrar automaticamente dados apenas da sua organização via RLS
4. THE System SHALL implementar tabelas: `organizations`, `suppliers`, `products_unified`, `users`, `audit_logs`
5. THE System SHALL garantir que queries sem `org_id` no contexto sejam bloqueadas pelo RLS

### Requirement 2: Data Migration from JSON

**User Story:** Como desenvolvedor, quero migrar os dados existentes de JSON para PostgreSQL, para manter a continuidade dos dados atuais.

#### Acceptance Criteria

1. WHEN a migração é executada, THE System SHALL transferir todos os fornecedores de `data/suppliers.json` para a tabela `suppliers`
2. WHEN a migração é executada, THE System SHALL transferir todos os produtos de `data/catalog/catalog_repository.json` para `products_unified`
3. THE System SHALL criar uma organização padrão "Made in Natural" com `org_id = 1`
4. THE System SHALL preservar todos os metadados existentes (hashes, timestamps, source_url)
5. WHEN a migração falha, THE System SHALL fazer rollback completo e reportar erros detalhados

### Requirement 3: Connection Pooling

**User Story:** Como desenvolvedor, quero um pool de conexões eficiente, para otimizar performance e uso de recursos.

#### Acceptance Criteria

1. THE System SHALL implementar connection pooling com no mínimo 5 e no máximo 20 conexões simultâneas
2. WHEN uma conexão é solicitada, THE System SHALL reutilizar conexões existentes do pool
3. WHEN o pool está cheio, THE System SHALL aguardar até 30 segundos por uma conexão disponível
4. THE System SHALL fechar conexões ociosas após 300 segundos
5. THE System SHALL registrar métricas de uso do pool (conexões ativas, tempo de espera)

### Requirement 4: Database Models with SQLAlchemy

**User Story:** Como desenvolvedor, quero modelos ORM bem definidos, para facilitar operações de banco de dados e manutenção.

#### Acceptance Criteria

1. THE System SHALL implementar modelos SQLAlchemy para todas as tabelas principais
2. WHEN um modelo é definido, THE System SHALL incluir validações de campos obrigatórios
3. THE System SHALL implementar relacionamentos entre modelos (Organization → Suppliers → Products)
4. THE System SHALL incluir timestamps automáticos (created_at, updated_at) em todos os modelos
5. THE System SHALL implementar soft delete com campo `deleted_at` para auditoria

### Requirement 5: Row-Level Security Policies

**User Story:** Como administrador de segurança, quero políticas RLS automáticas, para garantir isolamento de dados entre organizações.

#### Acceptance Criteria

1. THE System SHALL habilitar RLS em todas as tabelas multi-tenant
2. WHEN um usuário executa SELECT, THE System SHALL filtrar apenas registros onde `org_id = current_setting('app.current_org_id')`
3. WHEN um usuário executa INSERT, THE System SHALL injetar automaticamente o `org_id` do contexto
4. WHEN um usuário executa UPDATE/DELETE, THE System SHALL permitir apenas registros da sua organização
5. THE System SHALL criar política especial para role `admin` que permite acesso cross-tenant

### Requirement 6: Database Configuration Management

**User Story:** Como DevOps, quero configuração centralizada do banco, para facilitar deploy em diferentes ambientes.

#### Acceptance Criteria

1. THE System SHALL carregar configurações de `config/database.yml` ou variáveis de ambiente
2. THE System SHALL suportar configurações diferentes para desenvolvimento, teste e produção
3. WHEN variáveis de ambiente estão definidas, THE System SHALL sobrescrever valores do arquivo YAML
4. THE System SHALL validar configurações obrigatórias na inicialização (host, port, database, user)
5. THE System SHALL falhar rapidamente com mensagem clara se configurações estiverem inválidas

### Requirement 7: Migration Scripts

**User Story:** Como desenvolvedor, quero scripts de migração versionados, para gerenciar evolução do schema de forma controlada.

#### Acceptance Criteria

1. THE System SHALL implementar migrations numeradas sequencialmente (001, 002, etc.)
2. WHEN uma migration é executada, THE System SHALL registrar versão na tabela `schema_migrations`
3. THE System SHALL executar apenas migrations ainda não aplicadas
4. THE System SHALL suportar rollback de migrations com scripts `down`
5. THE System SHALL validar integridade do schema após cada migration

### Requirement 8: Indexes and Performance

**User Story:** Como desenvolvedor, quero índices otimizados, para garantir performance em queries frequentes.

#### Acceptance Criteria

1. THE System SHALL criar índice em `products_unified(org_id, name)` para buscas por nome
2. THE System SHALL criar índice em `products_unified(org_id, category)` para filtros por categoria
3. THE System SHALL criar índice em `products_unified(org_id, supplier_id)` para queries por fornecedor
4. THE System SHALL criar índice GIN em campos de busca full-text (futuro)
5. THE System SHALL medir e reportar tempo de queries principais (< 100ms para 10k produtos)

### Requirement 9: Backup and Recovery

**User Story:** Como administrador, quero backups automáticos, para garantir recuperação de dados em caso de falha.

#### Acceptance Criteria

1. THE System SHALL implementar script de backup diário via `pg_dump`
2. WHEN backup é executado, THE System SHALL comprimir arquivo com gzip
3. THE System SHALL manter últimos 30 dias de backups
4. THE System SHALL implementar script de restore que valida integridade antes de aplicar
5. THE System SHALL testar restore automaticamente em ambiente de staging semanalmente

### Requirement 10: Health Checks

**User Story:** Como DevOps, quero health checks do banco, para monitorar disponibilidade e performance.

#### Acceptance Criteria

1. THE System SHALL implementar endpoint `/health/database` que verifica conectividade
2. WHEN health check é executado, THE System SHALL retornar status em < 1 segundo
3. THE System SHALL reportar métricas: conexões ativas, tamanho do banco, última migration
4. WHEN banco está indisponível, THE System SHALL retornar status 503 com mensagem clara
5. THE System SHALL registrar falhas de health check em logs de monitoramento
