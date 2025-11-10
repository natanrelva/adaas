"""Script para executar pipeline completo ETL RMoura."""

import sys
from pathlib import Path

# Adiciona o diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.extractors.rmoura_extractor import RMouraExtractor
from src.transformers.product_transformer import ProductTransformer
from src.catalog.catalog_manager import CatalogManager
from src.config import DATA_DIR
import json


def load_supplier_config():
    """Carrega configuração do fornecedor RMoura."""
    suppliers_file = DATA_DIR / "suppliers.json"
    with open(suppliers_file, "r", encoding="utf-8") as f:
        suppliers = json.load(f)
    
    for supplier in suppliers:
        if supplier["id"] == "rmoura":
            return supplier
    
    raise ValueError("Configuração do fornecedor RMoura não encontrada")


def main():
    """Executa pipeline completo: Extração → Transformação → Integração."""
    print("=" * 60)
    print("PIPELINE COMPLETO ETL RMOURA")
    print("=" * 60)
    
    try:
        # 1. EXTRAÇÃO
        print("\n[1/3] EXTRAÇÃO")
        print("-" * 60)
        config = load_supplier_config()
        extractor = RMouraExtractor(config)
        raw_products = extractor.extract()
        
        # 2. TRANSFORMAÇÃO
        print("\n[2/3] TRANSFORMAÇÃO")
        print("-" * 60)
        transformer = ProductTransformer("rmoura")
        normalized_products = transformer.transform()
        
        # 3. INTEGRAÇÃO
        print("\n[3/3] INTEGRAÇÃO NO CATÁLOGO")
        print("-" * 60)
        catalog = CatalogManager()
        integrated_count = catalog.integrate_supplier("rmoura")
        
        # RESUMO
        stats = catalog.get_statistics()
        print("\n" + "=" * 60)
        print("✅ PIPELINE CONCLUÍDO COM SUCESSO")
        print("=" * 60)
        print(f"📥 Extraídos: {len(raw_products)} produtos")
        print(f"🔄 Normalizados: {len(normalized_products)} produtos")
        print(f"🔗 Integrados: {integrated_count} produtos")
        print(f"📊 Total no catálogo: {stats['total_products']} produtos")
        print(f"💰 Preço médio: R$ {stats['price_range']['avg']:.2f}")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ ERRO NO PIPELINE: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
