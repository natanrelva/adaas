"""Script para executar extração de produtos Gramore."""

import json
import sys
from pathlib import Path

# Adiciona o diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.extractors.gramore_extractor import GramoreExtractor
from src.config import DATA_DIR


def load_supplier_config():
    """Carrega configuração do fornecedor Gramore."""
    suppliers_file = DATA_DIR / "suppliers.json"
    with open(suppliers_file, "r", encoding="utf-8") as f:
        suppliers = json.load(f)
    
    for supplier in suppliers:
        if supplier["id"] == "gramore":
            return supplier
    
    raise ValueError("Configuração do fornecedor Gramore não encontrada")


def main():
    """Executa extração Gramore."""
    print("=" * 60)
    print("EXTRAÇÃO GRAMORE - Made in Natural")
    print("=" * 60)
    
    try:
        # Carrega configuração
        config = load_supplier_config()
        
        # Verifica consentimento
        if not config.get("consent_obtained"):
            print("❌ Consentimento não obtido. Extração cancelada.")
            return
        
        # Executa extração
        extractor = GramoreExtractor(config)
        products = extractor.extract()
        
        print("\n" + "=" * 60)
        print(f"✅ EXTRAÇÃO CONCLUÍDA")
        print(f"📦 Total de produtos: {len(products)}")
        print(f"📁 Arquivo: {extractor.output_file}")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ ERRO: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
