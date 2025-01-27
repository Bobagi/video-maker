import requests

class PexelsAPI:
    def __init__(self, api_key):
        self.base_url = "https://api.pexels.com/v1"
        self.headers = {"Authorization": api_key}
    
    def buscar_imagens(self, query, num=5):
        url = f"{self.base_url}/search?query={query}&per_page={num}"
        response = requests.get(url, headers=self.headers)
        if response.status_code == 200:
            return response.json()['photos']
        else:
            print("Erro ao buscar imagens:", response.status_code, response.text)
            return []

    def buscar_videos(self, query, num=5, orientation="portrait"):
        url = f"{self.base_url}/videos/search?query={query}&per_page={num}&orientation={orientation}"
        response = requests.get(url, headers=self.headers)
        if response.status_code == 200:
            return response.json()['videos']
        else:
            print("Erro ao buscar vídeos:", response.status_code, response.text)
            return []
        
    def baixar_arquivo(self, url, destino):
        try:
            response = requests.get(url, stream=True)
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
