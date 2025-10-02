import threading
import customtkinter as ctk
import datetime
import tkinter as tk

from entities.period_filter import PeriodFilter
from entities.report_config import ReportConfig
from logger import Logger
from repo_management import RepoManagement

class GUI(ctk.CTk):
    app_width, app_height = 850, 500

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.init_window()
        self.init_frame()

    def init_window(self) -> None:
        self.iconbitmap('./imgs/logo.ico')
        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("green")
        self.title("Git Repo Stats")
        self.centerWindow()
        self.minsize(600, 400)

    def centerWindow(self) -> None:
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width / 2) - (self.app_width / 2)
        y = (screen_height / 2) - (self.app_height / 2)
        self.geometry(f'{self.app_width}x{self.app_height}+{int(x)}+{int(y)}')

    def init_frame(self) -> None:
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)

        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(2, weight=0)

        self.filters_frame = ctk.CTkFrame(self)
        self.filters_frame.grid(row=0, column=0, columnspan=2, padx=10, pady=5, sticky="ew")
        self.filters_frame.grid_columnconfigure(0, weight=0)
        self.filters_frame.grid_columnconfigure(1, weight=1)

        label_repopath = ctk.CTkLabel(self.filters_frame, text="Workspace path:")
        label_repopath.grid(row=0, column=0, padx=5, pady=5, sticky="w")

        self.entry_repopath = ctk.CTkEntry(self.filters_frame, placeholder_text="local repo to scan")
        self.entry_repopath.grid(row=0, column=1, padx=(0, 5), pady=5, sticky="ew")

        label_start_date = ctk.CTkLabel(self.filters_frame, text="Start date (Optional):")
        label_start_date.grid(row=1, column=0, padx=5, pady=5, sticky="w")

        self.entry_start_date = ctk.CTkEntry(self.filters_frame, placeholder_text="DD-MM-YYYY")
        self.entry_start_date.grid(row=1, column=1, padx=(0, 5), pady=5, sticky="ew")

        label_end_date = ctk.CTkLabel(self.filters_frame, text="End date (Optional):")
        label_end_date.grid(row=2, column=0, padx=5, pady=5, sticky="w")

        self.entry_end_date = ctk.CTkEntry(self.filters_frame, placeholder_text="DD-MM-YYYY")
        self.entry_end_date.grid(row=2, column=1, padx=(0, 5), pady=5, sticky="ew")

        self.stats_vars = {
            "author": tk.BooleanVar(value=True),
            "commits": tk.BooleanVar(value=True),
            "branches": tk.BooleanVar(value=True),
            "files": tk.BooleanVar(value=True),
            "code": tk.BooleanVar(value=True),
            "busfactor": tk.BooleanVar(value=True)
        }

        checkbox_frame = ctk.CTkFrame(self.filters_frame)
        checkbox_frame.grid(row=3, column=0, columnspan=2, pady=10, sticky="w")

        self.check_author = ctk.CTkCheckBox(checkbox_frame, text="Author stats", variable=self.stats_vars["author"], command=self.ensure_one_checked)
        self.check_commits = ctk.CTkCheckBox(checkbox_frame, text="Commits stats", variable=self.stats_vars["commits"], command=self.ensure_one_checked)
        self.check_branches = ctk.CTkCheckBox(checkbox_frame, text="Branches stats", variable=self.stats_vars["branches"], command=self.ensure_one_checked)
        self.check_files = ctk.CTkCheckBox(checkbox_frame, text="File stats", variable=self.stats_vars["files"], command=self.ensure_one_checked)
        self.check_code_analysis = ctk.CTkCheckBox(checkbox_frame, text="Code Analysis", variable=self.stats_vars["code"], command=self.ensure_one_checked)
        self.check_bus_factor = ctk.CTkCheckBox(checkbox_frame, text="Code Ownership", variable=self.stats_vars["busfactor"], command=self.ensure_one_checked)

        self.check_author.pack(side="left", padx=5)
        self.check_commits.pack(side="left", padx=5)
        self.check_branches.pack(side="left", padx=5)
        self.check_files.pack(side="left", padx=5)
        self.check_code_analysis.pack(side="left", padx=5)
        self.check_bus_factor.pack(side="left", padx=5)

        self.log_box = ctk.CTkTextbox(self)
        self.log_box.grid(row=1, column=0, columnspan=2, padx=10, pady=(10, 0), sticky="nsew")

        self.log_box.tag_config("date", foreground="#888888")
        self.log_box.tag_config("[info]", foreground="green")
        self.log_box.tag_config("[debug]", foreground="blue")
        self.log_box.tag_config("[warn]", foreground="orange")
        self.log_box.tag_config("[error]", foreground="red")

        self.get_button = ctk.CTkButton(self, text="Get stats", border_width=2, command=self.run_get_stats_thread)
        self.get_button.grid(row=2, column=0, columnspan=2, pady=15, sticky="s")

    def ensure_one_checked(self):
        if not any(var.get() for var in self.stats_vars.values()):
            self.stats_vars["author"].set(True)

    def get_dates(self):
        start_date_str = self.entry_start_date.get().strip()
        end_date_str = self.entry_end_date.get().strip()
        try:
            start_date = datetime.datetime.strptime(start_date_str, "%d-%m-%Y") if start_date_str else None
            end_date = datetime.datetime.strptime(end_date_str, "%d-%m-%Y") if end_date_str else None
        except ValueError:
            Logger.write_log("Invalid date format, use DD-MM-YYYY", log_box=self, log_type=Logger.LogType.ERROR)
            return None, None

        if start_date and end_date and end_date < start_date:
            Logger.write_log("End date cannot be earlier than start date", log_box=self, log_type=Logger.LogType.ERROR)
            return None, None

        return start_date, end_date

    def run_get_stats_thread(self) -> None:
        repo_path = self.entry_repopath.get()
        start_date, end_date = self.get_dates()
        if start_date is None and end_date is None and (
            self.entry_start_date.get().strip() or self.entry_end_date.get().strip()
        ):
            return
        threading.Thread(target=self.get_stats, args=(repo_path, start_date, end_date), daemon=True).start()

    def get_stats(self, repo_path: str, start_date, end_date) -> None:
        try:
            self.get_button.configure(state="disabled")
            period = PeriodFilter(start_date, end_date)
            report_config = ReportConfig(self.stats_vars["author"].get(), self.stats_vars["commits"].get(), self.stats_vars["branches"].get(), self.stats_vars["files"].get(), self.stats_vars["code"].get(), self.stats_vars["busfactor"].get())

            repo = RepoManagement(repo_path, self, period, report_config)
            repo.obtain_all_info_from_repo()
        except Exception as e:
            Logger.write_log(message="Unexpected error", log_type=Logger.LogType.ERROR, log_box=self, exception=e)
        finally:
            self.get_button.configure(state="normal")

    def write_to_logbox(self, message: str) -> None:
        message = str(message).encode("utf-8", errors="replace").decode("utf-8")
        self.after(0, lambda: self.__append_to_log(message))

    def __append_to_log(self, message: str) -> None:
        self.log_box.insert(tk.END, message + "\n")

        start_index = self.log_box.index("end-2c linestart")

        first_space = message.find(" ")
        second_space = message.find(" ", first_space + 1)
        date_end_index = second_space if second_space != -1 else first_space
        if date_end_index != -1:
            self.log_box.tag_add(
                "date",
                f"{start_index} + 0c",
                f"{start_index} + {date_end_index}c"
            )

        log_types = ["[INFO]", "[DEBUG]", "[WARN]", "[ERROR]"]
        for log_type in log_types:
            type_start = message.find(log_type)
            if type_start != -1:
                type_end = type_start + len(log_type)
                self.log_box.tag_add(
                    log_type.lower(),
                    f"{start_index} + {type_start}c",
                    f"{start_index} + {type_end}c"
                )
                break

        self.log_box.see(tk.END)
