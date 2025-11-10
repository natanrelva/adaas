"""Script para integrar produtos Gramore no catálogo central."""

import sys
from pathlib import Path

# Adiciona o diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.catalog.catalog_manager import CatalogManager


def main():
    """Integra produtos Gramore no catálogo."""
    print("=" * 60)
    print("INTEGRAÇÃO GRAMORE → CATÁLOGO CENTRAL")
    print("=" * 60)
    
    try:
        # Integra produtos
        catalog = CatalogManager()
        count = catalog.integrate_supplier("gramore")
        
        # Exibe estatísticas
        stats = catalog.get_statistics()
        
        print("\n" + "=" * 60)
        print(f"✅ INTEGRAÇÃO CONCLUÍDA")
        print(f"📦 Produtos integrados: {count}")
        print(f"📊 Total no catálogo: {stats['total_products']}")
        print(f"💰 Faixa de preço: R$ {stats['price_range']['min']:.2f} - R$ {stats['price_range']['max']:.2f}")
        print(f"📁 Categorias: {len(stats['categories'])}")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ ERRO: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
