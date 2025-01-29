import os
from PIL import Image, ImageDraw, ImageFont
import numpy as np
from moviepy.editor import *
import moviepy.config as mpy_config
from dotenv import load_dotenv

load_dotenv()

# Defina o caminho completo para o magick.exe
mpy_config.IMAGEMAGICK_BINARY = os.getenv('IMAGEMAGICK_PATH')

# Função para criar texto estilizado com sombra, outline e preenchimento
def criar_texto_estilizado(texto_linha1, texto_linha2, width, height, font_path="fonts/Roboto.ttf", font_size=120):
    """
    Cria texto estilizado com outline preto, sombra verde e preenchimento branco.
    """
    # Criar imagem base
    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Carregar a fonte
    font = ImageFont.truetype(font_path, font_size)

    # Medir os textos
    text1_width, text1_height = draw.textsize(texto_linha1, font=font)
    text2_width, text2_height = draw.textsize(texto_linha2, font=font)

    # Calcular as posições para o topo
    text1_x = (width - text1_width) // 2
    text1_y = 50  # Margem do topo para o texto da linha 1
    text2_x = (width - text2_width) // 2
    text2_y = text1_y + text1_height + 10

    # Parâmetros do estilo
    outline_range = 10  # Espessura do outline
    shadow_offset = (4, 4)  # Deslocamento da sombra (x, y)
    shadow_color = "green"  # Cor da sombra
    text_color = "white"  # Cor do texto principal

    # Desenhar outline do texto (contorno preto)
    for dx in range(-outline_range, outline_range + 1):
        for dy in range(-outline_range, outline_range + 1):
            if dx != 0 or dy != 0:
                draw.text((text1_x + dx, text1_y + dy), texto_linha1, font=font, fill="black")
                draw.text((text2_x + dx, text2_y + dy), texto_linha2, font=font, fill="black")

    # Desenhar sombra (deslocada para baixo e direita)
    draw.text((text1_x + shadow_offset[0], text1_y + shadow_offset[1]), texto_linha1, font=font, fill=shadow_color)
    draw.text((text2_x + shadow_offset[0], text2_y + shadow_offset[1]), texto_linha2, font=font, fill=shadow_color)

    # Desenhar texto principal (branco)
    draw.text((text1_x, text1_y), texto_linha1, font=font, fill=text_color)
    draw.text((text2_x, text2_y), texto_linha2, font=font, fill=text_color)

    return img

# Função para criar o efeito typewriter no texto
def criar_texto_typewriter(texto, width, height, font_path="fonts/Roboto.ttf", font_size=80, duration=3, hold_time=2):
    """
    Cria um efeito de typewriter para o texto, caractere por caractere,
    usando a função criar_texto_estilizado e permitindo que o texto permaneça visível após o efeito.
    """
    clips = []
    for i in range(1, len(texto) + 1):
        # Gerar o texto estilizado para cada caractere
        img = criar_texto_estilizado(
            texto[:i], "",  # Apenas a linha 1 será preenchida caractere por caractere
            width, height,
            font_path=font_path,
            font_size=font_size
        )

        # Criar clipe de imagem para o texto parcial
        clip = ImageClip(np.array(img)).set_duration(duration / len(texto))
        clips.append(clip)

    # Concatenar todos os clipes do typewriter
    typewriter_clip = concatenate_videoclips(clips, method="compose")

    # Adicionar o tempo de "hold" após o efeito
    texto_completo = criar_texto_estilizado(
        texto, "",  # Texto completo
        width, height,
        font_path=font_path,
        font_size=font_size
    )
    hold_clip = ImageClip(np.array(texto_completo)).set_duration(hold_time)

    # Combinar o efeito typewriter com o tempo de espera
    return concatenate_videoclips([typewriter_clip, hold_clip], method="compose")

