import os
import requests
from dotenv import load_dotenv

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()

JAMENDO_CLIENT_ID = os.getenv("JAMENDO_CLIENT_ID")
DOWNLOAD_DIR = "downloads/music"  # Diretório para salvar músicas

class JamendoAPI:
    def __init__(self, client_id):
        self.base_url = "https://api.jamendo.com/v3.0"
        self.client_id = client_id

    def buscar_musicas(self, query, num=5):
        """Busca músicas pelo Jamendo."""
        url = f"{self.base_url}/tracks/?client_id={self.client_id}&format=json&limit={num}&search={query}"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            return data.get("results", [])
        else:
            print(f"Erro ao buscar músicas: {response.status_code} - {response.text}")
            return []

    def baixar_musica(self, url, destino):
        """Baixa uma música do Jamendo."""
        try:
            response = requests.get(url, stream=True)
            if response.status_code == 200:
                with open(destino, "wb") as arquivo:
                    for chunk in response.iter_content(1024):
                        arquivo.write(chunk)
                print(f"Música baixada: {destino}")
            else:
                print(f"Erro ao baixar música: {url}")
        except Exception as e:
            print(f"Erro durante o download: {e}")

# Função principal para testar
if __name__ == "__main__":
    # Verifica se a chave da API está configurada
    if not JAMENDO_CLIENT_ID:
        print("Erro: Defina a variável JAMENDO_CLIENT_ID no arquivo .env.")
        exit()

    # Criar o diretório de downloads
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)

    # Instanciar a API do Jamendo
    jamendo = JamendoAPI(JAMENDO_CLIENT_ID)

    # Buscar músicas
    query = "relaxing"
    print(f"Buscando músicas para: {query}...")
    musicas = jamendo.buscar_musicas(query, num=3)

    if musicas:
        print("Músicas encontradas:")
        for i, musica in enumerate(musicas):
            print(f"{i + 1}. {musica['name']} - {musica['artist_name']}")

            # Baixar cada música
            url_download = musica.get("audio")
            if url_download:
                destino = os.path.join(DOWNLOAD_DIR, f"{musica['name']}.mp3")
                jamendo.baixar_musica(url_download, destino)
            else:
                print(f"Música {musica['name']} não possui link para download.")
    else:
        print("Nenhuma música encontrada.")
