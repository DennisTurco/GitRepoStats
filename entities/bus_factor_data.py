from collections import defaultdict
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

    def __get_total_file_lines(self) -> int:
        return sum(owner.lines for owner in self.owners)

    def __get_total_file_lines_by_author(self, author: Author) -> int:
        lines = 0
        for owner in self.owners:
            if owner.author != author: continue
            lines += owner.lines
        return lines

    @staticmethod
    def csv_header_summary() -> str:
        return "Owner,Lines,Percentage"

    @staticmethod
    def csv_header() -> str:
        return "Filename,Owner,Lines,Percentage"

    @staticmethod
    def to_csv_data_list_summary(stats: list["BusFactorData"], header: bool = True) -> list[str]:
        data = [BusFactorData.csv_header_summary()] if header else []
        bus_data = BusFactorData.__calculate_bus_data_grouped_by_author(stats)

        total_lines = sum(bd_value for bd_value in bus_data.values())
        for bd_key, bd_value in bus_data.items():
            percentage = (bd_value / total_lines * 100) if total_lines > 0 else 0
            data.append(f"{bd_key},{bd_value},{percentage:.2f}%")
        return data

    @staticmethod
    def __calculate_bus_data_grouped_by_author(stats: list["BusFactorData"]) -> defaultdict[str, int]:
        bus_data: defaultdict[str, int] = defaultdict(int)
        for stat in stats:
            for owner in stat.owners:
                bus_data[owner.author.main_username] += stat.__get_total_file_lines_by_author(owner.author)
        return bus_data

    @staticmethod
    def to_csv_data_list(stats: list["BusFactorData"], header: bool = True) -> list[str]:
        data = [BusFactorData.csv_header()] if header else []
        for stat in stats:
            data.extend(stat.to_csv())
        return data
