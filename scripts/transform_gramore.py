"""Script para executar transformação de produtos Gramore."""

import sys
from pathlib import Path

# Adiciona o diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.transformers.product_transformer import ProductTransformer


def main():
    """Executa transformação Gramore."""
    print("=" * 60)
    print("TRANSFORMAÇÃO GRAMORE - Made in Natural")
    print("=" * 60)
    
    try:
        # Executa transformação
        transformer = ProductTransformer("gramore")
        products = transformer.transform()
        
        print("\n" + "=" * 60)
        print(f"✅ TRANSFORMAÇÃO CONCLUÍDA")
        print(f"📦 Total de produtos normalizados: {len(products)}")
        print(f"📁 Arquivo: {transformer.normalized_file}")
        print("=" * 60)
        
        # Exibe exemplo de produto normalizado
        if products:
            print("\n📋 Exemplo de produto normalizado:")
            print(f"  ID: {products[0]['id']}")
            print(f"  Nome: {products[0]['name']}")
            print(f"  Preço base: R$ {products[0]['price']['base']:.2f}")
            print(f"  Preço final: R$ {products[0]['price']['final']:.2f}")
            print(f"  Margem: {products[0]['price']['margin']:.0f}%")
        
    except Exception as e:
        print(f"\n❌ ERRO: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
