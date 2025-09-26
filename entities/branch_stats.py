from entities.author import Author

class BranchStats():

    def __init__(self, name: str, author: Author, commits: int, date: str):
        self.name = name
        self.author = author
        self.commits = commits
        self.date = date.strftime("%Y-%m")

    def __str__(self):
        return f"name: {self.name}, author: {self.author.main_username}, commits: {self.commits}, date: {self.date}"