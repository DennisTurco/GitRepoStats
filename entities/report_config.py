from dataclasses import dataclass


@dataclass
class ReportConfig:
    authors: bool
    commits: bool
    branches: bool
    files: bool
    code_complexity: bool
    code_duplication: bool
    bus_factor: bool

    def get_total_requested_steps(self):
        return self.authors + self.commits + self.branches + self.files + self.code_complexity + self.code_duplication + self.bus_factor