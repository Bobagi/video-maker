import os
from dotenv import load_dotenv
from src.pexels import PexelsAPI
from src.pixabay import PixabayAPI

load_dotenv()

PEXELS_API_KEY = os.getenv("PEXELS_API_KEY")
PIXABAY_API_KEY = os.getenv("PIXABAY_API_KEY")
DOWNLOAD_DIR = os.getenv("DOWNLOAD_DIR", "downloads")

def main():
    # query = "waterfall"
    query = "Mountain"
    print("=== Testando API do Pexels ===")
    pexels(query)
    print("\n=== Testando API do Pixabay ===")
    pixabay(query)

    
def pixabay(query):
    pixabay = PixabayAPI(PIXABAY_API_KEY)
    
    # Teste: Buscar imagens
    imagens = pixabay.buscar_imagens(query, num=3, orientation="vertical")
    print("Imagens Encontradas no Pixabay:")
    for img in imagens:
        print(f"URL: {img['pageURL']}, Tags: {img['tags']}")
    
    # Teste: Buscar vídeos
    videos = pixabay.buscar_videos(query, num=3)
    print("\nVídeos Encontrados no Pixabay:")
    for vid in videos:
        print(f"URL: {vid['pageURL']}, Duração: {vid['duration']} segundos")
        
    # Criar pasta de downloads, se não existir
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)
        
    # Baixar imagens
    print("\nDownload das imagens encontradas:")
    for i, img in enumerate(imagens):
        url = img['largeImageURL']  # Link direto para o arquivo de imagem
        destino = os.path.join(DOWNLOAD_DIR, f"imagem_{i+1+3}.jpg")
        pixabay.baixar_arquivo(url, destino)
        
    # Baixar vídeos
    print("\nDownload dos videos encontrados:")
    for i, vid in enumerate(videos):
        url = vid['videos']['medium']['url']  # Link direto para o arquivo de vídeo
        destino = os.path.join(DOWNLOAD_DIR, f"video_{i+1+3}.mp4")
        pixabay.baixar_arquivo(url, destino)

def pexels(query):
    pexels = PexelsAPI(PEXELS_API_KEY)
    
    # Teste: Buscar imagens
    imagens = pexels.buscar_imagens(query, num=3)
    print("Imagens Encontradas:")
    for img in imagens:
        print(f"URL: {img['url']}, Fotógrafo: {img['photographer']}")
    
    # Teste: Buscar vídeos
    videos = pexels.buscar_videos(query, num=3, orientation="portrait")
    print("\nVídeos Encontrados:")
    for vid in videos:
        print(f"URL: {vid['url']}, Duração: {vid['duration']} segundos")
        
    # Create download folder if does not exist
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)
        
    # Download images
    print("\nDownload das imagens encontradas:")
    for i, img in enumerate(imagens):
        url = img['src']['original']  # Link direto para o arquivo de imagem
        destino = os.path.join(DOWNLOAD_DIR, f"imagem_{i+1}.jpg")
        pexels.baixar_arquivo(url, destino)
        
    # Download videos
    print("\nDownload dos videos encontrados:")
    for i, vid in enumerate(videos):
        url = vid['video_files'][0]['link']  # Link direto para o arquivo de vídeo
        destino = os.path.join(DOWNLOAD_DIR, f"video_{i+1}.mp4")
        pexels.baixar_arquivo(url, destino)

if __name__ == "__main__":
    main()
