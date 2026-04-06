# Resumo Técnico: Projeto BaixarVideo by Jair Lima

Este projeto é um aplicativo CLI (Command Line Interface) desenvolvido em Python para baixar vídeos de diversas plataformas, incluindo YouTube, Facebook, entre outras.

## Dependências
- Python 3
- `yt-dlp`: Biblioteca robusta para extração e download de vídeos, lidando de forma transparente com dezenas de plataformas.
- `ffmpeg`: Necessário para converter áudios e mesclar os melhores formatos de vídeo/áudio (O caminho para o binário já está pré-configurado internamente para `C:\Users\jairs\Claude\AlbumSplitter`).

## Como usar
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
- `baixarvideo.bat` / `baixarvideo.ps1`: Wrappers para facilitar a execução no terminal Windows chamando diretamente o executável Python do ambiente virtual, evitando problemas de subprocessos.
- `venv/`: Ambiente virtual Python isolado contendo as dependências do projeto.
- `LICENSE`: O projeto possui código aberto sob a licença MIT.

## Observações Adicionais
- Este repositório foi configurado como **PÚBLICO** no GitHub mediante solicitação explícita do usuário, constituindo uma exceção à regra geral de repositórios privados.
- O uso de wrappers no PowerShell para utilitários CLI segue a recomendação de chamar diretamente os executáveis nativos.
