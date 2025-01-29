import os
from PIL import Image, ImageDraw, ImageFont
import numpy as np
from moviepy.editor import *
import moviepy.config as mpy_config
from moviepy.audio.fx import all as afx
from dotenv import load_dotenv

load_dotenv()

# Defina o caminho completo para o magick.exe
mpy_config.IMAGEMAGICK_BINARY = os.getenv('IMAGEMAGICK_PATH')

# Diretórios
AUDIO_DIR = "output/audio"  # Onde os áudios gerados estão salvos
SCRIPT_PATH = "scripts/roteiro.txt"  # Caminho para o arquivo do roteiro

def quebrar_texto(texto, largura_maxima, fonte):
    """ Quebra o texto automaticamente para caber dentro da largura do vídeo, mantendo a centralização. """
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

def criar_texto_estilizado(texto, width, height, font_path="fonts/Roboto.ttf", font_size=120):
    """ 
    Cria texto estilizado com outline preto, sombra verde e preenchimento branco, 
    garantindo centralização e ajuste automático do tamanho da fonte.
    """
    max_height = int(height * 0.8)  # Permitir que o texto ocupe até 80% da tela

    # Criar imagem base
    img = Image.new("RGBA", (width, max_height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Ajuste dinâmico do tamanho da fonte se necessário
    fonte_tamanho = font_size
    fonte = ImageFont.truetype(font_path, fonte_tamanho)

    while True:
        texto_formatado = quebrar_texto(texto, int(width * 0.9), fonte)
        linhas = texto_formatado.split("\n")

        # Calcular altura total do bloco de texto para centralizar
        text_heights = [draw.textsize(linha, font=fonte)[1] for linha in linhas]
        total_text_height = sum(text_heights) + (len(linhas) - 1) * 10  # 10px de espaçamento entre linhas

        if total_text_height <= max_height:
            break  # Se couber dentro do espaço, manter esse tamanho de fonte
        else:
            fonte_tamanho -= 2  # Reduzir fonte se não couber
            fonte = ImageFont.truetype(font_path, fonte_tamanho)
    
    outline_range = 10
    shadow_offset = (4, 4)
    shadow_color = "green"
    text_color = "white"

    y = (max_height - total_text_height) // 2  # Centralizar verticalmente

    for linha in linhas:
        text_width, text_height = draw.textsize(linha, font=fonte)
        x = (width - text_width) // 2  # Centralizar horizontalmente

        # Desenhar contorno preto
        for dx in range(-outline_range, outline_range + 1):
            for dy in range(-outline_range, outline_range + 1):
                if dx != 0 or dy != 0:
                    draw.text((x + dx, y + dy), linha, font=fonte, fill="black")

        # Desenhar sombra verde
        draw.text((x + shadow_offset[0], y + shadow_offset[1]), linha, font=fonte, fill=shadow_color)

        # Desenhar texto principal branco
        draw.text((x, y), linha, font=fonte, fill=text_color)

        y += text_height + 10  # Mover para a próxima linha

    return img

def criar_clipe_texto(texto, duracao_audio, width, height, font_path="fonts/Roboto.ttf", font_size=120):
    """
    Cria um clipe de texto sincronizado com a duração do áudio, aplicando efeito typewriter acelerado.
    """
    clips = []
    linhas_quebradas = quebrar_texto(texto, int(width * 0.9), ImageFont.truetype(font_path, font_size))
    texto_final = "\n".join(linhas_quebradas)

    # **ACELERANDO O TYPEWRITER:** Agora ele será escrito na **metade** do tempo do áudio
    duracao_typewriter = duracao_audio * 0.3  # O texto será digitado em 30% do tempo do áudio

    for i in range(1, len(texto_final) + 1):
        img = criar_texto_estilizado(texto_final[:i], width, height, font_path, font_size)
        clip = ImageClip(np.array(img)).set_duration(duracao_typewriter / len(texto_final))
        clips.append(clip)

    typewriter_clip = concatenate_videoclips(clips, method="compose")

    # **TEXTO SOME APÓS O ÁUDIO:** O texto agora desaparece exatamente quando o áudio termina
    return typewriter_clip.set_duration(duracao_audio)

def adicionar_texto_e_audio(video_final_path, output_file="final_video_com_audio.mp4",
                            volume_narracao=1.5, volume_musica=0.3):
    """  
    Pega o vídeo já gerado e adiciona os textos e áudios sincronizados sobre ele,  
    ajustando os volumes da música e da narração.  
    """  
    if not os.path.exists(video_final_path):  
        print("❌ ERRO: Vídeo final não encontrado!")  
        return  
    
    video_clip = VideoFileClip(video_final_path)  
    screen_width, screen_height = video_clip.size  
    
    # Mantendo o áudio original do vídeo  
    audio_original = video_clip.audio  
    
    # Carregar roteiro  
    narracoes = carregar_roteiro(SCRIPT_PATH)  
    
    clipes_texto = []  
    clipes_audio = []  
    tempo_atual = 0  
    
    fonte_path = "fonts/Roboto.ttf"
    fonte_tamanho = int(screen_width * 0.05)
    fonte = ImageFont.truetype(fonte_path, fonte_tamanho)
    
    for narracao_id, partes_texto in narracoes.items():  
        parte_id = 1  
        for texto in partes_texto:  
            audio_path = os.path.join(AUDIO_DIR, f"narracao_{narracao_id}_{parte_id}.wav")  
            if os.path.exists(audio_path):  
                audio_clip = AudioFileClip(audio_path).fx(afx.volumex, volume_narracao)  # 📌 Aumentar volume da narração
                
                # Quebrar o texto automaticamente para caber dentro do vídeo  
                texto_formatado = quebrar_texto(texto, int(screen_width * 0.95), fonte)  
                
                # Criar um clipe de texto que aparece no início do áudio e desaparece no final  
                texto_clip = criar_texto_estilizado(texto_formatado, int(screen_width * 0.95), screen_height // 2)  
                texto_clip = ImageClip(np.array(texto_clip)).set_duration(audio_clip.duration)  
                texto_clip = texto_clip.set_position(("center", "center")).set_start(tempo_atual)  
                
                # Adicionar ao vídeo  
                clipes_texto.append(texto_clip)  
                clipes_audio.append(audio_clip.set_start(tempo_atual))  
                
                # Avançar o tempo para a próxima narração  
                tempo_atual += audio_clip.duration  
            parte_id += 1  
    
    if not clipes_texto or not clipes_audio:  
        print("⚠️ Nenhum texto ou áudio encontrado. O vídeo será gerado sem narração.")  
        return  
    
    # Combinar todos os textos e áudios  
    texto_final = CompositeVideoClip([video_clip] + clipes_texto)  
    audio_narracao = CompositeAudioClip(clipes_audio)  
    
    # Reduzindo volume da música de fundo  
    audio_original = audio_original.fx(afx.volumex, volume_musica)  # 📌 Diminuir volume da música  

    # Combinar áudio original com narrações  
    audio_final = CompositeAudioClip([audio_original, audio_narracao])  
    texto_final = texto_final.set_audio(audio_final)  

    # 🔥 Adicionar créditos ao final  
    credits_path = os.path.join("output", "credits.mp4")  
    if os.path.exists(credits_path):  
        credits_clip = VideoFileClip(credits_path)
        
        # Garantir que os créditos tenham a mesma largura do vídeo final
        credits_clip = credits_clip.resize(width=screen_width)

        # Concatenar o vídeo final com os créditos  
        texto_final = concatenate_videoclips([texto_final, credits_clip], method="compose")  
        print("🎬 Créditos adicionados ao final do vídeo.")

    output_dir = os.path.join('output')  
    os.makedirs(output_dir, exist_ok=True)  
    
    # Exportar o vídeo final com textos e áudios sincronizados  
    texto_final.write_videofile(os.path.join(output_dir, output_file), fps=24)  
    
    texto_final.close()  
    video_clip.close()  
    
    print(f"🎥 Vídeo final com narração e música ajustadas criado: {output_file}")

def carregar_roteiro(script_path):
    """ Lê o roteiro e separa os textos corretamente, como foi feito no script de geração de voz. """
    narracoes = {}

    try:
        with open(script_path, "r", encoding="utf-8") as file:
            linhas = file.readlines()

        narracao_id = 0  # Número da narração no roteiro

        for linha in linhas:
            linha = linha.strip()

            # Ignora a linha "NARRACAO:"
            if linha.startswith("NARRACAO:"):
                continue  

            # Detecta uma nova narração baseada no número inicial da linha
            if linha and linha[0].isdigit() and "." in linha:
                texto_completo = linha.split(". ", 1)[1]  # Pega apenas o texto, ignorando o número da narração
                narracao_id += 1
                partes = texto_completo.split(",")  # Divide a frase nas vírgulas
                
                # Adiciona cada parte no dicionário
                narracoes[narracao_id] = [parte.strip() for parte in partes if parte.strip()]

        print("✅ Roteiro carregado corretamente!")
        return narracoes

    except Exception as e:
        print(f"❌ Erro ao carregar o roteiro: {e}")
        return {}
    
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

    # Adicionar vídeos respeitando o tempo total desejado
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

            # 🔥 NOVA CORREÇÃO: Garantir que o vídeo preencha 1080x1920 sem bordas pretas
            proporcao_video = video_clip.w / video_clip.h
            proporcao_tela = screen_width / screen_height

            if proporcao_video > proporcao_tela:
                # Se o vídeo for mais largo que a tela, redimensionamos para altura e cortamos os lados
                video_clip = video_clip.resize(height=screen_height)
                video_clip = video_clip.crop(width=screen_width, height=screen_height,
                                             x_center=video_clip.w / 2, y_center=video_clip.h / 2)
            else:
                # Se o vídeo for mais estreito, redimensionamos para a largura e cortamos o topo/fundo
                video_clip = video_clip.resize(width=screen_width)
                video_clip = video_clip.crop(width=screen_width, height=screen_height,
                                             x_center=video_clip.w / 2, y_center=video_clip.h / 2)

            clips.append(video_clip)
            tempo_acumulado += duracao_video

    print(f"Total final acumulado: {tempo_acumulado:.1f}s")

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
        
    print(f"🎥 Vídeo final criado: {output_file}")

# Diretório onde os arquivos foram baixados
download_dir = os.path.join('downloads')

# Caminho para a música (adicione manualmente a música desejada)
music_path = os.path.join('musics', 'musica.mp3')

# Criar vídeo com música
criar_video(download_dir, music=music_path, tempo_total_desejado=60, tempo_maximo_por_video=15)
video_base_path = os.path.join("output", "final_video.mp4")

# Agora adicionamos os textos e a narração por cima
adicionar_texto_e_audio(video_base_path, output_file="final_video_com_audio.mp4")