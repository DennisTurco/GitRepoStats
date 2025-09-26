from git import Repo
from dashboard import Dashboard
from entities.author import Author
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
        # to obtain only the unique author without duplications
        authors = self.__get_authors()

        author_stats = self.__get_authors_stats_list(authors)
        file_stats = self.__get_files_stats_list(authors)
        commits_stats = self.__get_commits_stats_list(authors)
        branches_stats = self.__get_branches_stats_list(authors)

        self.__plot_all_stats(author_stats, file_stats, commits_stats, branches_stats)


    def __get_authors_stats_list(self, authors: list[Author]) -> list[AuthorStats]:
        Logger.write_log("Getting authors stats list...", log_box=self.log_box)

        stats = []
        for author in authors:
            Logger.write_log(f"Getting author stats for {author.main_username}", log_box=self.log_box)
            stats.append(self.__get_author_stats(author))

        Logger.write_log(f"Author stats list obtained ({len(stats)} authors)", log_box=self.log_box)
        return stats

    def __get_authors(self) -> list[Author]:
        Logger.write_log("Getting authors...", log_box=self.log_box)

        authors: list[Author] = []

        for commit in self._repo_obj.iter_commits():
            email = commit.author.email.lower()
            name = commit.author.name.strip()
            new_author = Author(email, name)

            pos = new_author.get_pos_inside(authors)

            if pos != -1:
                authors[pos].add_email_if_not_saved(email)
                authors[pos].add_username_alias_if_not_saved(name)
            else:
                authors.append(new_author)

        return authors


    def __get_files_stats_list(self, authors: list[Author]) -> list[FileStats]:
        Logger.write_log("Getting files stats list...", log_box=self.log_box)

        files = {file for commit in self._repo_obj.iter_commits() for file in commit.stats.files.keys()}

        stats: list[FileStats] = []
        for file in files:
            Logger.write_log(f"Getting file stats for {file}", log_box=self.log_box)
            stats.append(self.__get_file_stats(file, authors))

        # rimuovi file senza modifiche
        stats = [stat for stat in stats if stat.changes != 0]

        Logger.write_log(f"File stats list obtained ({len(stats)} files)", log_box=self.log_box)
        return stats

    def __get_commits_stats_list(self, authors: list[Author]) -> list[CommitStats]:
        Logger.write_log("Getting commits stats list...", log_box=self.log_box)

        commits_stats = []
        for commit in self._repo_obj.iter_commits():
            Logger.write_log(f"Getting commit stats for {commit.hexsha}", log_box=self.log_box)

            author = self.__find_author(commit.author.email, authors)
            commits_stats.append(
                CommitStats(commit, author, len(commit.stats.files.keys()), commit.committed_datetime)
            )

        return commits_stats

    def __get_branches_stats_list(self, authors: list[Author]):
        Logger.write_log("Getting ALL branches (local + remote)...", log_box=self.log_box)

        branches = []

        self._repo_obj.remotes.origin.fetch()

        for ref in self._repo_obj.refs:
            if ref.name.startswith("origin/") or ref in self._repo_obj.branches:
                Logger.write_log(f"Getting branch stats for {ref.name}", log_box=self.log_box)

                commit = ref.commit
                commit_count = sum(1 for _ in self._repo_obj.iter_commits(ref))

                author_obj = self.__find_author(commit.author.email if commit else "", authors)

                branches.append(
                    BranchStats(
                        ref.name,
                        author_obj,
                        commit_count,
                        commit.committed_datetime if commit else None
                    )
                )

        return branches


    # git log --author="<authorname>" --oneline --shortstat
    def __get_author_stats(self, author: Author) -> AuthorStats:
        commits = insertions = deletions = lines = files = 0

        for email in author.emails:
            for commit in self._repo_obj.iter_commits(author=email):
                s = commit.stats.total
                commits += 1
                insertions += s.get('insertions', 0)
                deletions += s.get('deletions', 0)
                lines += s.get('lines', 0)
                files += s.get('files', 0)

        author.main_username = author.main_username.encode("utf-8", errors="replace").decode("utf-8")

        Logger.write_log(f"Author stat obtained: commits={commits}, insertions={insertions}, deletions={deletions}, lines={lines}, files={files}", log_box=self.log_box)
        return AuthorStats(author, commits, insertions, deletions, lines, files)


    def __get_file_stats(self, file_name: str, authors: list[Author]) -> FileStats:
        changes = 0
        last_update = None
        last_author = None

        for commit in self._repo_obj.iter_commits(paths=file_name):
            changes += 1
            if last_update is None or commit.committed_datetime > last_update:
                last_update = commit.committed_datetime

                last_author = self.__find_author(commit.author.email, authors)

        return FileStats(file_name, changes, last_update, last_author)

    def __find_author(self, email: str, authors: list[Author]) -> Author:
        email = email.lower()
        for author in authors:
            if email in author.emails:
                return author
        return Author(email, "Unknown")


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
