import threading
import customtkinter as ctk
import tkinter as tk
from repo_management import RepoManagement

class GUI(ctk.CTk):
    app_width, app_height = 950, 400

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.init_window()
        self.init_frame()

    def init_window(self):
        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("green")
        self.title("Git Repo Stats")
        self.centerWindow()
        self.minsize(300, 200)

    def centerWindow(self):
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width / 2) - (self.app_width / 2)
        y = (screen_height / 2) - (self.app_height / 2)
        self.geometry(f'{self.app_width}x{self.app_height}+{int(x)}+{int(y)}')

    def init_frame(self):
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=1)

        label_repopath = ctk.CTkLabel(self, text="Workspace path:")
        label_repopath.grid(row=0, column=0, padx=10, pady=5, sticky="w")

        self.entry_repopath = ctk.CTkEntry(self, placeholder_text="local repo to scan")
        self.entry_repopath.grid(row=0, column=1, padx=(0, 10), pady=5, sticky="ew")

        self.log_box = ctk.CTkTextbox(self)
        self.log_box.grid(row=2, column=0, columnspan=2, padx=10, pady=(10, 0), sticky="nsew")

        get_button = ctk.CTkButton(
            self,
            text="Get stats",
            border_width=2,
            command=self.run_get_stats_thread
        )
        get_button.grid(row=1, column=0, columnspan=2, pady=15, sticky="n")

    def run_get_stats_thread(self):
        """separated thread"""
        repo_path = self.entry_repopath.get()
        threading.Thread(target=self.get_stats, args=(repo_path,), daemon=True).start()

    def get_stats(self, repo_path: str):
        try:
            repo = RepoManagement(repo_path, self)
            repo.obtain_all_info_from_repo()
        except Exception as e:
            self.write_to_logbox(f"Errore: {e}") #TODO: fixhere

    def write_to_logbox(self, message: str):
        """Thread-safe"""
        self.after(0, lambda: self._append_to_log(message))

    def _append_to_log(self, message: str):
        self.log_box.insert(tk.END, message + "\n")
        self.log_box.see(tk.END) # move cursor to the bottom
