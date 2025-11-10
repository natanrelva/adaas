"""Transformador para normalizar produtos em schema único."""

import json
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List
from jsonschema import validate, ValidationError
from src.compliance.logger import ComplianceLogger
from src.config import RAW_DATA_DIR, NORMALIZED_DATA_DIR, SCHEMAS_DIR, BUSINESS_RULES


class ProductTransformer:
    """Transforma produtos brutos em formato normalizado."""
    
    def __init__(self, supplier_id: str):
        self.supplier_id = supplier_id
        self.logger = ComplianceLogger(supplier_id)
        self.raw_file = RAW_DATA_DIR / f"{supplier_id}_raw_products.json"
        self.normalized_file = NORMALIZED_DATA_DIR / f"{supplier_id}_products_normalized.json"
        self.schema = self._load_schema()
    
    def _load_schema(self) -> Dict[str, Any]:
        """Carrega schema de validação de produtos."""
        schema_file = SCHEMAS_DIR / "product_schema.json"
        with open(schema_file, "r", encoding="utf-8") as f:
            return json.load(f)
    
    def transform(self) -> List[Dict[str, Any]]:
        """Transforma todos os produtos do fornecedor."""
        print(f"🔄 Iniciando transformação: {self.supplier_id}")
        
        # Carrega dados brutos
        raw_data = self._load_raw_data()
        products = raw_data.get("products", [])
        
        print(f"📦 Produtos a transformar: {len(products)}")
        
        normalized_products = []
        
        for raw_product in products:
            try:
                # Normaliza produto
                normalized = self._normalize_product(raw_product)
                
                # Valida schema
                is_valid, errors = self._validate_product(normalized)
                
                if is_valid:
                    # Registra transformação
                    raw_hash = raw_product.get("extraction_hash", "unknown")
                    normalized_hash = self.logger.log_transformation(
                        normalized["id"],
                        raw_hash,
                        normalized
                    )
                    
                    # Registra validação
                    self.logger.log_validation(normalized["id"], True)
                    
                    normalized_products.append(normalized)
                    print(f"  ✓ {normalized['name']}")
                else:
                    print(f"  ✗ Validação falhou: {raw_product.get('name', 'unknown')}")
                    self.logger.log_validation(
                        raw_product.get("supplier_product_id", "unknown"),
                        False,
                        errors
                    )
                    
            except Exception as e:
                print(f"  ✗ Erro ao transformar: {str(e)}")
                continue
        
        # Salva produtos normalizados
        self._save_normalized_data(normalized_products)
        
        print(f"✅ Transformação concluída: {len(normalized_products)} produtos")
        return normalized_products
    
    def _load_raw_data(self) -> Dict[str, Any]:
        """Carrega dados brutos extraídos."""
        if not self.raw_file.exists():
            raise FileNotFoundError(f"Arquivo de dados brutos não encontrado: {self.raw_file}")
        
        with open(self.raw_file, "r", encoding="utf-8") as f:
            return json.load(f)
    
    def _normalize_product(self, raw_product: Dict[str, Any]) -> Dict[str, Any]:
        """Normaliza produto para schema único."""
        # Gera ID único baseado em supplier + supplier_product_id
        product_id = self._generate_product_id(
            self.supplier_id,
            raw_product["supplier_product_id"]
        )
        
        # Calcula preço final com margem e frete
        base_price = float(raw_product.get("price", 0))
        margin = BUSINESS_RULES["default_margin"]
        shipping = BUSINESS_RULES["default_shipping"]
        final_price = self._calculate_final_price(base_price, margin, shipping)
        
        # Monta produto normalizado
        normalized = {
            "id": product_id,
            "supplier": self.supplier_id,
            "supplier_product_id": raw_product["supplier_product_id"],
            "name": raw_product["name"],
            "brand": raw_product.get("brand", ""),
            "category": raw_product.get("category", "Geral"),
            "weight": float(raw_product.get("weight", 0)),
            "unit": raw_product.get("unit", "un"),
            "price": {
                "base": base_price,
                "margin": margin * 100,  # Converte para percentual
                "shipping": shipping,
                "final": final_price
            },
            "stock": {
                "available": raw_product.get("stock_available", True),
                "quantity": raw_product.get("stock_quantity", BUSINESS_RULES["min_stock_quantity"])
            },
            "metadata": {
                "extraction_date": datetime.utcnow().isoformat() + "Z",
                "source_url": raw_product.get("source_url", ""),
                "hash": raw_product.get("extraction_hash", "")
            },
            "created_at": datetime.utcnow().isoformat() + "Z",
            "updated_at": datetime.utcnow().isoformat() + "Z"
        }
        
        return normalized
    
    def _generate_product_id(self, supplier_id: str, supplier_product_id: str) -> str:
        """Gera ID único para o produto."""
        combined = f"{supplier_id}:{supplier_product_id}"
        return hashlib.sha256(combined.encode()).hexdigest()[:16]
    
    def _calculate_final_price(self, base_price: float, margin: float, shipping: float) -> float:
        """Calcula preço final com margem e frete."""
        price_with_margin = base_price * (1 + margin)
        final_price = price_with_margin + shipping
        return round(final_price, 2)
    
    def _validate_product(self, product: Dict[str, Any]) -> tuple[bool, List[str]]:
        """Valida produto contra schema JSON."""
        try:
            validate(instance=product, schema=self.schema)
            return True, []
        except ValidationError as e:
            return False, [str(e.message)]
    
    def _save_normalized_data(self, products: List[Dict[str, Any]]):
        """Salva produtos normalizados."""
        output = {
            "supplier": self.supplier_id,
            "transformation_date": datetime.utcnow().isoformat() + "Z",
            "total_products": len(products),
            "products": products
        }
        
        with open(self.normalized_file, "w", encoding="utf-8") as f:
            json.dump(output, f, ensure_ascii=False, indent=2)
        
        print(f"💾 Produtos salvos em: {self.normalized_file}")
