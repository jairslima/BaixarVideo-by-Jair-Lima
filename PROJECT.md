# BaixarVideo by Jair Lima

## Descrição
Aplicativo Windows (GUI Tkinter + CLI) para baixar vídeos, áudios (MP3) e fotos de links suportados pelo yt-dlp (YouTube, Facebook, Instagram etc.). Detalhes de escopo e critérios em `SPEC.md` e `GEMINI.md`.

## Stack
Python 3.14, yt-dlp (atualizado para 2026.08.19 no venv em 2026-10-06), Tkinter, PyInstaller 6.22.3, ffmpeg (`C:\Users\jairs\Claude\AlbumSplitter`), Node.js (runtime JS exigido pelo YouTube).

## Estrutura
- `baixarvideo.py`: lógica de download (`baixar_video`, `limpar_url`, fotos do Instagram, verificação de áudio) e CLI.
- `baixarvideo_gui.py`: interface (importa `baixar_video`).
- `BaixarVideo by Jair Lima.spec`: build PyInstaller (onedir) em `dist\BaixarVideo by Jair Lima\`.
- Atalhos: `C:\Users\jairs\bin\baixarvideo.cmd` (CLI, usa o `venv` do projeto, que foi apagado pela limpeza de 2026-10-14 e precisa ser recriado com `python -m venv venv` e `pip install yt-dlp`), `baixarvideo-gui.cmd` e atalho do Desktop.
- **Instalacao (desde 2026-10-14):** o app em pasta fica em `C:\Users\jairs\bin\BaixarVideo\` (fora do projeto, porque a limpeza mensal de harness trata `dist` como descartavel). `baixarvideo-gui.cmd` e o atalho do Desktop apontam para `C:\Users\jairs\bin\BaixarVideo\BaixarVideo by Jair Lima.exe`. Depois de recompilar, copiar `dist\BaixarVideo by Jair Lima\` para essa pasta.

## Comandos
- CLI: `baixarvideo "URL" [--best] [--audio] [--path PASTA] [--playlist] [--cookies-browser chrome]`
- Build: `.\venv\Scripts\pyinstaller.exe "BaixarVideo by Jair Lima.spec" --noconfirm`
- Antes de buildar nesta máquina (Tcl/Tk 9.0): `venv\Scripts\python.exe -m pip install -U pyinstaller pyinstaller-hooks-contrib`.
- Testar o `.exe` de verdade (abrir e checar a janela); "Build complete" não basta.

## Decisões
- O modo padrão usa `best/bestvideo+bestaudio` e mescla em `.mkv` quando não há arquivo único (lives do YouTube não têm). `--best` força vídeo + áudio mesclados.
- `js_runtimes` aponta para o Node quando `node` está no PATH (YouTube não libera formatos sem runtime JS).
- Cookies do navegador só com `--cookies-browser` explícito.

## Estado atual
Corrigido em 2026-10-06: live da TV Senado (5h40) falhava com "Requested format is not available". Agora seleciona 1080p + áudio. `.exe` rebuildado e aberto com sucesso.

## Problemas conhecidos
- A GUI ainda não tem opção de limitar resolução nem baixar só um trecho (lives longas em 1080p passam de 4 GB).
- YouTube pode pedir login ("confirme que você não é um robô"); nesse caso só com `--cookies-browser` e aval do usuário.
