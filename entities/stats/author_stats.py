from dataclasses import dataclass
from entities.author import Author
from entities.count_per_extension import CountPerExtension

@dataclass
class AuthorStats():
    author: Author
    commits: int
    insertions: CountPerExtension
    deletions: CountPerExtension
    lines: CountPerExtension
    files: CountPerExtension

    def __str__(self) -> str:
        return f"author: {self.author.main_username}, commits: {self.commits}, insertions: {self.insertions.total}, deletions: {self.deletions.total}, lines: {self.lines.total}, files: {self.files.total}"

    def to_csv(self) -> str:
        return f"{self.author.main_username},{self.commits.total},{self.insertions.total},{self.deletions.total},{self.lines.total},{self.files.total}"

    def has_stats(self) -> bool:
        return self.commits != 0 or self.insertions.total != 0 or self.deletions.total != 0 or self.lines.total != 0 or self.files.total != 0

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
        stats.sort(key=lambda stat: stat.insertions.total)

    @staticmethod
    def sort_by_deletions(stats: list["AuthorStats"]) -> None:
        stats.sort(key=lambda stat: stat.deletions.total)

    @staticmethod
    def sort_by_lines(stats: list["AuthorStats"]) -> None:
        stats.sort(key=lambda stat: stat.lines.total)

    @staticmethod
    def sort_by_files(stats: list["AuthorStats"]) -> None:
        stats.sort(key=lambda stat: stat.files.total)
