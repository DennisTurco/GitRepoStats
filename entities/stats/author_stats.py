from dataclasses import dataclass
from entities.author import Author

@dataclass
class AuthorStats():
    author: Author
    commits: int
    insertions: int
    deletions: int
    lines: int
    files: int

    def __str__(self) -> str:
        return f"author: {self.author.main_username}, commits: {self.commits}, insertions: {self.insertions}, deletions: {self.deletions}, lines: {self.lines}, files: {self.files}"

    def to_csv(self) -> str:
        return f"{self.author.main_username},{self.commits},{self.insertions},{self.deletions},{self.lines},{self.files}"

    def has_stats(self) -> bool:
        return self.commits != 0 or self.insertions != 0 or self.deletions != 0 or self.lines != 0 or self.files != 0

    @staticmethod
    def csv_header() -> str:
        return "Author,Commits,Insertions,Deletions,Lines,Files"

    @staticmethod
    def to_csv_data_list(stats: list["AuthorStats"], header: bool = True) -> list[str]:
        data = [AuthorStats.csv_header()] if header else []
        data += [stat.to_csv() for stat in stats]
        return data

    @staticmethod
    def sort_by_commits(stats: list["AuthorStats"]) -> None:
        stats.sort(key=lambda stat: stat.commits)

    @staticmethod
    def sort_by_insertions(stats: list["AuthorStats"]) -> None:
        stats.sort(key=lambda stat: stat.insertions)

    @staticmethod
    def sort_by_deletions(stats: list["AuthorStats"]) -> None:
        stats.sort(key=lambda stat: stat.deletions)

    @staticmethod
    def sort_by_lines(stats: list["AuthorStats"]) -> None:
        stats.sort(key=lambda stat: stat.lines)

    @staticmethod
    def sort_by_files(stats: list["AuthorStats"]) -> None:
        stats.sort(key=lambda stat: stat.files)
