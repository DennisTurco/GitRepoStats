import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from entities.author_stats import AuthorStats
from entities.branch_stats import BranchStats
from entities.commit_stats import CommitStats
from entities.file_stats import FileStats

class Plot:
    def __init__(self):
        pass

    def init_dataframe_authors(self, author_stats: list[AuthorStats]):
        self.author_stats = author_stats

    def init_dataframe_files(self, file_stats: list[FileStats]):
        self.file_stats = file_stats

    def init_dataframe_commits(self, commit_stats: list[CommitStats]):
        self.commit_stats = commit_stats

    def init_dataframe_branches(self, branch_stats: list[BranchStats]):
        self.branch_stats = branch_stats

    def get_authors_html(self):
        fig = make_subplots(
            rows=3, cols=2,
            subplot_titles=(
                "Commits per Author", "Insertions per Author",
                "Deletions per Author", "Lines per Author",
                "Files per Author", ""
            ),
            vertical_spacing=0.2,
            horizontal_spacing=0.1
        )

        AuthorStats.sort_by_commits(self.author_stats)
        dataframe_author_commits = pd.DataFrame({
            "Authors": [s.author.main_username for s in self.author_stats],
            "Commits": [s.commits for s in self.author_stats]
        })
        fig.add_trace(go.Bar(x=dataframe_author_commits["Authors"], y=dataframe_author_commits["Commits"], name="Commits"), row=1, col=1)

        AuthorStats.sort_by_insertions(self.author_stats)
        dataframe_author_insertions = pd.DataFrame({
            "Authors": [s.author.main_username for s in self.author_stats],
            "Insertions": [s.insertions for s in self.author_stats]
        })
        fig.add_trace(go.Bar(x=dataframe_author_insertions["Authors"], y=dataframe_author_insertions["Insertions"], name="Insertions"), row=1, col=2)

        AuthorStats.sort_by_deletions(self.author_stats)
        dataframe_author_deletions = pd.DataFrame({
            "Authors": [s.author.main_username for s in self.author_stats],
            "Deletions": [s.deletions for s in self.author_stats]
        })
        fig.add_trace(go.Bar(x=dataframe_author_deletions["Authors"], y=dataframe_author_deletions["Deletions"], name="Deletions"), row=2, col=1)

        AuthorStats.sort_by_lines(self.author_stats)
        dataframe_author_lines = pd.DataFrame({
            "Authors": [s.author.main_username for s in self.author_stats],
            "Lines": [s.lines for s in self.author_stats]
        })
        fig.add_trace(go.Bar(x=dataframe_author_lines["Authors"], y=dataframe_author_lines["Lines"], name="Lines"), row=2, col=2)

        AuthorStats.sort_by_files(self.author_stats)
        dataframe_author_files = pd.DataFrame({
            "Authors": [s.author.main_username for s in self.author_stats],
            "Files": [s.files for s in self.author_stats]
        })
        fig.add_trace(go.Bar(x=dataframe_author_files["Authors"], y=dataframe_author_files["Files"], name="Files"), row=3, col=1)

        fig.update_layout(
            margin=dict(l=100, r=100, t=100, b=100),
            height=1400,
            width=1800
        )

        return fig.to_html(full_html=False, include_plotlyjs='cdn')

    def get_files_html(self):
        fig = make_subplots(rows=1, cols=1, subplot_titles=("Changes Count", "Files"))

        FileStats.sort_by_changes(self.file_stats)
        dataframe_files = pd.DataFrame({
            "Files": [s.name for s in self.file_stats],
            "Changes": [s.changes for s in self.file_stats]
        })
        fig.add_trace(go.Bar(x=dataframe_files["Files"], y=dataframe_files["Changes"], name="Changes"), row=1, col=1)
        return fig.to_html(full_html=False, include_plotlyjs=False)

    def get_commits_html(self):
        df = pd.DataFrame({
            "Author": [s.author.main_username for s in self.commit_stats],
            "Date": [pd.to_datetime(s.date) for s in self.commit_stats],  # parsing date
            "Commit": [s.name for s in self.commit_stats]
        })

        commits_per_day = (
            df.groupby(["Author", "Date"])
            .size()
            .reset_index(name="CommitCount")
        )

        commits_per_day = commits_per_day.sort_values(by="Date")

        fig = go.Figure()

        for author, data in commits_per_day.groupby("Author"):
            fig.add_trace(
                go.Scatter(
                    x=data["Date"],
                    y=data["CommitCount"],
                    mode="lines+markers",
                    name=author
                )
            )

        fig.update_layout(
            title="Commits by author over time",
            xaxis_title="Date",
            yaxis_title="Commits",
            template="plotly_white",
            autosize=True,
            width=None,
            height=600,
            margin=dict(l=50, r=50, t=80, b=50)
        )

        return fig.to_html(full_html=False, include_plotlyjs=False)


    def get_commits_cumulative_html(self):
        df = pd.DataFrame({
            "Author": [s.author.main_username for s in self.commit_stats],
            "Date": [pd.to_datetime(s.date) for s in self.commit_stats],
            "Commit": [s.name for s in self.commit_stats]
        })

        commits_per_day = (
            df.groupby(["Author", "Date"])
            .size()
            .reset_index(name="CommitCount")
        )

        commits_per_day = commits_per_day.sort_values(by="Date")

        fig = go.Figure()

        for author, data in commits_per_day.groupby("Author"):
            data = data.sort_values(by="Date")
            data["CumulativeCommits"] = data["CommitCount"].cumsum()

            fig.add_trace(
                go.Scatter(
                    x=data["Date"],
                    y=data["CumulativeCommits"],
                    mode="lines+markers",
                    name=author
                )
            )

        total_data = commits_per_day.groupby("Date")["CommitCount"].sum().sort_index().cumsum()
        fig.add_trace(
            go.Scatter(
                x=total_data.index,
                y=total_data.values,
                mode="lines",
                name="Total Commits",
                line=dict(color="black", dash="dot")
            )
        )

        fig.update_layout(
            title="Cumulative Commits Over Time",
            xaxis_title="Date",
            yaxis_title="Cumulative Commits",
            template="plotly_white",
            autosize=True,
            width=None,
            height=600,
            margin=dict(l=50, r=50, t=80, b=50)
        )

        return fig.to_html(full_html=False, include_plotlyjs=False)


    def get_branches_html(self):
        df = pd.DataFrame({
            "Author": [s.author.main_username for s in self.branch_stats],
            "Date": [pd.to_datetime(s.date) for s in self.branch_stats],  # parsing date
            "Branch": [s.name for s in self.branch_stats]
        })

        branches_per_day = (
            df.groupby(["Author", "Date"])
            .size()
            .reset_index(name="BranchCount")
        )

        branches_per_day = branches_per_day.sort_values(by="Date")

        fig = go.Figure()

        for author, data in branches_per_day.groupby("Author"):
            fig.add_trace(
                go.Scatter(
                    x=data["Date"],
                    y=data["BranchCount"],
                    mode="lines+markers",
                    name=author
                )
            )

        fig.update_layout(
            title="Branch by author over time",
            xaxis_title="Date",
            yaxis_title="Branch",
            template="plotly_white",
            autosize=True,
            width=None,
            height=600,
            margin=dict(l=50, r=50, t=80, b=50)
        )

        return fig.to_html(full_html=False, include_plotlyjs=False)


    def get_branches_cumulative_html(self):
        df = pd.DataFrame({
            "Author": [s.author.main_username for s in self.branch_stats],
            "Date": [pd.to_datetime(s.date) for s in self.branch_stats],
            "Branch": [s.name for s in self.branch_stats]
        })

        branches_per_day = (
            df.groupby(["Author", "Date"])
            .size()
            .reset_index(name="BranchCount")
        )

        branches_per_day = branches_per_day.sort_values(by="Date")

        fig = go.Figure()

        for author, data in branches_per_day.groupby("Author"):
            data = data.sort_values(by="Date")
            data["CumulativeBranches"] = data["BranchCount"].cumsum()

            fig.add_trace(
                go.Scatter(
                    x=data["Date"],
                    y=data["CumulativeBranches"],
                    mode="lines+markers",
                    name=author
                )
            )

        total_data = branches_per_day.groupby("Date")["BranchCount"].sum().sort_index().cumsum()
        fig.add_trace(
            go.Scatter(
                x=total_data.index,
                y=total_data.values,
                mode="lines",
                name="Total Branches",
                line=dict(color="black", dash="dot")
            )
        )

        fig.update_layout(
            title="Cumulative Branches Over Time",
            xaxis_title="Date",
            yaxis_title="Cumulative Branches",
            template="plotly_white",
            autosize=True,
            width=None,
            height=600,
            margin=dict(l=50, r=50, t=80, b=50)
        )

        return fig.to_html(full_html=False, include_plotlyjs=False)

