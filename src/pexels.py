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

    def buscar_videos(self, query, num=5):
        url = f"{self.base_url}/videos/search?query={query}&per_page={num}"
        response = requests.get(url, headers=self.headers)
        if response.status_code == 200:
            return response.json()['videos']
        else:
            print("Erro ao buscar vídeos:", response.status_code, response.text)
            return []
