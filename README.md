# Projeto Produtos – BioExtratus

Este repositório contém scripts Python para:

- Extrair imagens de arquivos PSD e convertê‑las para JPEG.
- Gerar metadados JSON com descrição de produto, iluminação e renderização 4K usando Gemini.
- Auditar imagens em busca de cortes indesejados.

## Estrutura do projeto
```
Projeto_Produtos/
├─ extrair_psds.py           # Conversão de PSD → JPEG
├─ vision_auto_json.py       # Geração automática de metadados JSON
├─ atualizar_json.py         # Atualiza estrutura dos JSONs para o padrão premium
├─ verificar_cortes.py       # Detecta cortes nas imagens via Gemini
├─ .gitignore                # Exclui imagens grandes e arquivos temporários
└─ README.md                 # Este documento
```

## Como usar
1. Clone o repositório:
   ```bash
   git clone https://github.com/bioextratus/projeto_produtos.git
   cd projeto_produtos
   ```
2. Instale as dependências (Python 3.11+):
   ```bash
   pip install -r requirements.txt   # (crie este arquivo caso ainda não exista)
   ```
3. Execute os scripts conforme necessário, por exemplo:
   ```bash
   python3 extrair_psds.py
   python3 vision_auto_json.py
   python3 verificar_cortes.py
   ```

> **Nota:** É necessário possuir uma chave de API do Google Gemini para gerar os metadados.

---
*Este README foi gerado automaticamente por Antigravity.*
