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
        
    # Create download folder if does not exist
    download_dir = "downloads"
    os.makedirs(download_dir, exist_ok=True)
        
    # Download images
    for i, img in enumerate(imagens):
        url = img['src']['original']  # Link direto para o arquivo de imagem
        destino = os.path.join(download_dir, f"imagem_{i+1}.jpg")
        pexels.baixar_arquivo(url, destino)
        
    # Download videos
    for i, vid in enumerate(videos):
        url = vid['video_files'][0]['link']  # Link direto para o arquivo de vídeo
        destino = os.path.join(download_dir, f"video_{i+1}.mp4")
        pexels.baixar_arquivo(url, destino)

if __name__ == "__main__":
    main()
