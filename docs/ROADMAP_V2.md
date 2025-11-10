# Roadmap V2 - Add'as Platform Evolution

## 📋 Visão Geral

Evolução do projeto Made in Natural para Add'as - Plataforma SaaS B2B/B2C completa com ingestão multi-formato, ETL as a Service, portal white-label e rastreabilidade blockchain-light.

**Base Atual:** Sistema ETL funcional com 3 fornecedores e catálogo unificado  
**Objetivo:** Plataforma SaaS multi-tenant com monetização e escalabilidade

---

## 🎯 Fases de Implementação

### FASE 1: Fundação SaaS (Passos 11-15)
**Objetivo:** Transformar sistema monolítico em arquitetura multi-tenant

### FASE 2: Ingestão Multi-Formato (Passos 16-20)
**Objetivo:** Suportar múltiplos formatos e protocolos de entrada

### FASE 3: ETL as a Service (Passos 21-25)
**Objetivo:** API pública de ETL com configuração zero-code

### FASE 4: Portal B2C White-Label (Passos 26-30)
**Objetivo:** Interface embedável com checkout e rastreabilidade

### FASE 5: Rastreabilidade e Compliance (Passos 31-35)
**Objetivo:** Blockchain-light e compliance LGPD completo

### FASE 6: Monetização e Analytics (Passos 36-40)
**Objetivo:** Sistema de billing e dashboards analíticos

---

## 📦 FASE 1: Fundação SaaS (Passos 11-15)

### Passo 11: Banco de Dados Multi-Tenant
**Commit:** `feat: PostgreSQL multi-tenant com RLS`

**Arquivos a Criar:**
- `src/database/__init__.py`
- `src/database/connection.py` - Pool de conexões PostgreSQL
- `src/database/models.py` - SQLAlchemy models
- `src/database/migrations/001_initial_schema.sql`
- `src/database/migrations/002_rls_policies.sql`
- `config/database.yml` - Configuração do banco

**Funcionalidades:**
- Migração de JSON para PostgreSQL
- Row-Level Security (RLS) por organização
- Tabelas: `organizations`, `suppliers`, `products_unified`, `audit_logs`
- Índices otimizados para busca
- Conexão pooling

**Saída:**
- Banco PostgreSQL configurado
- Dados migrados do JSON
- RLS ativo por tenant

---

### Passo 12: Sistema de Autenticação Multi-Tenant
**Commit:** `feat: autenticação JWT com multi-tenancy`

**Arquivos a Criar:**
- `src/auth/__init__.py`
- `src/auth/jwt_handler.py` - Geração e validação JWT
- `src/auth/middleware.py` - Middleware de autenticação
- `src/auth/models.py` - User, Organization, Role
- `scripts/create_organization.py` - Script de criação de org

**Funcionalidades:**
- JWT com claims: `user_id`, `org_id`, `role`
- Roles: `admin`, `supplier`, `retailer`, `viewer`
- Refresh tokens
- Password hashing (bcrypt)
- Rate limiting por organização

**Saída:**
- Sistema de auth funcional
- API de login/logout
- Middleware de proteção de rotas

---

### Passo 13: API REST Base (FastAPI)
**Commit:** `feat: API REST base com FastAPI`

**Arquivos a Criar:**
- `src/api/__init__.py`
- `src/api/main.py` - App FastAPI principal
- `src/api/routes/health.py` - Health check
- `src/api/routes/auth.py` - Endpoints de autenticação
- `src/api/routes/suppliers.py` - CRUD de fornecedores
- `src/api/routes/products.py` - CRUD de produtos
- `src/api/dependencies.py` - Dependências comuns
- `src/api/schemas.py` - Pydantic schemas

**Endpoints:**
```
GET  /health
POST /auth/login
POST /auth/refresh
GET  /suppliers
POST /suppliers
GET  /products
GET  /products/{id}
POST /products/search
```

**Saída:**
- API REST funcional
- Documentação Swagger automática
- Validação de dados com Pydantic

---

### Passo 14: Containerização (Docker)
**Commit:** `feat: containerização com Docker e docker-compose`

