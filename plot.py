import hashlib

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from entities.complexity_trend import ComplexityTrendData
from entities.data_overview import OverviewData
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

    def init_dataframe_complexity_trend(self, complexity_trend: list[ComplexityTrendData]):
        self.complexity_trend = complexity_trend


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
        extensions = sorted(
            {
                ext
                for s in self.author_stats
                for metric in METRICS
                for ext in getattr(s, metric).per_extension.keys()
            },
            reverse=False,
        )

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
                        y=[getattr(s, attr).per_extension.get(ext, 0) for s in stats],
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
        dataframe_files = pd.DataFrame(
            {
                "Files": [s.name for s in self.file_stats],
                "Changes": [s.changes for s in self.file_stats],
            }
        )
        fig.add_trace(
            go.Bar(x=dataframe_files["Files"], y=dataframe_files["Changes"], name="Changes"),
            row=1,
            col=1,
        )
        return fig.to_html(full_html=False, include_plotlyjs=False)

    def get_languages_chart(self):
        df_lang = pd.DataFrame({"Language": [s.file_language for s in self.file_stats]})

        lang_counts = (
            df_lang.value_counts()
            .reset_index(name="Count")
            .rename(columns={"Language": "Language"})
            .head(20)
        )

        fig = go.Figure(
            data=[go.Pie(labels=lang_counts["Language"], values=lang_counts["Count"], hole=0.3)]
        )
        fig.update_layout(title="Top 20 Languages")
        return fig.to_html(full_html=False, include_plotlyjs=False)

    def get_commits_html(self):
        df = pd.DataFrame(
            {
                "Author": [s.author.main_username for s in self.commit_stats],
                "Date": [pd.to_datetime(s.date) for s in self.commit_stats],  # parsing date
                "Commit": [s.name for s in self.commit_stats],
            }
        )

        commits_per_day = df.groupby(["Author", "Date"]).size().reset_index(name="CommitCount")

        commits_per_day = commits_per_day.sort_values(by="Date")

        fig = go.Figure()

        for author, data in commits_per_day.groupby("Author"):
            fig.add_trace(
                go.Scatter(x=data["Date"], y=data["CommitCount"], mode="lines+markers", name=author)
            )

        fig.update_layout(
            title="Commits by author over time",
            xaxis_title="Date",
            yaxis_title="Commits",
            template="plotly_white",
            autosize=True,
            width=None,
            height=600,
            margin=dict(l=50, r=50, t=80, b=50),
        )

        return fig.to_html(full_html=False, include_plotlyjs=False)

    def get_commits_cumulative_html(self):
        df = pd.DataFrame(
            {
                "Author": [s.author.main_username for s in self.commit_stats],
                "Date": [pd.to_datetime(s.date) for s in self.commit_stats],
                "Commit": [s.name for s in self.commit_stats],
            }
        )

        commits_per_day = df.groupby(["Author", "Date"]).size().reset_index(name="CommitCount")

        commits_per_day = commits_per_day.sort_values(by="Date")

        fig = go.Figure()

        for author, data in commits_per_day.groupby("Author"):
            data = data.sort_values(by="Date")
            data["CumulativeCommits"] = data["CommitCount"].cumsum()

            fig.add_trace(
                go.Scatter(
                    x=data["Date"], y=data["CumulativeCommits"], mode="lines+markers", name=author
                )
            )

        total_data = commits_per_day.groupby("Date")["CommitCount"].sum().sort_index().cumsum()
        fig.add_trace(
            go.Scatter(
                x=total_data.index,
                y=total_data.values,
                mode="lines",
                name="Total Commits",
                line=dict(color="black", dash="dot"),
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
            margin=dict(l=50, r=50, t=80, b=50),
        )

        return fig.to_html(full_html=False, include_plotlyjs=False)

    def get_branches_html(self):
        df = pd.DataFrame(
            {
                "Author": [s.author.main_username for s in self.branch_stats],
                "Date": [pd.to_datetime(s.date) for s in self.branch_stats],  # parsing date
                "Branch": [s.name for s in self.branch_stats],
            }
        )

        branches_per_day = df.groupby(["Author", "Date"]).size().reset_index(name="BranchCount")

        branches_per_day = branches_per_day.sort_values(by="Date")

        fig = go.Figure()

        for author, data in branches_per_day.groupby("Author"):
            fig.add_trace(
                go.Scatter(x=data["Date"], y=data["BranchCount"], mode="lines+markers", name=author)
            )

        fig.update_layout(
            title="Branch by author over time",
            xaxis_title="Date",
            yaxis_title="Branch",
            template="plotly_white",
            autosize=True,
            width=None,
            height=600,
            margin=dict(l=50, r=50, t=80, b=50),
        )

        return fig.to_html(full_html=False, include_plotlyjs=False)

    def get_branches_cumulative_html(self):
        df = pd.DataFrame(
            {
                "Author": [s.author.main_username for s in self.branch_stats],
                "Date": [pd.to_datetime(s.date) for s in self.branch_stats],
                "Branch": [s.name for s in self.branch_stats],
            }
        )

        branches_per_day = df.groupby(["Author", "Date"]).size().reset_index(name="BranchCount")

        branches_per_day = branches_per_day.sort_values(by="Date")

        fig = go.Figure()

        for author, data in branches_per_day.groupby("Author"):
            data = data.sort_values(by="Date")
            data["CumulativeBranches"] = data["BranchCount"].cumsum()

            fig.add_trace(
                go.Scatter(
                    x=data["Date"], y=data["CumulativeBranches"], mode="lines+markers", name=author
                )
            )

        total_data = branches_per_day.groupby("Date")["BranchCount"].sum().sort_index().cumsum()
        fig.add_trace(
            go.Scatter(
                x=total_data.index,
                y=total_data.values,
                mode="lines",
                name="Total Branches",
                line=dict(color="black", dash="dot"),
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
            margin=dict(l=50, r=50, t=80, b=50),
        )

        return fig.to_html(full_html=False, include_plotlyjs=False)

    def get_complexity_trend_html(self):
        df = pd.DataFrame({
            'Period': [t.period for t in self.complexity_trend],
            'Date': [pd.to_datetime(t.date) for t in self.complexity_trend],
            'Avg CCN': [t.avg_ccn for t in self.complexity_trend],
            'Avg NLOC': [t.avg_nloc for t in self.complexity_trend],
            'Avg Token': [t.avg_token for t in self.complexity_trend],
            'Function Count': [t.function_count for t in self.complexity_trend],
        })

        df = df.sort_values('Date')

        fig = go.Figure()

        # Main line: Average CCN (Cyclomatic Complexity)
        fig.add_trace(
            go.Scatter(
                x=df['Date'],
                y=df['Avg CCN'],
                mode='lines+markers',
                name='Avg CCN',
                line=dict(color='#d62728', width=3),
                marker=dict(size=8),
            )
        )

        # Secondary axis: Average NLOC
        fig.add_trace(
            go.Scatter(
                x=df['Date'],
                y=df['Avg NLOC'],
                mode='lines+markers',
                name='Avg NLOC',
                line=dict(color='#1f77b4', width=2, dash='dash'),
                marker=dict(size=6),
                yaxis='y2',
            )
        )

        # Calculate and add trend line (CCN)
        if len(df) > 1:
            z = np.polyfit(range(len(df)), df['Avg CCN'].values, 1)
            p = np.poly1d(z)
            trend_line = p(range(len(df)))

            fig.add_trace(
                go.Scatter(
                    x=df['Date'],
                    y=trend_line,
                    mode='lines',
                    name='CCN Trend',
                    line=dict(color='rgba(214, 39, 40, 0.3)', width=2, dash='dot'),
                )
            )

        fig.update_layout(
            title='Cyclomatic Complexity Evolution Over Time',
            xaxis_title='Date',
            yaxis_title='Average Cyclomatic Complexity (CCN)',
            yaxis2=dict(
                title='Average Lines of Code (NLOC)',
                overlaying='y',
                side='right',
            ),
            template='plotly_white',
            autosize=True,
            width=None,
            height=600,
            margin=dict(l=50, r=80, t=80, b=50),
            hovermode='x unified',
            legend=dict(x=0.01, y=0.99),
        )

        return fig.to_html(full_html=False, include_plotlyjs=False)

    def get_overview_html(self, overview: OverviewData) -> str:

        def value(v):
            return v if v is not None else "N/A"

        cards = [
            {
                "title": "Commits",
                "value": value(overview.commits),
                "icon": "📦",
                "desc": "Total number of commits in the selected period.",
            },
            {
                "title": "Last Commit",
                "value": value(overview.last_commit),
                "icon": "📅",
                "desc": "Last commit in the selected period.",
            },
            {
                "title": "Branches",
                "value": value(overview.branches),
                "icon": "🌿",
                "desc": "Branches created by contributors.",
            },
            {
                "title": "Authors",
                "value": value(overview.authors),
                "icon": "👨‍💻",
                "desc": "Contributors active in this repository.",
            },
            {
                "title": "Files",
                "value": value(overview.files),
                "icon": "📁",
                "desc": "Total files in this repository.",
            },
            # {
            #     "title": "Code Duplication",
            #     "value": f"{overview.duplication_percentage:.2f}%"
            #     if overview.duplication_percentage is not None
            #     else "N/A",
            #     "icon": "🧬",
            #     "desc": "Percentage of duplicated code blocks.",
            # },
            {
                "title": "Avg Complexity",
                "value": f"{overview.complexity_avg:.2f}"
                if overview.complexity_avg is not None
                else "N/A",
                "icon": "📈",
                "desc": "Average cyclomatic complexity of functions.",
            },
        ]

        cards_html = ""

        for c in cards:
            cards_html += f"""
            <div class="overview-card">
                <div class="overview-icon">{c['icon']}</div>
                <div class="overview-title">{c['title']}</div>
                <div class="overview-value">{c['value']}</div>
                <div class="overview-desc">{c['desc']}</div>
            </div>
            """

        html = f"""
            <style>

            .overview-container {{
                display: grid;
                grid-template-columns: repeat(3, 1fr);
                gap: 22px;
                margin: 40px 0;
                font-family: Arial, sans-serif;
            }}

            /* Tablet */
            @media (max-width: 1100px) {{
                .overview-container {{
                    grid-template-columns: repeat(2, 1fr);
                }}
            }}

            /* Mobile */
            @media (max-width: 700px) {{
                .overview-container {{
                    grid-template-columns: 1fr;
                }}
            }}

            .overview-card {{
                background: white;
                border-radius: 14px;
                padding: 28px;
                box-shadow: 0 6px 18px rgba(0,0,0,0.08);
                transition: all 0.25s ease;
            }}

            .overview-card:hover {{
                transform: translateY(-6px);
                box-shadow: 0 10px 28px rgba(0,0,0,0.15);
            }}

            .overview-icon {{
                font-size: 34px;
                margin-bottom: 10px;
            }}

            .overview-title {{
                font-size: 13px;
                font-weight: bold;
                color: #888;
                letter-spacing: 1px;
                text-transform: uppercase;
            }}

            .overview-value {{
                font-size: 34px;
                font-weight: 700;
                margin: 8px 0;
                color: #111;
            }}

            .overview-desc {{
                font-size: 13px;
                color: #666;
                line-height: 1.4em;
            }}

            </style>

            <div class="overview-container">
                {cards_html}
            </div>
            """

        return html