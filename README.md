# BaixarVideo by Jair Lima

Aplicativo Windows para baixar vídeos, áudios e fotos de links suportados pelo `yt-dlp`, com foco em posts e Reels do Instagram.

## Funcionalidades

- Download de vídeos e áudios de centenas de plataformas (YouTube, Instagram, TikTok, etc.)
- Suporte a fotos de carrossel do Instagram via consulta ao metadata público
- Interface gráfica com log em tempo real e seleção de pasta de destino
- CLI com suporte a cookies do navegador para conteúdo restrito
- Nomeação automática no formato `ID - título.ext` para evitar colisões
- Aviso quando o vídeo não contém faixa de áudio

## Stack

| Componente | Tecnologia |
|---|---|
| Linguagem | Python 3 |
| Download | `yt-dlp` |
| Interface | Tkinter |
| Processamento | FFmpeg / FFprobe |
| Build | PyInstaller |

## Instalação

```bash
pip install yt-dlp
```

FFmpeg e FFprobe devem estar disponíveis no sistema.

## Uso

**GUI:**
```bash
python baixarvideo_gui.py
# ou pelo atalho instalado: baixarvideo-gui
```

**CLI:**
```bash
baixarvideo "https://www.instagram.com/p/..."
baixarvideo --cookies-browser chrome "https://..."
```

## Build

```bash
python -m PyInstaller --noconfirm --windowed --name "BaixarVideo by Jair Lima" baixarvideo_gui.py
```

O executável é gerado em `dist/BaixarVideo by Jair Lima/`.

## Autor

**Jair Lima** — [github.com/jairslima](https://github.com/jairslima)