**Arquivos a Criar:**
- `Dockerfile` - Container da aplicação
- `docker-compose.yml` - Orquestração de serviços
- `.dockerignore`
- `docker/postgres/init.sql` - Inicialização do banco
- `docker/nginx/nginx.conf` - Reverse proxy

**Serviços:**
```yaml
services:
  - postgres: PostgreSQL 15
  - redis: Cache e sessões
  - api: FastAPI app
  - nginx: Reverse proxy
```

**Saída:**
- Aplicação containerizada
- Ambiente reproduzível
- Deploy simplificado

---

### Passo 15: Testes Automatizados
**Commit:** `test: suite de testes com pytest`

**Arquivos a Criar:**
- `tests/__init__.py`
- `tests/conftest.py` - Fixtures
- `tests/test_extractors.py`
- `tests/test_transformers.py`
- `tests/test_catalog.py`
- `tests/test_api.py`
- `tests/test_auth.py`
- `.github/workflows/tests.yml` - CI/CD

**Funcionalidades:**
- Testes unitários (80%+ cobertura)
- Testes de integração
- Testes de API (pytest + httpx)
- CI/CD com GitHub Actions
- Coverage report

**Saída:**
- Suite de testes completa
- CI/CD configurado
- Badge de cobertura

---

## 📥 FASE 2: Ingestão Multi-Formato (Passos 16-20)

### Passo 16: Ingestion Gateway Base
**Commit:** `feat: gateway de ingestão multi-formato`

**Arquivos a Criar:**
- `src/ingestion/__init__.py`
- `src/ingestion/gateway.py` - Gateway principal
- `src/ingestion/parsers/csv_parser.py`
- `src/ingestion/parsers/excel_parser.py`
- `src/ingestion/parsers/xml_parser.py`
- `src/ingestion/parsers/json_parser.py`
- `src/api/routes/ingestion.py`

**Endpoints:**
```
POST /ingestion/upload
POST /ingestion/webhook
GET  /ingestion/status/{job_id}
```

**Saída:**
- Upload de arquivos CSV/Excel/XML/JSON
- Parsing automático por tipo
- Job tracking

---

### Passo 17: Integração Google Sheets
**Commit:** `feat: integração com Google Sheets API`

**Arquivos a Criar:**
- `src/ingestion/connectors/google_sheets.py`
- `src/auth/oauth_google.py` - OAuth 2.0 flow
- `scripts/setup_google_sheets.py`

**Funcionalidades:**
- OAuth 2.0 com Google
- Leitura de planilhas
- Sync automático (polling)
- Webhook de mudanças

**Saída:**
- Integração Google Sheets funcional
- Sync bidirecional

---

### Passo 18: Webhooks para ERPs
**Commit:** `feat: sistema de webhooks para ERPs`

**Arquivos a Criar:**
- `src/ingestion/webhooks/__init__.py`
- `src/ingestion/webhooks/handler.py`
- `src/ingestion/webhooks/validator.py` - HMAC validation
- `src/api/routes/webhooks.py`

**Endpoints:**
```
POST /webhooks/{supplier_id}
GET  /webhooks/logs
```

**Funcionalidades:**
- Validação HMAC SHA-256
- Retry automático
- Dead letter queue
- Webhook logs

**Saída:**
- Sistema de webhooks robusto
- Integração com ERPs

---

### Passo 19: Mapeamento de Campos (Field Mapping)
**Commit:** `feat: sistema de mapeamento de campos configurável`

**Arquivos a Criar:**
- `src/ingestion/mapping/__init__.py`
- `src/ingestion/mapping/mapper.py`
- `src/ingestion/mapping/templates.py` - Templates pré-definidos
- `src/api/routes/mapping.py`
- `frontend/mapping-ui/` - Interface drag-and-drop (React)

**Funcionalidades:**
- Mapeamento visual de campos
- Templates por tipo de fornecedor
- Validação de mapeamento
- Sugestões com IA (futuro)

**Saída:**
- UI de mapeamento funcional
- Templates salvos por fornecedor

---

### Passo 20: Validação e Enriquecimento
**Commit:** `feat: validação e enriquecimento de dados`

**Arquivos a Criar:**
- `src/ingestion/validation/__init__.py`
- `src/ingestion/validation/rules.py`
- `src/ingestion/enrichment/semantic.py` - NLP para categorização
- `src/ingestion/enrichment/deduplication.py`

