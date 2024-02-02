from dash import dcc, html
import plotly.graph_objects as go


class Filter(html.Div):
    def __init__(self, filter_feature, comparator, value, n_clicks):
        # A filter object having the attribute, which comparator is used and what value it is compared to
        self.filter_feature = filter_feature
        self.comparator = comparator
        self.value = value

        # Equivalent to `html.Div([...])`
        super().__init__(
            className="twelve columns",
            children=[
                html.Div(
                    id={"type": "filter-container", "index": n_clicks},
                    className="twelve columns",
                    children=[html.Div(
                            id={"type": "filter-text-container", "index": n_clicks},
                            className="eight columns",
                            children=[html.H6(children=str(filter_feature)+" "+str(comparator)+" "+str(value), id={"type": "filter-text", "index": n_clicks})],
                        ),
                        html.Button("X", id={"type": "remove-filter", "index": n_clicks}),
                    ]
                )
            ],
        )
