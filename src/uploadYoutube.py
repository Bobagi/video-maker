#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import datetime
from datetime import timedelta, time
import shutil
import json

from dotenv import load_dotenv
load_dotenv()

import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
from googleapiclient.http import MediaFileUpload

# Para gerenciamento e renovação das credenciais
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request

# Escopos atualizados para upload e leitura
SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube.readonly"
]

class YouTubeUploader:
    def __init__(self, client_secrets_filename="client_secrets.json", output_dir="output", backup_dir="output_backup"):
        """
        Inicializa a classe YouTubeUploader.
        
        Parâmetros:
          - client_secrets_filename: caminho do arquivo de credenciais OAuth (client_secrets.json)
          - output_dir: pasta onde estão os vídeos a serem enviados
          - backup_dir: pasta para onde os vídeos serão movidos após o upload
        """
        # Diretório deste script e raiz do projeto
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        self.project_root = os.path.abspath(os.path.join(self.script_dir, ".."))
        self.client_secrets_file = os.path.join(self.project_root, client_secrets_filename)
        self.output_dir = os.path.join(self.project_root, output_dir)
        self.backup_dir = os.path.join(self.project_root, backup_dir)
        
        # Garante que a pasta de backup exista
        if not os.path.exists(self.backup_dir):
            os.makedirs(self.backup_dir)
            
        # Inicialmente, o serviço do YouTube não foi autenticado
        self.youtube = None

    def authenticate(self):
        """
        Realiza a autenticação com a API do YouTube usando OAuth 2.0.
        Armazena as credenciais em um arquivo (token.json) para evitar a necessidade
        de login a cada execução.
        """

        token_path = os.path.join(self.project_root, 'token.json')
        creds = None

        # Tenta carregar as credenciais salvas
        if os.path.exists(token_path):
            try:
                creds = Credentials.from_authorized_user_file(token_path, SCOPES)
            except Exception as e:
                print("Erro ao ler o token salvo:", e)
                creds = None  # Força nova autorização se houver problema ao ler o token

        # Se não houver credenciais válidas, tenta atualizar ou força o fluxo OAuth
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                except Exception as e:
                    print("Erro ao atualizar as credenciais:", e)
                    # Se a atualização falhar, remove o token antigo e força nova autorização
                    if os.path.exists(token_path):
                        os.remove(token_path)
                        print("Token antigo removido devido a falha na atualização.")
                    creds = None
            if not creds:
                # Verifica se o arquivo de client_secrets existe
                if not os.path.exists(self.client_secrets_file):
                    print("Arquivo client_secrets.json não encontrado em:", self.client_secrets_file)
                    sys.exit(1)
                
                # Permite o transporte inseguro (útil em ambientes de teste)
                os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
                
                # Cria o fluxo OAuth, solicitando acesso offline e forçando o consentimento
                flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
                    self.client_secrets_file, SCOPES)
                creds = flow.run_local_server(port=8080, access_type='offline', prompt='consent')
                
                # Salva as credenciais para a próxima execução
                with open(token_path, 'w') as token_file:
                    token_file.write(creds.to_json())
        
        # Inicializa o serviço da API do YouTube com as credenciais obtidas
        self.youtube = googleapiclient.discovery.build("youtube", "v3", credentials=creds)
        print("Autenticação realizada com sucesso!")

    def test_connection(self):
        """
        Método de teste para verificar se a conexão com a API do YouTube está funcionando.
        Lista os canais do usuário autenticado.
        """
        if self.youtube is None:
            print("Serviço do YouTube não autenticado. Chame o método authenticate() primeiro.")
            return
        
        try:
            request = self.youtube.channels().list(
                part="snippet",
                mine=True
            )
            response = request.execute()
            print("Conexão com a API bem-sucedida! Dados do canal:")
            print(response)
        except Exception as e:
            print("Falha na conexão com a API:", e)

    def get_video_files(self):
        """
        Retorna uma lista com os caminhos completos dos arquivos de vídeo encontrados na pasta de output.
        """
        video_extensions = ('.mp4', '.mov', '.avi', '.mkv')
        files = []
        if not os.path.exists(self.output_dir):
            print("Diretório de output não existe:", self.output_dir)
            return files
        for file in os.listdir(self.output_dir):
            if file.lower().endswith(video_extensions):
                files.append(os.path.join(self.output_dir, file))
        return files

    def generate_schedule(self, num_videos, start_time=None):
        """
        Gera uma lista de horários para agendamento dos uploads.
        São definidos os slots: 08:00, 12:00 e 18:00.
        Se start_time for fornecido, os agendamentos serão calculados a partir dele;
        caso contrário, utiliza a hora atual.
        
        Parâmetros:
        - num_videos: quantidade de vídeos a serem agendados.
        - start_time: (opcional) objeto datetime (timezone-aware) a partir do qual os agendamentos serão calculados.
        
        Retorna:
        - Lista de objetos datetime (timezone-aware) com os horários agendados.
        """
        schedule = []
        if start_time is None:
            now = datetime.datetime.now().astimezone()
        else:
            now = start_time  # Usa o horário base informado

        current_date = now.date()
        slots = [time(8, 0), time(12, 0), time(18, 0)]
        
        while len(schedule) < num_videos:
            for slot in slots:
                scheduled_dt = datetime.datetime.combine(current_date, slot)
                scheduled_dt = scheduled_dt.replace(tzinfo=now.tzinfo)
                if scheduled_dt > now:
                    schedule.append(scheduled_dt)
                    if len(schedule) == num_videos:
                        break
            current_date += timedelta(days=1)
        return schedule

    def upload_all_videos(self):
        """
        Faz o upload de todos os vídeos encontrados na pasta de output, agendando-os conforme os
        horários definidos (08:00, 12:00 e 18:00) e movendo-os para a pasta de backup após o upload.
        """
        video_files = self.get_video_files()
        if not video_files:
            print("Nenhum vídeo encontrado na pasta:", self.output_dir)
            return
        
        schedule_times = self.generate_schedule(len(video_files))
        
        for video_file, scheduled_time in zip(video_files, schedule_times):
            sucesso = self._do_upload(video_file, None, None, scheduled_time)
            if sucesso:
                backup_path = os.path.join(self.backup_dir, os.path.basename(video_file))
                try:
                    shutil.move(video_file, backup_path)
                    print(f"Vídeo movido para backup: {backup_path}")
                except Exception as e:
                    print("Erro ao mover o arquivo para backup:", e)
            else:
                print("Upload falhou para o vídeo:", video_file)

    def upload_single_video(self, video_file, title, description, scheduled_time=None):
        """
        Faz o upload de um vídeo individual, recebendo como parâmetros:
          - video_file: caminho para o arquivo de vídeo
          - title: título do vídeo
          - description: descrição do vídeo
          - scheduled_time: (opcional) objeto datetime (timezone-aware) com a data/hora de publicação.
            Se não informado, utiliza o primeiro slot disponível da função generate_schedule().
          
        Após o upload com sucesso, o vídeo é movido para a pasta de backup.
        
        Retorna:
          - True se o upload foi bem-sucedido, False caso contrário.
        """
        if not os.path.exists(video_file):
            print(f"Arquivo de vídeo não encontrado: {video_file}")
            return False
    
        if scheduled_time is None:
            # Gera o primeiro slot disponível para 1 vídeo
            scheduled_time = self.generate_schedule(1)[0]
        
        sucesso = self._do_upload(video_file, title, description, scheduled_time)
        if sucesso:
            backup_path = os.path.join(self.backup_dir, os.path.basename(video_file))
            try:
                # shutil.move(video_file, backup_path)
                # print(f"Vídeo movido para backup: {backup_path}")
                print(f"YouTube upload done")
            except Exception as e:
                print("Erro ao mover o arquivo para backup:", e)
        return sucesso

    def _do_upload(self, video_file, title, description, scheduled_time):
        """
        Método interno que realiza o upload do vídeo para o YouTube.
        Se title e description forem None, eles serão gerados a partir do nome do arquivo.
        """
        base_name = os.path.splitext(os.path.basename(video_file))[0]
        if title is None:
            title = f"{base_name} - YouTube Short #Shorts"
        if description is None:
            description = f"Upload automático do vídeo {base_name}.\n#Shorts"
        
        # Converte o horário agendado para UTC no formato ISO 8601 (RFC 3339)
        scheduled_time_utc = scheduled_time.astimezone(datetime.timezone.utc).isoformat()
        
        # Extrai as hashtags da descrição (remove o '#' e adiciona à lista)
        hashtags = [tag[1:] for tag in description.split() if tag.startswith('#')]

        # Combina as tags existentes com as novas hashtags
        # tags = ["Shorts", "Automated Upload"] + hashtags
        tags = hashtags
        
        body = {
            "snippet": {
                "title": title,
                "description": description,
                "tags": tags,
                "categoryId": "24" # Entertainment
            },
            "status": {
                "privacyStatus": "private",
                "publishAt": scheduled_time_utc,
                "selfDeclaredMadeForKids": False
            }
        }
        
        media = MediaFileUpload(video_file, chunksize=-1, resumable=True)
        
        print(f"\nIniciando upload do vídeo: {video_file}")
        print(f"Título: {title}")
        print(f"Descrição: {description}")
        print(f"Agendado para: {scheduled_time} (local) / {scheduled_time_utc} (UTC)")
        
        try:
            request = self.youtube.videos().insert(
                part="snippet,status",
                body=body,
                media_body=media
            )
            response = None
            while response is None:
                status, response = request.next_chunk()
                if status:
                    progresso = int(status.progress() * 100)
                    print(f"Upload em andamento: {progresso}%")
            print("Upload concluído para:", video_file)
            print("Resposta da API:", response)
            return True
        except googleapiclient.errors.HttpError as e:
            print("Erro no upload do vídeo", video_file, ":", e)
            return False
        
    def _parse_iso8601(self, date_str):
        """
        Método interno para converter uma string de data em formato ISO 8601 para um objeto datetime.
        Se a string terminar com 'Z', substitui por '+00:00' para representar UTC.
        """
        if date_str.endswith('Z'):
            date_str = date_str[:-1] + '+00:00'
        return datetime.datetime.fromisoformat(date_str)
    
    def get_last_scheduled_video_date(self):
        """
        Retorna a data de publicação (publishAt) do último vídeo agendado (aquele com a data mais avançada)
        dentre os vídeos agendados do canal. Caso não haja vídeos agendados, retorna None.
        O horário é convertido para o fuso horário local.
        """
        # Realiza uma busca pelos vídeos do canal do usuário autenticado
        try:
            search_response = self.youtube.search().list(
                part="id",
                forMine=True,
                type="video",
                maxResults=50
            ).execute()
        except Exception as e:
            print("Erro ao buscar vídeos:", e)
            return None

        video_ids = [item["id"]["videoId"] for item in search_response.get("items", [])]
        if not video_ids:
            print("Nenhum vídeo encontrado.")
            return None

        try:
            videos_response = self.youtube.videos().list(
                part="status",
                id=",".join(video_ids),
                maxResults=50
            ).execute()
        except Exception as e:
            print("Erro ao obter detalhes dos vídeos:", e)
            return None

        scheduled_dates = []
        for video in videos_response.get("items", []):
            status = video.get("status", {})
            publishAt = status.get("publishAt")
            if publishAt:
                try:
                    scheduled_date = self._parse_iso8601(publishAt)
                    scheduled_dates.append(scheduled_date)
                except Exception as e:
                    print("Erro ao converter data:", publishAt, e)
        
        if not scheduled_dates:
            print("Nenhum vídeo agendado encontrado.")
            return None

        last_scheduled_date = max(scheduled_dates)
        # Converte o horário para o fuso horário local
        last_scheduled_date_local = last_scheduled_date.astimezone()
        return last_scheduled_date_local

    def testar_ambiente(self):
        """
        Função de teste para verificar se o ambiente está configurado corretamente.
        Realiza as seguintes verificações:
          - Verifica se o arquivo client_secrets.json existe;
          - Verifica se o diretório de output existe;
          - Testa se o diretório de backup é gravável;
          - Tenta autenticar e testar a conexão com a API do YouTube;
          - Testa a geração de agendamentos para os uploads.
        
        Retorna True se todos os testes forem bem-sucedidos; caso contrário, retorna False.
        """
        # Verifica a existência do arquivo de credenciais
        if not os.path.exists(self.client_secrets_file):
            print("❌ Erro: Arquivo client_secrets.json não encontrado em:", self.client_secrets_file)
            return False

        # Verifica se o diretório de output existe
        if not os.path.exists(self.output_dir):
            print("❌ Erro: Diretório de output não encontrado em:", self.output_dir)
            return False

        # Testa se o diretório de backup é gravável
        try:
            teste_file = os.path.join(self.backup_dir, "teste.txt")
            with open(teste_file, "w") as f:
                f.write("teste")
            os.remove(teste_file)
        except Exception as e:
            print("❌ Erro: Diretório de backup não é gravável:", e)
            return False

        # Testa a autenticação e conexão com a API
        try:
            print("Iniciando testes de autenticação e conexão com a API do YouTube...")
            self.authenticate()
            print("✅ Autenticação realizada com sucesso.")
            self.test_connection()
        except Exception as e:
            print("❌ Erro durante autenticação ou teste de conexão:", e)
            return False

        # Testa a geração de agendamento de uploads
        try:
            schedule = self.generate_schedule(3)
            if not schedule or len(schedule) != 3:
                print("❌ Erro: Falha ao gerar agendamento de vídeos.")
                return False
            print("✅ Teste de agendamento concluído com sucesso. Horários gerados:")
            for dt in schedule:
                print("   -", dt)
        except Exception as e:
            print("❌ Erro ao testar geração de agendamento:", e)
            return False

        print("✅ Todos os testes do ambiente foram concluídos com sucesso.")
        return True

# Exemplo de teste: se este módulo for executado diretamente, realiza os testes de ambiente.
if __name__ == '__main__':
    uploader = YouTubeUploader()
    
    # Primeiro, testa o ambiente
    if uploader.testar_ambiente():
        print("Iniciando operações com o YouTubeUploader...")
        # Descomente as linhas abaixo conforme o teste desejado:
        # uploader.upload_all_videos()
        # uploader.upload_single_video(os.path.join("output", "seu_video.mp4"), "Título Personalizado", "Descrição Personalizada")
        
        last_date = uploader.get_last_scheduled_video_date()
        if last_date:
            print("O último vídeo agendado está marcado para:", last_date)
        else:
            print("Nenhum vídeo agendado foi encontrado.")
    else:
        print("Verifique os erros acima e corrija antes de continuar.")
