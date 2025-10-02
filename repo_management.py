import os
from git import Repo
from dashboard import Dashboard
from entities.bus_factor_data import BusFactorData, FileOwner
from logger import Logger
from plot import Plot
import lizard

from entities.data import Data
from entities.author import Author
from entities.lizard_data import LizardData, LizardLocation
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
        authors = self.__get_authors() # to obtain only the unique author without duplications
        code_complexity = self.__analyze_code_complexity_with_lizard() if self.report_config.code_complexity else None
        bus_factor = self.__get_bus_factor_data(authors) if self.report_config.code_complexity else None
        author_stats = self.__get_authors_stats_list(authors) if self.report_config.authors else None
        file_stats = self.__get_files_stats_list(authors) if self.report_config.files else None
        commits_stats = self.__get_commits_stats_list(authors) if self.report_config.commits else None
        branches_stats = self.__get_branches_stats_list(authors) if self.report_config.branches else None

        self.__plot_all_stats(author_stats, file_stats, commits_stats, branches_stats, code_complexity, bus_factor)

    def __analyze_code_complexity_with_lizard(self) -> list[LizardData]:
        Logger.write_log(f"Calculating code complexity for {self.repo_path}", log_box=self.log_box)
        results = lizard.analyze([self.repo_path])
        all_functions: list[LizardData] = []

        for file_info in results:
            for fun in file_info.function_list:
                if self.__skip_function_from_analysis(fun.name, fun.start_line, fun.end_line, self.__get_extension_from_file(file_info.filename)):
                    continue
                data = LizardData(
                    nloc=fun.nloc,
                    ccn=fun.cyclomatic_complexity,
                    token=fun.token_count,
                    param=fun.parameter_count,
                    length=fun.length,
                    location=LizardLocation(
                        function=fun.name,
                        lines=f"{fun.start_line}-{fun.end_line}",
                        file=file_info.filename
                    )
                )
                all_functions.append(data)

        Logger.write_log(f"Code complexity calculated successfully", log_box=self.log_box)
        return all_functions

    def __skip_function_from_analysis(self, function_name: str, start_line: int, end_line: int, file_extension: str) -> bool:
        return (file_extension == "js" and start_line == end_line) or function_name == "" or function_name == "(anonymous)"

    def __get_bus_factor_data(self, authors: list[Author]) -> list[BusFactorData]:
        Logger.write_log("Calculating code ownership by file stats...", log_box=self.log_box)
        file_counts_map: list[BusFactorData] = []

        # All file in the current branch
        tracked_files = self._repo_obj.git.ls_tree("-r", "--name-only", "HEAD").splitlines()

        for rel_path in tracked_files:
            if rel_path.endswith((".png", ".jpg", ".jpeg", ".gif", ".exe", ".dll", ".so", ".svg", ".log", ".ico")):
                continue

            try:
                abs_path = os.path.join(self._repo_obj.working_tree_dir, rel_path)
                bus_factor = BusFactorData(abs_path)
                self.__map_blame_file_into_bus_factor(bus_factor, authors)
                file_counts_map.append(bus_factor)

            except Exception as e:
                Logger.write_log(f"Error occurred while calculating code ownership for file {rel_path}: {e}", log_box=self.log_box, log_type=Logger.LogType.WARN)

        Logger.write_log("Code ownership successfully calculated", log_box=self.log_box)
        return file_counts_map

    def __map_blame_file_into_bus_factor(self, bus_factor: BusFactorData, authors: list[Author]) -> None:
        from collections import defaultdict
        authors_count = defaultdict(int)
        owners: list[FileOwner] = []

        rel_path = os.path.relpath(bus_factor.filepath, self._repo_obj.working_tree_dir).replace("\\", "/")

        Logger.write_log(f"calculating ownership for file: {rel_path}", log_box=self.log_box)

        try:
            result = self._repo_obj.git.blame("--line-porcelain", rel_path)
        except Exception as e:
            Logger.write_log(f"Git blame exited with error on file {rel_path}: {e}", log_box=self.log_box, log_type=Logger.LogType.WARN)
            return

        for line in result.splitlines():
            if line.startswith("author "):
                author_name = line[len("author "):].strip()
                authors_count[author_name] += 1

        for author_name, lines in authors_count.items():
            author_obj = Author.get_author_by_username(authors, author_name)

            if author_obj is None:
                Logger.write_log(f"Author '{author_name}' not found, ignored in {rel_path}", log_box=self.log_box, log_type=Logger.LogType.WARN)
                continue

            bus_factor.add_owner(FileOwner(author=author_obj, lines=lines))

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
        for commit in self._repo_obj.iter_commits(): # No filters!
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


    def __plot_all_stats(self, all_stats: list[AuthorStats], file_stats: list[FileStats], commits_stats: list[CommitStats], branches_stats: list[BranchStats], code_complexity: list[LizardData], bus_factor: list[BusFactorData]) -> None:
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
        csv_bus_factor = BusFactorData.to_csv_data_list(bus_factor) if self.report_config.bus_factor and bus_factor else ["No data available"]

        data_to_plot = Data(self.repo_name, self.period, authors_html, files_html, languages_html, commits_html, cumulative_commits_html, branches_html, cumulative_branches_html, csv_files, csv_branches, csv_code_complexity, csv_bus_factor)

        Logger.write_log("Generating dashboard file .html", log_box=self.log_box)
        Dashboard.generate_html_page(data_to_plot)

        Logger.write_log(message="Opening Dashboard", log_box=self.log_box)
        Dashboard.open_result_website()
