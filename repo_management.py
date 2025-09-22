from git import Repo
from entities.author_stats import Stats
from dashboard import Dashboard
from logger import Logger
from plot import Plot
from typing import Dict, Any

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
        file_info: Dict[str, Dict[str, Any]] = self.__get_info_per_file()

        for name, info in file_info.items():
            print(f"{name}, {info["changes"]}, {info["last_update"]}")

        authors = self.__get_authors_list()

        # # todo: only for test
        # authors = set(list(authors)[:5])

        all_stats: list[Stats] = []
        for author in authors:
            stats = self.__get_changed_statts_count_per_author(author)
            author_stats = Stats(author, stats.get('commits'), stats.get('insertions'), stats.get('deletions'), stats.get('lines'), stats.get('files'))
            all_stats.append(author_stats)

        self.__get_totals_and_percents_per_author(all_stats)

        self.__plot_all_stats(all_stats, file_info)


    def __get_authors_list(self):
        Logger.write_log("Getting authors list", log_box=self.log_box)
        authors = set() # to obtain only the unique author without duplications
        for commit in self._repo_obj.iter_commits():
            authors.add(commit.author.name)

        Logger.write_log(f"Stats list: {authors}", log_box=self.log_box)
        return authors

    # git log --name-only --pretty=format:""
    def __get_info_per_file(self)-> Dict[str, Dict[str, Any]]:
        Logger.write_log("Getting changes by file", log_box=self.log_box)
        file_info = {}
        for commit in self._repo_obj.iter_commits():
            for file in commit.stats.files:
                last_update = commit.committed_datetime
                last_author = commit.author.name
                if file not in file_info:
                    file_info[file] = {
                        "changes": 0,
                        "last_author": last_author,
                        "last_update": last_update
                    }
                file_info[file]["changes"] += 1

                if last_update > file_info[file]["last_update"]:
                    file_info[file]["last_update"] = last_update
                    file_info[file]["last_author"] = last_author

        return file_info

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

    def __get_totals_and_percents_per_author(self, all_stats: list[Stats]):
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

    def __plot_all_stats(self, all_stats: list[Stats], file_info: Dict[str, Dict[str, Any]]) -> None:
        Logger.write_log("Plotting data", log_box=self.log_box)
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

        Logger.write_log(f"=============== Files stats ===============", log_box=self.log_box)
        file_name = []
        changes_per_file = []
        last_update_per_file_csv = ["File,LastUpdate,LastEditor"]
        for key, value in file_info.items():
            file_name.append(key)
            count = value["changes"]
            changes_per_file.append(count)

            last_update = value["last_update"]
            last_author = value["last_author"]

            last_update_per_file_csv.append(f"{key},{last_update},{last_author}")
            Logger.write_log(f"File: {key}, Last Update: {last_update}, Last Author: {last_author}, Changed: {count} times", log_box=self.log_box)

        plot = Plot()
        plot.init_dataframe_authors(authors_list, commits_list, insertions_list, deletions_list, lines_list, files_list)
        plot.init_dataframe_files(file_name, changes_per_file)

        authors_html = plot.get_authors_html()
        files_html = plot.get_files_html()

        Logger.write_log("Generating dashboard file .html", log_box=self.log_box)
        Dashboard.generate_html_page(self.repo_name, authors_html, files_html, last_update_per_file_csv)

        Logger.write_log("Opening Dashboard", log_box=self.log_box)
        Dashboard.open_result_website()
