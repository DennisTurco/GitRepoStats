from dataclasses import dataclass

@dataclass
class ReportConfig():
    authors: bool
    commits: bool
    branches: bool
    files: bool
    code_complexity: bool
    code_duplication: bool
    bus_factor: bool
