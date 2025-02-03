import os
import sys
import math
import datetime
import shutil
from dotenv import load_dotenv
from src.pexels import PexelsAPI
from src.pixabay import PixabayAPI
from src.googleVoice import GoogleVoice
from src.videomaker import VideoMaker
from src.uploadYoutube import YouTubeUploader
from src.uploadTiktok import TikTokUploader

load_dotenv()

PEXELS_API_KEY = os.getenv("PEXELS_API_KEY")
PIXABAY_API_KEY = os.getenv("PIXABAY_API_KEY")
DOWNLOAD_DIR = os.getenv("DOWNLOAD_DIR", "downloads")
SCRIPT_PATH = os.getenv("SCRIPT_PATH", "scripts")

def main():
    if not os.path.exists(SCRIPT_PATH):
        print(f"Erro: A pasta '${SCRIPT_PATH}' não foi encontrada.")
        sys.exit(1)

    for arquivo in os.listdir(SCRIPT_PATH):
        roteiro_path = os.path.join(SCRIPT_PATH, arquivo)

        if not os.path.isfile(roteiro_path):
            continue

        print(f"\n=== Processando arquivo: {arquivo} ===")

        google_voice = GoogleVoice()
        tempo_total = google_voice.processar_roteiro(roteiro_path)
        print(f"Tempo total de áudio gerado: {tempo_total:.2f} segundos")

        query = find_value(roteiro_path, "SEARCH:")
        buscar_imagens = False
        tempo_total_desejado = math.ceil(tempo_total / 10) * 10
        tempo_maximo_por_video = 10

        print(f"=== Testando API do Pexels com query: '{query}' ===")
        contador_videos = pexels(query, buscar_imagens, tempo_total_desejado, tempo_maximo_por_video)

        # print(f"\n=== Testando API do Pixabay com query: '{query}' ===")
        # pixabay(query, buscar_imagens, tempo_total_desejado, tempo_maximo_por_video, contador_videos)

        videomaker = VideoMaker()
        videomaker.criar_video("downloads", os.path.join("musics", "musica.mp3"), tempo_total_desejado=tempo_total_desejado)
        videomaker.adicionar_texto_e_audio(os.path.join("output", "final_video.mp4"), output_file=f"{arquivo}.mp4", script_file=roteiro_path)
        
        youtube = YouTubeUploader()
        youtube.authenticate()
        
        last_date = youtube.get_last_scheduled_video_date()
        if last_date:
            print("O último vídeo agendado está marcado para:", last_date)
            base_time = last_date + datetime.timedelta(seconds=1)
        else:
            print("Nenhum vídeo agendado foi encontrado.")
            base_time = None 
            
        next_schedule = youtube.generate_schedule(1, start_time=base_time)[0]
        
        titulo = find_value(roteiro_path, "TÍTULO:")
        hashtags = find_value(roteiro_path, "HASHTAGS:")
        video_path = os.path.join("output", f"{arquivo}.mp4")

        upload_success = youtube.upload_single_video(
            video_path,
            titulo,
            hashtags,
            scheduled_time=next_schedule  # Passa o horário calculado
        )
        
        if upload_success:
            print("Upload realizado com sucesso no YouTube!")
        else:
            print("Houve um erro no upload.")
            
        tiktok = TikTokUploader()
        description_tiktok = f"{titulo.strip()}\n{hashtags.strip()}"
            
        # next_schedule = datetime.datetime(2025, 2, 6, 18, 35)

        sucesso_tiktok = tiktok.upload_video_to_tiktok(video_path, description_tiktok, next_schedule)
        if sucesso_tiktok:
            print("Upload agendado com sucesso no TikTok!")
        else:
            print("Falha no upload.")
            
        SCRIPT_BACKUP_PATH = "script_backup"
        os.makedirs(SCRIPT_BACKUP_PATH, exist_ok=True)
        shutil.move(roteiro_path, os.path.join(SCRIPT_BACKUP_PATH, arquivo))
    
def find_value(arquivo, termo):
    with open(arquivo, 'r', encoding='utf-8') as f:
        for linha in f:
            if linha.startswith(termo):
                return linha.split(termo, 1)[1].strip()
    return None

def pixabay(query, buscar_imagens, tempo_total_desejado, tempo_maximo_por_video, contador_videos=0):
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


def pexels(query, buscar_imagens, tempo_total_desejado, tempo_maximo_por_video, contador_videos=0):
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