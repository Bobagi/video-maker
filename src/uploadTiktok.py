#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import time
import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from dotenv import load_dotenv

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

# Recupera as variáveis necessárias
CHROMEDRIVER_PATH = os.getenv("CHROMEDRIVER_PATH")
USER_DATA_DIR = os.getenv("USER_DATA_DIR")
# Se desejar, você pode também definir o perfil via variável; caso contrário, "Default" é o padrão.
PROFILE_DIRECTORY = os.getenv("PROFILE_DIRECTORY", "Default")

class TikTokUploader:
    def __init__(self, driver_path = CHROMEDRIVER_PATH, user_data_dir = USER_DATA_DIR, profile_directory = PROFILE_DIRECTORY, headless=False):
        """
        Inicializa a classe TikTokUploader.
        
        :param driver_path: Caminho para o executável do ChromeDriver.
        :param user_data_dir: Caminho para o diretório de dados do usuário do Chrome.
        :param profile_directory: Nome do perfil a ser usado (ex.: "Default" ou "Profile 1").
        :param headless: Se True, roda o Chrome em modo headless.
        """
        self.driver_path = driver_path
        self.user_data_dir = user_data_dir
        self.profile_directory = profile_directory
        self.headless = headless
        self.driver = None

    def start_browser(self):
        """Inicia o navegador usando o perfil logado."""
        options = webdriver.ChromeOptions()
        options.add_argument(f"--user-data-dir={self.user_data_dir}")
        options.add_argument(f"--profile-directory={self.profile_directory}")
        if self.headless:
            options.add_argument("--headless")
        options.add_argument("--disable-notifications")
        service = Service(self.driver_path)
        self.driver = webdriver.Chrome(service=service, options=options)
        self.driver.maximize_window()

    def open_upload_page(self):
        """Navega diretamente para a página de upload do TikTok Studio."""
        url = "https://www.tiktok.com/tiktokstudio/upload?from=creator_center"
        self.driver.get(url)
        # Aguarda alguns segundos para a página carregar completamente
        time.sleep(5)

    def upload_video(self, video_file, description, scheduled_time=None):
        """
        Realiza o upload de um vídeo no TikTok Studio seguindo os passos:
          1. Seleciona o vídeo através do input file;
          2. Aguarda o processamento do upload;
          3. Insere a descrição no campo abaixo da label "Descrição";
          4. Seleciona o radiobutton "Programação" (na seção "Quando publicar");
          5. Se fornecido, configura os campos de data e hora através de cliques nos inputs readonly e seleção da opção desejada;
          6. Clica no botão "Programação" para finalizar o agendamento.
        
        :param video_file: Caminho do arquivo de vídeo.
        :param title: Título do vídeo (não utilizado, pois não há campo específico para título).
        :param description: Descrição (ou legenda) do vídeo.
        :param scheduled_time: (Opcional) objeto datetime com a data/hora para agendamento.
        :return: True se o upload foi realizado com sucesso, False caso contrário.
        """
        if not os.path.exists(video_file):
            print(f"Arquivo de vídeo não encontrado: {video_file}")
            return False

        # Abre a página de upload já logada
        self.open_upload_page()

        # 1. Seleciona o vídeo via input file (mesmo que oculto)
        try:
            file_input = WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.XPATH, "//input[@type='file']"))
            )
            file_input.send_keys(os.path.abspath(video_file))
            print("Arquivo selecionado para upload.")
        except Exception as e:
            print("Erro ao selecionar o arquivo de vídeo:", e)
            return False

        # 2. Aguarda o processamento do upload
        print("Aguardando o processamento do upload...")
        time.sleep(15)

        # 3. Insere a descrição
        try:
            # Localiza o campo de descrição (container contenteditable) abaixo da label "Descrição"
            desc_field = WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located((By.XPATH, "//div[@data-e2e='caption_container']//div[@contenteditable='true']"))
            )
            # Limpa o conteúdo existente via JavaScript
            self.driver.execute_script("arguments[0].innerText = '';", desc_field)
            # Insere a descrição desejada
            self.driver.execute_script("arguments[0].innerText = arguments[1];", desc_field, description)
            print("Descrição inserida.")
        except Exception as e:
            print("Erro ao inserir descrição:", e)
            return False

        # 4. Seleciona o radiobutton "Programação"
        try:
            radio_prog = WebDriverWait(self.driver, 30).until(
                EC.element_to_be_clickable((By.XPATH, "//label[contains(., 'Programação')]"))
            )
            radio_prog.click()
            print("Radiobutton 'Programação' selecionado.")
        except Exception as e:
            print("Erro ao selecionar o radiobutton 'Programação':", e)
            return False

        # 5. Se houver agendamento, configura os campos de data e hora.
        if scheduled_time:
            try:
                # Converte scheduled_time para strings:
                # Data: YYYY-MM-DD (ex.: "2025-02-05")
                # Hora: HH (ex.: "10")
                # Minuto: MM (ex.: "30")
                date_str = scheduled_time.strftime("%Y-%m-%d")
                hour_str = scheduled_time.strftime("%H")
                minute_str = scheduled_time.strftime("%M")
                # Para seleção do dia, remova o zero à esquerda, se houver
                day = str(int(scheduled_time.strftime("%d")))
                
                # -- Configurando a data --
                date_input = WebDriverWait(self.driver, 30).until(
                    EC.element_to_be_clickable(
                        (By.XPATH, "//input[contains(@class, 'TUXTextInputCore-input') and contains(@value, '-') and not(contains(@value, ':'))]")
                    )
                )
                date_input.click()
                print("Campo de data aberto!")
                time.sleep(1)  # Aguarda o dropdown do calendário abrir
                
                date_cell = WebDriverWait(self.driver, 30).until(
                    EC.element_to_be_clickable(
                        (By.XPATH, f"//div[contains(@class, 'calendar-wrapper')]//span[contains(@class, 'day') and normalize-space(text())='{day}']")
                    )
                )
                date_cell.click()
                print("Data selecionada:", date_str)
                
                # -- Configurando a hora --
                time_input = WebDriverWait(self.driver, 30).until(
                    EC.element_to_be_clickable(
                        (By.XPATH, "//input[contains(@class, 'TUXTextInputCore-input') and contains(@value, ':')]")
                    )
                )
                time_input.click()
                print("Campo de hora aberto!")
                time.sleep(1)  # Aguarda o dropdown de horários abrir
                print(f"Selecionando hora {hour_str}:{minute_str}...")
                
                # Seleciona a opção de hora na primeira lista (lado esquerdo)
                hour_option = WebDriverWait(self.driver, 30).until(
                    EC.element_to_be_clickable(
                        (By.XPATH, f"(//div[contains(@class, 'tiktok-timepicker-time-scroll-container')])[1]//span[contains(@class, 'tiktok-timepicker-option-text') and contains(@class, 'tiktok-timepicker-left') and normalize-space(text())='{hour_str}']")
                    )
                )
                hour_option.click()
                print("Hora selecionada:", hour_str)
                time.sleep(1)
                
                # Seleciona a opção de minuto na segunda lista (lado direito)
                minute_option = WebDriverWait(self.driver, 30).until(
                    EC.element_to_be_clickable(
                        (By.XPATH, f"(//div[contains(@class, 'tiktok-timepicker-time-scroll-container')])[2]//span[contains(@class, 'tiktok-timepicker-option-text') and contains(@class, 'tiktok-timepicker-right') and normalize-space(text())='{minute_str}']")
                    )
                )
                minute_option.click()
                print("Minuto selecionado:", minute_str)
            except Exception as e:
                print("Erro ao configurar data e hora:", e)
                return False
        else:
            print("Agendamento não solicitado. Prosseguindo sem agendar.")

        # 6. Clica no botão "Programação" para finalizar o upload agendado
        try:
            prog_button = WebDriverWait(self.driver, 30).until(
                EC.element_to_be_clickable((By.XPATH, "//button[normalize-space()='Programação']"))
            )
            prog_button.click()
            print("Botão 'Programação' clicado. Upload agendado!")
        except Exception as e:
            print("Erro ao clicar no botão 'Programação':", e)
            return False

        # 7. Aguarda a confirmação final do processo
        print("Aguardando a confirmação final do upload...")
        time.sleep(10)
        return True

    def close_browser(self):
        """Fecha o navegador."""
        if self.driver:
            self.driver.quit()

    def upload_video_to_tiktok(self, video_file, description, scheduled_time):
        """
        Função para realizar o upload de um vídeo no TikTok Studio.
        
        :param video_file: Caminho do arquivo de vídeo.
        :param description: Descrição (ou legenda) do vídeo.
        :param scheduled_time: Objeto datetime com a data/hora para agendamento.
        :return: True se o upload foi realizado com sucesso, False caso contrário.
        """
        
        self.start_browser()
        # Note que o título não é utilizado (não há campo para título) e é apenas passado para compatibilidade.
        success = self.upload_video(video_file, description=description, scheduled_time=scheduled_time)
        self.close_browser()
        return success

# Exemplo de uso quando o módulo é executado diretamente:
if __name__ == '__main__':
    # Configure os parâmetros:
    VIDEO_FILE = os.path.join("output", "final_video.mp4")
    TITLE = "Meu vídeo TikTok"  # Parâmetro não utilizado
    DESCRIPTION = "Descrição do vídeo com hashtags e outros detalhes."
    # Exemplo: agendar para 6 de fevereiro de 2025 às 18:35.
    SCHEDULED_TIME = datetime.datetime(2025, 2, 6, 18, 35)
    
    tiktok = TikTokUploader();

    result = tiktok.upload_video_to_tiktok(VIDEO_FILE, DESCRIPTION, SCHEDULED_TIME)
    if result:
        print("Upload agendado com sucesso!")
    else:
        print("Falha no upload.")
