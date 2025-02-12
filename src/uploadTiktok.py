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
CHROME_DRIVER_PATH = os.getenv("CHROME_DRIVER_PATH")
USER_DATA_DIR = os.getenv("USER_DATA_DIR")
PROFILE_DIRECTORY = os.getenv("PROFILE_DIRECTORY", "Default")

class TikTokUploader:
    def __init__(self, driver_path=CHROME_DRIVER_PATH, user_data_dir=USER_DATA_DIR, profile_directory=PROFILE_DIRECTORY, headless=False):
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
        try:
            options = webdriver.ChromeOptions()
            options.add_argument(f"--user-data-dir={self.user_data_dir}")
            options.add_argument(f"--profile-directory={self.profile_directory}")
            if self.headless:
                options.add_argument("--headless")
            options.add_argument("--disable-notifications")
            service = Service(self.driver_path)
            self.driver = webdriver.Chrome(service=service, options=options)
            self.driver.maximize_window()
            return True
        except Exception as e:
            print("Erro ao iniciar o navegador:", e)
            return False

    def open_upload_page(self):
        """Navega diretamente para a página de upload do TikTok Studio."""
        url = "https://www.tiktok.com/tiktokstudio/upload?from=creator_center"
        self.driver.get(url)
        time.sleep(5)  # Aguarda a página carregar completamente

    def upload_video(self, video_file, description, scheduled_time=None):
        """
        Realiza o upload de um vídeo no TikTok Studio seguindo os passos:
          1. Seleciona o vídeo via input file;
          2. Aguarda o processamento do upload;
          3. Insere a descrição;
          4. Seleciona o radiobutton "Programação";
          5. Se fornecido, configura data e hora;
          6. Clica no botão "Programação" para finalizar.
        """
        if not os.path.exists(video_file):
            print(f"Arquivo de vídeo não encontrado: {video_file}")
            return False

        self.open_upload_page()

        # 1. Seleciona o vídeo via input file
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
            desc_field = WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located((By.XPATH, "//div[@data-e2e='caption_container']//div[@contenteditable='true']"))
            )
            self.driver.execute_script("arguments[0].innerText = '';", desc_field)
            self.driver.execute_script("arguments[0].innerText = arguments[1];", desc_field, description)
            print("Descrição inserida.")
        except Exception as e:
            print("Erro ao inserir descrição:", e)
            return False
        
        time.sleep(5)
        # 3.1. Insere a descrição novamente
        try:
            desc_field = WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located((By.XPATH, "//div[@data-e2e='caption_container']//div[@contenteditable='true']"))
            )
            self.driver.execute_script("arguments[0].innerText = '';", desc_field)
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

        # 5. Configuração de data e hora (caso agendamento seja solicitado)
        if scheduled_time:
            try:
                # Formata os valores desejados
                date_str = scheduled_time.strftime("%Y-%m-%d")
                hour_str = scheduled_time.strftime("%H")
                minute_str = scheduled_time.strftime("%M")
                day = str(int(scheduled_time.strftime("%d")))  # remove zero à esquerda

                # --- Seleção da Data ---
                date_input = WebDriverWait(self.driver, 30).until(
                    EC.element_to_be_clickable(
                        (By.XPATH, "//input[contains(@class, 'TUXTextInputCore-input') and contains(@value, '-') and not(contains(@value, ':'))]")
                    )
                )
                date_input.click()
                print("\nCampo de data aberto!")
                time.sleep(1)  # Aguarda o dropdown do calendário abrir

                date_cell = WebDriverWait(self.driver, 30).until(
                    EC.element_to_be_clickable(
                        (By.XPATH, f"//div[contains(@class, 'calendar-wrapper')]//span[contains(@class, 'day') and normalize-space(text())='{day}']")
                    )
                )
                date_cell.click()
                print("\nData selecionada:", date_str)

                # --- Seleção de Hora e Minuto ---
                time_input = WebDriverWait(self.driver, 30).until(
                    EC.element_to_be_clickable(
                        (By.XPATH, "//input[contains(@class, 'TUXTextInputCore-input') and contains(@value, ':')]")
                    )
                )
                time_input.click()
                print("\nDropdown de hora aberto!")
                # Aguarda que o container do time picker esteja visível (aumentei para 15 segundos)
                WebDriverWait(self.driver, 5).until(
                    EC.visibility_of_element_located((By.XPATH, "//div[contains(@class, 'tiktok-timepicker-time-picker-container')]"))
                )
                print("Dropdown de hora visível!")
                time.sleep(2)

                # Seleciona a hora desejada
                hour_option_xpath = f"(//div[contains(@class, 'tiktok-timepicker-time-scroll-container')])[1]//span[normalize-space(.)='{hour_str}']"
                try:
                    hour_option = self.driver.find_element(By.XPATH, hour_option_xpath)
                except Exception as e:
                    print("Elemento de hora não encontrado:", e)
                    return False
                self.driver.execute_script("arguments[0].scrollIntoView(true);", hour_option)
                self.driver.execute_script("arguments[0].click();", hour_option)
                print("Hora selecionada:", hour_str)
                time.sleep(2)

                # Seleciona o minuto desejado
                minute_option_xpath = f"(//div[contains(@class, 'tiktok-timepicker-time-scroll-container')])[2]//span[normalize-space(.)='{minute_str}']"
                try:
                    minute_option = self.driver.find_element(By.XPATH, minute_option_xpath)
                except Exception as e:
                    print("Elemento de minuto não encontrado:", e)
                    return False
                self.driver.execute_script("arguments[0].scrollIntoView(true);", minute_option)
                self.driver.execute_script("arguments[0].click();", minute_option)
                print("Minuto selecionado:", minute_str)
                time.sleep(2)

                # Verifica se as seleções foram aplicadas
                active_hour = self.driver.find_element(By.XPATH, "(//div[contains(@class, 'tiktok-timepicker-time-scroll-container')])[1]//span[contains(@class, 'tiktok-timepicker-is-active')]")
                active_minute = self.driver.find_element(By.XPATH, "(//div[contains(@class, 'tiktok-timepicker-time-scroll-container')])[2]//span[contains(@class, 'tiktok-timepicker-is-active')]")
                if active_hour.text.strip() != hour_str:
                    print(f"\n🆘 Erro: A hora ativa ({active_hour.text.strip()}) não corresponde à hora desejada ({hour_str}).")
                    return False
                if active_minute.text.strip() != minute_str:
                    print(f"\n🆘 Erro: O minuto ativo ({active_minute.text.strip()}) não corresponde ao minuto desejado ({minute_str}).")
                    return False

                # Confirma a seleção clicando fora do dropdown
                self.driver.execute_script("document.body.click();")
                time.sleep(1)
            except Exception as e:
                print("\n🆘 Erro ao configurar data e hora:", e)
                return False
        else:
            print("\nAgendamento não solicitado. Prosseguindo sem agendar.")

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
        :param description: Descrição do vídeo.
        :param scheduled_time: Objeto datetime com a data/hora para agendamento.
        :return: True se o upload foi realizado com sucesso, False caso contrário.
        """
        self.start_browser()
        success = self.upload_video(video_file, description=description, scheduled_time=scheduled_time)
        self.close_browser()
        return success

# Exemplo de uso quando o módulo é executado diretamente:
if __name__ == '__main__':
    VIDEO_FILE = os.path.join("output", "final_video.mp4")
    DESCRIPTION = "Descrição do vídeo com hashtags e outros detalhes."
    # Exemplo: agendar para 6 de fevereiro de 2025 às 18:35.
    SCHEDULED_TIME = datetime.datetime(2025, 2, 6, 18, 35)
    
    tiktok = TikTokUploader()
    result = tiktok.upload_video_to_tiktok(VIDEO_FILE, DESCRIPTION, SCHEDULED_TIME)
    if result:
        print("Upload agendado com sucesso!")
    else:
        print("Falha no upload.")
