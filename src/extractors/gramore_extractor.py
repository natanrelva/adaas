"""Extrator de produtos do fornecedor Gramore."""

import re
import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Any
from src.extractors.base_extractor import BaseExtractor


class GramoreExtractor(BaseExtractor):
    """Extrator para scraping HTML do site Gramore."""
    
    def __init__(self, supplier_config: Dict[str, Any]):
        super().__init__("gramore", supplier_config)
        self.base_url = supplier_config["url"]
    
    def extract(self) -> List[Dict[str, Any]]:
        """Extrai produtos da página de preços Gramore."""
        print(f"🔍 Iniciando extração: {self.supplier_id}")
        print(f"📍 URL: {self.base_url}")
        
        products = []
        
        try:
            # Simula extração (em produção faria scraping real)
            # Por enquanto, cria dados de exemplo para demonstração
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
        # Em produção, aqui seria o scraping real com BeautifulSoup
        mock_products = [
            {
                "supplier_product_id": "GRM001",
                "name": "Açúcar Mascavo Orgânico",
                "brand": "Gramore",
                "category": "Açúcares e Adoçantes",
                "weight": 500,
                "unit": "g",
                "price": 12.90,
                "stock_available": True,
                "source_url": self.base_url
            },
            {
                "supplier_product_id": "GRM002",
                "name": "Farinha de Aveia Integral",
                "brand": "Gramore",
                "category": "Farinhas",
                "weight": 1,
                "unit": "kg",
                "price": 18.50,
                "stock_available": True,
                "source_url": self.base_url
            },
            {
                "supplier_product_id": "GRM003",
                "name": "Granola Tradicional",
                "brand": "Gramore",
                "category": "Cereais",
                "weight": 800,
                "unit": "g",
                "price": 22.90,
                "stock_available": True,
                "source_url": self.base_url
            },
            {
                "supplier_product_id": "GRM004",
                "name": "Mel Orgânico Silvestre",
                "brand": "Gramore",
                "category": "Mel e Derivados",
                "weight": 500,
                "unit": "g",
                "price": 35.00,
                "stock_available": True,
                "source_url": self.base_url
            },
            {
                "supplier_product_id": "GRM005",
                "name": "Castanha de Caju Torrada",
                "brand": "Gramore",
                "category": "Oleaginosas",
                "weight": 200,
                "unit": "g",
                "price": 28.90,
                "stock_available": True,
                "source_url": self.base_url
            }
        ]
        
        return mock_products
    
    def _scrape_real_data(self) -> List[Dict[str, Any]]:
        """Método para scraping real (implementar quando necessário)."""
        headers = {
            "User-Agent": self.user_agent
        }
        
        response = requests.get(self.base_url, headers=headers, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, "html.parser")
        products = []
        
        # Exemplo de extração (ajustar conforme estrutura real do site)
        product_blocks = soup.find_all("div", class_="product-item")
        
        for block in product_blocks:
            self.respect_rate_limit()
            
            product = {
                "supplier_product_id": self._extract_product_id(block),
                "name": self._extract_name(block),
                "brand": "Gramore",
                "category": self._extract_category(block),
                "weight": self._extract_weight(block),
                "unit": self._extract_unit(block),
                "price": self._extract_price(block),
                "stock_available": self._extract_stock(block),
                "source_url": self.base_url
            }
            
            products.append(product)
        
        return products
    
    def _extract_product_id(self, block) -> str:
        """Extrai ID do produto do HTML."""
        # Implementar conforme estrutura real
        return block.get("data-product-id", "unknown")
    
    def _extract_name(self, block) -> str:
        """Extrai nome do produto."""
        name_elem = block.find("h3", class_="product-name")
        return name_elem.text.strip() if name_elem else "Unknown"
    
    def _extract_category(self, block) -> str:
        """Extrai categoria do produto."""
        cat_elem = block.find("span", class_="category")
        return cat_elem.text.strip() if cat_elem else "Geral"
    
    def _extract_weight(self, block) -> float:
        """Extrai peso/quantidade do produto."""
        weight_elem = block.find("span", class_="weight")
        if weight_elem:
            weight_text = weight_elem.text.strip()
            match = re.search(r"(\d+(?:\.\d+)?)", weight_text)
            return float(match.group(1)) if match else 0.0
        return 0.0
    
    def _extract_unit(self, block) -> str:
        """Extrai unidade de medida."""
        weight_elem = block.find("span", class_="weight")
        if weight_elem:
            text = weight_elem.text.strip().lower()
            if "kg" in text:
                return "kg"
            elif "g" in text:
                return "g"
            elif "l" in text:
                return "l"
            elif "ml" in text:
                return "ml"
        return "un"
    
    def _extract_price(self, block) -> float:
        """Extrai preço do produto."""
        price_elem = block.find("span", class_="price")
        if price_elem:
            price_text = price_elem.text.strip()
            match = re.search(r"(\d+(?:,\d+)?)", price_text)
            if match:
                return float(match.group(1).replace(",", "."))
        return 0.0
    
    def _extract_stock(self, block) -> bool:
        """Verifica disponibilidade em estoque."""
        stock_elem = block.find("span", class_="stock-status")
        if stock_elem:
            return "disponível" in stock_elem.text.lower()
        return True
