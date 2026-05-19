import os
import json
import time
import google.generativeai as genai
from PIL import Image

def configurar_api():
    print("\n" + "="*50)
    print("🧠 INICIANDO O CÉREBRO DE VISÃO DA IA (GEMINI PRO) 🧠")
    print("="*50)
    print("AVISO: Sua API Key nunca será salva. Ela só fica ativa nesta sessão.")
    api_key = input("Cole aqui a sua API Key do Google Gemini e aperte Enter: ").strip()
    
    if not api_key:
        print("Erro: API Key não fornecida. Encerrando o script.")
        exit(1)
        
    genai.configure(api_key=api_key)
    
    # Busca dinamicamente qual é o modelo mais moderno liberado na sua chave
    modelo_escolhido = "gemini-1.5-flash" # Fallback inicial
    try:
        modelos_disponiveis = [m for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        for m in modelos_disponiveis:
            # Dá preferência para os modelos mais novos (flash ou pro) e ignora os antigos 'vision'
            if 'flash' in m.name.lower():
                modelo_escolhido = m.name.replace('models/', '')
                break
            elif 'pro' in m.name.lower():
                modelo_escolhido = m.name.replace('models/', '')
    except Exception as e:
        print(f"Aviso ao buscar modelos: {e}")

    print(f"🤖 Cérebro visual conectado! Modelo em uso: {modelo_escolhido}")
    model = genai.GenerativeModel(modelo_escolhido)
    return model

def analisar_imagem(model, caminho_imagem):
    try:
        Image.MAX_IMAGE_PIXELS = None
        img = Image.open(caminho_imagem)
        # Força o resize
        img.thumbnail((1024, 1024), Image.Resampling.LANCZOS)
        # Salva num arquivo temporário blindado
        import tempfile
        import os
        temp_path = os.path.join(tempfile.gettempdir(), 'temp_vision.jpg')
        # Converte para RGB para poder salvar como JPG e ignorar transparências pesadas
        if img.mode in ('RGBA', 'P'):
            img = img.convert('RGB')
        img.save(temp_path, format='JPEG', quality=85)
        # Recarrega a imagem leve do disco
        img_leve = Image.open(temp_path)
    except Exception as e:
        print(f"Erro ao abrir/redimensionar a imagem {caminho_imagem}: {e}")
        return None

    prompt = """
Você é um diretor de arte e especialista em fotografia de cosméticos.
Analise a embalagem do produto nesta imagem e extraia os detalhes com extrema precisão para compormos um prompt de IA generativa no futuro.

Retorne APENAS um objeto JSON válido (não use formatação de blocos markdown como ```json) com as seguintes chaves exatas:
1. "formato": Descreva fisicamente o shape do frasco, o tipo de tampa e o MATERIAL APARENTE da embalagem (ex: plástico fosco, plástico brilhante, vidro transparente, bisnaga de alumínio, spray, etc).
2. "design_e_cores": Descreva as cores exatas do frasco, da tampa e os detalhes visuais do design para que a IA não altere a paleta.
3. "textos_exatos_do_rotulo": Um array de strings com todas as frases, palavras e gramaturas (ex: 350ml) legíveis no rótulo frontal.

Exemplo de saída esperada (retorne apenas isso):
{
  "formato": "Frasco cilíndrico de plástico fosco com tampa flip-top roxa de plástico liso.",
  "design_e_cores": "Frasco inteiramente roxo fosco com textos em branco e dourado.",
  "textos_exatos_do_rotulo": ["BIO EXTRATUS", "COSMÉTICOS NATURAIS", "+HIDRA", "Condicionador", "350mL"]
}
"""
    try:
        response = model.generate_content([prompt, img_leve])
        texto_resposta = response.text.strip()
        
        # Tratamento caso o Gemini retorne com blocos de markdown
        if texto_resposta.startswith("```json"):
            texto_resposta = texto_resposta[7:]
        if texto_resposta.startswith("```"):
            texto_resposta = texto_resposta[3:]
        if texto_resposta.endswith("```"):
            texto_resposta = texto_resposta[:-3]
            
        return json.loads(texto_resposta.strip())
    except Exception as e:
        print(f"Erro na comunicação com a API para {caminho_imagem}: {e}")
        return None

def varrer_e_processar(diretorio="Repositorio_Final_JPG"):
    model = configurar_api()
    
    print("\n🔍 Buscando produtos que ainda precisam de análise visual...\n")
    
    arquivos_processados = 0
    erros = 0
    processados = 0
    
    for root, dirs, files in os.walk(diretorio):
        for file in files:
            if file.lower().endswith(".json"):
                caminho_json = os.path.join(root, file)
                caminho_jpg = os.path.splitext(caminho_json)[0] + ".jpg"
                
                try:
                    with open(caminho_json, 'r', encoding='utf-8') as f:
                        dados = json.load(f)
                    
                    # Verifica se o JSON tem os colchetes (ou seja, se está pendente)
                    formato_atual = dados.get("produto", {}).get("formato", "")
                    if "[" in formato_atual or "Descreva" in formato_atual:
                        if not os.path.exists(caminho_jpg):
                            print(f"⚠️ Imagem correspondente não encontrada para {file}")
                            continue
                            
                        print(f"\n📸 Analisando produto: {file}...")
                        resultado_ia = analisar_imagem(model, caminho_jpg)
                        
                        if resultado_ia:
                            # 1. Substitui os colchetes pela descrição brilhante do Gemini
                            dados["produto"]["formato"] = resultado_ia.get("formato", "")
                            dados["produto"]["design_e_cores"] = resultado_ia.get("design_e_cores", "")
                            dados["produto"]["textos_exatos_do_rotulo"] = resultado_ia.get("textos_exatos_do_rotulo", [])
                            
                            # 2. Injeção brutal de fotorrealismo 4K
                            dados["iluminacao_e_renderizacao"]["qualidade"] = "Ultra-detalhado, fotografia de produto hiper-realista em 4K, lente 85mm macro f/8, qualidade de campanha publicitária, texturas de material ricas e foco absolutamente nítido nos textos."
                            
                            with open(caminho_json, 'w', encoding='utf-8') as f:
                                json.dump(dados, f, ensure_ascii=False, indent=4)
                            
                            print("✅ JSON preenchido e atualizado com a IA Visual!")
                            processados += 1
                            
                            # Pausa para evitar rate limits na API gratuita do Gemini
                            time.sleep(3)
                except Exception as e:
                    print(f"Erro ao processar {file}: {e}")
                    erros += 1
                    
    print("\n" + "="*50)
    print("🎉 ANÁLISE DE CÉREBRO VISUAL CONCLUÍDA!")
    print(f"Produtos processados e preenchidos automaticamente: {processados}")
    print(f"Erros encontrados: {erros}")
    print("="*50)

if __name__ == "__main__":
    varrer_e_processar()
