"""Classe base para extratores de fornecedores."""

import json
import time
from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime
from src.compliance.logger import ComplianceLogger
from src.config import RAW_DATA_DIR


class BaseExtractor(ABC):
    """Classe base para todos os extratores."""
    
    def __init__(self, supplier_id: str, supplier_config: Dict[str, Any]):
        self.supplier_id = supplier_id
        self.supplier_config = supplier_config
        self.logger = ComplianceLogger(supplier_id)
        self.rate_limit = supplier_config.get("extraction_config", {}).get("rate_limit", 10)
        self.user_agent = supplier_config.get("extraction_config", {}).get("user_agent", "MadeInNatural-Bot/1.0")
        self.output_file = RAW_DATA_DIR / f"{supplier_id}_raw_products.json"
    
    @abstractmethod
    def extract(self) -> List[Dict[str, Any]]:
        """Extrai produtos do fornecedor. Deve ser implementado por cada extrator."""
        pass
    
    def save_raw_data(self, products: List[Dict[str, Any]]):
        """Salva dados brutos extraídos."""
        output = {
            "supplier": self.supplier_id,
            "extraction_date": datetime.utcnow().isoformat() + "Z",
            "total_products": len(products),
            "products": products
        }
        
        with open(self.output_file, "w", encoding="utf-8") as f:
            json.dump(output, f, ensure_ascii=False, indent=2)
        
        print(f"✓ {len(products)} produtos salvos em {self.output_file}")
    
    def respect_rate_limit(self):
        """Respeita limite de requisições por minuto."""
        sleep_time = 60 / self.rate_limit
        time.sleep(sleep_time)
    
    def log_extraction(self, product: Dict[str, Any], source_url: str) -> str:
        """Registra extração no sistema de compliance."""
        return self.logger.log_extraction(product, source_url)
