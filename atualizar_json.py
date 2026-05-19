import os
import json

def atualizar_estrutura_json(diretorio_base="Extracao_PSDs"):
    atualizados = 0
    print(f"🔄 Atualizando a estrutura dos JSONs na pasta {diretorio_base}...")
    for root, dirs, files in os.walk(diretorio_base):
        for file in files:
            if file.endswith(".json"):
                caminho = os.path.join(root, file)
                
                try:
                    with open(caminho, 'r', encoding='utf-8') as f:
                        dados = json.load(f)
                    
                    # Força a atualização da luz
              # No extra processing needed here
                        
                    # Puxa dados antigos se existirem
                    nome = dados.get("nome_arquivo", file.replace(".json", ".jpg")).replace(".jpg", "")
                    linha = dados.get("linha", "")
                    categoria = dados.get("categoria", "")
                    
                    # Nova Estrutura Premium
                    nova_estrutura = {
                        "produto": {
                            "nome": nome,
                            "linha": linha,
                            "categoria": categoria,
                            "formato": "[Descreva o shape do frasco. Ex: Frasco cilíndrico com tampa pump]",
                            "design_e_cores": "[Descreva as cores exatas da embalagem para a IA não errar. Ex: Frasco inteiramente roxo fosco.]",
                            "textos_exatos_do_rotulo": [
                                "BIO EXTRATUS",
                                "COSMÉTICOS NATURAIS",
                                "Adicione outras frases importantes do rótulo aqui para garantir a legibilidade"
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
                    
                    with open(caminho, 'w', encoding='utf-8') as f:
                        json.dump(nova_estrutura, f, ensure_ascii=False, indent=4)
                        
                    atualizados += 1
                except Exception as e:
                    print(f"Erro em {file}: {e}")
                    
    print(f"✅ Sucesso! {atualizados} arquivos JSON foram atualizados para a estrutura Premium.")

if __name__ == "__main__":
    atualizar_estrutura_json()