**Funcionalidades:**
- Validação de campos obrigatórios
- Detecção de duplicatas (fuzzy matching)
- Enriquecimento semântico com NLP
- Sugestão de categorias

**Saída:**
- Dados validados e enriquecidos
- Deduplicação automática

---

## 🔄 FASE 3: ETL as a Service (Passos 21-25)

### Passo 21: Airflow Integration
**Commit:** `feat: integração com Apache Airflow`

**Arquivos a Criar:**
- `airflow/dags/etl_supplier_dag.py`
- `airflow/dags/catalog_sync_dag.py`
- `airflow/operators/custom_operators.py`
- `docker-compose.airflow.yml`

**Funcionalidades:**
- DAGs dinâmicos por fornecedor
- Scheduling configurável (15min → 1min)
- Retry logic
- Alertas de falha

**Saída:**
- Airflow configurado
- ETL automatizado

---

### Passo 22: ETL API Pública
**Commit:** `feat: API pública de ETL`

**Arquivos a Criar:**
- `src/api/routes/etl.py`
- `src/etl/api_service.py`
- `src/etl/job_manager.py`
- `docs/ETL_API.md` - Documentação da API

**Endpoints:**
```
POST /etl/run
GET  /etl/jobs
GET  /etl/jobs/{job_id}
POST /etl/jobs/{job_id}/cancel
GET  /etl/logs/{job_id}
```

**Funcionalidades:**
- Execução de ETL via API
- Job tracking em tempo real
- Logs streaming
- Rate limiting por plano

**Saída:**
- API de ETL funcional
- Documentação completa

---

### Passo 23: Configuração Zero-Code
**Commit:** `feat: configuração zero-code de ETL`

**Arquivos a Criar:**
- `frontend/etl-config/` - UI de configuração
- `src/etl/config_generator.py`
- `src/etl/templates/` - Templates de ETL

**Funcionalidades:**
- Interface visual de configuração
- Geração automática de DAGs
- Preview de dados
- Validação de configuração

**Saída:**
- UI de configuração funcional
- ETL configurável sem código

---

### Passo 24: Monitoramento de ETL
**Commit:** `feat: monitoramento e alertas de ETL`

**Arquivos a Criar:**
- `src/monitoring/__init__.py`
- `src/monitoring/metrics.py` - Prometheus metrics
- `src/monitoring/alerts.py` - Sistema de alertas
- `docker-compose.monitoring.yml` - Prometheus + Grafana

**Métricas:**
- Taxa de sucesso de jobs
- Tempo médio de execução
- Produtos processados/hora
- Erros por fornecedor

**Saída:**
- Dashboard Grafana
- Alertas automáticos

---

### Passo 25: Rate Limiting e Quotas
**Commit:** `feat: rate limiting e quotas por plano`

**Arquivos a Criar:**
- `src/billing/__init__.py`
- `src/billing/plans.py` - Definição de planos
- `src/billing/quota_manager.py`
- `src/api/middleware/rate_limiter.py`

**Quotas por Plano:**
```python
FREE: 1 supplier, 100 SKUs, sync 4h
BASIC: 5 suppliers, 1k SKUs, sync 1h
PRO: Unlimited, sync 15min, ETL API
ENTERPRISE: Custom, SLA 99.99%
```

**Saída:**
- Rate limiting ativo
- Quotas por plano

---

## 🌐 FASE 4: Portal B2C White-Label (Passos 26-30)

### Passo 26: Frontend Next.js Base
**Commit:** `feat: portal B2C com Next.js`

**Arquivos a Criar:**
- `frontend/b2c-portal/` - App Next.js
- `frontend/b2c-portal/pages/index.tsx`
- `frontend/b2c-portal/pages/products/[id].tsx`
- `frontend/b2c-portal/components/ProductCard.tsx`
- `frontend/b2c-portal/lib/api.ts`

**Páginas:**
- Home com produtos em destaque
- Listagem de produtos
- Detalhes do produto
- Busca e filtros

**Saída:**
- Portal B2C funcional
- SSR com Next.js

---

### Passo 27: Carrinho e Checkout
**Commit:** `feat: carrinho consolidado e checkout`

