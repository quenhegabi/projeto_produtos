import os
import json
import subprocess

def processar_psds(diretorio_origem="/Users/gabi/Library/CloudStorage/GoogleDrive-gabriella.felisberto@lapisraro.com.br/.shortcut-targets-by-id/19AUSXE15xCEArtTH4swt28M8vENztgI7/00 Produtos", diretorio_destino="Repositorio_Final_JPG"):
    os.makedirs(diretorio_destino, exist_ok=True)
    arquivos_processados = 0
    erros = 0
    
    print("🚀 Iniciando a conversão dos arquivos PSD para JPEG (Fundo Branco)...")
    print(f"Buscando originais em: {diretorio_origem}")
    print(f"Salvando resultados em: {os.path.abspath(diretorio_destino)}\n")
    
    # Pastas para ignorar na varredura
    ignorar_pastas = {"Extracao_PSDs", "Repositorio_Produtos", "Repositorio_PNGs", "Repositorio_Final_JPG", ".git"}
    
    for root, dirs, files in os.walk(diretorio_origem):
        # Ignorar as pastas especificadas
        dirs[:] = [d for d in dirs if d not in ignorar_pastas]
        
        for file in files:
            if file.lower().endswith(".psd"):
                caminho_psd = os.path.join(root, file)
                
                # Caminho relativo para manter a estrutura de pastas
                caminho_relativo = os.path.relpath(root, diretorio_origem)
                pasta_destino_arquivo = os.path.join(diretorio_destino, caminho_relativo)
                os.makedirs(pasta_destino_arquivo, exist_ok=True)
                
                # Nome final em JPG
                nome_imagem = os.path.splitext(file)[0] + ".jpg"
                caminho_imagem = os.path.join(pasta_destino_arquivo, nome_imagem)
                
                # Nome final em JSON
                caminho_json = os.path.splitext(caminho_imagem)[0] + ".json"
                
                # Converte usando o sips se a imagem não existir
                if not os.path.exists(caminho_imagem):
                    try:
                        # Executa o sips convertendo para JPEG com qualidade máxima (achata em fundo branco)
                        subprocess.run(
                            ["sips", "-s", "format", "jpeg", "-s", "formatOptions", "best", caminho_psd, "--out", caminho_imagem],
                            stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL,
                            check=True
                        )
                    except Exception as e:
                        # Em caso de erro tenta continuar
                        erros += 1
                        continue
                
                # Gera o JSON
                if not os.path.exists(caminho_json):
                    partes_caminho = caminho_relativo.strip(os.sep).split(os.sep)
                    linha = partes_caminho[0] if len(partes_caminho) > 0 and partes_caminho[0] != "." else "Geral"
                    categoria = partes_caminho[1] if len(partes_caminho) > 1 else ""
                    
                    dados = {
                        "produto": {
                            "nome": nome_imagem.replace(".jpg", ""),
                            "linha": linha,
                            "categoria": categoria,
                            "formato": "[Descreva o shape do frasco. Ex: Frasco cilíndrico com tampa pump]",
                            "design_e_cores": "[Descreva as cores exatas da embalagem para a IA não errar. Ex: Frasco inteiramente roxo fosco.]",
                            "textos_exatos_do_rotulo": [
                                "BIO EXTRATUS",
                                "COSMÉTICOS NATURAIS",
                                "Adicione outras frases importantes do rótulo aqui"
                            ]
                        },
                        "iluminacao_e_renderizacao": {
                            "tipo_de_luz": "Iluminação geral de estúdio (studio lighting), clara, neutra e suave.",
                            "sombras": "Sombras nítidas e marcadas projetadas para um lado, destacando a textura tridimensional e o volume.",
                            "texturas": "[Ex: Reflexos especulares sutis no plástico e material fosco realista.]",
                            "qualidade": "Ultra-detalhado, foco perfeito e nítido nos textos dos rótulos, renderização hiper-realista como em uma campanha publicitária."
                        },
                        "prompt_negativo": "texto borrado, erros ortográficos nos rótulos, proporções distorcidas, iluminação plana, aspecto de pintura ou desenho animado, cores desbotadas, sombras suaves ou ausentes."
                    }
                    with open(caminho_json, 'w', encoding='utf-8') as f:
                        json.dump(dados, f, ensure_ascii=False, indent=4)
                
                arquivos_processados += 1
                if arquivos_processados % 15 == 0:
                    print(f"Progresso: {arquivos_processados} produtos processados...")

    print("\n" + "=" * 40)
    print(f"✅ Processo Concluído!")
    print(f"Imagens extraídas e JSONs gerados: {arquivos_processados}")
    if erros > 0:
        print(f"Aviso: {erros} arquivos falharam na conversão.")
    print("=" * 40)

if __name__ == "__main__":
    processar_psds()
