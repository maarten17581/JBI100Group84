import base64
import io
import pandas as pd
from jbi100_app.main import app
from jbi100_app.views.menu import make_menu_layout
from jbi100_app.views.scatterplot import Scatterplot

from dash import html, dcc
import dash
import plotly.express as px
from dash.dependencies import Input, Output, State


if __name__ == '__main__':

    app.layout = html.Div(
        id="app-container",
        children=[
            
            dcc.Store(id="stored-data", data=""),
            
            # Left column
            html.Div(
                id="left-column",
                className="three columns",
                children=make_menu_layout()
            ),

            # Right column
            html.Div(
                id="right-column",
                className="nine columns",
                children=[],
            ),
        ],
    )

    # Define interactions
    @app.callback(
        Output('right-column', 'children'),
        Input('add-plot-button', 'n_clicks'),
        State('right-column', 'children'),
    )
    def add_plot(n_clicks, children):
        if n_clicks:
            plot = Scatterplot("Scatterplot 1", 'sepal_length', 'sepal_width', df)
            children.append(plot)
            return children
        else:
            return children

    @app.callback(
        Output('add-plot-button', 'disabled'),
        Output('stored-data', 'data'),
        Output('upload-data-button', 'children'),
        Input('upload-data', 'contents'),
        State('upload-data', 'filename'),
        State('upload-data', 'last_modified'),
    )
    def upload_data(contents, filename, last_modified):
        # Check if data is uploaded
        print(filename)
        if contents is not None:
            content_type, content_string = contents.split(',')
            print("got here")
            decoded = base64.b64decode(content_string)
            try:
                if "csv" in filename:
                    print("saw this")
                    df = pd.read_csv(io.StringIO(decoded.decode("utf-8")), on_bad_lines='skip')
                else:
                    # Create popup
                    print("whut 1")
                    return dash.no_update, dash.no_update, dash.no_update
            except Exception as e:
                print(e)
                return dash.no_update, dash.no_update
            stored_data = df.to_json()
            print("got here in the end")
            return True, stored_data, filename

        return dash.no_update, dash.no_update, dash.no_update

    app.run_server(debug=False, dev_tools_ui=False)