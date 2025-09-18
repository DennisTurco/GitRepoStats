class Stats():
    name: str
    commits: int
    insertions: int
    deletions: int
    lines: int
    files: int

    def __init__(self, name: str, commits: int, insertions: int, deletetions: int, lines: int, files: int):
        self.name = name
        self.commits = commits
        self.insertions = insertions
        self.deletions = deletetions
        self.lines = lines
        self.files = files

    def __str__(self):
        return f"name: {self.name}, commits: {self.commits}, insertions: {self.insertions}, deletions: {self.deletions}, lines: {self.lines}, files: {self.files}"