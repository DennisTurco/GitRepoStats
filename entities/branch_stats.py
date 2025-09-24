class BranchStats():
    name: str
    author_name: str
    commits: int
    date: str

    def __init__(self, name: str, author_name: str, commits: int, date: str):
        self.name = name
        self.author_name = author_name
        self.commits = commits
        self.date = date.strftime("%Y-%m")

    def __str__(self):
        return f"name: {self.name}, author: {self.author_name}, commits: {self.commits}, date: {self.date}"