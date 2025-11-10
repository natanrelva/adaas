"""Script para executar auditoria de compliance e governança."""

import sys
from pathlib import Path

# Adiciona o diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.compliance.auditor import ComplianceAuditor
from datetime import datetime


def display_audit_result(result: dict):
    """Exibe resultado de auditoria formatado."""
    print(f"\n{'=' * 60}")
    print(f"AUDITORIA: {result['supplier'].upper()}")
    print(f"{'=' * 60}")
    
    if result.get("status") == "no_logs":
        print(f"\n⚠️  {result['message']}")
        return
    
    print(f"\n📅 Data da auditoria: {result['audit_date']}")
    print(f"📊 Total de operações: {result['total_operations']}")
    
    print(f"\n🔄 OPERAÇÕES POR TIPO:")
    for op_type, count in result['operations_by_type'].items():
        print(f"   • {op_type}: {count}")
    
    print(f"\n✅ TAXA DE SUCESSO: {result['success_rate']:.1%}")
    
    print(f"\n🔐 INTEGRIDADE DOS DADOS:")
    integrity = result['data_integrity']
    print(f"   • Extrações: {integrity['total_extractions']}")
    print(f"   • Transformações: {integrity['total_transformations']}")
    print(f"   • Status: {integrity['hash_integrity']}")
    
    status_icon = "✅" if result['compliance_status'] == "compliant" else "⚠️"
    print(f"\n{status_icon} STATUS DE COMPLIANCE: {result['compliance_status'].upper()}")
    
    if result.get('issues'):
        print(f"\n⚠️  PROBLEMAS IDENTIFICADOS:")
        for issue in result['issues']:
            print(f"   • {issue}")


def audit_all_suppliers(auditor: ComplianceAuditor):
    """Audita todos os fornecedores."""
    print("=" * 60)
    print("AUDITORIA COMPLETA - TODOS OS FORNECEDORES")
    print("=" * 60)
    
    results = auditor.audit_all_suppliers()
    
    for result in results:
        display_audit_result(result)
    
    # Resumo geral
    print(f"\n{'=' * 60}")
    print("RESUMO GERAL DE COMPLIANCE")
    print(f"{'=' * 60}")
    
    compliant = sum(1 for r in results if r.get('compliance_status') == 'compliant')
    warning = sum(1 for r in results if r.get('compliance_status') == 'warning')
    no_logs = sum(1 for r in results if r.get('status') == 'no_logs')
    
    print(f"\n📊 STATUS:")
    print(f"   ✅ Compliant: {compliant}")
    print(f"   ⚠️  Warning: {warning}")
    print(f"   ❌ Sem logs: {no_logs}")
    
    total_ops = sum(r.get('total_operations', 0) for r in results)
    print(f"\n📈 TOTAL DE OPERAÇÕES AUDITADAS: {total_ops}")


def verify_product_traceability(auditor: ComplianceAuditor):
    """Verifica rastreabilidade de um produto específico."""
    print("\n" + "=" * 60)
    print("VERIFICAÇÃO DE RASTREABILIDADE")
    print("=" * 60)
    
    supplier = input("\n🏢 Fornecedor (gramore/elmar/rmoura): ").strip().lower()
    product_id = input("📦 ID do produto: ").strip()
    
    if not supplier or not product_id:
        print("❌ Fornecedor e ID do produto são obrigatórios.")
        return
    
    result = auditor.verify_traceability(product_id, supplier)
    
    print(f"\n{'=' * 60}")
    print(f"RASTREABILIDADE: {product_id}")
    print(f"{'=' * 60}")
    
    if not result['traceable']:
        print(f"\n❌ NÃO RASTREÁVEL")
        print(f"   Motivo: {result['reason']}")
        return
    
    print(f"\n✅ PRODUTO RASTREÁVEL")
    print(f"   Fornecedor: {result['supplier']}")
    print(f"   Operações encontradas: {', '.join(result['operations_found'])}")
    
    print(f"\n📅 LINHA DO TEMPO:")
    for log in result['timeline']:
        timestamp = log['timestamp']
        operation = log['operation']
        status = log.get('status', 'N/A')
        print(f"   • {timestamp} - {operation} ({status})")


def check_retention_policy(auditor: ComplianceAuditor):
    """Verifica política de retenção de logs."""
    print("\n" + "=" * 60)
    print("POLÍTICA DE RETENÇÃO DE LOGS")
    print("=" * 60)
    
    result = auditor.check_retention_policy()
    
    print(f"\n📅 Período de retenção: {result['retention_days']} dias")
    print(f"📅 Data de corte: {result['cutoff_date']}")
    print(f"📁 Logs para arquivar: {result['logs_to_archive']}")
    
    if result['logs_to_archive'] > 0:
        print(f"\n⚠️  Existem logs antigos que devem ser arquivados.")
    else:
        print(f"\n✅ Todos os logs estão dentro do período de retenção.")


