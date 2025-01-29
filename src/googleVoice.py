import os
from google.cloud import texttospeech_v1 as texttospeech
from dotenv import load_dotenv

# Carregar variáveis do .env
load_dotenv()

# Pegar a API Key do arquivo .env
API_KEY = os.getenv("GOOGLE_API_KEY")

# Caminhos das pastas
SCRIPT_PATH = "scripts/roteiro_gatos.txt"  # Caminho do roteiro
OUTPUT_DIR = "output/audio"  # Pasta onde os áudios serão salvos
os.makedirs(OUTPUT_DIR, exist_ok=True)

def gerar_audio_google(texto, idioma="pt-BR", nome_voz="pt-BR-Wavenet-A", arquivo_audio="output.wav"):
    try:
        # Criar o cliente da API com a API Key
        client = texttospeech.TextToSpeechClient(
            client_options={"api_key": API_KEY}
        )

        # Configurar o texto e as configurações de voz
        synthesis_input = texttospeech.SynthesisInput(text=texto)
        voice = texttospeech.VoiceSelectionParams(
            language_code=idioma,
            name=nome_voz  # Nome da voz específico
        )
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.LINEAR16,  # Formato especificado no demo
            effects_profile_id=["small-bluetooth-speaker-class-device"],  # Perfil de efeitos
            speaking_rate=1.0,  # Velocidade de fala
            pitch=2.0  # Tom
        )

        # Solicitar a síntese de fala
        response = client.synthesize_speech(
            input=synthesis_input,
            voice=voice,
            audio_config=audio_config
        )

        # Salvar o arquivo de áudio
        with open(arquivo_audio, "wb") as out:
            out.write(response.audio_content)
        print(f"✅ Áudio gerado: {arquivo_audio}")

    except Exception as e:
        print(f"❌ Erro ao gerar áudio: {e}")

def processar_roteiro(script_path):
    """
    Lê o arquivo de roteiro e gera os áudios apenas para as frases da NARRAÇÃO.
    """
    try:
        with open(script_path, "r", encoding="utf-8") as file:
            linhas = file.readlines()

        narracao_textos = []
        
        for linha in linhas:
            if linha.startswith("NARRACAO:"):
                continue  # Ignora o cabeçalho "NARRACAO:"
            if linha.strip() and linha[0].isdigit() and "." in linha:
                narracao_textos.append(linha.strip().split(". ", 1)[1])  # Remove numeração

        print(f"🎙️ {len(narracao_textos)} frases encontradas para narração.")

        # Gerar áudios para cada frase da narração
        for i, texto in enumerate(narracao_textos, start=1):
            arquivo_audio = os.path.join(OUTPUT_DIR, f"narracao_{i}.wav")
            print(f"\n🔊 {texto}")
            gerar_audio_google(texto, nome_voz="pt-BR-Wavenet-A", arquivo_audio=arquivo_audio)

        print("✅ Todos os áudios foram gerados!")

    except Exception as e:
        print(f"❌ Erro ao processar o roteiro: {e}")

if __name__ == "__main__":
    processar_roteiro(SCRIPT_PATH)
