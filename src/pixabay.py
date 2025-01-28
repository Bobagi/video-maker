import requests

class PixabayAPI:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://pixabay.com/api"
    
    def buscar_imagens(self, query, num=3, orientation="vertical"):
        url = f"{self.base_url}/"
        params = {
            "key": self.api_key,
            "q": query,
            "per_page": num,
            "orientation": orientation
        }
        response = requests.get(url, params=params)
        if response.status_code == 200:
            return response.json().get("hits", [])
        else:
            print("Erro ao buscar imagens:", response.status_code, response.text)
            return []

    def buscar_videos(self, query, num=5):
        url = f"{self.base_url}/videos/"
        params = {
            "key": self.api_key,
            "q": query,
            "per_page": num
        }
        response = requests.get(url, params=params)
        if response.status_code == 200:
            return response.json().get("hits", [])
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