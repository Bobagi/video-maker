import os
import requests
from dotenv import load_dotenv

class FreesoundAPI:
    def __init__(self, api_key):
        self.base_url = "https://freesound.org/apiv2"
        self.headers = {"Authorization": f"Token {api_key}"}

    def buscar_sons(self, query, num=10):
        url = f"{self.base_url}/search/text/"
        page = 1
        results_com_preview = []

        while len(results_com_preview) < num:
            params = {
                "query": query,
                "page_size": 20,  # Buscar até 20 resultados por página
                "page": page
            }
            response = requests.get(url, headers=self.headers, params=params)

            if response.status_code == 200:
                results = response.json().get('results', [])
                print(f"Página {page}: {len(results)} resultados encontrados.")

                # Filtrar apenas sons com preview
                filtered_results = [
                    r for r in results if 'previews' in r and 'preview-hq-mp3' in r['previews']
                ]
                results_com_preview.extend(filtered_results)

                # Verificar se não há mais resultados para buscar
                if len(results) < 20:
                    break

                page += 1
            else:
                print("Erro ao buscar sons:", response.status_code, response.text)
                break

        return results_com_preview[:num]

    def baixar_arquivo(self, url, destino):
        try:
            response = requests.get(url, stream=True, headers=self.headers)
            if response.status_code == 200:
                with open(destino, "wb") as f:
                    for chunk in response.iter_content(1024):
                        f.write(chunk)
                print(f"Arquivo baixado: {destino}")
                return True
            else:
                print(f"Erro ao baixar arquivo: {url}")
                return False
        except Exception as e:
            print(f"Erro durante o download: {e}")
            return False

if __name__ == "__main__":
    # Carregar variáveis de ambiente
    load_dotenv()
    FREESOUND_API_KEY = os.getenv("FREESOUND_API_KEY")
    DOWNLOAD_DIR = "downloads/music"

    # Verificar se a API Key está configurada
    if not FREESOUND_API_KEY:
        print("Erro: Defina a variável FREESOUND_API_KEY no arquivo .env.")
        exit()

    # Inicializar API
    freesound = FreesoundAPI(FREESOUND_API_KEY)

    # Teste: Buscar sons
    query = "relaxing"
    sons = freesound.buscar_sons(query, num=20)  # Buscar até encontrar 20 sons com preview
    print("Sons encontrados com preview:")

    for som in sons:
        print(f"ID: {som['id']}, Nome: {som['name']}, URL: {som['previews']['preview-hq-mp3']}")

    # Criar diretório de downloads
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)

    # Download dos sons
    for i, som in enumerate(sons):
        preview = som['previews']['preview-hq-mp3']  # Todos os sons retornados terão preview
        destino = os.path.join(DOWNLOAD_DIR, f"musica_{i+1}.mp3")
        freesound.baixar_arquivo(preview, destino)
