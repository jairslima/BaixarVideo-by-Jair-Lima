import sys
import yt_dlp

def baixar_video(url):
    ydl_opts = {
        'outtmpl': '%(title)s.%(ext)s',
        'format': 'best',
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
            print("\nDownload concluído com sucesso!")
    except Exception as e:
        print(f"\nOcorreu um erro ao tentar baixar o vídeo: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: baixarvideo <URL>")
        sys.exit(1)
    
    url = sys.argv[1]
    print(f"Iniciando o download de: {url}")
    baixar_video(url)
