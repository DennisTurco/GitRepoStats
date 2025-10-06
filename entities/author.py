from typing import Optional

class Author:
    def __init__(self, main_email: str, main_username: str, usernames: Optional[list[str]] = None, emails: Optional[list[str]] = None) -> None:
        self.main_email = main_email
        self.main_username = main_username
        self.usernames = usernames if usernames is not None else []
        self.emails = emails if emails is not None else [main_email]

    def __str__(self) -> str:
        return (f"main_email: {self.main_email}, username: {self.main_username}, "
                f"emails: {self.emails}, usernames: {self.usernames}")

    def get_pos_inside(self, authors: list["Author"]) -> int:
        for i in range(len(authors)):
            if self.main_email in authors[i].emails:
                return i
            if self.main_username.lower() == authors[i].main_username.lower():
                return i
        return -1

    def add_username_alias_if_not_saved(self, username: str) -> None:
        if username not in self.usernames:
            self.usernames.append(username)

    def add_email_if_not_saved(self, main_email: str) -> None:
        if main_email not in self.emails:
            self.emails.append(main_email)

    @staticmethod
    def get_author_by_username(authors: list["Author"], username: str):
        for author in authors:
            if author.main_username == username or username in author.usernames:
                return author
        return None
