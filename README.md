# Made in Natural – Hub Modular e Orquestrado

Plataforma intermediária conectando fornecedores B2B de produtos naturais ao varejo B2C, com pipeline modular ETL, unificação de catálogo, interface B2C e governança completa.

## 🎯 Visão Geral

Sistema completo de integração B2B2C que:
- Extrai produtos de múltiplos fornecedores (HTML, XML, APIs)
- Normaliza dados em schema único padronizado
- Unifica catálogo central com busca e comparação
- Garante rastreabilidade e compliance total

## 📦 Fornecedores Integrados

| Fornecedor | Tipo de Dados | Produtos | Status |
|------------|---------------|----------|--------|
| **Gramore** | HTML Scraping | 5 produtos | ✅ Ativo |
| **Elmar** | XML/Planilhas | 6 produtos | ✅ Ativo |
| **RMoura** | HTML Scraping | 7 produtos | ✅ Ativo |

## 🚀 Início Rápido

### Instalação

```bash
# Instalar dependências
pip install -r requirements.txt
```

### Executar Pipeline Completo

```bash
# Processar todos os fornecedores
python scripts/run_all_pipelines.py

# Ou processar individualmente
python scripts/run_gramore_pipeline.py
python scripts/run_elmar_pipeline.py
python scripts/run_rmoura_pipeline.py
```

### Buscar no Catálogo

```bash
# Interface interativa de busca
python scripts/search_catalog.py
```

### Auditoria e Compliance

```bash
# Sistema de auditoria completo
python scripts/audit_compliance.py
```

## 📁 Estrutura do Projeto

```
made-in-natural-full/
├── src/
│   ├── extractors/          # Extratores por fornecedor
│   │   ├── base_extractor.py
│   │   ├── gramore_extractor.py
│   │   ├── elmar_extractor.py
│   │   └── rmoura_extractor.py
│   ├── transformers/        # Normalização de dados
│   │   └── product_transformer.py
│   ├── catalog/             # Catálogo central
│   │   └── catalog_manager.py
│   ├── compliance/          # Auditoria e governança
│   │   ├── logger.py
│   │   └── auditor.py
│   └── config.py            # Configurações centrais
├── schemas/                 # Schemas JSON de validação
│   ├── product_schema.json
│   └── supplier_schema.json
├── data/
│   ├── suppliers.json       # Registro de fornecedores
│   ├── raw/                 # Dados brutos extraídos
│   ├── normalized/          # Dados normalizados
│   └── catalog/             # Catálogo unificado
│       └── catalog_repository.json
├── logs/                    # Logs de auditoria (JSONL)
├── scripts/                 # Scripts executáveis
│   ├── run_all_pipelines.py
│   ├── search_catalog.py
│   └── audit_compliance.py
└── main.yml                 # Planejamento completo
```

## 🔄 Fluxo ETL

### 1. Extração
- Captura dados do fornecedor (HTML, XML, API)
- Respeita rate limits e robots.txt
- Registra hash SHA-256 para rastreabilidade
- Logs imutáveis em formato JSONL

### 2. Transformação
- Normaliza para schema único JSON
- Aplica regras de negócio:
  - Margem padrão: 30%
  - Frete padrão: R$ 15,00
- Valida integridade dos dados
- Gera IDs únicos por produto

### 3. Integração
- Unifica produtos no catálogo central
- Remove duplicatas do mesmo fornecedor
- Indexa para busca e comparação
- Atualiza metadados e estatísticas

### 4. Compliance
- Logs imutáveis de todas as operações
- Rastreabilidade completa produto-a-produto
- Auditoria trimestral automatizada
- Política de retenção: 365 dias

## 🔍 Funcionalidades do Catálogo

### Busca de Produtos
```python
from src.catalog.catalog_manager import CatalogManager

catalog = CatalogManager()

# Busca por texto
products = catalog.search_products(query="açúcar")

# Filtro por categoria
products = catalog.search_products(category="Oleaginosas")

# Filtro por faixa de preço
products = catalog.search_products(min_price=20, max_price=50)
```

### Comparação de Produtos
```python
# Compara produtos similares de diferentes fornecedores
similar = catalog.compare_products("castanha")
# Retorna produtos ordenados por preço
```

### Estatísticas
```python
stats = catalog.get_statistics()
# {
#   "total_products": 18,
#   "suppliers": {"gramore": 5, "elmar": 6, "rmoura": 7},
#   "price_range": {"min": 12.90, "max": 53.50, "avg": 32.45}
# }
```

## 🔐 Compliance e Auditoria

### Logs Imutáveis
Todas as operações são registradas em formato JSONL:
```json
{
  "timestamp": "2025-11-10T12:00:00Z",
  "operation": "extraction",
  "supplier": "gramore",
  "product_id": "GRM001",
  "data_hash": "a1b2c3d4...",
  "status": "success"
}
```

### Rastreabilidade
```python
from src.compliance.auditor import ComplianceAuditor

auditor = ComplianceAuditor()

# Verifica rastreabilidade de um produto
trace = auditor.verify_traceability("GRM001", "gramore")
# Retorna linha do tempo completa: extração → transformação → validação → integração
```

### Auditoria
```python
# Audita fornecedor específico
result = auditor.audit_supplier("gramore")

# Audita todos os fornecedores
results = auditor.audit_all_suppliers()

# Verifica política de retenção
retention = auditor.check_retention_policy()
```

## 📊 Schema de Dados

### Produto Normalizado
```json
{
  "id": "a1b2c3d4e5f6g7h8",
  "supplier": "gramore",
  "supplier_product_id": "GRM001",
  "name": "Açúcar Mascavo Orgânico",
  "brand": "Gramore",
  "category": "Açúcares e Adoçantes",
  "weight": 500,
  "unit": "g",
  "price": {
    "base": 12.90,
    "margin": 30,
    "shipping": 15.00,
    "final": 31.77
  },
  "stock": {
    "available": true,
    "quantity": 100
  },
  "metadata": {
    "extraction_date": "2025-11-10T12:00:00Z",
    "source_url": "https://gramore.com.br/precos",
    "hash": "a1b2c3d4..."
  }
}
```

## 🛠️ Scripts Disponíveis

| Script | Descrição |
|--------|-----------|
| `run_all_pipelines.py` | Executa ETL completo de todos os fornecedores |
| `run_gramore_pipeline.py` | Pipeline individual Gramore |
| `run_elmar_pipeline.py` | Pipeline individual Elmar |
| `run_rmoura_pipeline.py` | Pipeline individual RMoura |
| `search_catalog.py` | Interface de busca e comparação |
| `audit_compliance.py` | Sistema de auditoria e relatórios |

## 📋 Requisitos

- Python 3.8+
- requests
- beautifulsoup4
- lxml
- jsonschema
- python-dateutil

## 🎯 Próximos Passos

Ver `main.yml` para planejamento completo das próximas fases:
- Interface B2C web
- Carrinho unificado multi-fornecedor
- API REST para integração
- Dashboard de analytics
- Sistema de notificações

## 📄 Licença

Projeto interno - Made in Natural © 2025
