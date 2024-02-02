from dash import dcc, html
import plotly.graph_objects as go


class Scatterplot(html.Div):
    """
    A Div containing the dropdowns and figures for a specific scatter plot
    """
    def __init__(self, name, n_clicks, df):
        self.df = df

        # Equivalent to `html.Div([...])`
        super().__init__(
            id = {"type": "scatter-plot-card", "index": n_clicks},
            children=[
                dcc.Store(id={"type": "scatter-data-used", "index": n_clicks}, data=""),
                html.Div(
                    id={"type": "scatterplot-header", "index": n_clicks},
                    className="twelve columns",
                    children=[html.H6(name)],
                ),
                html.Div(
                    id={"type": "scatterplot-left-column", "index": n_clicks},
                    className="three columns",
                    children=[
                        html.Label("X-axis"),
                        dcc.Dropdown(
                            id={"type": "scatter-x-axis", "index": n_clicks},
                            options=[{"label": x, "value": x} for x in list(df.columns)],
                        ),
                        html.Label("Y-axis"),
                        dcc.Dropdown(
                            id={"type": "scatter-y-axis", "index": n_clicks},
                            options=[{"label": y, "value": y} for y in list(df.columns)],
                        ),
                        html.Label("Color seperation"),
                        dcc.Dropdown(
                            id={"type": "scatter-color", "index": n_clicks},
                            options=[{"label": c, "value": c} for c in list(df.columns)],
                        ),
                    ]
                ),
                html.Div(
                    id={"type": "scatter-plot-right-column", "index": n_clicks},
                    className="nine columns",
                    children=[dcc.Graph(id={"type": "scatter-plot", "index": n_clicks})]
                ),
            ],
        )
