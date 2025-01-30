import os
from PIL import Image, ImageDraw, ImageFont
import numpy as np
from moviepy.editor import *
import moviepy.config as mpy_config
from moviepy.audio.fx import all as afx
from dotenv import load_dotenv

load_dotenv()

mpy_config.IMAGEMAGICK_BINARY = os.getenv('IMAGEMAGICK_PATH')

class VideoMaker:
    def __init__(self, audio_dir="output/audio", script_path="scripts/roteiro.txt"):
        self.audio_dir = audio_dir
        self.script_path = script_path

    def quebrar_texto(self, texto, largura_maxima, fonte):
        linhas = []
        palavras = texto.split()
        linha_atual = ""
        draw = ImageDraw.Draw(Image.new("RGB", (largura_maxima, 100)))

        for palavra in palavras:
            linha_teste = linha_atual + " " + palavra if linha_atual else palavra
            largura_texto, _ = draw.textsize(linha_teste, font=fonte)
            if largura_texto <= largura_maxima:
                linha_atual = linha_teste
            else:
                linhas.append(linha_atual)
                linha_atual = palavra

        if linha_atual:
            linhas.append(linha_atual)

        return "\n".join(linhas)

    def criar_texto_estilizado(self, texto, width, height, font_path="fonts/Roboto.ttf", font_size=120):
        max_height = int(height * 0.8)
        img = Image.new("RGBA", (width, max_height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        fonte_tamanho = font_size
        fonte = ImageFont.truetype(font_path, fonte_tamanho)

        while True:
            texto_formatado = self.quebrar_texto(texto, int(width * 0.9), fonte).rstrip('.')
            linhas = texto_formatado.split("\n")
            text_heights = [draw.textsize(linha, font=fonte)[1] for linha in linhas]
            total_text_height = sum(text_heights) + (len(linhas) - 1) * 10

            if total_text_height <= max_height:
                break
            else:
                fonte_tamanho -= 2
                fonte = ImageFont.truetype(font_path, fonte_tamanho)
        
        outline_range = 10
        shadow_offset = (4, 4)
        shadow_color = "green"
        text_color = "white"

        y = (max_height - total_text_height) // 2

        for linha in linhas:
            text_width, text_height = draw.textsize(linha, font=fonte)
            x = (width - text_width) // 2

            for dx in range(-outline_range, outline_range + 1):
                for dy in range(-outline_range, outline_range + 1):
                    if dx != 0 or dy != 0:
                        draw.text((x + dx, y + dy), linha, font=fonte, fill="black")

            draw.text((x + shadow_offset[0], y + shadow_offset[1]), linha, font=fonte, fill=shadow_color)
            draw.text((x, y), linha, font=fonte, fill=text_color)

            y += text_height + 10

        return img

    def carregar_roteiro(self):
        narracoes = {}

        try:
            with open(self.script_path, "r", encoding="utf-8") as file:
                linhas = file.readlines()

            narracao_id = 0

            for linha in linhas:
                linha = linha.strip()

                if linha.startswith("NARRACAO:"):
                    continue  

                if linha and linha[0].isdigit() and "." in linha:
                    texto_completo = linha.split(". ", 1)[1]
                    narracao_id += 1
                    partes = texto_completo.split(",")

                    narracoes[narracao_id] = [parte.strip() for parte in partes if parte.strip()]

            return narracoes

        except Exception as e:
            return {}

    def criar_video(self, download_dir, music=None, output_file="final_video.mp4", tempo_total_desejado=80, tempo_maximo_por_video=10):
        clips = []
        screen_width, screen_height = 1080, 1920
        tempo_acumulado = 0

        for i in range(1, 100):
            if tempo_acumulado >= tempo_total_desejado:
                break

            video_path = os.path.join(download_dir, f"video_{i}.mp4")
            if os.path.exists(video_path):
                video_clip = VideoFileClip(video_path)
                duracao_video = min(video_clip.duration, tempo_maximo_por_video)

                if tempo_acumulado + duracao_video > tempo_total_desejado:
                    duracao_video = tempo_total_desejado - tempo_acumulado

                video_clip = video_clip.subclip(0, duracao_video)

                proporcao_video = video_clip.w / video_clip.h
                proporcao_tela = screen_width / screen_height

                if proporcao_video > proporcao_tela:
                    video_clip = video_clip.resize(height=screen_height)
                    video_clip = video_clip.crop(width=screen_width, height=screen_height,
                                                 x_center=video_clip.w / 2, y_center=video_clip.h / 2)
                else:
                    video_clip = video_clip.resize(width=screen_width)
                    video_clip = video_clip.crop(width=screen_width, height=screen_height,
                                                 x_center=video_clip.w / 2, y_center=video_clip.h / 2)

                clips.append(video_clip)
                tempo_acumulado += duracao_video

        if not clips:
            return

        clips_com_transicoes = []
        duration_transicao = 0.3

        clips_com_transicoes.append(clips[0])

        for i in range(1, len(clips)):
            clipe_atual = clips[i].crossfadein(duration_transicao)
            clips_com_transicoes.append(clipe_atual)

        final_clip = concatenate_videoclips(clips_com_transicoes, method="compose")

        if music is not None:
            audio_clip = AudioFileClip(music)

            if audio_clip.duration < final_clip.duration:
                audio_clip = audio_clip.audio_loop(duration=final_clip.duration)
            else:
                audio_clip = audio_clip.subclip(0, final_clip.duration)

            final_clip = final_clip.set_audio(audio_clip)

        output_dir = os.path.join('output')
        os.makedirs(output_dir, exist_ok=True)

        final_clip.write_videofile(os.path.join(output_dir, output_file), fps=24)

        final_clip.close()
        for clip in clips:
            clip.close()

    def adicionar_texto_e_audio(self, video_final_path, output_file="final_video_com_audio.mp4",
                                volume_narracao=1.5, volume_musica=0.2):
        if not os.path.exists(video_final_path):
            return  

        video_clip = VideoFileClip(video_final_path)
        screen_width, screen_height = video_clip.size
        audio_original = video_clip.audio.fx(afx.volumex, volume_musica)
        narracoes = self.carregar_roteiro()
        clipes_texto = []
        clipes_audio = []
        tempo_atual = 0
        fonte_path = "fonts/Roboto.ttf"
        fonte_tamanho = int(screen_width * 0.05)
        fonte = ImageFont.truetype(fonte_path, fonte_tamanho)

        for narracao_id, partes_texto in narracoes.items():
            parte_id = 1
            for texto in partes_texto:
                audio_path = os.path.join(self.audio_dir, f"narracao_{narracao_id}_{parte_id}.wav")
                if os.path.exists(audio_path):
                    audio_clip = AudioFileClip(audio_path).fx(afx.volumex, volume_narracao)
                    texto_formatado = self.quebrar_texto(texto, int(screen_width * 0.95), fonte)
                    texto_clip = self.criar_texto_estilizado(texto_formatado, int(screen_width * 0.95), screen_height // 2)
                    texto_clip = ImageClip(np.array(texto_clip)).set_duration(audio_clip.duration).set_position(("center", "center")).set_start(tempo_atual)
                    clipes_texto.append(texto_clip)
                    clipes_audio.append(audio_clip.set_start(tempo_atual))
                    tempo_atual += audio_clip.duration
                parte_id += 1

        texto_final = CompositeVideoClip([video_clip] + clipes_texto).set_audio(CompositeAudioClip([audio_original, CompositeAudioClip(clipes_audio)]))
        texto_final.write_videofile(os.path.join("output", output_file), fps=24)

if __name__ == "__main__":
    vm = VideoMaker()
    vm.criar_video("downloads", "musics/musica.mp3")
    vm.adicionar_texto_e_audio("output/final_video.mp4")
