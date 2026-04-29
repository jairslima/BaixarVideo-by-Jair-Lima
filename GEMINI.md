# Resumo Técnico: Projeto BaixarVideo by Jair Lima

Este projeto é um aplicativo CLI (Command Line Interface) desenvolvido em Python para baixar vídeos de diversas plataformas, incluindo YouTube, Facebook, entre outras.

## Dependências
- Python 3
- `yt-dlp`: Biblioteca robusta para extração e download de vídeos, lidando de forma transparente com dezenas de plataformas.
- `ffmpeg`: Necessário para converter áudios e mesclar os melhores formatos de vídeo/áudio (O caminho para o binário já está pré-configurado internamente para `C:\Users\jairs\Claude\AlbumSplitter`).

## Como usar pela linha de comando
O aplicativo pode ser executado através dos scripts `baixarvideo.bat` (Prompt de Comando) ou `baixarvideo.ps1` (PowerShell) na raiz do projeto.
Basta passar o link do vídeo como parâmetro.

Exemplo de uso básico:
```powershell
.\baixarvideo.ps1 "https://www.youtube.com/watch?v=..."
```

Opções avançadas:
- `--best`: Baixa e mescla a melhor qualidade de vídeo e áudio disponível (geralmente 1080p+).
- `--audio` ou `-a`: Extrai o áudio e salva em MP3.
- `--path "C:\Caminho"` ou `-p`: Define uma pasta customizada para salvar o arquivo.
- `--playlist`: Permite o download de playlists inteiras (por padrão apenas o vídeo especificado é baixado).

## Estrutura do Projeto
- `baixarvideo.py`: Script principal contendo a lógica de configuração e download via `yt-dlp`.
- `baixarvideo_gui.py`: Interface gráfica Windows em Tkinter, com campo de link, pasta de destino, opções e log.
- `baixarvideo.bat` / `baixarvideo.ps1`: Wrappers para facilitar a execução no terminal Windows chamando diretamente o executável Python do ambiente virtual, evitando problemas de subprocessos.
- `C:\Users\jairs\bin\baixarvideo.cmd`: Wrapper no `PATH` do usuário para executar o aplicativo pelo comando `baixarvideo`.
- `C:\Users\jairs\bin\baixarvideo-gui.cmd`: Wrapper no `PATH` do usuário para abrir a interface gráfica pelo comando `baixarvideo-gui`.
- `venv/`: Ambiente virtual Python isolado contendo as dependências do projeto.
- `LICENSE`: O projeto possui código aberto sob a licença MIT.
- `SPEC.md`: Especificação operacional para continuidade por agentes de IA.

## Observações Adicionais
- Este repositório foi configurado como **PÚBLICO** no GitHub mediante solicitação explícita do usuário, constituindo uma exceção à regra geral de repositórios privados.
- O uso de wrappers no PowerShell para utilitários CLI segue a recomendação de chamar diretamente os executáveis nativos.
- **Tratamento de URLs**: O script agora possui uma função dedicada (`limpar_url`) para remover automaticamente parâmetros de rastreamento e *querystrings* de plataformas como o Instagram (`igsh`, etc.). Isso previne falhas no `yt-dlp` causadas por URLs poluídas.
- **Compatibilidade com console Windows**: As mensagens finais evitam emojis porque alguns terminais em `cp1252` falham ao imprimir esses caracteres. Os wrappers `baixarvideo.ps1` e `baixarvideo.bat` propagam o código de saída do Python para permitir automação confiável.
- **Nomes de arquivos**: Os downloads usam o padrão `ID - título.ext` para evitar colisões quando plataformas retornam títulos genéricos, como carrosséis do Instagram com itens chamados `Video 2`, `Video 3` etc.
- **Fotos do Instagram**: Carrosséis do Instagram podem conter fotos que o `yt-dlp` ignora ao baixar somente vídeos. O script consulta o metadata público do post e salva os nós de imagem junto com os vídeos.
- **Verificação de áudio**: Depois de baixar posts do Instagram, o script usa `ffprobe` para avisar quando arquivos de vídeo foram entregues sem faixa de áudio. Alguns carrosséis retornam `has_audio=False` no metadata público do Instagram, nesses casos não há áudio separado disponível pelo fluxo atual.
- **Interface gráfica**: `baixarvideo_gui.py` reaproveita a função `baixar_video`, roda o download em uma thread e exibe o log do processo na janela.
- **Executável gráfico**: O build atual fica em `dist\BaixarVideo by Jair Lima\BaixarVideo by Jair Lima.exe`, com atalho em `C:\Users\jairs\Desktop\BaixarVideo by Jair Lima.lnk`.
- **Comando no PATH**: `C:\Users\jairs\bin\baixarvideo.cmd` aponta para o wrapper do projeto e permite executar `baixarvideo` em qualquer terminal.
- **Cookies do navegador**: O CLI aceita `--cookies-browser chrome` ou outro navegador suportado pelo `yt-dlp`; a GUI possui seletor de cookies. Isso permite tentar acessar conteudo do Instagram usando a sessao local do navegador, sem versionar cookies.
- **Interface no PATH**: `C:\Users\jairs\bin\baixarvideo-gui.cmd` abre a interface grafica pelo comando `baixarvideo-gui`.
