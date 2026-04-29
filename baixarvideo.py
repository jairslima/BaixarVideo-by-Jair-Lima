import sys
import argparse
import http.cookiejar
import json
import mimetypes
import os
import re
import subprocess
import urllib.parse
import urllib.request
import yt_dlp

FFMPEG_LOCATION = r'C:\Users\jairs\Claude\AlbumSplitter'
INSTAGRAM_BASE64 = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_'
HTTP_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                  '(KHTML, like Gecko) Chrome/124.0 Safari/537.36',
    'Accept': '*/*',
    'Accept-Language': 'pt-BR,pt;q=0.9,en;q=0.8',
}
BROWSERS_COM_COOKIES = {'brave', 'chrome', 'chromium', 'edge', 'firefox', 'opera', 'safari', 'vivaldi', 'whale'}

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

def shortcode_para_pk(shortcode):
    if len(shortcode) > 28:
        shortcode = shortcode[:-28]

    pk = 0
    for char in shortcode:
        pk = pk * 64 + INSTAGRAM_BASE64.index(char)
    return pk

def extrair_shortcode_instagram(url):
    parsed = urllib.parse.urlparse(url)
    if 'instagram.com' not in parsed.netloc:
        return None

    match = re.search(r'/(?:p|tv|reels?)/([^/?#&]+)', parsed.path)
    return match.group(1) if match else None

def nome_seguro(nome):
    nome = re.sub(r'[<>:"/\\|?*\x00-\x1f]', '_', nome)
    nome = re.sub(r'\s+', ' ', nome).strip()
    return nome.rstrip('. ') or 'arquivo'

def extensao_por_url_ou_resposta(url, resposta):
    caminho = urllib.parse.urlparse(url).path
    extensao = os.path.splitext(caminho)[1].lower()
    if extensao:
        return extensao

    content_type = resposta.headers.get('Content-Type', '').split(';', 1)[0].strip()
    return mimetypes.guess_extension(content_type) or '.jpg'

def maior_imagem(node):
    recursos = node.get('display_resources') or []
    recursos_validos = [recurso for recurso in recursos if recurso.get('src')]
    if recursos_validos:
        recurso = max(
            recursos_validos,
            key=lambda item: (item.get('config_width') or 0) * (item.get('config_height') or 0),
        )
        return recurso.get('src')

    return node.get('display_url') or node.get('display_src') or node.get('thumbnail_src')

def obter_media_instagram(shortcode, referer):
    cookie_jar = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cookie_jar))
    pk = shortcode_para_pk(shortcode)

    try:
        ruling_url = (
            'https://i.instagram.com/api/v1/web/get_ruling_for_content/'
            f'?content_type=MEDIA&target_id={pk}'
        )
        opener.open(urllib.request.Request(ruling_url, headers={**HTTP_HEADERS, 'Referer': referer}), timeout=30)
    except Exception:
        pass

    csrf_token = ''
    for cookie in cookie_jar:
        if cookie.name == 'csrftoken':
            csrf_token = cookie.value
            break

    variables = {
        'shortcode': shortcode,
        'child_comment_count': 3,
        'fetch_comment_count': 40,
        'parent_comment_count': 24,
        'has_threaded_comments': True,
    }
    query = urllib.parse.urlencode({
        'doc_id': '8845758582119845',
        'variables': json.dumps(variables, separators=(',', ':')),
    })
    graphql_url = f'https://www.instagram.com/graphql/query/?{query}'
    headers = {
        **HTTP_HEADERS,
        'X-CSRFToken': csrf_token,
        'X-Requested-With': 'XMLHttpRequest',
        'Referer': referer,
    }

    with opener.open(urllib.request.Request(graphql_url, headers=headers), timeout=30) as resposta:
        dados = json.loads(resposta.read().decode('utf-8'))

    return ((dados.get('data') or {}).get('xdt_shortcode_media') or {})

def baixar_fotos_instagram(url, options):
    shortcode = extrair_shortcode_instagram(url)
    if not shortcode or options.audio:
        return True

    try:
        media = obter_media_instagram(shortcode, url)
    except Exception as e:
        print(f"Nao foi possivel obter fotos do Instagram: {e}", file=sys.stderr)
        return False

    edges = (((media.get('edge_sidecar_to_children') or {}).get('edges')) or [])
    fotos = []
    for indice, edge in enumerate(edges, start=1):
        node = edge.get('node') or {}
        if node.get('__typename') == 'GraphVideo' or node.get('is_video') is True:
            continue

        imagem_url = maior_imagem(node)
        if imagem_url:
            fotos.append((indice, node, imagem_url))

    if not fotos:
        return True

    print(f"Fotos encontradas no carrossel: {len(fotos)}")
    os.makedirs(options.path, exist_ok=True)

    sucesso = True
    for indice, node, imagem_url in fotos:
        foto_id = node.get('shortcode') or node.get('id') or f'{shortcode}_{indice:02d}'
        nome_base = nome_seguro(f'{foto_id} - Foto {indice}')
        try:
            request = urllib.request.Request(
                imagem_url,
                headers={**HTTP_HEADERS, 'Referer': 'https://www.instagram.com/'},
            )
            with urllib.request.urlopen(request, timeout=60) as resposta:
                extensao = extensao_por_url_ou_resposta(imagem_url, resposta)
                caminho = os.path.join(options.path, f'{nome_base}{extensao}')
                if os.path.exists(caminho):
                    print(f"[foto] {os.path.basename(caminho)} ja existe")
                    continue

                with open(caminho, 'wb') as arquivo:
                    arquivo.write(resposta.read())

            print(f"[foto] Baixada: {os.path.basename(caminho)}")
        except Exception as e:
            sucesso = False
            print(f"[foto] Erro ao baixar foto {indice}: {e}", file=sys.stderr)

    return sucesso

