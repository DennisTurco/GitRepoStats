from entities.author import Author

class BranchStats():

    def __init__(self, name: str, author: Author, commits: int, date: str):
        self.name = name
        self.author = author
        self.commits = commits
        self.date = date.strftime("%Y-%m")

    def __str__(self):
        return f"name: {self.name}, author: {self.author.main_username}, commits: {self.commits}, date: {self.date}"

    def to_csv(self):
        return f"{self.name},{self.author.main_username},{self.date}"

    @staticmethod
    def csv_header():
        return "Branch,Author,Date"

    @staticmethod
    def to_csv_data_list(stats: list["BranchStats"], header: bool = True) -> list[str]:
        data = [BranchStats.csv_header()] if header else []
        data += [stat.to_csv() for stat in stats]
        return data