**Arquivos a Criar:**
- `frontend/b2c-portal/pages/cart.tsx`
- `frontend/b2c-portal/pages/checkout.tsx`
- `src/api/routes/cart.py`
- `src/api/routes/orders.py`
- `src/orders/__init__.py`
- `src/orders/manager.py`

**Funcionalidades:**
- Carrinho multi-fornecedor
- Cálculo de frete por fornecedor
- Checkout unificado
- Geração de pedidos

**Saída:**
- Carrinho funcional
- Checkout completo

---

### Passo 28: Integração de Pagamento (Stripe)
**Commit:** `feat: integração com Stripe`

**Arquivos a Criar:**
- `src/payments/__init__.py`
- `src/payments/stripe_handler.py`
- `src/api/routes/payments.py`
- `frontend/b2c-portal/pages/payment.tsx`

**Funcionalidades:**
- Checkout Stripe
- Webhooks de pagamento
- Reembolsos
- Histórico de transações

**Saída:**
- Pagamentos funcionais
- Webhooks configurados

---

### Passo 29: White-Label e Temas
**Commit:** `feat: sistema white-label com temas`

**Arquivos a Criar:**
- `src/themes/__init__.py`
- `src/themes/manager.py`
- `frontend/b2c-portal/styles/themes/`
- `src/api/routes/themes.py`

**Funcionalidades:**
- Temas customizáveis (cores, logo, fontes)
- CSS dinâmico por organização
- Preview de temas
- Embed code para sites externos

**Saída:**
- Portal white-label
- Temas customizáveis

---

### Passo 30: PWA e Offline Mode
**Commit:** `feat: PWA com cache offline`

**Arquivos a Criar:**
- `frontend/b2c-portal/public/manifest.json`
- `frontend/b2c-portal/public/sw.js` - Service Worker
- `frontend/b2c-portal/lib/offline-cache.ts`

**Funcionalidades:**
- Service Worker para cache
- Offline-first para produtos
- Push notifications
- Instalável como app

**Saída:**
- PWA funcional
- Cache offline

---

## 🔐 FASE 5: Rastreabilidade e Compliance (Passos 31-35)

### Passo 31: Merkle Tree para Rastreabilidade
**Commit:** `feat: merkle tree para rastreabilidade blockchain-light`

**Arquivos a Criar:**
- `src/traceability/__init__.py`
- `src/traceability/merkle_tree.py`
- `src/traceability/blockchain_light.py`
- `src/api/routes/traceability.py`

**Funcionalidades:**
- Merkle Tree para cada lote
- Hash chain de operações
- QR code com rastreabilidade
- Verificação pública

**Saída:**
- Sistema de rastreabilidade
- QR codes gerados

---

### Passo 32: Compliance LGPD
**Commit:** `feat: compliance LGPD completo`

**Arquivos a Criar:**
- `src/compliance/lgpd/__init__.py`
- `src/compliance/lgpd/consent_manager.py`
- `src/compliance/lgpd/data_export.py`
- `src/compliance/lgpd/data_deletion.py`
- `src/api/routes/lgpd.py`

**Funcionalidades:**
- Gestão de consentimento
- Exportação de dados (GDPR)
- Direito ao esquecimento
- Logs de acesso a dados pessoais

**Saída:**
- Compliance LGPD ativo
- APIs de privacidade

---

### Passo 33: Criptografia End-to-End
**Commit:** `feat: criptografia E2E e TLS 1.3`

**Arquivos a Criar:**
- `src/security/__init__.py`
- `src/security/encryption.py` - AES-256-GCM
- `src/security/key_manager.py`
- `config/tls/` - Certificados

**Funcionalidades:**
- Criptografia de dados sensíveis
- Key rotation automático
- TLS 1.3 obrigatório
- Secrets management (Vault)

**Saída:**
- Dados criptografados
- TLS 1.3 ativo

---

### Passo 34: Auditoria Avançada
**Commit:** `feat: auditoria avançada com imutabilidade`

**Arquivos a Criar:**
- `src/compliance/audit_advanced.py`
- `src/compliance/immutable_log.py`
- `src/api/routes/audit.py`
- `frontend/admin/audit-viewer/`

