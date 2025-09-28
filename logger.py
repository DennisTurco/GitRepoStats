from datetime import datetime
from typing import Optional
from enum import Enum
import sys
import os

FILE_PATH = "./config/logs.log"

class Logger:
    class LogType(Enum):
        INFO = "INFO"
        DEBUG = "DEBUG"
        WARN = "WARN"
        ERROR = "ERROR"

    LogTypeEnabled = {
        LogType.INFO: True,
        LogType.DEBUG: True,
        LogType.WARN: True,
        LogType.ERROR: True,
    }

    MAX_LINES = 10000
    LINES_TO_KEEP_AFTER_FILE_CLEAR = 3000

    @classmethod
    def _set(cls, key: str, value: bool):
        """Set the value for a given log type."""
        for log_type in cls.LogType:
            if log_type.name == key:
                cls.LogTypeEnabled[log_type] = value
                return
        raise KeyError(f"Key '{key}' not found in Logger.LogType")

    @staticmethod
    def write_log(
        message: str,
        log_type: Optional["Logger.LogType"] = None,
        log_box=None,
        exception: Optional[Exception] = None
    ):
        """
        Write a log entry to the file, always adding it to the top of the log file.
        """

        if log_type is None:
            log_type = Logger.LogType.INFO

        if not isinstance(log_type, Logger.LogType):
            raise ValueError(
                f"Invalid log type: '{log_type}'. "
                f"Allowed types: {', '.join(Logger.LogType.__members__.keys())}"
            )

        # Check if this log type is enabled
        if not Logger.LogTypeEnabled.get(log_type, True):
            return

        log_prefix = f"[{log_type.name}]"

        if exception:
            new_log_entry = f"{datetime.now()} {log_prefix} {message}: {exception}\n"
        else:
            new_log_entry = f"{datetime.now()} {log_prefix} {message}\n"

        safe_message = new_log_entry.strip()

        # --- Console output ---
        try:
            sys.stdout.buffer.write((safe_message + "\n").encode("utf-8", errors="replace"))
        except Exception:
            print(safe_message.encode("ascii", errors="replace").decode("ascii"))

        # --- GUI log box ---
        if log_box is not None:
            log_box.write_to_logbox(safe_message)

        # --- File logging ---
        if not os.path.exists(os.path.dirname(FILE_PATH)):
            os.makedirs(os.path.dirname(FILE_PATH))

        try:
            with open(FILE_PATH, "r", encoding="utf-8") as file:
                existing_content = file.readlines()
        except FileNotFoundError:
            existing_content = []

        if len(existing_content) >= Logger.MAX_LINES:
            existing_content = existing_content[-Logger.LINES_TO_KEEP_AFTER_FILE_CLEAR:]

        with open(FILE_PATH, "w", encoding="utf-8") as file:
            file.write(new_log_entry)
            file.writelines(existing_content)
