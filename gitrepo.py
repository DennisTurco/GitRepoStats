from repo_management import RepoManagement

if __name__ == "__main__":
    repo_path = r"C:\Users\Utente\Desktop\Dennis\Programmazione\clean-code-summary"
    repo = RepoManagement(repo_path)
    repo.obtain_all_info_from_repo()