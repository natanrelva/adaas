# Guia de Deploy

## Ambiente de Desenvolvimento

### Pré-requisitos
- Python 3.8+
- pip
- Git

### Instalação Local

```bash
# Clone o repositório
git clone <repository-url>
cd made-in-natural-full

# Crie ambiente virtual
python -m venv venv

# Ative o ambiente (Windows)
venv\Scripts\activate

# Ative o ambiente (Linux/Mac)
source venv/bin/activate

# Instale dependências
pip install -r requirements.txt
```

### Configuração

1. Verifique `data/suppliers.json` para configurar fornecedores
2. Ajuste regras de negócio em `src/config.py` se necessário
3. Configure rate limits por fornecedor

### Execução

```bash
# Pipeline completo
python scripts/run_all_pipelines.py

# Busca no catálogo
python scripts/search_catalog.py

# Auditoria
python scripts/audit_compliance.py
```

## Ambiente de Produção

### Opção 1: Servidor Linux

```bash
# Instalar Python
sudo apt update
sudo apt install python3.8 python3-pip

# Deploy da aplicação
cd /opt
git clone <repository-url> made-in-natural
cd made-in-natural

# Ambiente virtual
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configurar cron para execução automática
crontab -e

# Executar pipeline diariamente às 2h
0 2 * * * cd /opt/made-in-natural && venv/bin/python scripts/run_all_pipelines.py

# Auditoria semanal (domingo às 3h)
0 3 * * 0 cd /opt/made-in-natural && venv/bin/python scripts/audit_compliance.py
```

### Opção 2: Docker (futuro)

```dockerfile
FROM python:3.8-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["python", "scripts/run_all_pipelines.py"]
```

## Monitoramento

### Logs
- Logs ETL: `logs/*_etl_log.jsonl`
- Logs de auditoria: `logs/audit_log.jsonl`
- Relatórios: `logs/compliance_report_*.txt`

### Métricas Importantes
- Taxa de sucesso de extração (> 95%)
- Tempo de execução do pipeline
- Total de produtos no catálogo
- Erros de validação

## Backup

```bash
# Backup diário dos dados
tar -czf backup_$(date +%Y%m%d).tar.gz data/ logs/

# Manter últimos 30 dias
find . -name "backup_*.tar.gz" -mtime +30 -delete
```

## Troubleshooting

### Erro de Extração
- Verificar conectividade com fornecedor
- Checar rate limits
- Validar consentimento em `suppliers.json`

### Erro de Validação
- Verificar schema em `schemas/product_schema.json`
- Checar dados brutos em `data/raw/`

### Catálogo Vazio
- Executar pipeline completo
- Verificar logs de integração
