import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

class Plot:

    def __init__(self, authors: list[str], commits: list[int], insertions: list[int],
                 deletions: list[int], lines: list[int], files: list[int]):
        self.df = pd.DataFrame({
            "Authors": authors,
            "Commits": commits,
            "Insertions": insertions,
            "Deletions": deletions,
            "Lines": lines,
            "Files": files
        })

    def plot_all(self):
        fig = make_subplots(
            rows=3, cols=2,
            subplot_titles=(
                "Commits per Author", "Insertions per Author",
                "Deletions per Author", "Lines per Author",
                "Files per Author", ""
            )
        )

        fig.add_trace(go.Bar(x=self.df["Authors"], y=self.df["Commits"], name="Commits"), row=1, col=1)
        fig.add_trace(go.Bar(x=self.df["Authors"], y=self.df["Insertions"], name="Insertions"), row=1, col=2)
        fig.add_trace(go.Bar(x=self.df["Authors"], y=self.df["Deletions"], name="Deletions"), row=2, col=1)
        fig.add_trace(go.Bar(x=self.df["Authors"], y=self.df["Lines"], name="Lines"), row=2, col=2)
        fig.add_trace(go.Bar(x=self.df["Authors"], y=self.df["Files"], name="Files"), row=3, col=1)

        fig.update_layout(
            title_text="Repo Statistics",
            height=1400,
            width=1800,
            margin=dict(l=50, r=50, t=100, b=50)
        )
        fig.show()
