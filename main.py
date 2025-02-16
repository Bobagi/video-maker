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
from src.roteiroProcessor import RoteiroProcessor

load_dotenv()

PEXELS_API_KEY = os.getenv("PEXELS_API_KEY")
PIXABAY_API_KEY = os.getenv("PIXABAY_API_KEY")
DOWNLOAD_DIR = os.getenv("DOWNLOAD_DIR", "downloads")
SCRIPT_PATH = os.getenv("SCRIPT_PATH", "scripts")

def main():
    
    if not os.path.exists(SCRIPT_PATH):
        print(f"Error: The folder '${SCRIPT_PATH}' was not found.")
        sys.exit(1)
        
    print("\n🔧 Testing YouTube environment")
    if not YouTubeUploader().testar_ambiente():
        print("\n🆘 YouTube upload test failed in `main.py`.")
        sys.exit(1)
    else:
        print("\n🔧✅ YouTube test passed in `main.py`.")
        
    print("\n🔧 Testing TikTok environment\n")
    if not TikTokUploader().start_browser_test():
        print("\n🆘 TikTok upload test failed in `main.py`.")
        sys.exit(1)
    else:
        print("\n🔧✅ TikTok test passed in `main.py`.")
        
    print("\n🔧 Testing Google Voice environment")
    if not GoogleVoice().testar_ambiente():
        print("\n🆘 Google Voice test failed in `main.py`.")
        sys.exit(1)
    else:
        print("\n🔧✅ Google Voice test passed in `main.py`.")
        
    print("\n📰 Splitting scripts")
    processor = RoteiroProcessor(os.path.join("scripts", "roteiro.txt"))
    processor.processar()
    processor.exportar("scripts")
    # processor.deletar_arquivo_original()
    print("📰 Scripts processed\n")

    print("📹 Starting video generation\n\n")
    for arquivo in os.listdir(SCRIPT_PATH):
        if arquivo == "roteiro.txt":
            continue

        print(f"\nGenerating video for {arquivo}")
        roteiro_path = os.path.join(SCRIPT_PATH, arquivo)

        if not os.path.isfile(roteiro_path):
            continue

        print(f"\n=== 🔊 Generating audio for file: {arquivo} ===")

        google_voice = GoogleVoice()
        tempo_total = google_voice.processar_roteiro(roteiro_path)
        print(f"\n=== 🔊 Total audio generated: {tempo_total:.2f} seconds ===")

        query = find_value(roteiro_path, "SEARCH:")
        buscar_imagens = False
        tempo_total_desejado = math.ceil(tempo_total / 10) * 10
        tempo_maximo_por_video = 10

        print(f"\n=== 📼 Searching videos on Pexels: '{query}' ===")
        contador_videos = pexels(query, buscar_imagens, tempo_total_desejado, tempo_maximo_por_video)
        print(f"\n=== 📼 Pexels video search completed! ===")
        # print(f"\n=== Testing Pixabay API with query: '{query}' ===")
        # pixabay(query, buscar_imagens, tempo_total_desejado, tempo_maximo_por_video, contador_videos)

        print(f"\n=== 📼 Generating base video ===")
        videomaker = VideoMaker()
        videomaker.criar_video("downloads", os.path.join("musics", "musica.mp3"), tempo_total_desejado=tempo_total_desejado)
        print(f"\n=== 📼 Base video generated ===")
        
        print(f"\n=== 📼 Generating video with voice and text ===")
        videomaker.adicionar_texto_e_audio(os.path.join("output", "final_video.mp4"), output_file=f"{arquivo}.mp4", script_file=roteiro_path)
        print(f"\n=== 📼 Video with voice and text generated ===")
        
        print(f"\n=== 🟦 Authenticating YouTube ===")
        youtube = YouTubeUploader()
        youtube.authenticate()
        print(f"\n=== ✅ YouTube authenticated ===")
        
        print(f"\n=== ⏲️ Fetching last scheduled video on YouTube ===")
        last_date = youtube.get_last_scheduled_video_date()
        if last_date:
            print("📅 The last scheduled video is set for:", last_date)
            base_time = last_date + datetime.timedelta(seconds=1)
        else:
            print("📅 No scheduled videos found.")
            base_time = None 
            
        next_schedule = youtube.generate_schedule(1, start_time=base_time)[0]
        
        titulo = find_value(roteiro_path, "TÍTULO:")
        hashtags = find_value(roteiro_path, "HASHTAGS:")
        video_path = os.path.join("output", f"{arquivo}.mp4")

        print(f"\n=== ⬆️ Starting YouTube upload ===")
        upload_success = youtube.upload_single_video(
            video_path,
            titulo,
            hashtags,
            scheduled_time=next_schedule  # Pass the calculated time
        )
        
        if upload_success:
            print("⬆️✅ Upload successful on YouTube!")
        else:
            print("⬆️🆘 Upload failed.")
            
        print(f"\n=== ⬆️ Starting TikTok upload ===")        
        tiktok = TikTokUploader()
        description_tiktok = f"{titulo.strip()}\n{hashtags.strip()}"
            
        # next_schedule = datetime.datetime(2025, 2, 6, 18, 35)
        print("\n🆚 TikTok description: ", description_tiktok)

        sucesso_tiktok = tiktok.upload_video_to_tiktok(video_file=video_path, description=description_tiktok, scheduled_time=next_schedule)
        if sucesso_tiktok:
            print("⬆️✅ Upload scheduled successfully on TikTok!")
        else:
            print("⬆️🆘 Upload failed.")
            
        SCRIPT_BACKUP_PATH = "script_backup"
        os.makedirs(SCRIPT_BACKUP_PATH, exist_ok=True)
        shutil.move(roteiro_path, os.path.join(SCRIPT_BACKUP_PATH, arquivo))
        
    # Move videos from output to output_backup
    for arquivo in os.listdir("output"):
        try:
            video_path = os.path.join("output", arquivo)
            shutil.move(video_path, os.path.join("output_backup", arquivo))
        except Exception as e:
            print(f"Error moving file {arquivo} to output_backup: {e}")
            continue
    
