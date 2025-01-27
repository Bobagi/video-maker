import os
from dotenv import load_dotenv
from moviepy.editor import *

load_dotenv()

def criar_video(download_dir, output_file="top5_video.mp4"):
    clips = []
    screen_width, screen_height = 1080, 1920  # Resolução 9:16

    # Adicionar imagens
    for i in range(1, 4):  # Supondo 3 imagens
        imagem_path = os.path.join(download_dir, f"imagem_{i}.jpg")
        if os.path.exists(imagem_path):
            imagem_clip = ImageClip(imagem_path, duration=5)  # 5 segundos por imagem
            
            # Redimensionar e centralizar imagem
            imagem_clip = imagem_clip.resize(height=screen_height)
            imagem_clip = imagem_clip.on_color(
                size=(screen_width, screen_height),
                color=(0, 0, 0),
                pos="center"
            )
            
            imagem_clip = imagem_clip.set_fps(24)
            clips.append(imagem_clip)

    # Adicionar vídeos
    for i in range(1, 4):  # Supondo 3 vídeos
        video_path = os.path.join(download_dir, f"video_{i}.mp4")
        if os.path.exists(video_path):
            video_clip = VideoFileClip(video_path).subclip(0, 5)  # Usar apenas 5 segundos
            
            # Redimensionar vídeo ao formato vertical
            video_clip = video_clip.resize(height=screen_height)
            video_clip = video_clip.crop(width=screen_width, height=screen_height, x_center=video_clip.w/2, y_center=video_clip.h/2)

            clips.append(video_clip)
            
    if clips == []:
        print("Nenhum arquivo encontrado para criar o vídeo.")
        return

    # Concatenar todos os clipes
    final_clip = concatenate_videoclips(clips, method="compose")

    output_dir = os.path.join('output')
    os.makedirs(output_dir, exist_ok=True)
    
    # Exportar o vídeo final
    final_clip.write_videofile(output_dir + "/" + output_file, fps=24)
    print(f"Vídeo final criado: {output_file}")

# Diretório onde os arquivos foram baixados
download_dir = os.path.join('downloads')
criar_video(download_dir)
