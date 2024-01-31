from dash import dcc, html
import plotly.graph_objects as go


class Barplot(html.Div):
    def __init__(self, name, n_clicks, df):
        self.df = df

        # Equivalent to `html.Div([...])`
        super().__init__(
            id = {"type": "bar-plot-card", "index": n_clicks},
            children=[
                dcc.Store(id={"type": "bar-data-used", "index": n_clicks}, data=""),
                html.Div(
                    id={"type": "barplot-header", "index": n_clicks},
                    className="twelve columns",
                    children=[html.H6(name)],
                ),
                html.Div(
                    id={"type": "barplot-left-column", "index": n_clicks},
                    className="three columns",
                    children=[
                        html.Label("X-axis"),
                        dcc.Dropdown(
                            id={"type": "bar-x-axis", "index": n_clicks},
                            options=[{"label": x, "value": x} for x in list(df.columns)],
                        ),
                    ]
                ),
                html.Div(
                    id={"type": "bar-plot-right-column", "index": n_clicks},
                    className="nine columns",
                    children=[dcc.Graph(id={"type": "bar-plot", "index": n_clicks})]
                ),
            ],
        )
