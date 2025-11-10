# API de Referência

## CatalogManager

Gerenciador do catálogo central de produtos.

### Métodos

#### `integrate_supplier(supplier_id: str) -> int`
Integra produtos de um fornecedor no catálogo.

**Parâmetros:**
- `supplier_id`: ID do fornecedor (gramore, elmar, rmoura)

**Retorna:**
- Número de produtos integrados

**Exemplo:**
```python
catalog = CatalogManager()
count = catalog.integrate_supplier("gramore")
print(f"Integrados: {count} produtos")
```

---

#### `search_products(query=None, category=None, supplier=None, min_price=None, max_price=None) -> List[Dict]`
Busca produtos com filtros opcionais.

**Parâmetros:**
- `query`: Termo de busca (nome, marca, categoria)
- `category`: Filtro por categoria
- `supplier`: Filtro por fornecedor
- `min_price`: Preço mínimo
- `max_price`: Preço máximo

**Retorna:**
- Lista de produtos que atendem aos critérios

**Exemplo:**
```python
# Busca por texto
products = catalog.search_products(query="açúcar")

# Busca com múltiplos filtros
products = catalog.search_products(
    category="Oleaginosas",
    min_price=20,
    max_price=50
)
```

---

#### `compare_products(product_name: str) -> List[Dict]`
Compara produtos similares de diferentes fornecedores.

**Parâmetros:**
- `product_name`: Nome do produto para comparação

**Retorna:**
- Lista de produtos similares ordenados por preço

**Exemplo:**
```python
similar = catalog.compare_products("castanha")
for product in similar:
    print(f"{product['name']} - R$ {product['price']['final']:.2f}")
```

---

#### `get_statistics() -> Dict`
Retorna estatísticas do catálogo.

**Retorna:**
```python
{
    "total_products": int,
    "suppliers": {
        "gramore": int,
        "elmar": int,
        "rmoura": int
    },
    "categories": List[str],
    "price_range": {
        "min": float,
        "max": float,
        "avg": float
    }
}
```

---

## ComplianceLogger

Sistema de logging para auditoria.

### Métodos

#### `log_extraction(product_data: Dict, source_url: str, status="success") -> str`
Registra extração de produto.

**Parâmetros:**
- `product_data`: Dados do produto extraído
- `source_url`: URL de origem
- `status`: Status da operação (success/error)

**Retorna:**
- Hash SHA-256 dos dados

**Exemplo:**
```python
logger = ComplianceLogger("gramore")
hash_id = logger.log_extraction(product, "https://gramore.com.br")
```

---

#### `log_transformation(product_id: str, raw_hash: str, normalized_data: Dict, status="success") -> str`
Registra transformação de produto.

**Parâmetros:**
- `product_id`: ID do produto
- `raw_hash`: Hash dos dados brutos
- `normalized_data`: Dados normalizados
- `status`: Status da operação

**Retorna:**
- Hash SHA-256 dos dados normalizados

---

#### `log_validation(product_id: str, validation_result: bool, errors=None)`
Registra validação de schema.

**Parâmetros:**
- `product_id`: ID do produto
- `validation_result`: Resultado da validação (True/False)
- `errors`: Lista de erros (opcional)

---

#### `log_catalog_integration(product_id: str, catalog_id: str, status="success")`
Registra integração no catálogo.

**Parâmetros:**
- `product_id`: ID do produto
- `catalog_id`: ID no catálogo
- `status`: Status da operação

---

## ComplianceAuditor

Sistema de auditoria e compliance.

### Métodos

#### `audit_supplier(supplier_id: str) -> Dict`
Audita logs de um fornecedor.

**Parâmetros:**
- `supplier_id`: ID do fornecedor

**Retorna:**
```python
{
    "supplier": str,
    "audit_date": str,
    "total_operations": int,
    "operations_by_type": Dict[str, int],
    "success_rate": float,
    "data_integrity": Dict,
    "compliance_status": str  # "compliant" ou "warning"
}
```

---

#### `audit_all_suppliers() -> List[Dict]`
Audita todos os fornecedores.

**Retorna:**
- Lista de resultados de auditoria

---

#### `verify_traceability(product_id: str, supplier_id: str) -> Dict`
Verifica rastreabilidade de um produto.

**Parâmetros:**
- `product_id`: ID do produto
- `supplier_id`: ID do fornecedor

**Retorna:**
```python
{
    "traceable": bool,
    "product_id": str,
    "supplier": str,
    "operations_found": List[str],
    "timeline": List[Dict]  # Linha do tempo completa
}
```

---

#### `check_retention_policy() -> Dict`
Verifica política de retenção de logs.

**Retorna:**
```python
{
    "retention_days": int,
    "logs_to_archive": int,
    "cutoff_date": str
}
```

---

## ProductTransformer

Transformador de produtos para schema único.

### Métodos

#### `transform() -> List[Dict]`
Transforma todos os produtos do fornecedor.

**Retorna:**
- Lista de produtos normalizados

**Exemplo:**
```python
transformer = ProductTransformer("gramore")
products = transformer.transform()
```

---

## BaseExtractor

Classe base para extratores (abstrata).

### Métodos

#### `extract() -> List[Dict]`
Extrai produtos do fornecedor (método abstrato).

**Retorna:**
- Lista de produtos brutos

---

#### `save_raw_data(products: List[Dict])`
Salva dados brutos extraídos.

**Parâmetros:**
- `products`: Lista de produtos

---

#### `respect_rate_limit()`
Aguarda conforme rate limit configurado.

---

## Exemplos de Uso Completo

### Pipeline Manual

```python
from src.extractors.gramore_extractor import GramoreExtractor
from src.transformers.product_transformer import ProductTransformer
from src.catalog.catalog_manager import CatalogManager
import json

# 1. Carregar configuração
with open("data/suppliers.json") as f:
    suppliers = json.load(f)
    config = next(s for s in suppliers if s["id"] == "gramore")

# 2. Extração
extractor = GramoreExtractor(config)
raw_products = extractor.extract()

# 3. Transformação
transformer = ProductTransformer("gramore")
normalized = transformer.transform()

# 4. Integração
catalog = CatalogManager()
count = catalog.integrate_supplier("gramore")

print(f"Pipeline concluído: {count} produtos integrados")
```

### Busca Avançada

```python
catalog = CatalogManager()

# Busca produtos de oleaginosas entre R$ 20 e R$ 40
products = catalog.search_products(
    category="Oleaginosas",
    min_price=20,
    max_price=40
)

# Exibe resultados
for p in products:
    print(f"{p['name']} ({p['supplier']}) - R$ {p['price']['final']:.2f}")
```

### Auditoria Completa

```python
from src.compliance.auditor import ComplianceAuditor

auditor = ComplianceAuditor()

# Audita todos os fornecedores
results = auditor.audit_all_suppliers()

for result in results:
    print(f"{result['supplier']}: {result['compliance_status']}")
    print(f"  Taxa de sucesso: {result['success_rate']:.1%}")

# Verifica rastreabilidade de produto específico
trace = auditor.verify_traceability("GRM001", "gramore")
if trace['traceable']:
    print("Produto rastreável!")
    for log in trace['timeline']:
        print(f"  {log['timestamp']} - {log['operation']}")
```
