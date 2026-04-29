import contextlib
import os
import queue
import threading
import tkinter as tk
from types import SimpleNamespace
from tkinter import filedialog, messagebox, ttk

from baixarvideo import baixar_video


APP_NAME = 'BaixarVideo by Jair Lima'


class QueueWriter:
    def __init__(self, output_queue):
        self.output_queue = output_queue

    def write(self, text):
        if text:
            self.output_queue.put(('log', text))

    def flush(self):
        pass


class BaixarVideoApp:
    def __init__(self, root):
        self.root = root
        self.root.title(APP_NAME)
        self.root.minsize(760, 560)

        self.output_queue = queue.Queue()
        self.worker = None

        self.url_var = tk.StringVar()
        self.path_var = tk.StringVar(value=self.default_download_folder())
        self.best_var = tk.BooleanVar(value=False)
        self.audio_var = tk.BooleanVar(value=False)
        self.playlist_var = tk.BooleanVar(value=False)
        self.cookies_browser_var = tk.StringVar(value='nenhum')
        self.status_var = tk.StringVar(value='Pronto')

        self.build_ui()
        self.root.protocol('WM_DELETE_WINDOW', self.on_close)
        self.root.after(100, self.process_queue)

    def default_download_folder(self):
        downloads = os.path.join(os.path.expanduser('~'), 'Downloads')
        return downloads if os.path.isdir(downloads) else os.getcwd()

    def build_ui(self):
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(2, weight=1)

        main = ttk.Frame(self.root, padding=16)
        main.grid(row=0, column=0, sticky='nsew')
        main.columnconfigure(1, weight=1)

        ttk.Label(main, text='Link').grid(row=0, column=0, sticky='w', padx=(0, 8), pady=(0, 10))
        url_entry = ttk.Entry(main, textvariable=self.url_var)
        url_entry.grid(row=0, column=1, sticky='ew', pady=(0, 10))
        url_entry.focus_set()

        ttk.Label(main, text='Pasta').grid(row=1, column=0, sticky='w', padx=(0, 8), pady=(0, 10))
        path_entry = ttk.Entry(main, textvariable=self.path_var)
        path_entry.grid(row=1, column=1, sticky='ew', pady=(0, 10))
        ttk.Button(main, text='Escolher', command=self.choose_folder).grid(
            row=1, column=2, sticky='ew', padx=(8, 0), pady=(0, 10))

        options = ttk.Frame(main)
        options.grid(row=2, column=1, sticky='w', pady=(0, 12))

        ttk.Checkbutton(options, text='Melhor qualidade', variable=self.best_var).grid(row=0, column=0, padx=(0, 18))
        ttk.Checkbutton(options, text='Somente audio MP3', variable=self.audio_var).grid(row=0, column=1, padx=(0, 18))
        ttk.Checkbutton(options, text='Playlist completa', variable=self.playlist_var).grid(row=0, column=2, padx=(0, 18))
        ttk.Label(options, text='Cookies').grid(row=0, column=3, padx=(0, 6))
        cookies_combo = ttk.Combobox(
            options,
            textvariable=self.cookies_browser_var,
            values=('nenhum', 'chrome', 'edge', 'firefox', 'brave', 'chromium', 'opera', 'vivaldi'),
            width=10,
            state='readonly',
        )
        cookies_combo.grid(row=0, column=4)

        actions = ttk.Frame(main)
        actions.grid(row=3, column=1, sticky='w')

        self.download_button = ttk.Button(actions, text='Baixar', command=self.start_download)
        self.download_button.grid(row=0, column=0, padx=(0, 8))
        ttk.Button(actions, text='Abrir pasta', command=self.open_folder).grid(row=0, column=1)

        log_frame = ttk.Frame(self.root, padding=(16, 0, 16, 12))
        log_frame.grid(row=2, column=0, sticky='nsew')
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)

        self.log_text = tk.Text(log_frame, wrap='word', height=18, state='disabled')
        self.log_text.grid(row=0, column=0, sticky='nsew')

        scrollbar = ttk.Scrollbar(log_frame, command=self.log_text.yview)
        scrollbar.grid(row=0, column=1, sticky='ns')
        self.log_text.configure(yscrollcommand=scrollbar.set)

        status = ttk.Frame(self.root, padding=(16, 0, 16, 12))
        status.grid(row=3, column=0, sticky='ew')
        status.columnconfigure(0, weight=1)
        ttk.Label(status, textvariable=self.status_var).grid(row=0, column=0, sticky='w')

    def choose_folder(self):
        folder = filedialog.askdirectory(initialdir=self.path_var.get() or self.default_download_folder())
        if folder:
            self.path_var.set(folder)

    def open_folder(self):
        folder = self.path_var.get().strip()
        if not folder:
            return

        try:
            os.makedirs(folder, exist_ok=True)
            os.startfile(folder)
        except OSError as exc:
            messagebox.showerror(APP_NAME, f'Nao foi possivel abrir a pasta:\n{exc}')

    def start_download(self):
        if self.worker and self.worker.is_alive():
            return

        url = self.url_var.get().strip()
        folder = self.path_var.get().strip()
        if not url:
            messagebox.showwarning(APP_NAME, 'Informe um link.')
            return
        if not folder:
            messagebox.showwarning(APP_NAME, 'Informe uma pasta de destino.')
            return

        try:
            os.makedirs(folder, exist_ok=True)
        except OSError as exc:
            messagebox.showerror(APP_NAME, f'Nao foi possivel criar a pasta:\n{exc}')
            return

        options = SimpleNamespace(
            path=folder,
            best=self.best_var.get(),
            audio=self.audio_var.get(),
            playlist=self.playlist_var.get(),
            cookies_browser=self.cookies_browser_var.get(),
        )

        self.clear_log()
        self.download_button.configure(state='disabled')
        self.status_var.set('Baixando')

        self.worker = threading.Thread(target=self.run_download, args=(url, options), daemon=True)
        self.worker.start()

    def run_download(self, url, options):
        writer = QueueWriter(self.output_queue)
        try:
            with contextlib.redirect_stdout(writer), contextlib.redirect_stderr(writer):
                success = baixar_video(url, options)
        except Exception as exc:
            self.output_queue.put(('log', f'\nErro inesperado: {exc}\n'))
            success = False

        self.output_queue.put(('done', success))

    def process_queue(self):
        try:
            while True:
                kind, payload = self.output_queue.get_nowait()
                if kind == 'log':
                    self.append_log(payload)
                elif kind == 'done':
                    self.download_button.configure(state='normal')
                    self.status_var.set('Concluido' if payload else 'Erro')
                    if payload:
                        self.append_log('\nConcluido.\n')
                    else:
                        self.append_log('\nFinalizado com erro.\n')
        except queue.Empty:
            pass

        self.root.after(100, self.process_queue)

    def append_log(self, text):
        self.log_text.configure(state='normal')
        self.log_text.insert('end', text)
        self.log_text.see('end')
        self.log_text.configure(state='disabled')

    def clear_log(self):
        self.log_text.configure(state='normal')
        self.log_text.delete('1.0', 'end')
        self.log_text.configure(state='disabled')

    def on_close(self):
        if self.worker and self.worker.is_alive():
            if not messagebox.askyesno(APP_NAME, 'Ha um download em andamento. Deseja fechar mesmo assim?'):
                return

        self.root.destroy()


def main():
    root = tk.Tk()
    BaixarVideoApp(root)
    root.mainloop()


if __name__ == '__main__':
    main()
