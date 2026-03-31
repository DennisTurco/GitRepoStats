from dataclasses import dataclass
from datetime import datetime


@dataclass
class OverviewData:
    commits: int | None
    last_commit: datetime | None
    branches: int | None
    authors: int | None
    files: int | None
    complexity_avg: float | None
    #main_file_extension: str | None
