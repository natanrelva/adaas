"""Extrator de produtos do fornecedor RMoura."""

import re
from typing import List, Dict, Any
from src.extractors.base_extractor import BaseExtractor


class RMouraExtractor(BaseExtractor):
    """Extrator para scraping HTML do site RMoura."""
    
    def __init__(self, supplier_config: Dict[str, Any]):
        super().__init__("rmoura", supplier_config)
        self.base_url = supplier_config["url"]
    
    def extract(self) -> List[Dict[str, Any]]:
        """Extrai produtos da página de produtos RMoura."""
        print(f"🔍 Iniciando extração: {self.supplier_id}")
        print(f"📍 URL: {self.base_url}")
        
        products = []
        
        try:
            # Simula extração (em produção faria scraping real)
            products = self._extract_mock_data()
            
            # Registra cada produto no sistema de compliance
            for product in products:
                hash_id = self.log_extraction(product, self.base_url)
                product["extraction_hash"] = hash_id
            
            self.save_raw_data(products)
            print(f"✅ Extração concluída: {len(products)} produtos")
            
        except Exception as e:
            print(f"❌ Erro na extração: {str(e)}")
            self.logger.log_extraction({}, self.base_url, status="error")
            raise
        
        return products
    
    def _extract_mock_data(self) -> List[Dict[str, Any]]:
        """Gera dados mock para demonstração (substituir por scraping real)."""
        mock_products = [
            {
                "supplier_product_id": "RMR001",
                "name": "Castanha do Pará Premium",
                "brand": "RMoura",
                "category": "Oleaginosas",
                "weight": 250,
                "unit": "g",
                "price": 32.90,
                "stock_available": True,
                "source_url": self.base_url
            },
            {
                "supplier_product_id": "RMR002",
                "name": "Mix de Nuts Especial",
                "brand": "RMoura",
                "category": "Oleaginosas",
                "weight": 300,
                "unit": "g",
                "price": 38.50,
                "stock_available": True,
                "source_url": self.base_url
            },
            {
                "supplier_product_id": "RMR003",
                "name": "Tâmaras Medjool",
                "brand": "RMoura",
                "category": "Frutas Secas",
                "weight": 200,
                "unit": "g",
                "price": 29.90,
                "stock_available": True,
                "source_url": self.base_url
            },
            {
                "supplier_product_id": "RMR004",
                "name": "Amêndoas Torradas",
                "brand": "RMoura",
                "category": "Oleaginosas",
                "weight": 200,
                "unit": "g",
                "price": 34.90,
                "stock_available": True,
                "source_url": self.base_url
            },
            {
                "supplier_product_id": "RMR005",
                "name": "Goji Berry Desidratada",
                "brand": "RMoura",
                "category": "Frutas Secas",
                "weight": 100,
                "unit": "g",
                "price": 24.90,
                "stock_available": True,
                "source_url": self.base_url
            },
            {
                "supplier_product_id": "RMR006",
                "name": "Nozes Chilenas",
                "brand": "RMoura",
                "category": "Oleaginosas",
                "weight": 250,
                "unit": "g",
                "price": 36.90,
                "stock_available": True,
                "source_url": self.base_url
            },
            {
                "supplier_product_id": "RMR007",
                "name": "Cranberry Desidratada",
                "brand": "RMoura",
                "category": "Frutas Secas",
                "weight": 150,
                "unit": "g",
                "price": 22.90,
                "stock_available": True,
                "source_url": self.base_url
            }
        ]
        
        return mock_products
