# Made in Natural – Hub Modular e Orquestrado

Plataforma intermediária conectando fornecedores B2B de produtos naturais ao varejo B2C.

## Estrutura do Projeto

```
made-in-natural-full/
├── src/
│   ├── extractors/       # Módulos de extração por fornecedor
│   ├── transformers/     # Normalização e transformação
│   ├── catalog/          # Catálogo central unificado
│   ├── compliance/       # Logs, auditoria e governança
│   └── retail/           # Interface B2C
├── schemas/              # Schemas JSON de validação
├── data/                 # Dados processados
│   ├── raw/             # Dados brutos extraídos
│   ├── normalized/      # Dados normalizados
│   └── catalog/         # Catálogo final
├── logs/                # Logs de auditoria
└── tests/               # Testes automatizados
```

## Fornecedores

- **Gramore**: Scraping HTML
- **Elmar**: XML e planilhas
- **RMoura**: Scraping HTML

## Fluxo ETL

1. **Extração**: Captura dados do fornecedor
2. **Transformação**: Normaliza para schema único
3. **Unificação**: Integra no catálogo central
4. **Compliance**: Registra logs e hashes

## Próximos Passos

Ver `main.yml` para planejamento completo.
