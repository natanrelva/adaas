"""Configurações centrais do projeto Made in Natural."""

import os
from pathlib import Path

# Diretórios base
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
SCHEMAS_DIR = BASE_DIR / "schemas"
LOGS_DIR = BASE_DIR / "logs"

# Diretórios de dados
RAW_DATA_DIR = DATA_DIR / "raw"
NORMALIZED_DATA_DIR = DATA_DIR / "normalized"
CATALOG_DIR = DATA_DIR / "catalog"

# Criar diretórios se não existirem
for directory in [RAW_DATA_DIR, NORMALIZED_DATA_DIR, CATALOG_DIR, LOGS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# Configurações de negócio
BUSINESS_RULES = {
    "default_margin": 0.30,  # 30% de margem padrão
    "default_shipping": 15.00,  # R$ 15,00 frete padrão
    "min_stock_quantity": 1,
}

# Configurações de compliance
COMPLIANCE = {
    "log_retention_days": 365,
    "audit_frequency_days": 90,
    "require_consent": True,
}

# Fornecedores
SUPPLIERS_FILE = DATA_DIR / "suppliers.json"
CATALOG_FILE = CATALOG_DIR / "catalog_repository.json"
