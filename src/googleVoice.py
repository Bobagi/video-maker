import os
from google.cloud import texttospeech_v1 as texttospeech
from dotenv import load_dotenv

# Carregar variáveis do .env
load_dotenv()

# Pegar a API Key do arquivo .env
API_KEY = os.getenv("GOOGLE_API_KEY")

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
            pitch=0.0  # Tom
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
        print(f"Áudio gerado com sucesso: {arquivo_audio}")

    except Exception as e:
        print(f"Erro ao gerar áudio com Google Text-to-Speech: {e}")

if __name__ == "__main__":
    texto_teste = "O Grand Canyon é uma das maravilhas naturais mais impressionantes do mundo."
    gerar_audio_google(texto_teste, nome_voz="pt-BR-Wavenet-A", arquivo_audio="grand_canyon_feminina.wav")
