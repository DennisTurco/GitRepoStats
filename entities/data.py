from entities.period_filter import PeriodFilter

class Data():

    repo_name: str
    period: PeriodFilter
    chart_authors_html: str
    chart_files_html: str
    chart_languages_html: str
    chart_commits_html: str
    chart_comulative_commits_html: str
    chart_branches_html: str
    chart_comulative_branches_html: str
    csv_file_stats: list[str]
    csv_branches_stats: list[str]

    def __init__(self, repo_name: str, period: PeriodFilter, chart_authors_html: str, chart_files_html: str, chart_languages_html: str, chart_commits_html: str, chart_comulative_commits_html: str, chart_branches_html: str, chart_comulative_branches_html: str, csv_file_stats: list[str], csv_branches_stats: list[str]):
        self.repo_name = repo_name
        self.period = period
        self.chart_authors_html = chart_authors_html
        self.chart_files_html = chart_files_html
        self.chart_languages_html = chart_languages_html
        self.chart_commits_html = chart_commits_html
        self.chart_comulative_commits_html = chart_comulative_commits_html
        self.chart_branches_html = chart_branches_html
        self.chart_comulative_branches_html = chart_comulative_branches_html
        self.csv_file_stats = csv_file_stats
        self.csv_branches_stats = csv_branches_stats