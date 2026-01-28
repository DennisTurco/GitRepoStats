import hashlib
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from entities.stats.author_stats import AuthorStats
from entities.stats.branch_stats import BranchStats
from entities.stats.commit_stats import CommitStats
from entities.stats.file_stats import FileStats

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
        import plotly.graph_objects as go
        from plotly.subplots import make_subplots

        # ──────────────────────
        # CONFIG
        # ──────────────────────
        COLOR_MAP = {
            ".py": "#3572A5",
            ".js": "#f1e05a",
            ".ts": "#2b7489",
            ".md": "#083fa1",
            ".json": "#292929",
            ".yml": "#cb171e",
        }

        METRICS = {
            "insertions": lambda s: s.insertions.total,
            "deletions": lambda s: s.deletions.total,
            "lines": lambda s: s.lines.total,
            "files": lambda s: s.files.total,
        }

        # ──────────────────────
        # FIGURE
        # ──────────────────────
        fig = make_subplots(
            rows=3,
            cols=2,
            subplot_titles=(
                "Commits per Author",
                "Insertions per Author",
                "Deletions per Author",
                "Lines (insertions + deletions) per Author",
                "Files per Author",
                "",
            ),
            vertical_spacing=0.2,
            horizontal_spacing=0.1,
        )

        # ──────────────────────
        # GLOBAL EXTENSIONS (ONCE)
        # ──────────────────────
        extensions = sorted({
            ext
            for s in self.author_stats
            for metric in METRICS
            for ext in getattr(s, metric).per_extension.keys()
        }, reverse=False)

        # ──────────────────────
        # COMMITS
        # ──────────────────────
        commits_stats = sorted(
            self.author_stats,
            key=lambda s: s.commits,
            reverse=False,
        )

        authors_commits = [s.author.main_username for s in commits_stats]

        fig.add_trace(
            go.Bar(
                x=authors_commits,
                y=[s.commits for s in commits_stats],
                name="Commits",
                marker_color="#444",
            ),
            row=1,
            col=1,
        )

        def color_for_extension(ext: str) -> str:
            if ext in COLOR_MAP:
                return COLOR_MAP[ext]

            # colore deterministico da hash
            h = hashlib.md5(ext.encode()).hexdigest()
            return f"#{h[:6]}"

        # ──────────────────────
        # STACKED METRICS
        # ──────────────────────
        def add_stacked_metric(row, col, attr, sort_key):
            stats = sorted(self.author_stats, key=sort_key, reverse=False)
            authors = [s.author.main_username for s in stats]

            for ext in extensions:
                fig.add_trace(
                    go.Bar(
                        x=authors,
                        y=[
                            getattr(s, attr).per_extension.get(ext, 0)
                            for s in stats
                        ],
                        name=ext,
                        legendgroup=ext,
                        showlegend=(row == 1 and col == 2),
                        marker_color=color_for_extension(ext),
                    ),
                    row=row,
                    col=col,
                )

        positions = [(1, 2), (2, 1), (2, 2), (3, 1)]

        for (row, col), (attr, key) in zip(positions, METRICS.items()):
            add_stacked_metric(row, col, attr, key)

        # ──────────────────────
        # LAYOUT
        # ──────────────────────
        fig.update_layout(
            barmode="stack",
            legend=dict(
                groupclick="togglegroup",
                title="File extensions",
            ),
            margin=dict(l=100, r=120, t=100, b=100),
            height=1400,
            width=1800,
        )

        return fig.to_html(full_html=False, include_plotlyjs="cdn")



    def get_files_html(self):
        fig = make_subplots(rows=1, cols=1, subplot_titles=("Changes Count", "Files"))

        FileStats.sort_by_changes(self.file_stats)
        dataframe_files = pd.DataFrame({
            "Files": [s.name for s in self.file_stats],
            "Changes": [s.changes for s in self.file_stats]
        })
        fig.add_trace(go.Bar(x=dataframe_files["Files"], y=dataframe_files["Changes"], name="Changes"), row=1, col=1)
        return fig.to_html(full_html=False, include_plotlyjs=False)

    def get_languages_chart(self):
        df_lang = pd.DataFrame({
            "Language": [s.file_language for s in self.file_stats]
        })

        lang_counts = (
            df_lang.value_counts()
            .reset_index(name="Count")
            .rename(columns={"Language": "Language"})
            .head(20)
        )

        fig = go.Figure(
            data=[go.Pie(
                labels=lang_counts["Language"],
                values=lang_counts["Count"],
                hole=0.3
            )]
        )
        fig.update_layout(title="Top 20 Languages")
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

