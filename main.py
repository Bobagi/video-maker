import os
from dotenv import load_dotenv
from src.pexels import PexelsAPI

load_dotenv()

PEXELS_API_KEY = os.getenv("PEXELS_API_KEY")

def main():
    pexels = PexelsAPI(PEXELS_API_KEY)
    
    # Teste: Buscar imagens
    query = "waterfall"
    imagens = pexels.buscar_imagens(query, num=3)
    print("Imagens Encontradas:")
    for img in imagens:
        print(f"URL: {img['url']}, Fotógrafo: {img['photographer']}")
    
    # Teste: Buscar vídeos
    videos = pexels.buscar_videos(query, num=3)
    print("\nVídeos Encontrados:")
    for vid in videos:
        print(f"URL: {vid['url']}, Duração: {vid['duration']} segundos")

if __name__ == "__main__":
    main()
