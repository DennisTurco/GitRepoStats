from git import Repo

class RepoManagement:

    def __init__(self, repo_path: str):
        self._repo_obj = Repo(repo_path)

    def obtain_all_info_from_repo(self) -> None:
        commit_count = self.__get_commit_count_per_author()
        file_count = self.__get_cout_per_file()
        print(commit_count)
        print(file_count)

    # git shortlog -s -n
    def __get_commit_count_per_author(self) -> dict[str, int]:
        author_counts = {}
        for commit in self._repo_obj.iter_commits():
            name = commit.author.name
            author_counts[name] = author_counts.get(name, 0) + 1

        return author_counts

    # git log --name-only --pretty=format:""
    def __get_cout_per_file(self)-> dict[str, int]:
        file_counts = {}
        for commit in self._repo_obj.iter_commits():
            for file in commit.stats.files:
                file_counts[file] = file_counts.get(file, 0) + 1
        return file_counts

    def __get_changed_lines_count_per_author(self, ):
        lines_changed = {}
        for commit in self._repo_obj.iter_commits():
            print(commit)