def find_value(arquivo, termo):
    with open(arquivo, 'r', encoding='utf-8') as f:
        for linha in f:
            if linha.startswith(termo):
                return linha.split(termo, 1)[1].strip()
    return None

def pixabay(query, buscar_imagens, tempo_total_desejado, tempo_maximo_por_video, contador_videos=0):
    pixabay = PixabayAPI(PIXABAY_API_KEY)
    
    # Search for images if necessary
    if buscar_imagens:
        imagens = pixabay.buscar_imagens(query, num=3, orientation="vertical")
        print("Images Found on Pixabay:")
        for img in imagens:
            print(f"URL: {img['pageURL']}, Tags: {img['tags']}")
        
        # Create downloads folder if it doesn't exist
        os.makedirs(DOWNLOAD_DIR, exist_ok=True)
            
        # Download images
        print("\nDownloading found images:")
        for i, img in enumerate(imagens):
            url = img['largeImageURL']  # Direct link to the image file
            destino = os.path.join(DOWNLOAD_DIR, f"imagem_{i+1}.jpg")
            pixabay.baixar_arquivo(url, destino)

    # Search for videos
    videos = pixabay.buscar_videos(query, num=50)  # Search up to 50 videos to ensure enough time
    print("\nVideos Found on Pixabay:")
    tempo_acumulado = 0

    for vid in videos:
        if tempo_acumulado >= tempo_total_desejado:
            print("Desired total time reached for Pixabay.")
            break  # Stop if we've reached the desired time
        
        duracao = vid['duration']
        if duracao > 200:
            continue  # Ignore very long videos
        
        if duracao > tempo_maximo_por_video:
            duracao = tempo_maximo_por_video  # Limit the maximum time per video

        tempo_acumulado += duracao
        contador_videos += 1
        print(f"URL: {vid['pageURL']}, Duration: {vid['duration']} seconds, Considered: {duracao} seconds")

        # Create downloads folder if it doesn't exist
        os.makedirs(DOWNLOAD_DIR, exist_ok=True)

        # Download video
        print("\nDownloading found video:")
        url = vid['videos']['medium']['url']  # Direct link to the video file
        destino = os.path.join(DOWNLOAD_DIR, f"video_{contador_videos}.mp4")
        pixabay.baixar_arquivo(url, destino)
        
    return contador_videos


def pexels(query, buscar_imagens, tempo_total_desejado, tempo_maximo_por_video, contador_videos=0):
    pexels = PexelsAPI(PEXELS_API_KEY)
    
    # Search for images if necessary
    if buscar_imagens:
        imagens = pexels.buscar_imagens(query, num=3)
        print("Images Found on Pexels:")
        for img in imagens:
            print(f"URL: {img['url']}, Photographer: {img['photographer']}")
        
        # Create downloads folder if it doesn't exist
        os.makedirs(DOWNLOAD_DIR, exist_ok=True)
            
        # Download images
        print("\nDownloading found images:")
        for i, img in enumerate(imagens):
            url = img['src']['original']  # Direct link to the image file
            destino = os.path.join(DOWNLOAD_DIR, f"imagem_{i+1}.jpg")
            pexels.baixar_arquivo(url, destino)

    # Search for videos
    videos = pexels.buscar_videos(query, num=50, orientation="portrait")  # Search up to 50 videos to ensure enough time
    tempo_acumulado = 0

    for vid in videos:
        if tempo_acumulado >= tempo_total_desejado:
            print("Desired total time reached for Pexels.")
            break  # Stop if we've reached the desired time
        
        duracao = vid['duration']
        if duracao > 200:
            continue  # Ignore very long videos
        
        if duracao > tempo_maximo_por_video:
            duracao = tempo_maximo_por_video  # Limit the maximum time per video

        tempo_acumulado += duracao
        contador_videos += 1
        print(f"URL: {vid['url']}, Duration: {vid['duration']} seconds, Considered: {duracao} seconds")

        # Create downloads folder if it doesn't exist
        os.makedirs(DOWNLOAD_DIR, exist_ok=True)

        # Download video
        print("\nDownloading found video:")
        url = vid['video_files'][0]['link']  # Direct link to the video file
        destino = os.path.join(DOWNLOAD_DIR, f"video_{contador_videos}.mp4")
        pexels.baixar_arquivo(url, destino)
        
    return contador_videos

if __name__ == "__main__":
    main()
    
    print("\n🔚 Finished!\n")
    # os.system("shutdown /s /t 60")