"""Script para executar pipeline ETL completo de todos os fornecedores."""

import sys
from pathlib import Path

# Adiciona o diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.extractors.gramore_extractor import GramoreExtractor
from src.extractors.elmar_extractor import ElmarExtractor
from src.extractors.rmoura_extractor import RMouraExtractor
from src.transformers.product_transformer import ProductTransformer
from src.catalog.catalog_manager import CatalogManager
from src.config import DATA_DIR
import json


def load_suppliers_config():
    """Carrega configuração de todos os fornecedores."""
    suppliers_file = DATA_DIR / "suppliers.json"
    with open(suppliers_file, "r", encoding="utf-8") as f:
        return json.load(f)


def run_supplier_pipeline(supplier_id: str, extractor_class, config: dict):
    """Executa pipeline completo para um fornecedor."""
    print(f"\n{'=' * 60}")
    print(f"PIPELINE: {supplier_id.upper()}")
    print(f"{'=' * 60}")
    
    try:
        # 1. EXTRAÇÃO
        print(f"\n[1/3] Extração {supplier_id}")
        print("-" * 60)
        extractor = extractor_class(config)
        raw_products = extractor.extract()
        
        # 2. TRANSFORMAÇÃO
        print(f"\n[2/3] Transformação {supplier_id}")
        print("-" * 60)
        transformer = ProductTransformer(supplier_id)
        normalized_products = transformer.transform()
        
        # 3. INTEGRAÇÃO
        print(f"\n[3/3] Integração {supplier_id}")
        print("-" * 60)
        catalog = CatalogManager()
        integrated_count = catalog.integrate_supplier(supplier_id)
        
        print(f"\n✅ Pipeline {supplier_id} concluído:")
        print(f"   📥 Extraídos: {len(raw_products)}")
        print(f"   🔄 Normalizados: {len(normalized_products)}")
        print(f"   🔗 Integrados: {integrated_count}")
        
        return {
            "supplier": supplier_id,
            "extracted": len(raw_products),
            "normalized": len(normalized_products),
            "integrated": integrated_count,
            "status": "success"
        }
        
    except Exception as e:
        print(f"\n❌ Erro no pipeline {supplier_id}: {str(e)}")
        return {
            "supplier": supplier_id,
            "status": "error",
            "error": str(e)
        }


def main():
    """Executa pipeline completo de todos os fornecedores."""
    print("=" * 60)
    print("PIPELINE COMPLETO - TODOS OS FORNECEDORES")
    print("Made in Natural - Hub de Produtos Naturais")
    print("=" * 60)
    
    # Carrega configurações
    suppliers = load_suppliers_config()
    suppliers_map = {s["id"]: s for s in suppliers if s.get("active", True)}
    
    # Define extratores
    extractors = {
        "gramore": GramoreExtractor,
        "elmar": ElmarExtractor,
        "rmoura": RMouraExtractor
    }
    
    # Executa pipeline para cada fornecedor
    results = []
    
    for supplier_id, extractor_class in extractors.items():
        if supplier_id in suppliers_map:
            config = suppliers_map[supplier_id]
            
            # Verifica consentimento
            if not config.get("consent_obtained"):
                print(f"\n⚠️  {supplier_id}: Consentimento não obtido. Pulando...")
                results.append({
                    "supplier": supplier_id,
                    "status": "skipped",
                    "reason": "no_consent"
                })
                continue
            
            result = run_supplier_pipeline(supplier_id, extractor_class, config)
            results.append(result)
    
    # RESUMO FINAL
    print("\n" + "=" * 60)
    print("RESUMO FINAL")
    print("=" * 60)
    
    catalog = CatalogManager()
    stats = catalog.get_statistics()
    
    print(f"\n📊 ESTATÍSTICAS DO CATÁLOGO:")
    print(f"   Total de produtos: {stats['total_products']}")
    print(f"   Fornecedores:")
    for supplier, count in stats['suppliers'].items():
        print(f"      • {supplier}: {count} produtos")
    
    print(f"\n💰 PREÇOS:")
    print(f"   Mínimo: R$ {stats['price_range']['min']:.2f}")
    print(f"   Máximo: R$ {stats['price_range']['max']:.2f}")
    print(f"   Médio: R$ {stats['price_range']['avg']:.2f}")
    
    print(f"\n📁 CATEGORIAS ({len(stats['categories'])}):")
    for category in stats['categories']:
        print(f"   • {category}")
    
    print("\n🔍 RESULTADOS POR FORNECEDOR:")
    for result in results:
        if result["status"] == "success":
            print(f"   ✅ {result['supplier']}: {result['integrated']} produtos integrados")
        elif result["status"] == "skipped":
            print(f"   ⚠️  {result['supplier']}: Pulado ({result.get('reason', 'unknown')})")
        else:
            print(f"   ❌ {result['supplier']}: Erro - {result.get('error', 'unknown')}")
    
    print("\n" + "=" * 60)
    print("✅ PIPELINE COMPLETO FINALIZADO")
    print("=" * 60)


if __name__ == "__main__":
    main()
