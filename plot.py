import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

class Plot:
    def __init__(self):
        pass

    def init_dataframe_authors(self, authors: list[str], commits: list[int], insertions: list[int], deletions: list[int], lines: list[int], files: list[int]):
        self.dataframe_authors = pd.DataFrame({
            "Authors": authors,
            "Commits": commits,
            "Insertions": insertions,
            "Deletions": deletions,
            "Lines": lines,
            "Files": files
        })

    def init_dataframe_files(self, files: list[str], changes: list[int]):
        self.dataframe_files = pd.DataFrame({
            "Files": files,
            "Changes": changes
        })

    def plot_authors_stats(self):
        fig = make_subplots(
            rows=3, cols=2,
            subplot_titles=(
                "Commits per Author", "Insertions per Author",
                "Deletions per Author", "Lines per Author",
                "Files per Author", ""
            )
        )

        fig.add_trace(go.Bar(x=self.dataframe_authors["Authors"], y=self.dataframe_authors["Commits"], name="Commits"), row=1, col=1)
        fig.add_trace(go.Bar(x=self.dataframe_authors["Authors"], y=self.dataframe_authors["Insertions"], name="Insertions"), row=1, col=2)
        fig.add_trace(go.Bar(x=self.dataframe_authors["Authors"], y=self.dataframe_authors["Deletions"], name="Deletions"), row=2, col=1)
        fig.add_trace(go.Bar(x=self.dataframe_authors["Authors"], y=self.dataframe_authors["Lines"], name="Lines"), row=2, col=2)
        fig.add_trace(go.Bar(x=self.dataframe_authors["Authors"], y=self.dataframe_authors["Files"], name="Files"), row=3, col=1)

        fig.update_layout(
            title_text="Repo Statistics",
            height=1400,
            width=1800,
            margin=dict(l=50, r=50, t=100, b=50)
        )
        fig.show(renderer="browser")

    def plot_files_stats(self):
        fig = make_subplots(
            rows=1, cols=1,
            subplot_titles=(
                "Changes Count", "Files"
            )
        )

        fig.add_trace(go.Bar(x=self.dataframe_files["Files"], y=self.dataframe_files["Changes"], name="Changes"), row=1, col=1)

        fig.update_layout(
            title_text="Repo Statistics"
        )
        fig.show(renderer="browser")

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

        fig.add_trace(go.Bar(x=self.dataframe_authors["Authors"], y=self.dataframe_authors["Commits"], name="Commits"), row=1, col=1)
        fig.add_trace(go.Bar(x=self.dataframe_authors["Authors"], y=self.dataframe_authors["Insertions"], name="Insertions"), row=1, col=2)
        fig.add_trace(go.Bar(x=self.dataframe_authors["Authors"], y=self.dataframe_authors["Deletions"], name="Deletions"), row=2, col=1)
        fig.add_trace(go.Bar(x=self.dataframe_authors["Authors"], y=self.dataframe_authors["Lines"], name="Lines"), row=2, col=2)
        fig.add_trace(go.Bar(x=self.dataframe_authors["Authors"], y=self.dataframe_authors["Files"], name="Files"), row=3, col=1)

        fig.update_layout(
            margin=dict(l=100, r=100, t=100, b=100),
            height=1400,
            width=1800
        )

        return fig.to_html(full_html=False, include_plotlyjs='cdn')

    def get_files_html(self):
        fig = make_subplots(rows=1, cols=1, subplot_titles=("Changes Count", "Files"))
        fig.add_trace(go.Bar(x=self.dataframe_files["Files"], y=self.dataframe_files["Changes"], name="Changes"), row=1, col=1)
        return fig.to_html(full_html=False, include_plotlyjs=False)
