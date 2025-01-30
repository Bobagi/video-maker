import os
from dotenv import load_dotenv
from src.pexels import PexelsAPI
from src.pixabay import PixabayAPI

load_dotenv()

PEXELS_API_KEY = os.getenv("PEXELS_API_KEY")
PIXABAY_API_KEY = os.getenv("PIXABAY_API_KEY")
DOWNLOAD_DIR = os.getenv("DOWNLOAD_DIR", "downloads")

def main():
    # Parâmetros de teste
    query = "Cats"
    buscar_imagens = False
    tempo_total_desejado = 60  # Segundos desejados no vídeo final
    tempo_maximo_por_video = 10  # Máximo de segundos por vídeo

    print("=== Testando API do Pexels ===")
    contador_videos = pexels(query, buscar_imagens, tempo_total_desejado, tempo_maximo_por_video)

    print("\n=== Testando API do Pixabay ===")
    pixabay(query, buscar_imagens, 20, tempo_maximo_por_video, contador_videos)

    
def pixabay(query, buscar_imagens, tempo_total_desejado, tempo_maximo_por_video, contador_videos = 0):
    pixabay = PixabayAPI(PIXABAY_API_KEY)
    
    # Buscar imagens, se necessário
    if buscar_imagens:
        imagens = pixabay.buscar_imagens(query, num=3, orientation="vertical")
        print("Imagens Encontradas no Pixabay:")
        for img in imagens:
            print(f"URL: {img['pageURL']}, Tags: {img['tags']}")
        
        # Criar pasta de downloads, se não existir
        os.makedirs(DOWNLOAD_DIR, exist_ok=True)
            
        # Baixar imagens
        print("\nDownload das imagens encontradas:")
        for i, img in enumerate(imagens):
            url = img['largeImageURL']  # Link direto para o arquivo de imagem
            destino = os.path.join(DOWNLOAD_DIR, f"imagem_{i+1}.jpg")
            pixabay.baixar_arquivo(url, destino)

    # Buscar vídeos
    videos = pixabay.buscar_videos(query, num=50)  # Buscar até 50 vídeos para garantir tempo suficiente
    print("\nVídeos Encontrados no Pixabay:")
    tempo_acumulado = 0

    for vid in videos:
        if tempo_acumulado >= tempo_total_desejado:
            print("Tempo total desejado alcançado para pixabay.")
            break  # Interrompe se já alcançamos o tempo desejado
        
        duracao = vid['duration']
        if duracao > 200:
            continue  # Ignorar vídeos muito longos
        
        if duracao > tempo_maximo_por_video:
            duracao = tempo_maximo_por_video  # Limitar o tempo máximo por vídeo

        tempo_acumulado += duracao
        contador_videos += 1
        print(f"URL: {vid['pageURL']}, Duração: {vid['duration']} segundos, Considerado: {duracao} segundos")

        # Criar pasta de downloads, se não existir
        os.makedirs(DOWNLOAD_DIR, exist_ok=True)

        # Baixar vídeo
        print("\nDownload do vídeo encontrado:")
        url = vid['videos']['medium']['url']  # Link direto para o arquivo de vídeo
        destino = os.path.join(DOWNLOAD_DIR, f"video_{contador_videos}.mp4")
        pixabay.baixar_arquivo(url, destino)
        
    return contador_videos


def pexels(query, buscar_imagens, tempo_total_desejado, tempo_maximo_por_video, contador_videos = 0):
    pexels = PexelsAPI(PEXELS_API_KEY)
    
    # Buscar imagens, se necessário
    if buscar_imagens:
        imagens = pexels.buscar_imagens(query, num=3)
        print("Imagens Encontradas no Pexels:")
        for img in imagens:
            print(f"URL: {img['url']}, Fotógrafo: {img['photographer']}")
        
        # Criar pasta de downloads, se não existir
        os.makedirs(DOWNLOAD_DIR, exist_ok=True)
            
        # Baixar imagens
        print("\nDownload das imagens encontradas:")
        for i, img in enumerate(imagens):
            url = img['src']['original']  # Link direto para o arquivo de imagem
            destino = os.path.join(DOWNLOAD_DIR, f"imagem_{i+1}.jpg")
            pexels.baixar_arquivo(url, destino)

    # Buscar vídeos
    videos = pexels.buscar_videos(query, num=50, orientation="portrait")  # Buscar até 50 vídeos para garantir tempo suficiente
    tempo_acumulado = 0

    for vid in videos:
        if tempo_acumulado >= tempo_total_desejado:
            print("Tempo total desejado alcançado para pexels.")
            break  # Interrompe se já alcançamos o tempo desejado
        
        duracao = vid['duration']
        if duracao > 200:
            continue  # Ignorar vídeos muito longos
        
        if duracao > tempo_maximo_por_video:
            duracao = tempo_maximo_por_video  # Limitar o tempo máximo por vídeo

        tempo_acumulado += duracao
        contador_videos += 1
        print(f"URL: {vid['url']}, Duração: {vid['duration']} segundos, Considerado: {duracao} segundos")

        # Criar pasta de downloads, se não existir
        os.makedirs(DOWNLOAD_DIR, exist_ok=True)

        # Baixar vídeo
        print("\nDownload do vídeo encontrado:")
        url = vid['video_files'][0]['link']  # Link direto para o arquivo de vídeo
        destino = os.path.join(DOWNLOAD_DIR, f"video_{contador_videos}.mp4")
        pexels.baixar_arquivo(url, destino)
        
    return contador_videos


if __name__ == "__main__":
    main()
