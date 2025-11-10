# Arquitetura do Sistema

## Visão Geral

O Made in Natural é uma plataforma B2B2C modular que conecta fornecedores de produtos naturais ao varejo, utilizando uma arquitetura de pipeline ETL com governança completa.

## Componentes Principais

### 1. Camada de Extração (Extractors)

Responsável por capturar dados de diferentes fontes:

```
BaseExtractor (classe abstrata)
├── GramoreExtractor (HTML scraping)
├── ElmarExtractor (XML/planilhas)
└── RMouraExtractor (HTML scraping)
```

**Características:**
- Rate limiting configurável por fornecedor
- Respeito a robots.txt
- Logging automático de todas as operações
- Geração de hash SHA-256 para rastreabilidade
- Tratamento de erros e retry logic

### 2. Camada de Transformação (Transformers)

Normaliza dados heterogêneos em schema único:

```
ProductTransformer
├── Validação de schema JSON
├── Aplicação de regras de negócio
├── Cálculo de preços (margem + frete)
└── Geração de IDs únicos
```

**Regras de Negócio:**
- Margem padrão: 30%
- Frete padrão: R$ 15,00
- Estoque mínimo: 1 unidade

### 3. Catálogo Central (Catalog)

Repositório unificado de produtos:

```
CatalogManager
├── Integração de produtos normalizados
├── Sistema de busca e filtros
├── Comparação entre fornecedores
├── Estatísticas e analytics
└── Gerenciamento de metadados
```

**Funcionalidades:**
- Busca full-text
- Filtros por categoria, fornecedor, preço
- Comparação de produtos similares
- Remoção de duplicatas
- Atualização incremental

### 4. Sistema de Compliance

Garante rastreabilidade e auditoria:

```
Compliance
├── ComplianceLogger (logs imutáveis)
└── ComplianceAuditor (auditoria e relatórios)
```

**Características:**
- Logs em formato JSONL (append-only)
- Hash SHA-256 em cada operação
- Rastreabilidade produto-a-produto
- Auditoria automatizada
- Política de retenção configurável

## Fluxo de Dados

```
┌─────────────┐
│ Fornecedor  │
│  (HTML/XML) │
└──────┬──────┘
       │
       ▼
┌─────────────┐     ┌──────────────┐
│  Extractor  │────▶│ Raw Data     │
│             │     │ (JSON)       │
└──────┬──────┘     └──────────────┘
       │
       ▼
┌─────────────┐     ┌──────────────┐
│ Transformer │────▶│ Normalized   │
│             │     │ Data (JSON)  │
└──────┬──────┘     └──────────────┘
       │
       ▼
┌─────────────┐     ┌──────────────┐
│  Catalog    │────▶│ Catalog      │
│  Manager    │     │ Repository   │
└─────────────┘     └──────────────┘
       │
       ▼
┌─────────────┐
│   B2C API   │
│  (Futuro)   │
└─────────────┘

       │ (paralelo)
       ▼
┌─────────────┐     ┌──────────────┐
│ Compliance  │────▶│ Audit Logs   │
│  Logger     │     │ (JSONL)      │
└─────────────┘     └──────────────┘
```

## Padrões de Projeto

### 1. Template Method
`BaseExtractor` define o fluxo de extração, subclasses implementam detalhes específicos.

### 2. Strategy
Diferentes estratégias de extração (HTML, XML, API) encapsuladas em classes específicas.

### 3. Repository
`CatalogManager` abstrai acesso ao catálogo central.

### 4. Observer (implícito)
`ComplianceLogger` observa todas as operações ETL.

## Schemas de Dados

### Product Schema
```json
{
  "id": "string (hash)",
  "supplier": "enum [gramore, elmar, rmoura]",
  "name": "string",
  "price": {
    "base": "number",
    "margin": "number",
    "shipping": "number",
    "final": "number"
  },
  "stock": {
    "available": "boolean",
    "quantity": "integer"
  },
  "metadata": {
    "hash": "string (SHA-256)",
    "extraction_date": "datetime"
  }
}
```

### Supplier Schema
```json
{
  "id": "string",
  "name": "string",
  "data_type": "enum [html, xml, csv, api]",
  "url": "uri",
  "consent_obtained": "boolean",
  "extraction_config": {
    "rate_limit": "integer",
    "user_agent": "string"
  }
}
```

## Segurança e Compliance

### Rastreabilidade
- Cada operação gera hash SHA-256
- Logs imutáveis em formato JSONL
- Linha do tempo completa por produto

### Auditoria
- Taxa de sucesso das operações
- Verificação de integridade de dados
- Relatórios automatizados
- Política de retenção: 365 dias

### Consentimento
- Registro de consentimento por fornecedor
- Verificação antes de cada extração
- Metadados de data e validade

## Escalabilidade

### Horizontal
- Extratores independentes (podem rodar em paralelo)
- Catálogo centralizado com lock otimista
- Logs distribuídos por fornecedor

### Vertical
- Cache de produtos em memória (futuro)
- Índices de busca otimizados (futuro)
- Compressão de logs antigos (futuro)

## Monitoramento

### Métricas
- Total de produtos por fornecedor
- Taxa de sucesso de extração
- Tempo médio de pipeline
- Faixa de preços

### Alertas (futuro)
- Falha de extração
- Taxa de sucesso < 95%
- Logs fora da política de retenção

## Extensibilidade

### Adicionar Novo Fornecedor
1. Criar classe herdando de `BaseExtractor`
2. Implementar método `extract()`
3. Adicionar configuração em `suppliers.json`
4. Registrar em `run_all_pipelines.py`

### Adicionar Nova Regra de Negócio
1. Atualizar `BUSINESS_RULES` em `config.py`
2. Modificar `ProductTransformer._normalize_product()`
3. Atualizar schema se necessário

### Adicionar Novo Tipo de Auditoria
1. Adicionar método em `ComplianceAuditor`
2. Atualizar `audit_compliance.py`
3. Documentar no relatório
