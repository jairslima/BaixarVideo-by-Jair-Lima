import sys
import argparse
import os
import urllib.parse
import yt_dlp

def limpar_url(url):
    """Remove parâmetros de rastreamento conhecidos que podem interferir no download."""
    try:
        parsed = urllib.parse.urlparse(url)
        if 'instagram.com' in parsed.netloc:
            # Mantém apenas o caminho para o Instagram, ignorando a querystring (onde ficam igsh, etc.)
            return urllib.parse.urlunparse((parsed.scheme, parsed.netloc, parsed.path, parsed.params, '', parsed.fragment))
        # Para outras plataformas, podemos deixar a query intacta ou filtrar parâmetros específicos no futuro
        return url
    except Exception:
        return url

def baixar_video(url, options):
    url = limpar_url(url)
    print(f"\nIniciando processo para: {url}")

    
    ydl_opts = {
        'outtmpl': os.path.join(options.path, '%(title)s.%(ext)s'),
        'noplaylist': not options.playlist,
        'ffmpeg_location': r'C:\Users\jairs\Claude\AlbumSplitter',
    }

    if options.audio:
        ydl_opts['format'] = 'bestaudio/best'
        ydl_opts['postprocessors'] = [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }]
        print("Modo: Apenas Áudio (MP3)")
    elif options.best:
        ydl_opts['format'] = 'bestvideo+bestaudio/best'
        ydl_opts['merge_output_format'] = 'mkv'
        print("Modo: Melhor Qualidade (Vídeo + Áudio mesclados)")
    else:
        ydl_opts['format'] = 'best'
        print("Modo: Qualidade Padrão (Melhor arquivo único)")

    if not options.playlist:
        print("Modo Playlist: Desativado (Apenas vídeo único)")
    else:
        print("Modo Playlist: Ativado")

    print(f"Destino: {os.path.abspath(options.path)}\n")

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            print("Obtendo informações do vídeo...")
            # Extrai as informações sem baixar apenas para mostrar o título ao usuário
            info_dict = ydl.extract_info(url, download=False)
            if info_dict:
                titulo = info_dict.get('title', 'Desconhecido')
                print(f"Título: {titulo}\n")
            
            # Executa o download e mostra a barra de progresso nativa do yt-dlp
            ydl.download([url])
            print("\n✅ Processo finalizado com sucesso!")
            
    except Exception as e:
        print(f"\n❌ Ocorreu um erro durante o processo: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ferramenta para baixar vídeos e áudios usando yt-dlp.")
    
    parser.add_argument("url", help="A URL do vídeo ou playlist a ser baixado")
    parser.add_argument("--best", action="store_true", help="Baixar na melhor qualidade possível combinando vídeo e áudio (requer FFmpeg)")
    parser.add_argument("--audio", "-a", action="store_true", help="Baixar apenas o áudio e converter para MP3 (requer FFmpeg)")
    parser.add_argument("--path", "-p", default=".", help="Pasta de destino para o download (padrão: pasta atual)")
    parser.add_argument("--playlist", action="store_true", help="Permitir o download de playlists completas")

    # Tratamento caso o usuário chame sem argumentos (mostra help)
    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)

    args = parser.parse_args()

    # Tenta criar a pasta de destino caso ela não exista
    if not os.path.exists(args.path):
        try:
            os.makedirs(args.path)
            print(f"Pasta de destino criada: {os.path.abspath(args.path)}")
        except OSError as e:
            print(f"Erro ao criar pasta de destino: {e}")
            sys.exit(1)

    baixar_video(args.url, args)
