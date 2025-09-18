from datetime import datetime, timedelta
from typing import Counter
from git import Repo
from author_stats import Stats
from logger import Logger
from plot import Plot

class RepoManagement:

    def __init__(self, repo_path: str, log_box):
        self._repo_obj = Repo(repo_path)
        self.log_box = log_box

    def obtain_all_info_from_repo(self) -> None:
        # file_count = self.__get_cout_per_file()
        # print(file_count)

        authors = self.__get_authors_list()

        # # todo: only for test
        # authors = set(list(authors)[:5])

        all_stats: list[Stats] = []
        for author in authors:
            stats = self.__get_changed_statts_count_per_author(author)
            author_stats = Stats(author, stats.get('commits'), stats.get('insertions'), stats.get('deletions'), stats.get('lines'), stats.get('files'))
            all_stats.append(author_stats)

        # totals and percents
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

        # data for plotting
        authors_list = []
        commits_list = []
        insertions_list = []
        deletions_list = []
        lines_list = []
        files_list = []
        for stats in all_stats:
            authors_list.append(stats.name)
            commits_list.append(stats.commits)
            insertions_list.append(stats.insertions)
            deletions_list.append(stats.deletions)
            lines_list.append(stats.lines)
            files_list.append(stats.files)

        plot = Plot(authors_list, commits_list, insertions_list, deletions_list, lines_list, files_list)
        plot.plot_all()

    def __get_authors_list(self):
        Logger.write_log("Getting authors list", log_box=self.log_box)
        authors = set() # to obtain only the unique author without duplications
        for commit in self._repo_obj.iter_commits():
            authors.add(commit.author.name)

        Logger.write_log(f"Stats list: {authors}", log_box=self.log_box)
        return authors

    # git log --name-only --pretty=format:""
    def __get_cout_per_file(self)-> dict[str, int]:
        file_counts = {}
        for commit in self._repo_obj.iter_commits():
            for file in commit.stats.files:
                file_counts[file] = file_counts.get(file, 0) + 1
        return file_counts

    # git log --author="<authorname>" --oneline --shortstat
    def __get_changed_statts_count_per_author(self, author_name: str):
        Logger.write_log(f"Getting author stats for {author_name}", log_box=self.log_box)
        author_stats = {'commits':0, 'insertions':0, 'deletions':0, 'lines':0, 'files':0}
        for commit in self._repo_obj.iter_commits(author=author_name):
            stats = commit.stats.total
            author_stats['commits'] += 1
            author_stats['insertions'] += stats.get('insertions', 0)
            author_stats['deletions'] += stats.get('deletions', 0)
            author_stats['lines'] += stats.get('lines', 0)
            author_stats['files'] += stats.get('files', 0)

        Logger.write_log(f"Stats obtained: {author_stats}", log_box=self.log_box)
        return author_stats

    def __totals_values(self, all_stats: list[Stats]) -> Stats:
        Logger.write_log(f"Getting totals stats", log_box=self.log_box)
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
        totals = Stats('TOTAL', total_commits, total_insertions, total_deletions, total_lines, total_files)
        Logger.write_log(f"totals obtained: {totals}", log_box=self.log_box)
        return totals

    def __calculate_percentage_by_author(self, author_stats: Stats, total_stats: Stats) -> Stats:
        commits_percentage = author_stats.commits / total_stats.commits * 100
        insertions_percentage = author_stats.insertions / total_stats.insertions * 100
        deletions_percentage = author_stats.deletions / total_stats.deletions * 100
        lines_percentage = author_stats.lines / total_stats.lines * 100
        files_percentage = author_stats.files / total_stats.files * 100
        return Stats(author_stats.name, commits_percentage, insertions_percentage, deletions_percentage, lines_percentage, files_percentage)