'''gerar_packshots.py

Script para gerar packshots 4K (hiper‑realistas) a partir dos arquivos JSON
gerados por ``vision_auto_json.py``.

Requisitos
-----------
- Python 3.11+
- ``google-generativeai`` (ou outra API de geração de imagens)
- Uma chave de API do Google Gemini com permissões de geração de imagens

Uso
---
1. Defina a variável ``API_KEY`` com a sua chave de API ou configure a
   variável de ambiente ``GOOGLE_API_KEY``.
2. Execute:
   ``python3 gerar_packshots.py``
   O script criará a pasta ``Packshots_4K`` (se ainda não existir) e salvará
   as imagens geradas com o mesmo nome base dos JSONs.

Observações
-----------
- O modelo usado aqui é ``gemini-1.5-pro-vision`` (ou outro modelo que
  suporte geração de imagens). Ajuste ``MODEL_NAME`` conforme necessário.
- Um intervalo de 2 s entre chamadas evita limites de taxa da API.
- Caso a geração falhe, o script registra o erro e continua com os demais
  arquivos.
''' 

import os
import json
import time
from pathlib import Path

# -----------------------------------------------------------------------------
# Configurações
# -----------------------------------------------------------------------------
API_KEY = os.getenv("GOOGLE_API_KEY")  # pode ser definido externamente
MODEL_NAME = "gemini-1.5-pro-vision"
# Pasta onde estão os JSONs criados por ``vision_auto_json.py``
JSON_DIR = Path(__file__).parent / "Repositorio_Final_JPG"
# Pasta de saída para as imagens 4K
OUTPUT_DIR = Path(__file__).parent / "Packshots_4K"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# -----------------------------------------------------------------------------
# Funções auxiliares
# -----------------------------------------------------------------------------
def load_json(json_path: Path) -> dict:
    """Carrega o conteúdo de um arquivo JSON.
    
    Args:
        json_path: caminho absoluto ou relativo do JSON.
    
    Returns:
        Dicionário com os dados do JSON.
    """
    with open(json_path, "r", encoding="utf-8") as f:
        return json.load(f)

def build_prompt(data: dict) -> str:
    """Constrói o prompt de geração de imagem a partir do JSON.
    
    O JSON possui duas seções principais:
    - ``produto``: nome, linha, categoria, forma, cores e textos do rótulo.
    - ``iluminacao_e_renderizacao``: tipo de luz, sombras, texturas e qualidade.
    
    O prompt combina essas informações em uma descrição detalhada para a IA.
    """
    produto = data.get("produto", {})
    render = data.get("iluminacao_e_renderizacao", {})
    positivo = (
        f"Um frasco de {produto.get('nome', 'produto')} da linha {produto.get('linha', '')} "
        f"categorizado como {produto.get('categoria', '')}. "
        f"Forma: {produto.get('formato', '')}. "
        f"Cores: {produto.get('design_e_cores', '')}. "
        f"Rótulo com os textos: {', '.join(produto.get('textos_exatos_do_rotulo', []))}. "
        f"Iluminação: {render.get('tipo_de_luz', '')}. "
        f"Sombras: {render.get('sombras', '')}. "
        f"Texturas: {render.get('texturas', '')}. "
        f"Qualidade: {render.get('qualidade', '')}."
    )
    negativo = data.get("prompt_negativo", "")
    full_prompt = f"{positivo}\n\nNegativo: {negativo}" if negativo else positivo
    return full_prompt

def generate_image(prompt: str, output_path: Path):
    """Chama a API Gemini para gerar a imagem e salva em ``output_path``.
    
    Esta função assume que ``google.generativeai`` está instalado. Caso a
    biblioteca não esteja disponível, o usuário deve instalá‑la com:
    ``pip install google-generativeai``.
    """
    try:
        import google.generativeai as genai
    except ImportError as e:
        raise RuntimeError(
            "google-generativeai não está instalado. Instale com 'pip install google-generativeai'."
        ) from e

    if not API_KEY:
        raise RuntimeError("Variável de ambiente GOOGLE_API_KEY não definida.")

    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel(MODEL_NAME)
    # A API aceita prompt + imagens, mas aqui enviamos apenas texto que descreve a cena.
    response = model.generate_content(prompt, generation_config={"response_mime_type": "image/png"})
    # O conteúdo retornado contém a imagem em bytes.
    img_bytes = response._result  # tipo interno, pode mudar; aqui assumimos que é bytes
    with open(output_path, "wb") as out_f:
        out_f.write(img_bytes)

def main():
    json_files = list(JSON_DIR.rglob("*.json"))
    if not json_files:
        print("⚠️ Nenhum arquivo JSON encontrado em", JSON_DIR)
        return

    print(f"🚀 Iniciando geração de packshots 4K para {len(json_files)} produtos…")
    sucessos = 0
    falhas = 0
    for jf in json_files:
        try:
            data = load_json(jf)
            prompt = build_prompt(data)
            output_file = OUTPUT_DIR / (jf.stem + ".png")
            generate_image(prompt, output_file)
            print(f"✅ {jf.name} → {output_file.name}")
            sucessos += 1
            time.sleep(2)  # taxa de 1 chamada a cada 2 s
        except Exception as exc:
            print(f"❌ Erro ao processar {jf.name}: {exc}")
            falhas += 1
    print("\n=== Resumo ===")
    print(f"✅ Sucessos: {sucessos}")
    print(f"❌ Falhas: {falhas}")
    print("Packshots armazenados em:", OUTPUT_DIR)

if __name__ == "__main__":
    main()
