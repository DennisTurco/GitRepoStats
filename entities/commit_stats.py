'''
valutare se ha senso crera euna struttura così, in questo caso probabilmente ridurrei il costo per il popolamento
ma otterrei dei veri vantaggi per poi quando devo manipolare questi dati?

name: Gio, {[commit: adgasd12, filesedited: 5, date: 2025-09-13, file_edited: ['file1', 'file2', 'file3']], [commit: adgasd12, filesedited: 1, date: 2025-09-16, file_edited: ['file4', 'file5']]}

'''
from entities.author import Author

class CommitStats():

    def __init__(self, name: str, author: Author, files_edited: int, date: str):
        self.name = name
        self.author = author
        self.files_edited = files_edited
        self.date = date.strftime("%Y-%m")

    def __str__(self) -> str:
        return f"Commit: {self.name}, Author: {self.author.main_username}, FilesEdited: {self.files_edited}, Date: {self.date}"

    def to_csv(self) -> str:
        return f"{self.name},{self.author.main_username},{self.files_edited},{self.date}"

    @staticmethod
    def csv_header() -> str:
        return "Commit,Author,FilesEdited,Date"

    @staticmethod
    def to_csv_data_list(stats: list["CommitStats"], header: bool = False) -> list[str]:
        data = [CommitStats.csv_header()] if header else []
        data += [stat.to_csv() for stat in stats]
        return data

    @staticmethod
    def sort_by_date(stats: list["CommitStats"]) -> None:
        stats.sort(key=lambda stat: stat.date)