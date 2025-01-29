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

def gerar_audio_google(texto, idioma="pt-BR", nome_voz="pt-BR-Wavenet-B", arquivo_audio="output.wav"):
    try:
        client = texttospeech.TextToSpeechClient(
            client_options={"api_key": API_KEY}
        )

        synthesis_input = texttospeech.SynthesisInput(text=texto)
        voice = texttospeech.VoiceSelectionParams(
            language_code=idioma,
            name=nome_voz  
        )
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.LINEAR16,
            effects_profile_id=["small-bluetooth-speaker-class-device"],
            speaking_rate=1.0,
            pitch=0.5
        )

        response = client.synthesize_speech(
            input=synthesis_input,
            voice=voice,
            audio_config=audio_config
        )

        with open(arquivo_audio, "wb") as out:
            out.write(response.audio_content)
        print(f"✅ Áudio gerado: {arquivo_audio}")

    except Exception as e:
        print(f"❌ Erro ao gerar áudio: {e}")

def processar_roteiro(script_path):
    try:
        with open(script_path, "r", encoding="utf-8") as file:
            linhas = file.readlines()

        narracao_id = 0  # Número da narração no roteiro

        for linha in linhas:
            if linha.startswith("NARRACAO:"):
                continue  

            if linha.strip() and linha[0].isdigit() and "." in linha:
                texto_completo = linha.strip().split(". ", 1)[1]  
                narracao_id += 1
                partes = texto_completo.split(",")  # Divide a frase nas vírgulas
                
                # Gerar áudios para cada parte
                for parte_id, parte in enumerate(partes, start=1):
                    parte_texto = parte.strip()
                    arquivo_audio = os.path.join(OUTPUT_DIR, f"narracao_{narracao_id}_{parte_id}.wav")
                    gerar_audio_google(parte_texto, nome_voz="pt-BR-Wavenet-A", arquivo_audio=arquivo_audio)

        print("✅ Todos os áudios foram gerados!")

    except Exception as e:
        print(f"❌ Erro ao processar o roteiro: {e}")

if __name__ == "__main__":
    processar_roteiro(SCRIPT_PATH)
    # gerar_audio_google("Gostou? Curta e compartilhe para mais curiosidades!")