**Funcionalidades:**
- Logs imutáveis (append-only)
- Assinatura digital de logs
- Timeline de eventos
- Relatórios de auditoria

**Saída:**
- Auditoria imutável
- Dashboard de auditoria

---

### Passo 35: Certificações e Relatórios
**Commit:** `feat: geração de certificados e relatórios`

**Arquivos a Criar:**
- `src/reports/__init__.py`
- `src/reports/generator.py`
- `src/reports/templates/` - Templates PDF
- `src/api/routes/reports.py`

**Funcionalidades:**
- Certificados de rastreabilidade
- Relatórios de compliance
- Exportação em PDF
- Assinatura digital

**Saída:**
- Certificados gerados
- Relatórios automáticos

---

## 💰 FASE 6: Monetização e Analytics (Passos 36-40)

### Passo 36: Sistema de Billing
**Commit:** `feat: sistema de billing com Stripe`

**Arquivos a Criar:**
- `src/billing/subscription_manager.py`
- `src/billing/invoice_generator.py`
- `src/api/routes/billing.py`
- `frontend/admin/billing/`

**Funcionalidades:**
- Assinaturas recorrentes
- Upgrade/downgrade de planos
- Invoices automáticos
- Gestão de pagamentos

**Saída:**
- Billing funcional
- Assinaturas ativas

---

### Passo 37: Dashboard B2B (Admin)
**Commit:** `feat: dashboard B2B com React Admin`

**Arquivos a Criar:**
- `frontend/b2b-dashboard/` - React Admin
- `frontend/b2b-dashboard/resources/suppliers.tsx`
- `frontend/b2b-dashboard/resources/products.tsx`
- `frontend/b2b-dashboard/resources/orders.tsx`

**Funcionalidades:**
- CRUD completo de recursos
- Gráficos e métricas
- Gestão de fornecedores
- Relatórios de vendas

**Saída:**
- Dashboard B2B funcional
- Analytics em tempo real

---

### Passo 38: Analytics e BI
**Commit:** `feat: analytics e business intelligence`

**Arquivos a Criar:**
- `src/analytics/__init__.py`
- `src/analytics/metrics.py`
- `src/analytics/reports.py`
- `src/api/routes/analytics.py`

**Métricas:**
- Vendas por fornecedor
- Produtos mais vendidos
- Taxa de conversão
- Churn rate

**Saída:**
- Analytics completo
- Dashboards de BI

---

### Passo 39: IA para Demanda e Estoque
**Commit:** `feat: IA para previsão de demanda`

**Arquivos a Criar:**
- `src/ai/__init__.py`
- `src/ai/demand_forecast.py` - ML model
- `src/ai/stock_optimizer.py`
- `src/api/routes/ai.py`

**Funcionalidades:**
- Previsão de demanda (ARIMA/LSTM)
- Sugestões de estoque
- Alertas de ruptura
- Otimização de preços

**Saída:**
- IA de demanda ativa
- Sugestões automáticas

---

### Passo 40: Marketplace B2B
**Commit:** `feat: marketplace B2B para fornecedores`

**Arquivos a Criar:**
- `src/marketplace/__init__.py`
- `src/marketplace/listings.py`
- `src/api/routes/marketplace.py`
- `frontend/marketplace/`

**Funcionalidades:**
- Listagem de produtos B2B
- Negociação de preços
- Pedidos em lote
- Integração com logística

**Saída:**
- Marketplace B2B funcional
- Negociações ativas

---

## 📊 Resumo de Entregas

| Fase | Passos | Entregas Principais |
|------|--------|---------------------|
| 1 | 11-15 | PostgreSQL, Auth JWT, API REST, Docker, Testes |
| 2 | 16-20 | Ingestão multi-formato, Google Sheets, Webhooks, Mapeamento |
| 3 | 21-25 | Airflow, ETL API, Zero-code, Monitoramento, Quotas |
| 4 | 26-30 | Portal Next.js, Checkout, Stripe, White-label, PWA |
| 5 | 31-35 | Merkle Tree, LGPD, Criptografia, Auditoria, Certificados |
| 6 | 36-40 | Billing, Dashboard B2B, Analytics, IA, Marketplace |

**Total:** 30 passos commitáveis para transformar o projeto em plataforma SaaS completa.
