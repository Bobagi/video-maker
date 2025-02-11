import os
from google.cloud import texttospeech_v1 as texttospeech
from dotenv import load_dotenv
from pydub import AudioSegment  # Importar a biblioteca pydub para calcular a duração do áudio

# Carregar variáveis do .env
load_dotenv()

class GoogleVoice:
    def __init__(self):
        # Pegar a API Key do arquivo .env
        self.API_KEY = os.getenv("GOOGLE_API_KEY")
        # Caminhos das pastas
        self.SCRIPT_PATH = os.path.join("scripts", "roteiro.txt")  # Caminho do roteiro
        self.OUTPUT_DIR = os.path.join("output", "audio")          # Pasta onde os áudios serão salvos
        os.makedirs(self.OUTPUT_DIR, exist_ok=True)

    def gerar_audio_google(self, texto, idioma="pt-BR", nome_voz="pt-BR-Wavenet-A", arquivo_audio="output.wav"):
        try:
            client = texttospeech.TextToSpeechClient(
                client_options={"api_key": self.API_KEY}
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

            # Retornar o caminho do arquivo de áudio para calcular a duração
            return arquivo_audio

        except Exception as e:
            print(f"❌ Erro ao gerar áudio: {e}")
            return None

    def processar_roteiro(self, script_path=None):
        if script_path is None:
            script_path = self.SCRIPT_PATH

        try:
            with open(script_path, "r", encoding="utf-8") as file:
                linhas = file.readlines()

            narracao_id = 0  # Número da narração no roteiro
            tempo_total = 0  # Variável para armazenar o tempo total de áudio

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
                        arquivo_audio = os.path.join(self.OUTPUT_DIR, f"narracao_{narracao_id}_{parte_id}.wav")
                        arquivo_gerado = self.gerar_audio_google(parte_texto, nome_voz="pt-BR-Wavenet-A", arquivo_audio=arquivo_audio)
                        
                        # Calcular a duração do áudio gerado e adicionar ao tempo total
                        if arquivo_gerado:
                            audio = AudioSegment.from_file(arquivo_gerado)
                            duracao = len(audio) / 1000  # Converter milissegundos para segundos
                            tempo_total += duracao

            print(f"✅ Todos os áudios foram gerados! Tempo total: {tempo_total:.2f} segundos.")
            return tempo_total  # Retornar o tempo total

        except Exception as e:
            print(f"❌ Erro ao processar o roteiro: {e}")
            return 0  # Retornar 0 em caso de erro

    def testar_ambiente(self):
        # Verifica se a API Key está disponível
        if not self.API_KEY:
            print("❌ Erro: GOOGLE_API_KEY não encontrada no arquivo .env.")
            return False

        # Verifica se o arquivo de roteiro existe
        if not os.path.exists(self.SCRIPT_PATH):
            print(f"❌ Erro: Arquivo de roteiro não encontrado em {self.SCRIPT_PATH}.")
            return False

        # Verifica se a pasta de output é gravável
        try:
            teste_file = os.path.join(self.OUTPUT_DIR, "teste.txt")
            with open(teste_file, "w") as f:
                f.write("Teste")
            os.remove(teste_file)
        except Exception as e:
            print(f"❌ Erro: Pasta de saída não é gravável: {e}")
            return False

        # Teste de síntese de áudio com um texto curto
        print("🔄 Testando síntese de áudio com texto de teste...")
        teste_audio = os.path.join(self.OUTPUT_DIR, "teste.wav")
        resultado = self.gerar_audio_google("Teste de síntese de áudio", arquivo_audio=teste_audio)
        if not resultado or not os.path.exists(resultado):
            print("❌ Erro: Falha na síntese de áudio de teste.")
            return False

        # Tenta carregar o áudio gerado para verificar a integridade
        try:
            audio = AudioSegment.from_file(resultado)
            duracao = len(audio) / 1000  # Converter milissegundos para segundos
            print(f"✅ Teste de síntese concluído com sucesso. Duração: {duracao:.2f} segundos.")
            # Remove o arquivo de teste
            os.remove(resultado)
        except Exception as e:
            print(f"❌ Erro: Falha ao carregar o áudio de teste: {e}")
            return False

        print("✅ Todos os testes foram concluídos com sucesso.")
        return True

# Função para permitir a execução direta do script
if __name__ == "__main__":
    google_voice = GoogleVoice()
    # Primeiro, testar o ambiente
    if google_voice.testar_ambiente():
        print("Iniciando o processamento do roteiro...")
        google_voice.processar_roteiro()
    else:
        print("Verifique os erros acima e corrija antes de continuar.")