def generate_compliance_report(auditor: ComplianceAuditor):
    """Gera relatório completo de compliance."""
    print("\n" + "=" * 60)
    print("GERANDO RELATÓRIO DE COMPLIANCE")
    print("=" * 60)
    
    # Audita todos os fornecedores
    results = auditor.audit_all_suppliers()
    
    # Verifica política de retenção
    retention = auditor.check_retention_policy()
    
    # Gera relatório
    report_file = Path("logs") / f"compliance_report_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.txt"
    
    with open(report_file, "w", encoding="utf-8") as f:
        f.write("=" * 60 + "\n")
        f.write("RELATÓRIO DE COMPLIANCE E GOVERNANÇA\n")
        f.write(f"Made in Natural - Hub de Produtos Naturais\n")
        f.write(f"Data: {datetime.utcnow().isoformat()}Z\n")
        f.write("=" * 60 + "\n\n")
        
        # Resumo executivo
        f.write("RESUMO EXECUTIVO\n")
        f.write("-" * 60 + "\n")
        compliant = sum(1 for r in results if r.get('compliance_status') == 'compliant')
        total = len([r for r in results if r.get('status') != 'no_logs'])
        f.write(f"Fornecedores em compliance: {compliant}/{total}\n")
        f.write(f"Total de operações auditadas: {sum(r.get('total_operations', 0) for r in results)}\n\n")
        
        # Detalhes por fornecedor
        f.write("AUDITORIA POR FORNECEDOR\n")
        f.write("-" * 60 + "\n\n")
        
        for result in results:
            f.write(f"Fornecedor: {result['supplier'].upper()}\n")
            if result.get('status') == 'no_logs':
                f.write(f"  Status: Sem logs\n\n")
                continue
            
            f.write(f"  Total de operações: {result['total_operations']}\n")
            f.write(f"  Taxa de sucesso: {result['success_rate']:.1%}\n")
            f.write(f"  Status de compliance: {result['compliance_status']}\n")
            
            if result.get('issues'):
                f.write(f"  Problemas:\n")
                for issue in result['issues']:
                    f.write(f"    - {issue}\n")
            
            f.write("\n")
        
        # Política de retenção
        f.write("POLÍTICA DE RETENÇÃO\n")
        f.write("-" * 60 + "\n")
        f.write(f"Período de retenção: {retention['retention_days']} dias\n")
        f.write(f"Logs para arquivar: {retention['logs_to_archive']}\n\n")
        
        # Recomendações
        f.write("RECOMENDAÇÕES\n")
        f.write("-" * 60 + "\n")
        
        warnings = [r for r in results if r.get('compliance_status') == 'warning']
        if warnings:
            f.write("• Investigar fornecedores com taxa de sucesso abaixo de 95%\n")
        
        if retention['logs_to_archive'] > 0:
            f.write("• Arquivar logs antigos conforme política de retenção\n")
        
        if not warnings and retention['logs_to_archive'] == 0:
            f.write("• Sistema em conformidade. Manter monitoramento regular.\n")
        
        f.write("\n" + "=" * 60 + "\n")
        f.write("FIM DO RELATÓRIO\n")
        f.write("=" * 60 + "\n")
    
    print(f"\n✅ Relatório gerado: {report_file}")
    print(f"📄 Arquivo salvo com sucesso.")


def main():
    """Menu principal de auditoria."""
    auditor = ComplianceAuditor()
    
    while True:
        print("\n" + "=" * 60)
        print("SISTEMA DE AUDITORIA E COMPLIANCE")
        print("Made in Natural")
        print("=" * 60)
        print("\n[1] Auditar todos os fornecedores")
        print("[2] Verificar rastreabilidade de produto")
        print("[3] Verificar política de retenção")
        print("[4] Gerar relatório completo de compliance")
        print("[0] Sair")
        
        choice = input("\n➤ Escolha uma opção: ").strip()
        
        if choice == "1":
            audit_all_suppliers(auditor)
        elif choice == "2":
            verify_product_traceability(auditor)
        elif choice == "3":
            check_retention_policy(auditor)
        elif choice == "4":
            generate_compliance_report(auditor)
        elif choice == "0":
            print("\n👋 Até logo!")
            break
        else:
            print("\n❌ Opção inválida.")


if __name__ == "__main__":
    main()
