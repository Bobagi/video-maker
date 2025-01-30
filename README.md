# video-maker

Video maker for Dark channels

Python 3.11.9

```
    python -m venv venv  # Cria o ambiente virtual
    source venv/bin/activate  # Linux/Mac
    source venv/Scripts/activate  # Windows

    deactivate
```

```
    pip install -r requirements.txt
    pip freeze > requirements.txt
```

Need to have ImageMagick installed in the machine: https://imagemagick.org/script/download.php

notes:
main.py -> download videos and images
googleVoice.py -> convert text to voice using google api
videomaker.py -> create the videos using the videos and images downloaded

script sample:

```
**TEMA:** A volta do TikTok nos EUA: o que está por trás da decisão de Trump?

**TÍTULO:** Por que Trump trouxe o TikTok de volta? Descubra os motivos!

**HASHTAGS:** #tiktok #trump #politica #eua #midiasocial

**NARRAÇÃO:**

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
```