def caminho_ffprobe():
    nome = 'ffprobe.exe' if os.name == 'nt' else 'ffprobe'
    caminho = os.path.join(FFMPEG_LOCATION, nome)
    return caminho if os.path.exists(caminho) else nome

def arquivo_tem_audio(caminho):
    comando = [
        caminho_ffprobe(),
        '-v', 'error',
        '-select_streams', 'a',
        '-show_entries', 'stream=index',
        '-of', 'csv=p=0',
        caminho,
    ]
    resultado = subprocess.run(comando, capture_output=True, text=True, check=False)
    if resultado.returncode != 0:
        return None

    return bool(resultado.stdout.strip())

def avisar_videos_sem_audio(url, options):
    shortcode = extrair_shortcode_instagram(url)
    if options.audio or not shortcode:
        return

    ids_video = {shortcode}
    try:
        media = obter_media_instagram(shortcode, url)
        edges = (((media.get('edge_sidecar_to_children') or {}).get('edges')) or [])
        ids_carrossel = {
            (edge.get('node') or {}).get('shortcode')
            for edge in edges
            if (edge.get('node') or {}).get('is_video') is True
        }
        ids_video = {item for item in ids_carrossel if item} or ids_video
    except Exception:
        pass

    extensoes_video = {'.mp4', '.mkv', '.webm'}
    try:
        arquivos = [
            os.path.join(options.path, nome)
            for nome in os.listdir(options.path)
            if os.path.splitext(nome)[1].lower() in extensoes_video
            and any(nome.startswith(f'{video_id} - ') or nome.startswith(f'{video_id}.') for video_id in ids_video)
        ]
    except OSError:
        return

    sem_audio = []
    nao_verificados = []
    for caminho in arquivos:
        tem_audio = arquivo_tem_audio(caminho)
        if tem_audio is False:
            sem_audio.append(os.path.basename(caminho))
        elif tem_audio is None:
            nao_verificados.append(os.path.basename(caminho))

    if nao_verificados:
        print(f"Aviso: nao foi possivel verificar o audio de {len(nao_verificados)} arquivo(s).")

    if sem_audio:
        print(f"Aviso: {len(sem_audio)} arquivo(s) de video estao sem faixa de audio.")
        print("O Instagram entregou esses itens sem audio no metadata publico usado para download.")
        for nome in sem_audio:
            print(f"  {nome}")

def normalizar_cookies_browser(valor):
    valor = (valor or '').strip().lower()
    if not valor or valor in {'nenhum', 'none', 'off', 'desativado'}:
        return None
    return valor

def baixar_video(url, options):
    url = limpar_url(url)
    print(f"\nIniciando processo para: {url}")

    
    ydl_opts = {
        'outtmpl': os.path.join(options.path, '%(id)s - %(title)s.%(ext)s'),
        'noplaylist': not options.playlist,
        'ffmpeg_location': FFMPEG_LOCATION,
    }
    cookies_browser = normalizar_cookies_browser(getattr(options, 'cookies_browser', None))
    if cookies_browser:
        if cookies_browser not in BROWSERS_COM_COOKIES:
            print(f"Navegador de cookies nao suportado: {cookies_browser}", file=sys.stderr)
            return False
        ydl_opts['cookiesfrombrowser'] = (cookies_browser, None, None, None)
        print(f"Cookies do navegador: {cookies_browser}")

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
            if not baixar_fotos_instagram(url, options):
                return False

            avisar_videos_sem_audio(url, options)

            print("\nProcesso finalizado com sucesso!")
            return True
            
    except Exception as e:
        print(f"\nOcorreu um erro durante o processo: {e}", file=sys.stderr)
        return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ferramenta para baixar vídeos e áudios usando yt-dlp.")
    
    parser.add_argument("url", help="A URL do vídeo ou playlist a ser baixado")
    parser.add_argument("--best", action="store_true", help="Baixar na melhor qualidade possível combinando vídeo e áudio (requer FFmpeg)")
    parser.add_argument("--audio", "-a", action="store_true", help="Baixar apenas o áudio e converter para MP3 (requer FFmpeg)")
    parser.add_argument("--path", "-p", default=".", help="Pasta de destino para o download (padrão: pasta atual)")
    parser.add_argument("--playlist", action="store_true", help="Permitir o download de playlists completas")
    parser.add_argument(
        "--cookies-browser",
        choices=sorted(BROWSERS_COM_COOKIES),
        help="Usar cookies de um navegador instalado, util para conteudo do Instagram que exige login",
    )

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

    sucesso = baixar_video(args.url, args)
    sys.exit(0 if sucesso else 1)
