from dash import dcc, html
from ..config import color_list1, color_list2


def generate_description_card():
    """

    :return: A Div containing dashboard title & descriptions.
    """
    return html.Div(
        id="description-card",
        children=[
            html.H5("CreditVis"),
            html.Div(
                id="intro",
                children="Upload your credit data below and start visualizing!",
            ),
            html.Div(
                id="makers",
                children="By group 84 for the course JBI100, with members Maarten Dankers, Wout Heijne and Ties Hustinx",
            ),
        ],
    )
    
def generate_database_button():
    return dcc.Upload(
                id="upload-data",
                className="twelve columns",
                children=[html.Div(
                        html.Button(children="Upload Data", id="upload-data-button", className="twelve columns"),
                    )],
                multiple=False,
            )

def generate_filter():
    return html.Div(
        id="generate-filter",
        children=[
            html.Label("Select Filter"),
            html.Div(
                id="filter-container",
                children=[html.Div(
                        id="feature-filter",
                        className="ten columns",
                        children=[dcc.Dropdown(
                            id="select-filter-feature",
                            options=[],
                        ),]
                    ),
                    html.Div(
                        id="comparator-filter",
                        className="two columns",
                        children=[dcc.Dropdown(
                            id="select-filter-comparator",
                            options=[{"label": "=", "value": "="},{"label": "≠", "value": "≠"},{"label": "≥", "value": "≥"},{"label": "≤", "value": "≤"},{"label": ">", "value": ">"},{"label": "<", "value": "<"}],
                            value="=",
                        ),]
                    ),
                    html.Br(),
                    html.Br(),
                    html.Div(
                        id="value-filter",
                        className="ten columns",
                        children=[dcc.Input(id='select-filter-value', className="twelve columns", type='text', value="0")]
                    ),
                    html.Div(
                        id="add-filter",
                        className="two columns",
                        children=[html.Button("Add", style={"textAlign": "float-center"}, id="add-filter-button", className="twelve columns")]
                    ),
                    html.Div(
                        id="filter-elements",
                        className="twelve columns",
                        children=[]
                    )
                ]
            ),
            html.Div(
                id="filter-card-container",
                className="twelve columns",
                children=[],
            ),
        ], style={"textAlign": "float-left"}
    )

def generate_control_card():
    """

    :return: A Div containing controls for graphs.
    """
    return html.Div(
        id="control-card",
        children=[
            html.Label("Add Plot"),
            html.Div(
                id="add-plot-container",
                className="twelve columns",
                children=[dcc.Dropdown(
                    id="add-plot-dropdown",
                    options=[{"label": "Scatterplot", "value": "Scatterplot"},{"label": "Lineplot", "value": "Lineplot"},{"label": "Barplot", "value": "Barplot"},],
                    value="Scatterplot",
                ),]
            ),
            html.Button("Add Plot", id="add-plot-button", disabled=True),
        ], style={"textAlign": "float-left"}
    )


def make_menu_layout():
    return [generate_description_card(), generate_database_button(), generate_filter(), generate_control_card()]
