from dataclasses import dataclass
from entities.author import Author

@dataclass
class FileStats():

    name: str
    changes: int
    last_update: str
    last_author: Author
    file_language: str

    def to_csv(self) -> str:
        return f"{self.name},{self.changes},{self.last_update},{self.last_author.main_username},{self.file_language}"

    @staticmethod
    def csv_header() -> str:
        return "File,Changes,LastUpdate,LastAuthor,Language"

    @staticmethod
    def to_csv_data_list(stats: list["FileStats"], header: bool = True) -> list[str]:
        data = [FileStats.csv_header()] if header else []
        data += [stat.to_csv() for stat in stats]
        return data

    @staticmethod
    def sort_by_changes(stats: list["FileStats"]) -> None:
        stats.sort(key=lambda stat: stat.changes)

    @staticmethod
    def sort_by_last_update(stats: list["FileStats"]) -> None:
        stats.sort(key=lambda stat: stat.last_update)