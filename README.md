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
videomaker.py -> create the videos using the videos and images downloaded
googleVoice.py -> convert text to voice using google api