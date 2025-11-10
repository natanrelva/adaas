"""Script para buscar e comparar produtos no catálogo."""

import sys
from pathlib import Path

# Adiciona o diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.catalog.catalog_manager import CatalogManager


def display_product(product: dict, index: int = None):
    """Exibe informações de um produto."""
    prefix = f"[{index}] " if index is not None else ""
    print(f"\n{prefix}📦 {product['name']}")
    print(f"   Marca: {product.get('brand', 'N/A')}")
    print(f"   Fornecedor: {product['supplier']}")
    print(f"   Categoria: {product.get('category', 'N/A')}")
    print(f"   Peso: {product['weight']} {product['unit']}")
    print(f"   Preço base: R$ {product['price']['base']:.2f}")
    print(f"   Preço final: R$ {product['price']['final']:.2f}")
    print(f"   Margem: {product['price']['margin']:.0f}%")
    print(f"   Estoque: {'✓ Disponível' if product['stock']['available'] else '✗ Indisponível'}")


def search_products(catalog: CatalogManager):
    """Interface de busca de produtos."""
    print("\n" + "=" * 60)
    print("BUSCA DE PRODUTOS")
    print("=" * 60)
    
    query = input("\n🔍 Digite o termo de busca (ou Enter para listar todos): ").strip()
    
    if query:
        results = catalog.search_products(query=query)
        print(f"\n📋 Encontrados {len(results)} produtos para '{query}':")
    else:
        results = catalog.search_products()
        print(f"\n📋 Total de {len(results)} produtos no catálogo:")
    
    if not results:
        print("   Nenhum produto encontrado.")
        return
    
    for i, product in enumerate(results, 1):
        display_product(product, i)


def compare_products(catalog: CatalogManager):
    """Interface de comparação de produtos."""
    print("\n" + "=" * 60)
    print("COMPARAÇÃO DE PRODUTOS")
    print("=" * 60)
    
    query = input("\n🔍 Digite o nome do produto para comparar: ").strip()
    
    if not query:
        print("❌ Nome do produto não pode ser vazio.")
        return
    
    results = catalog.compare_products(query)
    
    if not results:
        print(f"   Nenhum produto encontrado para '{query}'.")
        return
    
    print(f"\n📊 Comparação de produtos similares a '{query}':")
    print(f"   Encontrados {len(results)} produtos (ordenados por preço):\n")
    
    for i, product in enumerate(results, 1):
        display_product(product, i)


def filter_by_category(catalog: CatalogManager):
    """Interface de filtro por categoria."""
    print("\n" + "=" * 60)
    print("FILTRO POR CATEGORIA")
    print("=" * 60)
    
    categories = catalog.get_categories()
    
    if not categories:
        print("   Nenhuma categoria disponível.")
        return
    
    print("\n📁 Categorias disponíveis:")
    for i, cat in enumerate(categories, 1):
        print(f"   [{i}] {cat}")
    
    choice = input("\n🔍 Digite o número da categoria: ").strip()
    
    try:
        index = int(choice) - 1
        if 0 <= index < len(categories):
            category = categories[index]
            results = catalog.search_products(category=category)
            
            print(f"\n📋 Produtos na categoria '{category}' ({len(results)}):")
            for i, product in enumerate(results, 1):
                display_product(product, i)
        else:
            print("❌ Número inválido.")
    except ValueError:
        print("❌ Entrada inválida.")


def show_statistics(catalog: CatalogManager):
    """Exibe estatísticas do catálogo."""
    print("\n" + "=" * 60)
    print("ESTATÍSTICAS DO CATÁLOGO")
    print("=" * 60)
    
    stats = catalog.get_statistics()
    
    print(f"\n📊 RESUMO:")
    print(f"   Total de produtos: {stats['total_products']}")
    
    print(f"\n🏢 FORNECEDORES:")
    for supplier, count in stats['suppliers'].items():
        print(f"   • {supplier}: {count} produtos")
    
    print(f"\n💰 FAIXA DE PREÇOS:")
    print(f"   Mínimo: R$ {stats['price_range']['min']:.2f}")
    print(f"   Máximo: R$ {stats['price_range']['max']:.2f}")
    print(f"   Médio: R$ {stats['price_range']['avg']:.2f}")
    
    print(f"\n📁 CATEGORIAS ({len(stats['categories'])}):")
    for category in stats['categories']:
        print(f"   • {category}")


def main():
    """Menu principal de busca no catálogo."""
    catalog = CatalogManager()
    
    while True:
        print("\n" + "=" * 60)
        print("CATÁLOGO CENTRAL - Made in Natural")
        print("=" * 60)
        print("\n[1] Buscar produtos")
        print("[2] Comparar produtos")
        print("[3] Filtrar por categoria")
        print("[4] Ver estatísticas")
        print("[0] Sair")
        
        choice = input("\n➤ Escolha uma opção: ").strip()
        
        if choice == "1":
            search_products(catalog)
        elif choice == "2":
            compare_products(catalog)
        elif choice == "3":
            filter_by_category(catalog)
        elif choice == "4":
            show_statistics(catalog)
        elif choice == "0":
            print("\n👋 Até logo!")
            break
        else:
            print("\n❌ Opção inválida.")


if __name__ == "__main__":
    main()
