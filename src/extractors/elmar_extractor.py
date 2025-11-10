"""Extrator de produtos do fornecedor Elmar."""

import xml.etree.ElementTree as ET
from typing import List, Dict, Any
from src.extractors.base_extractor import BaseExtractor


class ElmarExtractor(BaseExtractor):
    """Extrator para XML e planilhas do fornecedor Elmar."""
    
    def __init__(self, supplier_config: Dict[str, Any]):
        super().__init__("elmar", supplier_config)
        self.base_url = supplier_config["url"]
    
    def extract(self) -> List[Dict[str, Any]]:
        """Extrai produtos do XML/planilhas Elmar."""
        print(f"🔍 Iniciando extração: {self.supplier_id}")
        print(f"📍 URL: {self.base_url}")
        
        products = []
        
        try:
            # Simula extração (em produção faria parsing real de XML)
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
        """Gera dados mock para demonstração (substituir por parsing XML real)."""
        mock_products = [
            {
                "supplier_product_id": "ELM001",
                "name": "Quinoa em Grãos Orgânica",
                "brand": "Elmar",
                "category": "Grãos",
                "weight": 500,
                "unit": "g",
                "price": 24.90,
                "stock_available": True,
                "source_url": self.base_url
            },
            {
                "supplier_product_id": "ELM002",
                "name": "Chia Preta Premium",
                "brand": "Elmar",
                "category": "Sementes",
                "weight": 250,
                "unit": "g",
                "price": 19.90,
                "stock_available": True,
                "source_url": self.base_url
            },
            {
                "supplier_product_id": "ELM003",
                "name": "Linhaça Dourada Moída",
                "brand": "Elmar",
                "category": "Sementes",
                "weight": 200,
                "unit": "g",
                "price": 14.50,
                "stock_available": True,
                "source_url": self.base_url
            },
            {
                "supplier_product_id": "ELM004",
                "name": "Arroz Integral Orgânico",
                "brand": "Elmar",
                "category": "Grãos",
                "weight": 1,
                "unit": "kg",
                "price": 16.90,
                "stock_available": True,
                "source_url": self.base_url
            },
            {
                "supplier_product_id": "ELM005",
                "name": "Pasta de Amendoim Integral",
                "brand": "Elmar",
                "category": "Pastas",
                "weight": 500,
                "unit": "g",
                "price": 26.90,
                "stock_available": True,
                "source_url": self.base_url
            },
            {
                "supplier_product_id": "ELM006",
                "name": "Açúcar de Coco Natural",
                "brand": "Elmar",
                "category": "Açúcares e Adoçantes",
                "weight": 250,
                "unit": "g",
                "price": 21.90,
                "stock_available": True,
                "source_url": self.base_url
            }
        ]
        
        return mock_products
    
    def _parse_xml(self, xml_content: str) -> List[Dict[str, Any]]:
        """Método para parsing real de XML (implementar quando necessário)."""
        products = []
        
        try:
            root = ET.fromstring(xml_content)
            
            # Exemplo de parsing (ajustar conforme estrutura real do XML)
            for product_elem in root.findall(".//product"):
                product = {
                    "supplier_product_id": product_elem.find("id").text,
                    "name": product_elem.find("name").text,
                    "brand": product_elem.find("brand").text or "Elmar",
                    "category": product_elem.find("category").text or "Geral",
                    "weight": float(product_elem.find("weight").text or 0),
                    "unit": product_elem.find("unit").text or "un",
                    "price": float(product_elem.find("price").text or 0),
                    "stock_available": product_elem.find("stock").text.lower() == "true",
                    "source_url": self.base_url
                }
                
                products.append(product)
                self.respect_rate_limit()
        
        except ET.ParseError as e:
            print(f"❌ Erro ao parsear XML: {str(e)}")
            raise
        
        return products
