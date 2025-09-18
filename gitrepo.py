from repo_management import RepoManagement
from logger import Logger

if __name__ == "__main__":
    Logger.write_log("Program started")
    # repo_path = r"C:\Users\Utente\Desktop\Dennis\Programmazione\clean-code-summary"
    repo_path = r"D:\Projects\ISTrust"
    repo = RepoManagement(repo_path)
    repo.obtain_all_info_from_repo()