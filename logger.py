from datetime import datetime
from typing import Optional
from enum import Enum

FILE_PATH = "./config/logs.log"

class Logger:
    class LogType(Enum):
        INFO = True
        DEBUG = True
        WARN = True
        ERROR = True
        MAX_LINES = 10000
        LINES_TO_KEEP_AFTER_FILE_CLEAR = 3000

        @classmethod
        def _set(cls, key: str, value: bool):
            """Set the value for a given log type."""
            if key in cls.__members__:
                cls.__members__[key]._value_ = value  # Dynamically update the Enum value
            else:
                raise KeyError(f"Key '{key}' not found in Logger.LogType")

    @staticmethod
    def write_log(message: str, log_type: LogType = LogType.INFO, log_box = None, exception: Optional[Exception] = None):
        """
        Write a log entry to the file, always adding it to the top of the log file.
        """

        # Validate the log type
        if not isinstance(log_type, Logger.LogType):
            raise ValueError(
                f"Invalid log type: '{log_type}'. "
                f"Allowed types: {', '.join(Logger.LogType.__members__.keys())}"
            )

        # Check if the log type is enabled
        if not log_type.value:
            return

        # Ensure that an exception is provided if log type is ERROR
        if log_type == Logger.LogType.ERROR and exception is None:
            new_log_entry = f"{datetime.now()} [ERROR] {message}\n"
        elif exception:
            new_log_entry = f"{datetime.now()} [{log_type.name}] {message}: {exception}\n"
        else:
            new_log_entry = f"{datetime.now()} [{log_type.name}] {message}\n"

        # Prepare the new log entry
        if exception:
            new_log_entry = (
                f"{datetime.now()} [{log_type.name}] {message}: {exception}\n"
            )
        else:
            new_log_entry = f"{datetime.now()} [{log_type.name}] {message}\n"

        # Normalize message (strip line breaks for console/log_box display)
        safe_message = new_log_entry.strip()

        # --- Console output (force UTF-8 safe) ---
        try:
            sys.stdout.buffer.write((safe_message + "\n").encode("utf-8", errors="replace"))
        except Exception:
            # Fallback: replace problematic chars
            print(safe_message.encode("ascii", errors="replace").decode("ascii"))

        # --- GUI log box ---
        if log_box is not None:
            log_box.write_to_logbox(safe_message)

        # --- File logging (UTF-8, safe for special chars) ---
        try:
            with open(FILE_PATH, "r", encoding="utf-8") as file:
                existing_content = file.readlines()
        except FileNotFoundError:
            existing_content = []

        # Trim log file if needed
        if len(existing_content) >= Logger.LogType.MAX_LINES.value:
            existing_content = existing_content[
                -Logger.LogType.LINES_TO_KEEP_AFTER_FILE_CLEAR.value:
            ]

        # Write new entry to the top
        with open(FILE_PATH, "w", encoding="utf-8") as file:
            file.write(new_log_entry)
            file.writelines(existing_content)
