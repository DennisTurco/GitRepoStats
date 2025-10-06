from dataclasses import dataclass
from entities.period_filter import PeriodFilter

@dataclass
class Data():
    repo_name: str
    period: PeriodFilter
    chart_authors_html: str
    chart_files_html: str
    chart_languages_html: str
    chart_commits_html: str
    chart_cumulative_commits_html: str
    chart_branches_html: str
    chart_cumulative_branches_html: str
    csv_file_stats: list[str]
    csv_branches_stats: list[str]
    csv_code_complexity: list[str]
    csv_code_duplication: list[str]
    csv_bus_factor: list[str]
