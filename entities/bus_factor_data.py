from dataclasses import dataclass, field
from entities.author import Author

@dataclass
class FileOwner:
    author: Author
    lines: int

    def to_csv(self) -> str:
        return f"{self.author.main_username},{self.lines}"


@dataclass
class BusFactorData:
    filepath: str
    owners: list[FileOwner] = field(init=False)

    def __post_init__(self):
        self.owners = []

    def add_owner(self, owner: FileOwner):
        for existing in self.owners:
            if existing.author.main_email == owner.author.main_email:
                existing.lines += owner.lines
                return
        self.owners.append(owner)

    def to_csv(self) -> list[str]:
        lines = []
        total_lines = self.__get_total_file_lines()
        for owner in self.owners:
            percentage = (owner.lines / total_lines * 100) if total_lines > 0 else 0
            lines.append(f"{self.filepath},{owner.to_csv()},{percentage:.2f}%")
        return lines

    @staticmethod
    def csv_header() -> str:
        return "Filename,Owner,Lines,Percentage"

    @staticmethod
    def to_csv_data_list(stats: list["BusFactorData"], header: bool = True) -> list[str]:
        data = [BusFactorData.csv_header()] if header else []
        for stat in stats:
            data.extend(stat.to_csv())  # flatten invece che append
        return data

    def __get_total_file_lines(self) -> int:
        return sum(owner.lines for owner in self.owners)
