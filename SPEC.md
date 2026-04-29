# BaixarVideo by Jair Lima

## Objetivo
Aplicativo Windows para baixar videos, audios e fotos de links suportados pelo `yt-dlp`, com foco atual em posts e reels do Instagram.

## Escopo
- CLI em `baixarvideo.py`, mantido para automacao e uso por terminal.
- Interface grafica em `baixarvideo_gui.py`, usando Tkinter.
- Wrappers Windows em `baixarvideo.ps1` e `baixarvideo.bat`.
- Empacotamento Windows via PyInstaller.

## Arquitetura
- `baixarvideo.py` concentra a regra de download, limpeza de URL, suporte complementar a fotos do Instagram e verificacao de audio com `ffprobe`.
- `baixarvideo_gui.py` importa `baixar_video` e executa o download em thread separada para manter a interface responsiva.
- A GUI captura `stdout` e `stderr` em uma fila e mostra o log em tempo real na tela.
- `ffmpeg.exe` e `ffprobe.exe` sao usados a partir de `C:\Users\jairs\Claude\AlbumSplitter`.
- O suporte a cookies do navegador usa a opcao `cookiesfrombrowser` do `yt-dlp`, sem salvar cookies no repositorio.

## Dependencias
- Python 3.
- `yt-dlp`.
- Tkinter, biblioteca padrao do Python no Windows.
- FFmpeg e FFprobe no caminho configurado em `baixarvideo.py`.
- PyInstaller no `venv`, usado somente para gerar o executavel.

## Decisoes
- Os nomes de arquivos usam `ID - titulo.ext` para evitar colisoes.
- O Instagram pode omitir fotos de carrossel no fluxo normal do `yt-dlp`; por isso o script consulta o metadata publico e baixa imagens separadamente.
- Alguns videos de carrossel retornam `has_audio=False`; nesses casos o app avisa que o arquivo veio sem faixa de audio.
- O executavel da interface grafica deve ser gerado sem console.
- O comando de terminal fica em `C:\Users\jairs\bin\baixarvideo.cmd`.
- O comando da interface grafica fica em `C:\Users\jairs\bin\baixarvideo-gui.cmd`.

## Criterios de aceite
- A GUI abre com campo de link, pasta de destino, opcoes e log.
- O botao Baixar executa sem travar a interface.
- O app cria a pasta de destino se ela nao existir.
- O executavel Windows e gerado em `dist\BaixarVideo by Jair Lima\BaixarVideo by Jair Lima.exe`.
- Existe atalho na Area de Trabalho apontando para o executavel.

## Operacao
Executar pelo codigo:

```powershell
.\venv\Scripts\python.exe .\baixarvideo_gui.py
```

Gerar executavel:

```powershell
.\venv\Scripts\python.exe -m PyInstaller --noconfirm --windowed --name "BaixarVideo by Jair Lima" .\baixarvideo_gui.py
```

Executavel gerado:

```text
C:\Users\jairs\Gemini\BaixarVideo\dist\BaixarVideo by Jair Lima\BaixarVideo by Jair Lima.exe
```

Atalho:

```text
C:\Users\jairs\Desktop\BaixarVideo by Jair Lima.lnk
```

Comando no PATH:

```text
C:\Users\jairs\bin\baixarvideo.cmd
```

Uso pelo terminal:

```powershell
baixarvideo "https://www.instagram.com/..."
```

Uso pelo terminal com cookies do Chrome:

```powershell
baixarvideo --cookies-browser chrome "https://www.instagram.com/..."
```

Comando grafico no PATH:

```text
C:\Users\jairs\bin\baixarvideo-gui.cmd
```

Abrir a interface pelo terminal:

```powershell
baixarvideo-gui
```