# Função principal para criar o vídeo
def criar_video(download_dir, music=None, output_file="final_video.mp4", tempo_total_desejado=60, tempo_maximo_por_video=15):
    """
    Cria um vídeo final combinando vídeos e imagens baixadas, garantindo que o tempo total fique dentro do desejado.
    
    :param download_dir: Diretório onde os arquivos baixados estão armazenados.
    :param music: Caminho para o arquivo de música.
    :param output_file: Nome do arquivo de saída.
    :param tempo_total_desejado: Tempo total do vídeo final em segundos.
    :param tempo_maximo_por_video: Tempo máximo permitido para cada vídeo.
    """
    clips = []
    screen_width, screen_height = 1080, 1920  # Resolução 9:16
    tempo_acumulado = 0

    # Adicionar imagens (se houver espaço no tempo total)
    for i in range(1, 4):  # Supondo 3 imagens
        if tempo_acumulado >= tempo_total_desejado:
            break

        imagem_path = os.path.join(download_dir, f"imagem_{i}.jpg")
        if os.path.exists(imagem_path):
            duracao_imagem = 5  # Definimos que cada imagem dura 5 segundos

            if tempo_acumulado + duracao_imagem > tempo_total_desejado:
                duracao_imagem = tempo_total_desejado - tempo_acumulado  # Ajustar para não ultrapassar

            imagem_clip = ImageClip(imagem_path, duration=duracao_imagem)

            # Redimensionar e centralizar imagem
            imagem_clip = imagem_clip.resize(height=screen_height)
            imagem_clip = imagem_clip.on_color(
                size=(screen_width, screen_height),
                color=(0, 0, 0),
                pos="center"
            )

            # Criar efeito typewriter para o texto
            texto_clip = criar_texto_typewriter(
                f"TOP {i}: Montanha {i}",
                screen_width,
                screen_height // 4,
                font_size=120,
                duration=2,  # Duração do efeito typewriter
                hold_time=2  # Tempo que o texto permanece após o efeito
            ).set_position(("center", 50))  # Posição no topo do vídeo

            # Sobrepor o texto sobre a imagem
            imagem_clip = CompositeVideoClip([imagem_clip, texto_clip])

            imagem_clip = imagem_clip.set_fps(24)
            clips.append(imagem_clip)
            tempo_acumulado += duracao_imagem

    # Adicionar vídeos, respeitando o tempo total desejado
    for i in range(1, 10):  # Supondo até 10 vídeos para garantir que haja tempo suficiente
        if tempo_acumulado >= tempo_total_desejado:
            break

        video_path = os.path.join(download_dir, f"video_{i}.mp4")
        if os.path.exists(video_path):
            print(f"Adicionando vídeo {video_path}, total acumulado: {tempo_acumulado:.1f}s")
            video_clip = VideoFileClip(video_path)
            duracao_video = min(video_clip.duration, tempo_maximo_por_video)

            # Ajustar para que o tempo total não ultrapasse o limite desejado
            if tempo_acumulado + duracao_video > tempo_total_desejado:
                duracao_video = tempo_total_desejado - tempo_acumulado  # Ajustar para não ultrapassar

            video_clip = video_clip.subclip(0, duracao_video)  # Cortar para o tempo máximo permitido

            # Redimensionar vídeo ao formato vertical
            video_clip = video_clip.resize(height=screen_height)
            video_clip = video_clip.crop(width=screen_width, height=screen_height, x_center=video_clip.w / 2, y_center=video_clip.h / 2)

            # Criar efeito typewriter para o texto
            texto_clip = criar_texto_typewriter(
                f"TOP {i}: Montanha {i}",
                screen_width,
                screen_height // 4,
                font_size=120,
                duration=0.6,  # Duração do efeito typewriter
                hold_time=5  # Tempo que o texto permanece após o efeito
            ).set_position(("center", 50))  # Posição no topo do vídeo

            # Sobrepor o texto sobre o vídeo
            video_clip = CompositeVideoClip([video_clip, texto_clip])

            clips.append(video_clip)
            tempo_acumulado += duracao_video

    print(f"total final acumulado: {tempo_acumulado:.1f}s")
    # return

    if not clips:
        print("Nenhum arquivo encontrado para criar o vídeo.")
        return

    # Criar transições entre os clipes
    clips_com_transicoes = []
    duration_transicao = 0.3  # Duração da transição

    for i in range(len(clips) - 1):
        clipe_proximo = clips[i]
        clipe_proximo = clipe_proximo.crossfadein(duration_transicao)
        clips_com_transicoes.append(clipe_proximo)

    clips_com_transicoes.append(clips[-1])

    # Concatenar todos os clipes com as transições
    final_clip = concatenate_videoclips(clips_com_transicoes, method="compose")

    # Adicionar música (se fornecida)
    if music is not None:
        audio_clip = AudioFileClip(music)

        # Ajustar a duração do áudio para o vídeo final
        if audio_clip.duration < final_clip.duration:
            audio_clip = audio_clip.audio_loop(duration=final_clip.duration)
        else:
            audio_clip = audio_clip.subclip(0, final_clip.duration)

        final_clip = final_clip.set_audio(audio_clip)

    output_dir = os.path.join('output')
    os.makedirs(output_dir, exist_ok=True)

    # Exportar o vídeo final
    final_clip.write_videofile(os.path.join(output_dir, output_file), fps=24)
    
    final_clip.close()
    for clip in clips:
        clip.close()
        
    print(f"Vídeo final criado: {output_file}")

# Diretório onde os arquivos foram baixados
download_dir = os.path.join('downloads')

# Caminho para a música (adicione manualmente a música desejada)
music_path = os.path.join('musics', 'musica.mp3')

# Criar vídeo com música
criar_video(download_dir, music=music_path, tempo_total_desejado=60, tempo_maximo_por_video=15)
