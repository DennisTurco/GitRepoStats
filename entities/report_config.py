class ReportConfig():
    authors: bool
    commits: bool
    branches: bool
    files: bool
    code_complexity: bool

    def __init__(self, authors: bool, commits: bool, branches: bool, files: bool, code_complexity: bool):
        self.authors = authors
        self.commits = commits
        self.branches = branches
        self.files = files
        self.code_complexity = code_complexity