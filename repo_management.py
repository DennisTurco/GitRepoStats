import os
from git import Repo
from dashboard import Dashboard
from logger import Logger
from plot import Plot
import subprocess
import re

from entities.data import Data
from entities.author import Author
from entities.lizard_data import LizardData
from entities.report_config import ReportConfig
from entities.stats.commit_stats import CommitStats
from entities.stats.author_stats import AuthorStats
from entities.stats.file_stats import FileStats
from entities.stats.branch_stats import BranchStats
from entities.period_filter import PeriodFilter

class RepoManagement:

    def __init__(self, repo_path: str, log_box, period: PeriodFilter, report_config: ReportConfig):
        self.repo_path = repo_path
        self._repo_obj = Repo(repo_path)
        self.log_box = log_box
        self.period = period
        self.report_config = report_config
        self.repo_name = self.__get_repo_name_from_path(repo_path)

    def __get_repo_name_from_path(self, repo_path) -> str:
        pos = 0
        for i in range(len(repo_path)-1, 0, -1):
            if repo_path[i] != '\\':
                pos += 1
            else:
                break
        return repo_path[len(repo_path)-pos:]


    def obtain_all_info_from_repo(self) -> None:
        code_complexity = None
        authors = None
        author_stats = None
        file_stats = None
        commits_stats = None
        branches_stats = None
        if self.report_config.code_complexity:
            lizard_output = self.__analyze_code_complexity()
            code_complexity = self.__parse_lizard_output(lizard_output)
        if self.report_config.authors or self.report_config.branches or self.report_config.branches or self.report_config.commits or self.report_config.files:
            authors = self.__get_authors() # to obtain only the unique author without duplications
            author_stats = self.__get_authors_stats_list(authors) if self.report_config.authors else None
            file_stats = self.__get_files_stats_list(authors) if self.report_config.files else None
            commits_stats = self.__get_commits_stats_list(authors) if self.report_config.commits else None
            branches_stats = self.__get_branches_stats_list(authors) if self.report_config.branches else None

        self.__plot_all_stats(author_stats, file_stats, commits_stats, branches_stats, code_complexity)

    def __analyze_code_complexity(self) -> str:
        Logger.write_log(f"Calculating code complexity for {self.repo_path}", log_box=self.log_box)
        try:
            result = subprocess.run(
                ["lizard", self._repo_obj.working_tree_dir],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="ignore"
            )

            if result.returncode == 2:
                Logger.write_log(f"Code complexity analysis failed:\n{result.stderr}", log_box=self.log_box, log_type=Logger.LogType.ERROR)
                return ""
            if result.returncode == 1:
                Logger.write_log(f"Code complexity analysis completed with warnings.", log_box=self.log_box)

            Logger.write_log(f"Code complexity analysis completed for {self.repo_path}", log_box=self.log_box)
            return result.stdout

        except Exception as e:
            Logger.write_log(f"Unexpected error: {e}", log_box=self.log_box, log_type=Logger.LogType.ERROR)
            return ""

    def __parse_lizard_output(self, lizard_output) -> list[LizardData]:
        lines = lizard_output.splitlines()

        start = None
        for i, line in enumerate(lines):
            if line.startswith("==="):
                start = i + 2
                break

        if start is None:
            return []

        # read data from string
        data = []
        for line in lines[start:]:
            if line.strip() == "" or line.startswith("==="):
                break
            parts = re.split(r"\s+", line.strip(), maxsplit=5)
            if len(parts) == 6:
                nloc, ccn, token, param, length, location = parts
                data.append(LizardData(int(nloc), int(ccn), int(token), int(param), int(length), location))
        return data

    def __iter_filtered_commits(self, **kwargs):
        for commit in self._repo_obj.iter_commits(**kwargs):
            commit_date = commit.committed_datetime.replace(tzinfo=None)
            if self.period.start_date and commit_date < self.period.start_date:
                continue
            if self.period.end_date and commit_date > self.period.end_date:
                continue
            yield commit


    def __get_authors(self) -> list[Author]:
        Logger.write_log("Getting authors...", log_box=self.log_box)

        authors: list[Author] = []
        noreply_authors: list[Author] = []

        # from commits
        for commit in self.__iter_filtered_commits():
            email = commit.author.email.lower()
            name = commit.author.name.strip()
            new_author = Author(email, name)

            if "noreply.github.com" in email:
                noreply_authors.append(new_author)
                continue

            pos = new_author.get_pos_inside(authors)
            if pos != -1:
                authors[pos].add_email_if_not_saved(email)
                authors[pos].add_username_alias_if_not_saved(name)
            else:
                authors.append(new_author)
                Logger.write_log(f"User (from commit): {new_author.main_username} ({new_author.main_email})", log_box=self.log_box)

        # from branches
        self._repo_obj.remotes.origin.fetch()
        for ref in self._repo_obj.refs:
            if ref.name.startswith("origin/") or ref in self._repo_obj.branches:
                commit = ref.commit
                if commit:
                    email = commit.author.email.lower()
                    name = commit.author.name.strip()
                    new_author = Author(email, name)

                    if "noreply.github.com" in email:
                        noreply_authors.append(new_author)
                        continue

                    pos = new_author.get_pos_inside(authors)
                    if pos != -1:
                        authors[pos].add_email_if_not_saved(email)
                        authors[pos].add_username_alias_if_not_saved(name)
                    else:
                        authors.append(new_author)
                        Logger.write_log(f"User (from branch): {new_author.main_username} ({new_author.main_email})", log_box=self.log_box)

        # sanification github noreply
        for noreply in noreply_authors:
            main_found = False
            for author in authors:
                if (author.main_username.lower() in noreply.main_email or author.main_username == noreply.main_username):
                    author.add_email_if_not_saved(noreply.main_email)
                    author.add_username_alias_if_not_saved(noreply.main_username)
                    main_found = True
            if not main_found:
                authors.append(noreply)
                Logger.write_log(f"Main email not found for user: {noreply.main_username} ({noreply.main_email})", log_box=self.log_box, log_type=Logger.LogType.WARN)

        return authors

    def __get_authors_stats_list(self, authors: list[Author]) -> list[AuthorStats]:
        Logger.write_log("Getting authors stats list...", log_box=self.log_box)

        author_stats_map = {author.main_username: AuthorStats(author, 0, 0, 0, 0, 0) for author in authors}

        for commit in self.__iter_filtered_commits():
            author = self.__find_author(commit.author.email, authors)
            if not author:
                continue

            stats = commit.stats.total
            a_stats = author_stats_map[author.main_username]
            a_stats.commits += 1
            a_stats.insertions += stats.get('insertions', 0)
            a_stats.deletions += stats.get('deletions', 0)
            a_stats.lines += stats.get('lines', 0)
            a_stats.files += stats.get('files', 0)

        Logger.write_log(f"Author stats list obtained ({len(author_stats_map)})", log_box=self.log_box)
        return list(author_stats_map.values())

    def __get_files_stats_list(self, authors: list[Author]) -> list[FileStats]:
        Logger.write_log("Getting files stats list...", log_box=self.log_box)

        file_stats_map: dict[str, FileStats] = {}

        for commit in self.__iter_filtered_commits():
            author = self.__find_author(commit.author.email, authors)
            if not author:
                continue

            for file_name in commit.stats.files.keys():
                if file_name not in file_stats_map:
                    file_extension = self.__get_extension_from_file(file_name) or "Other"
                    file_stats_map[file_name] = FileStats(file_name, 0, None, None, file_extension)

                f_stats = file_stats_map[file_name]
                f_stats.changes += 1
                if f_stats.last_update is None or commit.committed_datetime > f_stats.last_update:
                    f_stats.last_update = commit.committed_datetime
                    f_stats.last_author = author
        files_stats = [stat for stat in file_stats_map.values() if stat.changes > 0]
        return files_stats

    def __get_commits_stats_list(self, authors: list[Author]) -> list[CommitStats]:
        Logger.write_log("Getting commits stats list...", log_box=self.log_box)

        commits_stats = []
        for commit in self.__iter_filtered_commits():
            Logger.write_log(f"Getting commit stats for {commit.hexsha}", log_box=self.log_box)
            author = self.__find_author(commit.author.email, authors)
            commits_stats.append(CommitStats(commit, author, len(commit.stats.files.keys()), commit.committed_datetime))

        return commits_stats

    def __get_branches_stats_list(self, authors: list[Author]) -> list[BranchStats]:
        Logger.write_log("Getting ALL branches (local + remote)...", log_box=self.log_box)

        branches = list(self._repo_obj.branches) + list(self._repo_obj.remotes.origin.refs)
        branches_stats = []

        for branch in branches:
            Logger.write_log(f"Getting branch stats for {branch.name}", log_box=self.log_box)

            try:
                commit = branch.commit
            except Exception as e:
                Logger.write_log(f"Cannot access commit for {branch.name}: {e}", log_box=self.log_box, log_type=Logger.LogType.WARN)
                continue

            try:
                commit_count = int(self._repo_obj.git.rev_list("--count", branch.name))
            except Exception as e:
                Logger.write_log(f"Cannot count commits for {branch.name}: {e}", log_box=self.log_box, log_type=Logger.LogType.WARN)
                commit_count = 0

            author_obj = self.__find_author(commit.author.email if commit else "", authors)

            branches_stats.append(
                BranchStats(
                    branch.name,
                    author_obj,
                    commit_count,
                    commit.committed_datetime if commit else None
                )
            )

        return branches_stats

    def __get_extension_from_file(self, file_path: str) -> str:
        _, ext = os.path.splitext(file_path)
        return ext.lstrip(".").lower()


    def __find_author(self, email: str, authors: list[Author]) -> Author:
        email = email.lower()
        for author in authors:
            if email in author.emails:
                return author
        Logger.write_log(f"No user with email {email} found, setting value to Unknown", log_box=self.log_box, log_type=Logger.LogType.WARN)
        return Author(email, "Unknown")


    def __plot_all_stats(self, all_stats: list[AuthorStats], file_stats: list[FileStats], commits_stats: list[CommitStats], branches_stats: list[BranchStats], code_complexity: list[LizardData]) -> None:
        Logger.write_log("Preparing data for plotting", log_box=self.log_box)

        plot = Plot()
        plot.init_dataframe_authors(all_stats)
        plot.init_dataframe_files(file_stats)
        plot.init_dataframe_commits(commits_stats)
        plot.init_dataframe_branches(branches_stats)

        authors_html = plot.get_authors_html() if self.report_config.authors else ""
        files_html = plot.get_files_html() if self.report_config.files else ""
        languages_html = plot.get_languages_chart() if self.report_config.files else ""
        commits_html = plot.get_commits_html() if self.report_config.commits else ""
        cumulative_commits_html = plot.get_commits_cumulative_html() if self.report_config.commits else ""
        branches_html = plot.get_branches_html() if self.report_config.branches else ""
        cumulative_branches_html = plot.get_branches_cumulative_html() if self.report_config.branches else ""
        csv_files = FileStats.to_csv_data_list(file_stats) if self.report_config.files and file_stats else ["No data available"]
        csv_branches = BranchStats.to_csv_data_list(branches_stats) if self.report_config.branches and branches_stats else ["No data available"]
        csv_code_complexity = LizardData.to_csv_data_list(code_complexity) if self.report_config.code_complexity and code_complexity else ["No data available"]

        data_to_plot = Data(self.repo_name, self.period, authors_html, files_html, languages_html, commits_html, cumulative_commits_html, branches_html, cumulative_branches_html, csv_files, csv_branches, csv_code_complexity)

        Logger.write_log("Generating dashboard file .html", log_box=self.log_box)
        Dashboard.generate_html_page(data_to_plot)

        Logger.write_log(message="Opening Dashboard", log_box=self.log_box)
        Dashboard.open_result_website()
