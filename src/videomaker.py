import os
from dotenv import load_dotenv
from moviepy.editor import *
import moviepy.config as mpy_config

load_dotenv()

# Defina o caminho completo para o magick.exe
mpy_config.IMAGEMAGICK_BINARY = os.getenv('IMAGEMAGICK_PATH')

def criar_video(download_dir, music=None, output_file="top5_video.mp4"):
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
            
            # Adicionar texto (título do item)
            txt_clip = TextClip(f"Top {i}: Cachoeira {i}", fontsize=50, color='white', font="Arial-Bold")
            txt_clip = txt_clip.set_position("center").set_duration(2)  # 2 segundos de duração para o texto

            # Sobrepor o texto sobre a imagem
            imagem_clip = CompositeVideoClip([imagem_clip, txt_clip])
            
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

            # Adicionar texto no vídeo
            txt_clip = TextClip(f"Top {i}: Cachoeira {i}", fontsize=50, color='white', font="Arial-Bold")
            txt_clip = txt_clip.set_position("center").set_duration(2)  # 2 segundos de duração para o texto

            # Sobrepor o texto sobre o vídeo
            video_clip = CompositeVideoClip([video_clip, txt_clip])
            
            clips.append(video_clip)
            
    if clips == []:
        print("Nenhum arquivo encontrado para criar o vídeo.")
        return

    # Concatenar todos os clipes
    final_clip = concatenate_videoclips(clips, method="compose")

    # Adicionar música (se fornecida)
    if music is not None:
        audio_clip = AudioFileClip(music)

        # Ajustar a duração do áudio para o vídeo final
        if audio_clip.duration < final_clip.duration:
            # Loop na música se for mais curta que o vídeo
            audio_clip = audio_clip.audio_loop(duration=final_clip.duration)
        else:
            # Cortar música se for mais longa que o vídeo
            audio_clip = audio_clip.subclip(0, final_clip.duration)

        # Vincular o áudio ao vídeo final
        final_clip = final_clip.set_audio(audio_clip)

    output_dir = os.path.join('output')
    os.makedirs(output_dir, exist_ok=True)
    
    # Exportar o vídeo final
    final_clip.write_videofile(os.path.join(output_dir, output_file), fps=24)
    print(f"Vídeo final criado: {output_file}")

# Diretório onde os arquivos foram baixados
download_dir = os.path.join('downloads')

# Caminho para a música (adicione manualmente a música desejada)
music_path = os.path.join('downloads', 'musica.mp3')

# Criar vídeo com música
criar_video(download_dir, music=music_path)
