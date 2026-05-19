import os
import glob
from PIL import Image
import google.generativeai as genai
import time

def main():
    print("==================================================")
    print("🔍 INICIANDO AUDITORIA VISUAL DE CORTES (GEMINI) 🔍")
    print("==================================================")
    
    api_key = input("Cole sua API Key do Google Gemini para a auditoria: ").strip()
    if not api_key:
        print("Erro: Chave não fornecida.")
        return
        
    genai.configure(api_key=api_key)
    
    # Usa o modelo super rápido que achamos
    model = genai.GenerativeModel("gemini-2.5-flash")
    
    pasta_repositorio = "Repositorio_Final_JPG"
    arquivos_jpg = glob.glob(os.path.join(pasta_repositorio, "**", "*.jpg"), recursive=True)
    
    print(f"Encontrados {len(arquivos_jpg)} produtos para auditar. Iniciando...\n")
    
    produtos_cortados = []
    
    prompt = """
    Aja como um controle de qualidade de fotografia de produtos.
    Sua única tarefa é descobrir se este frasco, pote ou embalagem sofreu um 'crop' acidental.
    A imagem está em um fundo branco absoluto. Verifique a silhueta inteira do produto: esquerda, direita, em cima e embaixo.
    Se a silhueta do produto for cortada por uma linha reta e abrupta (onde faltou imagem original), responda CORTADA.
    Mesmo o menor corte plano em uma tampa ou na base significa que está CORTADA.
    Responda APENAS com a palavra OK ou CORTADA.
    """
    
    for arquivo in arquivos_jpg:
        try:
            # Carrega a imagem
            img_original = Image.open(arquivo)
            img_original.thumbnail((1024, 1024), Image.Resampling.LANCZOS)
            
            # Cria um fundo branco absoluto para que os cortes retos na borda fiquem extremamente visíveis para a IA
            if img_original.mode in ('RGBA', 'LA') or (img_original.mode == 'P' and 'transparency' in img_original.info):
                alpha = img_original.convert('RGBA').split()[-1]
                img = Image.new("RGB", img_original.size, (255, 255, 255))
                img.paste(img_original, mask=alpha)
            else:
                img = img_original.convert('RGB')
            
            response = model.generate_content([prompt, img])
            resultado = response.text.strip().upper()
            
            if "CORTADA" in resultado:
                print(f"✂️ CORTADO: {os.path.basename(arquivo)}")
                produtos_cortados.append(arquivo)
            else:
                print(f"✅ OK: {os.path.basename(arquivo)}")
                
            time.sleep(1) # Intervalo seguro de 1 segundo para a API gratuita
            
        except Exception as e:
            print(f"⚠️ Erro ao verificar {os.path.basename(arquivo)}: {e}")
            
    print("\n==================================================")
    print("🎯 RELATÓRIO FINAL DE AUDITORIA")
    print(f"Total analisado: {len(arquivos_png)}")
    print(f"Produtos com corte na imagem: {len(produtos_cortados)}")
    for p in produtos_cortados:
        print(f" - {p}")
    print("==================================================")

if __name__ == "__main__":
    main()
