"""Gerenciador do catálogo central unificado."""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
from src.compliance.logger import ComplianceLogger
from src.config import CATALOG_FILE, NORMALIZED_DATA_DIR


class CatalogManager:
    """Gerencia o catálogo central de produtos."""
    
    def __init__(self):
        self.catalog_file = CATALOG_FILE
        self.catalog = self._load_catalog()
    
    def _load_catalog(self) -> Dict[str, Any]:
        """Carrega catálogo existente ou cria novo."""
        if self.catalog_file.exists():
            with open(self.catalog_file, "r", encoding="utf-8") as f:
                return json.load(f)
        
        return {
            "version": "1.0.0",
            "last_updated": datetime.utcnow().isoformat() + "Z",
            "products": [],
            "metadata": {
                "total_products": 0,
                "suppliers": {
                    "gramore": 0,
                    "elmar": 0,
                    "rmoura": 0
                }
            }
        }
    
    def integrate_supplier(self, supplier_id: str) -> int:
        """Integra produtos de um fornecedor no catálogo central."""
        print(f"🔗 Integrando produtos: {supplier_id}")
        
        # Carrega produtos normalizados
        normalized_file = NORMALIZED_DATA_DIR / f"{supplier_id}_products_normalized.json"
        
        if not normalized_file.exists():
            raise FileNotFoundError(f"Produtos normalizados não encontrados: {normalized_file}")
        
        with open(normalized_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        products = data.get("products", [])
        logger = ComplianceLogger(supplier_id)
        
        # Remove produtos antigos do mesmo fornecedor
        self.catalog["products"] = [
            p for p in self.catalog["products"]
            if p.get("supplier") != supplier_id
        ]
        
        # Adiciona novos produtos
        integrated_count = 0
        for product in products:
            # Indexa produto no catálogo
            self.catalog["products"].append(product)
            
            # Registra integração no log de compliance
            logger.log_catalog_integration(
                product["id"],
                product["id"],
                status="success"
            )
            
            integrated_count += 1
            print(f"  ✓ {product['name']}")
        
        # Atualiza metadados
        self._update_metadata()
        
        # Salva catálogo
        self._save_catalog()
        
        print(f"✅ Integração concluída: {integrated_count} produtos")
        return integrated_count
    
    def search_products(
        self,
        query: Optional[str] = None,
        category: Optional[str] = None,
        supplier: Optional[str] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None
    ) -> List[Dict[str, Any]]:
        """Busca produtos no catálogo com filtros."""
        results = self.catalog["products"]
        
        # Filtro por texto
        if query:
            query_lower = query.lower()
            results = [
                p for p in results
                if query_lower in p["name"].lower() or
                   query_lower in p.get("brand", "").lower() or
                   query_lower in p.get("category", "").lower()
            ]
        
        # Filtro por categoria
        if category:
            results = [p for p in results if p.get("category") == category]
        
        # Filtro por fornecedor
        if supplier:
            results = [p for p in results if p.get("supplier") == supplier]
        
        # Filtro por preço
        if min_price is not None:
            results = [p for p in results if p["price"]["final"] >= min_price]
        
        if max_price is not None:
            results = [p for p in results if p["price"]["final"] <= max_price]
        
        return results
    
    def compare_products(self, product_name: str) -> List[Dict[str, Any]]:
        """Compara produtos similares de diferentes fornecedores."""
        # Busca produtos com nome similar
        similar_products = self.search_products(query=product_name)
        
        # Ordena por preço final
        similar_products.sort(key=lambda p: p["price"]["final"])
        
        return similar_products
    
    def get_product_by_id(self, product_id: str) -> Optional[Dict[str, Any]]:
        """Busca produto por ID."""
        for product in self.catalog["products"]:
            if product["id"] == product_id:
                return product
        return None
    
    def get_supplier_products(self, supplier_id: str) -> List[Dict[str, Any]]:
        """Retorna todos os produtos de um fornecedor."""
        return [
            p for p in self.catalog["products"]
            if p.get("supplier") == supplier_id
        ]
    
    def get_categories(self) -> List[str]:
        """Retorna lista de categorias disponíveis."""
        categories = set()
        for product in self.catalog["products"]:
            if product.get("category"):
                categories.add(product["category"])
        return sorted(list(categories))
    
    def get_statistics(self) -> Dict[str, Any]:
        """Retorna estatísticas do catálogo."""
        products = self.catalog["products"]
        
        if not products:
            return {
                "total_products": 0,
                "suppliers": {},
                "categories": [],
                "price_range": {"min": 0, "max": 0, "avg": 0}
            }
        
        prices = [p["price"]["final"] for p in products]
        
        return {
            "total_products": len(products),
            "suppliers": self.catalog["metadata"]["suppliers"],
            "categories": self.get_categories(),
            "price_range": {
                "min": min(prices),
                "max": max(prices),
                "avg": round(sum(prices) / len(prices), 2)
            }
        }
    
    def _update_metadata(self):
        """Atualiza metadados do catálogo."""
        self.catalog["last_updated"] = datetime.utcnow().isoformat() + "Z"
        self.catalog["metadata"]["total_products"] = len(self.catalog["products"])
        
        # Conta produtos por fornecedor
        for supplier in ["gramore", "elmar", "rmoura"]:
            count = sum(1 for p in self.catalog["products"] if p.get("supplier") == supplier)
            self.catalog["metadata"]["suppliers"][supplier] = count
    
    def _save_catalog(self):
        """Salva catálogo em arquivo."""
        with open(self.catalog_file, "w", encoding="utf-8") as f:
            json.dump(self.catalog, f, ensure_ascii=False, indent=2)
        
        print(f"💾 Catálogo salvo: {self.catalog_file}")
