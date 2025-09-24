from git import Repo
from dashboard import Dashboard
from entities.commit_stats import CommitStats
from logger import Logger
from plot import Plot

from entities.author_stats import AuthorStats
from entities.file_stats import FileStats
from entities.branch_stats import BranchStats

class RepoManagement:

    def __init__(self, repo_path: str, log_box):
        self._repo_obj = Repo(repo_path)
        self.log_box = log_box
        self.repo_name = self.__get_repo_name_from_path(repo_path)

    def __get_repo_name_from_path(self, repo_path) -> str:
        pos = 0
        for i in range(len(repo_path)-1, 0, -1):
            if repo_path[i]!='\\':
                pos+=1
            else:
                break
        return repo_path[len(repo_path)-pos:]


    def obtain_all_info_from_repo(self) -> None:
        author_stats = self.__get_authors_stats_list()
        file_stats = self.__get_files_stats_list()
        commits_stats = self.__get_commits_stats_list()
        branches_stats = self.__get_branches_stats_list()

        self.__plot_all_stats(author_stats, file_stats, commits_stats, branches_stats)


    def __get_authors_stats_list(self) -> list[AuthorStats]:
        Logger.write_log("Getting authors stats list...", log_box=self.log_box)

        # to obtain only the unique author without duplications
        authors = {commit.author.name for commit in self._repo_obj.iter_commits()}

        stats = []
        for author in authors:
            Logger.write_log(f"Getting author stats for {author}", log_box=self.log_box)
            stats.append(self.__get_author_stats(author))

        Logger.write_log(f"Author stats list obtained ({len(stats)} authors)", log_box=self.log_box)
        return stats


    def __get_files_stats_list(self) -> list[FileStats]:
        Logger.write_log("Getting files stats list...", log_box=self.log_box)

        # to obtain only the unique file without duplications
        files = {file for commit in self._repo_obj.iter_commits() for file in commit.stats.files.keys()}

        stats: list[FileStats] = []
        for file in files:
            Logger.write_log(f"Getting file stats for {file}", log_box=self.log_box)
            stats.append(self.__get_file_stats(file))

        # remove files with 0 commits
        new_stats = []
        for stat in stats:
            if stat.changes != 0:
                new_stats.append(stat)
        stats = new_stats

        Logger.write_log(f"File stats list obtained ({len(stats)} files)", log_box=self.log_box)
        return stats

    def __get_commits_stats_list(self) -> list[CommitStats]:
        Logger.write_log("Getting commitss stats list...", log_box=self.log_box)

        commits = []
        for commit in self._repo_obj.iter_commits():
            Logger.write_log(f"Getting commit stats for {commit}", log_box=self.log_box)
            commits.append(CommitStats(commit, commit.author.name, len(commit.stats.files.keys()), commit.committed_datetime))

        return commits

    def __get_branches_stats_list(self):
        Logger.write_log("Getting branches stats list...", log_box=self.log_box)

        branches = []
        for branch in self._repo_obj.branches:
            Logger.write_log(f"Getting branch stats for {branch.name}", log_box=self.log_box)

            commit = branch.commit
            commit_count = sum(1 for _ in self._repo_obj.iter_commits(branch))

            branches.append(
                BranchStats(
                    branch.name,
                    commit.author.name if commit else "Unknown",
                    commit_count,
                    commit.committed_datetime if commit else None
                )
            )

        return branches

    # git log --author="<authorname>" --oneline --shortstat
    def __get_author_stats(self, author_name: str) -> AuthorStats:
        commits = insertions = deletions = lines = files = 0

        for commit in self._repo_obj.iter_commits(author=author_name):
            s = commit.stats.total
            commits += 1
            insertions += s.get('insertions', 0)
            deletions += s.get('deletions', 0)
            lines += s.get('lines', 0)
            files += s.get('files', 0)

        author_name = author_name.encode("utf-8", errors="replace").decode("utf-8")

        Logger.write_log(f"Author stat obtained: commits={commits}, insertions={insertions}, deletions={deletions}, lines={lines}, files={files}", log_box=self.log_box)
        return AuthorStats(author_name, commits, insertions, deletions, lines, files)


    def __get_file_stats(self, file_name: str) -> FileStats:
        changes = 0
        last_update = None
        last_author = ''

        for commit in self._repo_obj.iter_commits(paths=file_name):
            changes += 1
            if last_update is None or commit.committed_datetime > last_update:
                last_update = commit.committed_datetime
                last_author = commit.author.name

        return FileStats(file_name, changes, last_update, last_author)

    def __totals_values(self, all_stats: list[AuthorStats]) -> AuthorStats:
        Logger.write_log(f"Getting totals author stats", log_box=self.log_box)
        total_commits = 0
        total_insertions = 0
        total_deletions = 0
        total_lines = 0
        total_files = 0
        for stats in all_stats:
            total_commits += stats.commits
            total_insertions += stats.insertions
            total_deletions += stats.deletions
            total_files += stats.files
            total_lines += stats.lines

        # total author
        totals = AuthorStats('TOTAL', total_commits, total_insertions, total_deletions, total_lines, total_files)
        Logger.write_log(f"totals obtained: {totals}", log_box=self.log_box)
        return totals

    def __calculate_percentage_by_author(self, author_stats: AuthorStats, total_stats: AuthorStats) -> AuthorStats:
        commits_percentage = author_stats.commits / total_stats.commits * 100
        insertions_percentage = author_stats.insertions / total_stats.insertions * 100
        deletions_percentage = author_stats.deletions / total_stats.deletions * 100
        lines_percentage = author_stats.lines / total_stats.lines * 100
        files_percentage = author_stats.files / total_stats.files * 100
        return AuthorStats(author_stats.name, commits_percentage, insertions_percentage, deletions_percentage, lines_percentage, files_percentage)

    def __get_totals_and_percents_per_author(self, all_stats: list[AuthorStats]):
        totals = self.__totals_values(all_stats)
        stats_percentage = []
        for stats in all_stats:
            stat_percentage = self.__calculate_percentage_by_author(stats, totals)
            stats_percentage.append(stat_percentage)

        for stat in stats_percentage:
            print(f"name: {stat.name}, "
                f"commits: {stat.commits:.4f}%, "
                f"insertions: {stat.insertions:.4f}%, "
                f"deletions: {stat.deletions:.4f}%, "
                f"lines: {stat.lines:.4f}%, "
                f"files: {stat.files:.4f}%")

    def __plot_all_stats(self, all_stats: list[AuthorStats], file_stats: list[FileStats], commits_stats: list[CommitStats], branches_stats: list[BranchStats]) -> None:
        Logger.write_log("Preparing data for plotting", log_box=self.log_box)

        plot = Plot()
        plot.init_dataframe_authors(all_stats)
        plot.init_dataframe_files(file_stats)
        plot.init_dataframe_commits(commits_stats)
        plot.init_dataframe_branches(branches_stats)

        authors_html = plot.get_authors_html()
        files_html = plot.get_files_html()
        commits_html = plot.get_commits_html()
        comulative_commits_html = plot.get_commits_cumulative_html()
        branches_html = plot.get_branches_html()
        comulative_branches_html = plot.get_branches_cumulative_html()

        Logger.write_log("Generating dashboard file .html", log_box=self.log_box)
        Dashboard.generate_html_page(self.repo_name, authors_html, files_html, commits_html, comulative_commits_html, branches_html, comulative_branches_html, FileStats.to_csv_data_list(file_stats))

        Logger.write_log(message="Opening Dashboard", log_box=self.log_box)
        Dashboard.open_result_website()
