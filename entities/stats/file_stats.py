from entities.author import Author

class FileStats():

    def __init__(self, name: str, changes: int, last_update: str, last_author: Author, file_language: str) -> None:
        self.name = name
        self.changes = changes
        self.last_update = last_update
        self.last_author = last_author
        self.file_language = file_language

    def __str__(self) -> str:
        return f"name: {self.name}, changes: {self.changes}, last_update: {self.last_update}, last_author: {self.last_author.main_username}, language: {self.file_language}"

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