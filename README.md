# Video Maker for Dark Channels

Este projeto tem como objetivo automatizar a criação e o upload de vídeos para canais "Dark" no YouTube, utilizando diversas APIs para download de vídeos/imagens, conversão de texto em voz e criação de vídeos.

## Requisitos

- **Python:** 3.11.9  
- **APIs:**  
  - YouTube Data API v3  
  - Google Text-to-Speech (utilizado em `googleVoice.py`)
- **Outras Dependências:**  
  - [ImageMagick](https://imagemagick.org/script/download.php) (necessário para o processamento de imagens e vídeos)
  - [ChromeDriver](https://googlechromelabs.github.io/chrome-for-testing/#stable) (Stable 133.0.6943.98)
  - [FFmpeg](https://ffmpeg.org/download.html) (Put it in yout PATH)

## Configuração do Ambiente

### 1. Criando e Ativando o Ambiente Virtual

No terminal, execute:

    python -m venv venv  # Cria o ambiente virtual

Para ativar o ambiente:

- **Linux/Mac:**
  
      source venv/bin/activate

- **Windows:**
  
      source venv/Scripts/activate
    or
      .\venv\Scripts\Activate

Para desativar o ambiente, basta executar:

    deactivate

### 2. Instalando as Dependências

Atualize o `pip`:

    python -m pip install --upgrade --force-reinstall pip

Instale os pacotes necessários com:

    pip install -r requirements.txt

Caso precise atualizar seu arquivo `requirements.txt`, utilize:

    pip freeze > requirements.txt

### 3. Configuração do Google Cloud

Você precisará:

- Criar um projeto no [Google Cloud Console](https://console.cloud.google.com/).
- Habilitar a **YouTube Data API v3** para o projeto.
- Gerar e fazer o download do arquivo `client_secrets.json` e posicioná-lo na raiz do projeto.

### 4. ImageMagick

Certifique-se de que o [ImageMagick](https://imagemagick.org/script/download.php) esteja instalado em sua máquina, pois ele é utilizado para processar as imagens e vídeos.

## Estrutura do Projeto

- **main.py:** Responsável pelo download de vídeos e imagens.
- **googleVoice.py:** Converte texto em voz utilizando a API do Google.
- **videomaker.py:** Cria os vídeos utilizando os vídeos e imagens baixados.
- **uploadYoutube.py:** Contém a lógica para upload e agendamento dos vídeos no YouTube.

## Exemplo de Uso

A seguir, um exemplo de script (sample) com o conteúdo a ser processado:

    TEMA: A volta do TikTok nos EUA: o que está por trás da decisão de Trump?

    TÍTULO: Por que Trump trouxe o TikTok de volta? Descubra os motivos!

    HASHTAGS: #tiktok #trump #politica #eua #midiasocial

    SEARCH: TikTok

    NARRAÇÃO:
    1. Você sabia que o TikTok foi banido nos EUA e agora está de volta?
    2. O presidente Donald Trump assinou uma ordem executiva permitindo o retorno do aplicativo.
    3. Mas por que essa mudança repentina?
    4. Alguns dizem que é uma estratégia para conquistar o voto dos jovens, já que o TikTok é popular entre eles.
    5. Outros acreditam que há interesses econômicos, como a venda parcial da operação para empresas americanas.
    6. Há também preocupações com a segurança de dados, já que o TikTok é de origem chinesa.
    7. Afinal, o que realmente motivou essa decisão?
    8. Será que foi uma jogada política para aumentar a popularidade entre os jovens?
    9. Ou uma estratégia econômica visando benefícios futuros?
    10. Independente do motivo, o TikTok está de volta e promete continuar influenciando a cultura digital.
    11. Gostou? Curta e compartilhe para mais conteúdos como este!

## Considerações Finais

- **Autenticação:**  
  O upload de vídeos requer autenticação via OAuth 2.0. Certifique-se de ter o arquivo `client_secrets.json` configurado corretamente.

- **Agendamento:**  
  O sistema permite agendar os uploads nos horários pré-definidos (08:00, 12:00 e 18:00) e conta com funções para buscar o último vídeo agendado e calcular o próximo slot disponível.

- **Modularidade:**  
  O projeto está dividido em módulos (download, conversão de voz, criação de vídeos e upload), facilitando a manutenção e a reutilização do código.

Basta seguir as instruções acima para configurar e rodar o projeto. Se precisar de ajustes ou novas funcionalidades, sinta-se à vontade para modificar os scripts conforme necessário.
