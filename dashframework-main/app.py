import base64
import io
from math import ceil
import pandas as pd
from jbi100_app.main import app
from jbi100_app.views.menu import make_menu_layout
from jbi100_app.views.scatterplot import Scatterplot
from jbi100_app.views.lineplot import Lineplot
from jbi100_app.views.barplot import Barplot
from jbi100_app.views.filter import Filter

from dash import html, dcc, ALL, MATCH
import dash
from dash_extensions.enrich import Output, Input, State
import plotly.graph_objects as go


if __name__ == '__main__':
    
    # The datatypes of all attributes in the data, to compare and filter out wrong data
    dtypelist = {
        'ID' : 'object', 'Customer_ID' : 'category', 'Month' : 'category',
        'Name': 'category', 'Age': 'int64', 'SSN' : 'object', 'Occupation' : 'category',
        'Annual_Income' : 'float64', 'Monthly_Inhand_Salary' : 'float64',
        'Num_Bank_Accounts' : 'int64', 'Num_Credit_Card' : 'int64', 'Interest_Rate' : 'int64',
        'Num_of_Loan' : 'int64', 'Type_of_Loan' : 'object', 'Delay_from_due_date' : 'int64',
        'Num_of_Delayed_Payment' : 'int64', 'Changed_Credit_Limit' : 'float64',
        'Num_Credit_Inquiries' : 'int64', 'Credit_Mix' : 'category', 'Outstanding_Debt' : 'float64',
        'Credit_Utilization_Ratio' : 'float64', 'Credit_History_Age' : 'object', 
        'Payment_of_Min_Amount' : 'category', 'Total_EMI_per_month' : 'float64',
        'Amount_invested_monthly' : 'float64', 'Payment_Behaviour' : 'category',
        'Monthly_Balance' : 'float64', 'Credit_Score' : 'category'
    }
    app.layout = html.Div(
        id="app-container",
        children=[
            # The main dataframe storing all data that is uploaded
            dcc.Store(id="stored-data", data=""),
            
            # The dataframe storing all data that is filtered on the main filters
            dcc.Store(id="filtered-data", data=""),
            
            # The dataframe storing all data that is selected in a figure
            dcc.Store(id="selected-data", data=""),
            
            # The id of the figure that is selected from to stop updating this one
            dcc.Store(id="selected-id", data=""),
            
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

    # Add plot button interaction
    # Adds a plot based on the type of plot in the dropdown
    @app.callback(
        Output('right-column', 'children'),
        Input('add-plot-button', 'n_clicks'),
        State('add-plot-dropdown', 'value'),
        State('right-column', 'children'),
        State('stored-data', 'data'),
        State('filtered-data', 'data'),
    )
    def add_plot(n_clicks, option_value, children, stored_data, filtered_data):
        print("add plot")
        if n_clicks:
            if filtered_data != "":
                df = pd.read_json(filtered_data)
            else:
                df = pd.read_json(stored_data)
            df = df.astype(dtypelist)
            if option_value == "Scatterplot":
                plot = Scatterplot("Scatterplot "+str(n_clicks), n_clicks, df)
                children.append(plot)
            elif option_value == "Lineplot":
                plot = Lineplot("Lineplot "+str(n_clicks), n_clicks, df)
                children.append(plot)
            elif option_value == "Barplot":
                plot = Barplot("Barplot "+str(n_clicks), n_clicks, df)
                children.append(plot)
            return children
        else:
            return dash.no_update
    
    # Updates a scatter plot if the attributes used for it change
    # or if the filtered or selected data from filters or selections changes
    @app.callback(
        Output({"type": "scatter-plot", "index": MATCH}, 'figure'),
        Output({"type": "scatter-data-used", "index": MATCH}, 'data'),
        Input({"type": "scatter-x-axis", "index": MATCH}, 'value'),
        Input({"type": "scatter-y-axis", "index": MATCH}, 'value'),
        Input({"type": "scatter-color", "index": MATCH}, 'value'),
        State({"type": "scatter-x-axis", "index": MATCH}, 'id'),
        State('stored-data', 'data'),
        Input('filtered-data', 'data'),
        Input('selected-data', 'data'),
        State('selected-id', 'data'),
    )
    def change_scatter_plot(x_axis, y_axis, color, id, stored_data, filtered_data, selected_data, selected_id):
        print(str(id['index']))
        print(str(selected_id))
        print((str(id['index']) != str(selected_id)))
        if x_axis is not None and y_axis is not None and str(id['index']) != str(selected_id):
            print("update plot")
            if filtered_data != "" and selected_data != "":
                df1 = pd.read_json(filtered_data)
                df2 = pd.read_json(selected_data)
                df1 = df1.astype(dtypelist)
                df2 = df2.astype(dtypelist)
                df = pd.merge(df1, df2)
            elif filtered_data != "":
                df = pd.read_json(filtered_data)
            elif selected_data != "":
                df = pd.read_json(selected_data)
            else:
                df = pd.read_json(stored_data)
            df = df.astype(dtypelist)
            dfstring = ""
            if color != None:
                if df[color].dtype.name == 'int64' or df[color].dtype.name == 'float64':
                    start = df[color].min()
                    bucketrange = df[color].max()-df[color].min()
                    step = (bucketrange)**(0.5)
                    for i in range(ceil(bucketrange/step)):
                        df_step = df[(df[color] >= i*step+start) & (df[color] < (i+1)*step+start)]
                        dfstring = dfstring + df_step.to_json() + "#####"
                if df[color].dtype.name == 'object' or df[color].dtype.name == 'category':
                    categories = df[color].unique()
                    for cat in categories:
                        df_step = df[df[color] == cat]
                        dfstring = dfstring + df_step.to_json() + "#####"
            else:
                dfstring = df.to_json() + "#####"
            return update_scatter(color, x_axis, y_axis, df), dfstring
        else:
            return dash.no_update, dash.no_update
    
    # Updates a line plot if the attributes used for it change
    # or if the filtered or selected data from filters or selections changes
    @app.callback(
        Output({"type": "line-plot", "index": MATCH}, 'figure'),
        Output({"type": "line-data-used", "index": MATCH}, 'data'),
        Input({"type": "line-x-axis", "index": MATCH}, 'value'),
        Input({"type": "line-y-axis", "index": MATCH}, 'value'),
        Input({"type": "line-color", "index": MATCH}, 'value'),
        State({"type": "line-x-axis", "index": MATCH}, 'id'),
        State('stored-data', 'data'),
        Input('filtered-data', 'data'),
        Input('selected-data', 'data'),
        State('selected-id', 'data'),
    )
    def change_line_plot(x_axis, y_axis, color, id, stored_data, filtered_data, selected_data, selected_id):
        print(str(id['index']))
        print(str(selected_id))
        print((str(id['index']) != str(selected_id)))
        if x_axis is not None and y_axis is not None and str(id['index']) != str(selected_id):
            print("update plot")
            if filtered_data != "" and selected_data != "":
                df1 = pd.read_json(filtered_data)
                df2 = pd.read_json(selected_data)
                df1 = df1.astype(dtypelist)
                df2 = df2.astype(dtypelist)
                df = pd.merge(df1, df2)
            elif filtered_data != "":
                df = pd.read_json(filtered_data)
            elif selected_data != "":
                df = pd.read_json(selected_data)
            else:
                df = pd.read_json(stored_data)
            df = df.astype(dtypelist)
            dfstring = ""
            if df[x_axis].dtype.name == 'int64' or df[x_axis].dtype.name == 'float64':
                df = df.sort_values(x_axis)
            elif x_axis == 'Month':
                category_order = ['January','February','March','April','May','June','July','August','September','October','November','December']
                df['Month'] = pd.Categorical(df['Month'], ordered=True, categories=category_order)
                df = df.sort_values('Month')
            if color != None:
                if df[color].dtype.name == 'int64' or df[color].dtype.name == 'float64':
                    start = df[color].min()
                    bucketrange = df[color].max()-df[color].min()
                    step = (bucketrange)**(0.5)
                    for i in range(ceil(bucketrange/step)):
                        df_step = df[(df[color] >= i*step+start) & (df[color] < (i+1)*step+start)]
                        dfstring = dfstring + df_step.to_json() + "#####"
                if df[color].dtype.name == 'object' or df[color].dtype.name == 'category':
                    categories = df[color].unique()
                    for cat in categories:
                        df_step = df[df[color] == cat]
                        dfstring = dfstring + df_step.to_json() + "#####"
            else:
                dfstring = df.to_json() + "#####"
            return update_line(color, x_axis, y_axis, df), dfstring
        else:
            return dash.no_update, dash.no_update
    
    # Updates a bar plot if the attributes used for it change
    # or if the filtered or selected data from filters or selections changes
    @app.callback(
        Output({"type": "bar-plot", "index": MATCH}, 'figure'),
        Output({"type": "bar-data-used", "index": MATCH}, 'data'),
        Input({"type": "bar-x-axis", "index": MATCH}, 'value'),
        State({"type": "bar-x-axis", "index": MATCH}, 'id'),
        State('stored-data', 'data'),
        Input('filtered-data', 'data'),
        Input('selected-data', 'data'),
        State('selected-id', 'data'),
    )
    def change_bar_plot(x_axis, id, stored_data, filtered_data, selected_data, selected_id):
        print(str(id['index']))
        print(str(selected_id))
        print((str(id['index']) != str(selected_id)))
        if x_axis is not None and str(id['index']) != str(selected_id):
            print("update plot")
            if filtered_data != "" and selected_data != "":
                df1 = pd.read_json(filtered_data)
                df2 = pd.read_json(selected_data)
                df1 = df1.astype(dtypelist)
                df2 = df2.astype(dtypelist)
                df = pd.merge(df1, df2)
            elif filtered_data != "":
                df = pd.read_json(filtered_data)
            elif selected_data != "":
                df = pd.read_json(selected_data)
            else:
                df = pd.read_json(stored_data)
            df = df.astype(dtypelist)
            dfstring = ""
            dfstring = df.to_json()
            return update_bar(x_axis, df), dfstring
        else:
            return dash.no_update, dash.no_update

    # Handles the uploading of a csv file in the correct format
    # Filters out all rows that do not follow the correct format,
    # where underscore is removed and space is set to underscore to store in the dataframe
    @app.callback(
        Output('add-plot-button', 'disabled'),
        Output('stored-data', 'data'),
        Output('upload-data-button', 'children'),
        Output('select-filter-feature', 'options'),
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
                    
                    df = pd.read_csv(io.StringIO(decoded.decode("utf-8")), on_bad_lines='skip', sep=";", dtype='object')
                    df = df.stack().str.replace('_','').unstack()
                    df = df.stack().str.replace(' ','_').unstack()
                    df['Annual_Income'] = df['Annual_Income'].str.replace(',','.')
                    df['Monthly_Inhand_Salary'] = df['Monthly_Inhand_Salary'].str.replace(',','.')
                    df['Changed_Credit_Limit'] = df['Changed_Credit_Limit'].str.replace(',','.')
                    df['Outstanding_Debt'] = df['Outstanding_Debt'].str.replace(',','.')
                    df['Credit_Utilization_Ratio'] = df['Credit_Utilization_Ratio'].str.replace(',','.')
                    df['Total_EMI_per_month'] = df['Total_EMI_per_month'].str.replace(',','.')
                    df['Amount_invested_monthly'] = df['Amount_invested_monthly'].str.replace(',','.')
                    df['Monthly_Balance'] = df['Monthly_Balance'].str.replace(',','.')
                    mask = []
                    for _, row in df.iterrows():
                        possible = True
                        for col, type in dtypelist.items():
                            if type == 'object':
                                try:
                                    temp = (str(row[col]))
                                except:
                                    possible = False
                                    #print(str(_)+" "+str(row[col])+" "+str(col))
                                    break
                            if type == 'int64':
                                try:
                                    temp = (int(row[col]))
                                except:
                                    possible = False
                                    #print(str(_)+" "+str(row[col])+" "+str(col))
                                    break
                            if type == 'float64':
                                try:
                                    temp = (float(row[col]))
                                except:
                                    possible = False
                                    #print(str(_)+" "+str(row[col])+" "+str(col))
                                    break
                        mask.append(possible)
                    print(len(df))
                    df = df[mask]
                    print(len(df))
                    df = df.astype(dtypelist)
                                
                    print(df.dtypes)
                else:
                    # Create popup
                    print("whut 1")
                    return dash.no_update, dash.no_update, dash.no_update, dash.no_update
            except Exception as e:
                print(e)
                return dash.no_update, dash.no_update, dash.no_update, dash.no_update
            stored_data = df.to_json()
            print("got here in the end")
            print(df.columns)
            options = [{"label": x, "value": x} for x in list(df.columns)]
            return False, stored_data, filename, options

        return dash.no_update, dash.no_update, dash.no_update, dash.no_update
    
    # Handles adding and removing filter elements and updating the filtered dataframe
    @app.callback(
        Output('filter-card-container', 'children'),
        Output('filtered-data', 'data'),
        Input('add-filter-button', 'n_clicks'),
        Input({'type': 'remove-filter', 'index': ALL}, 'n_clicks'),
        State('select-filter-feature', 'value'),
        State('select-filter-comparator', 'value'),
        State('select-filter-value', 'value'),
        State('filter-card-container', 'children'),
        State({"type": "filter-text", "index": ALL}, 'children'),
        State('stored-data', 'data'),
    )
    def add_filter_and_remove(n_add_clicks, n_remove_clicks, feature_value, comparator_value, filter_value, children, texts, data):
        print("added filter")
        
        if data == "":
            return dash.no_update, dash.no_update
        
        clicked_indices = [index for index, clicks in enumerate(n_remove_clicks) if clicks is not None]
        for index in clicked_indices:
            children.pop(index)
            texts.pop(index)
    
        filters = [filter.split(" ") for filter in texts]
        
        if n_add_clicks and len(clicked_indices) == 0:
            filter_value = filter_value.replace('_','')
            filter_value = filter_value.replace(' ','_')
            filter = Filter(feature_value, comparator_value, filter_value, n_add_clicks)
            children.append(filter)
            filters.append([str(feature_value),str(comparator_value),str(filter_value)])
        
        df = pd.read_json(data)
        df = df.astype(dtypelist)
        for filter in filters:
            if filter[1] == "=":
                if df.dtypes[filter[0]] == 'object' or df.dtypes[filter[0]] == 'category':
                    df = df[df[filter[0]] == str(filter[2])]
                elif df.dtypes[filter[0]] == 'int64':
                    df = df[df[filter[0]] == int(filter[2])]
                elif df.dtypes[filter[0]] == 'float64':
                    df = df[df[filter[0]] == float(filter[2])]
            elif filter[1] == "≠":
                if df.dtypes[filter[0]] == 'object' or df.dtypes[filter[0]] == 'category':
                    df = df[df[filter[0]] != str(filter[2])]
                elif df.dtypes[filter[0]] == 'int64':
                    df = df[df[filter[0]] != int(filter[2])]
                elif df.dtypes[filter[0]] == 'float64':
                    df = df[df[filter[0]] != float(filter[2])]
            elif filter[1] == "≥":
                if df.dtypes[filter[0]] == 'int64':
                    df = df[df[filter[0]] >= int(filter[2])]
                elif df.dtypes[filter[0]] == 'float64':
                    df = df[df[filter[0]] >= float(filter[2])]
            elif filter[1] == "≤":
                if df.dtypes[filter[0]] == 'int64':
                    df = df[df[filter[0]] <= int(filter[2])]
                elif df.dtypes[filter[0]] == 'float64':
                    df = df[df[filter[0]] <= float(filter[2])]
            elif filter[1] == ">":
                if df.dtypes[filter[0]] == 'int64':
                    df = df[df[filter[0]] > int(filter[2])]
                elif df.dtypes[filter[0]] == 'float64':
                    df = df[df[filter[0]] > float(filter[2])]
            elif filter[1] == "<":
                if df.dtypes[filter[0]] == 'int64':
                    df = df[df[filter[0]] < int(filter[2])]
                elif df.dtypes[filter[0]] == 'float64':
                    df = df[df[filter[0]] < float(filter[2])]
        
        return children, df.to_json()
    
    # Updates the selection dataframe if a selection is made in a scatter plot
    @app.callback(
        Output('selected-data', 'data'),
        Output('selected-id', 'data'),
        Input({"type": "scatter-plot", "index": ALL}, 'selectedData'),
        State({"type": "scatter-plot", "index": ALL}, 'id'),
        State({"type": "scatter-data-used", "index": ALL}, 'data'),
    )
    def update_scatter_selection(selected_data, id, data_used):
        if dash.callback_context.triggered_id is not None:
            print("update selection")
            index = id.index(dash.callback_context.triggered_id)
            if selected_data[index] == None or len(selected_data[index]['points']) == 0:
                return "", ""
            dataframestrings = data_used[index].split("#####")[0:-1]
            dfs = []
            for dataframestring in dataframestrings:
                tempdf = pd.read_json(dataframestring)
                tempdf = tempdf.astype(dtypelist)
                dfs.append(tempdf)
            
            print(selected_data[index])
            selected_indices = {}
            for x in selected_data[index]['points']:
                if x.get('curveNumber', None) not in selected_indices:
                    selected_indices[x.get('curveNumber', None)] = []
                selected_indices[x.get('curveNumber', None)].append(x.get('pointIndex', None))
            for i in range(len(dfs)-1, -1, -1):
                if i in selected_indices:
                    dfs[i] = dfs[i].iloc[selected_indices[i]]
                else:
                    dfs.pop(i)
            df = pd.concat(dfs)
            return df.to_json(), id[index]['index']
        else:
            return dash.no_update, dash.no_update
    
    # Updates the selection dataframe if a selection is made in a line plot
    @app.callback(
        Output('selected-data', 'data'),
        Output('selected-id', 'data'),
        Input({"type": "line-plot", "index": ALL}, 'selectedData'),
        State({"type": "line-plot", "index": ALL}, 'id'),
        State({"type": "line-data-used", "index": ALL}, 'data'),
    )
    def update_line_selection(selected_data, id, data_used):
        if dash.callback_context.triggered_id is not None:
            print("update selection")
            index = id.index(dash.callback_context.triggered_id)
            if selected_data[index] == None or len(selected_data[index]['points']) == 0:
                return "", ""
            dataframestrings = data_used[index].split("#####")[0:-1]
            dfs = []
            for dataframestring in dataframestrings:
                tempdf = pd.read_json(dataframestring)
                tempdf = tempdf.astype(dtypelist)
                dfs.append(tempdf)
            
            print(selected_data[index])
            selected_indices = {}
            for x in selected_data[index]['points']:
                if x.get('curveNumber', None) not in selected_indices:
                    selected_indices[x.get('curveNumber', None)] = []
                selected_indices[x.get('curveNumber', None)].append(x.get('pointIndex', None))
            for i in range(len(dfs)-1, -1, -1):
                if i in selected_indices:
                    dfs[i] = dfs[i].iloc[selected_indices[i]]
                else:
                    dfs.pop(i)
            df = pd.concat(dfs)
            return df.to_json(), id[index]['index']
        else:
            return dash.no_update, dash.no_update
    
    # Updates the selection dataframe if a selection is made in a bar plot
    @app.callback(
        Output('selected-data', 'data'),
        Output('selected-id', 'data'),
        Input({"type": "bar-plot", "index": ALL}, 'selectedData'),
        State({"type": "bar-plot", "index": ALL}, 'id'),
        State({"type": "bar-data-used", "index": ALL}, 'data'),
        State({"type": "bar-x-axis", "index": ALL}, 'value'),
    )
    def update_bar_selection(selected_data, id, data_used, bar_feature):
        if dash.callback_context.triggered_id is not None:
            print("update selection")
            index = id.index(dash.callback_context.triggered_id)
            if selected_data[index] == None or len(selected_data[index]['points']) == 0:
                return "", ""
            dataframestring = data_used[index]
            df = pd.read_json(dataframestring)
            df = df.astype(dtypelist)
            selected_index = [  # show only selected indices
                x.get('pointIndex', None)
                for x in selected_data[index]['points']
            ]
            selected_dfs = []
            if df[bar_feature[index]].dtype.name == 'int64' or df[bar_feature[index]].dtype.name == 'float64':
                start = df[bar_feature[index]].min()
                bucketrange = df[bar_feature[index]].max()-df[bar_feature[index]].min()
                step = (bucketrange)**(0.5)
                if bucketrange/step > 20:
                    step = bucketrange/20
                for i in range(ceil(bucketrange/step)):
                    df_step = df[(df[bar_feature[index]] >= i*step+start) & (df[bar_feature[index]] < (i+1)*step+start)]
                    if i in selected_index:
                        selected_dfs.append(df_step)
            if df[bar_feature[index]].dtype.name == 'object' or df[bar_feature[index]].dtype.name == 'category':
                categories = df[bar_feature[index]].unique()
                if bar_feature[index] == 'Month':
                    categories = ['January','February','March','April','May','June','July','August','September','October','November','December']
                for i, cat in enumerate(categories):
                    df_step = df[df[bar_feature[index]] == cat]
                    if i in selected_index:
                        selected_dfs.append(df_step)
            df = pd.concat(selected_dfs)
            return df.to_json(), id[index]['index']
        else:
            return dash.no_update, dash.no_update
    
    # Makes the updated scatter plot based on the attributes and dataframe
    def update_scatter(selected_color, feature_x, feature_y, df):
        fig = go.Figure()
        print("got here")
        
        if selected_color == None:
            x_values = df[feature_x]
            y_values = df[feature_y]
            fig.add_trace(go.Scatter(
                x=x_values,
                y=y_values,
                mode='markers',
            ))
            
        else:
            print(df[selected_color].dtype.name)
            if df[selected_color].dtype.name == 'int64' or df[selected_color].dtype.name == 'float64':
                start = df[selected_color].min()
                bucketrange = df[selected_color].max()-df[selected_color].min()
                step = (bucketrange)**(0.5)
                for i in range(ceil(bucketrange/step)):
                    df_step = df[(df[selected_color] >= i*step+start) & (df[selected_color] < (i+1)*step+start)]
                    x_values = df_step[feature_x]
                    y_values = df_step[feature_y]
                    fig.add_trace(go.Scatter(
                        x=x_values,
                        y=y_values,
                        mode='markers',
                        name=f'{round(i*step+start, 1)}-{round((i+1)*step+start,1)}',
                    ))
            if df[selected_color].dtype.name == 'object' or df[selected_color].dtype.name == 'category':
                categories = df[selected_color].unique()
                for cat in categories:
                    df_step = df[df[selected_color] == cat]
                    x_values = df_step[feature_x]
                    y_values = df_step[feature_y]
                    fig.add_trace(go.Scatter(
                        x=x_values,
                        y=y_values,
                        mode='markers',
                        name=cat,
                    ))
        fig.update_traces(mode='markers', marker_size=10)
        fig.update_layout(
            yaxis_zeroline=False,
            xaxis_zeroline=False,
            dragmode='select'
        )
        if feature_x == 'Month':
            fig.update_xaxes(fixedrange=True, categoryorder='array', categoryarray= ['January','February','March','April','May','June','July','August','September','October','November','December'])
        else:
            fig.update_xaxes(fixedrange=True)
        if feature_y == 'Month':
            fig.update_yaxes(fixedrange=True, categoryorder='array', categoryarray= ['January','February','March','April','May','June','July','August','September','October','November','December'])
        else:
            fig.update_yaxes(fixedrange=True)
        fig.update_layout(
            xaxis_title=feature_x,
            yaxis_title=feature_y,
        )
        print("returned fig")
        return fig
    
    # Makes the updated line plot based on the attributes and dataframe
    def update_line(selected_color, feature_x, feature_y, df):
        fig = go.Figure()
        print("got here")
        
        if selected_color == None:
            x_values = df[feature_x]
            y_values = df[feature_y]
            fig.add_trace(go.Scatter(
                x=x_values,
                y=y_values,
                mode='lines+markers',
            ))
            
        else:
            print(df[selected_color].dtype.name)
            if df[selected_color].dtype.name == 'int64' or df[selected_color].dtype.name == 'float64':
                start = df[selected_color].min()
                bucketrange = df[selected_color].max()-df[selected_color].min()
                step = (bucketrange)**(0.5)
                for i in range(ceil(bucketrange/step)):
                    df_step = df[(df[selected_color] >= i*step+start) & (df[selected_color] < (i+1)*step+start)]
                    x_values = df_step[feature_x]
                    y_values = df_step[feature_y]
                    fig.add_trace(go.Scatter(
                        x=x_values,
                        y=y_values,
                        mode='lines+markers',
                        name=f'{round(i*step+start, 1)}-{round((i+1)*step+start,1)}',
                    ))
            if df[selected_color].dtype.name == 'object' or df[selected_color].dtype.name == 'category':
                categories = df[selected_color].unique()
                for cat in categories:
                    df_step = df[df[selected_color] == cat]
                    x_values = df_step[feature_x]
                    y_values = df_step[feature_y]
                    fig.add_trace(go.Scatter(
                        x=x_values,
                        y=y_values,
                        mode='lines+markers',
                        name=cat,
                    ))
        fig.update_traces(mode='lines+markers', marker_size=5)
        fig.update_layout(
            yaxis_zeroline=False,
            xaxis_zeroline=False,
            dragmode='select'
        )
        if feature_x == 'Month':
            fig.update_xaxes(fixedrange=True, categoryorder='array', categoryarray = ['January','February','March','April','May','June','July','August','September','October','November','December'])
        else:
            fig.update_xaxes(fixedrange=True)
        if feature_y == 'Month':
            fig.update_yaxes(fixedrange=True, categoryorder='array', categoryarray = ['January','February','March','April','May','June','July','August','September','October','November','December'])
        else:
            fig.update_yaxes(fixedrange=True)
        fig.update_layout(
            xaxis_title=feature_x,
            yaxis_title=feature_y,
        )
        print("returned fig")
        return fig
    
    # Makes the updated bar plot based on the attributes and dataframe
    def update_bar(feature_x, df):
        fig = go.Figure()
        print("got here")
        
        barnames = []
        counts = []
        if df[feature_x].dtype.name == 'int64' or df[feature_x].dtype.name == 'float64':
            start = df[feature_x].min()
            bucketrange = df[feature_x].max()-df[feature_x].min()
            step = (bucketrange)**(0.5)
            if bucketrange/step > 20:
                step = bucketrange/20
            for i in range(ceil(bucketrange/step)):
                barnames.append(f'{round(i*step+start, 1)}-{round((i+1)*step+start,1)}')
                df_step = df[(df[feature_x] >= i*step+start) & (df[feature_x] < (i+1)*step+start)]
                counts.append(len(df_step))
        if df[feature_x].dtype.name == 'object' or df[feature_x].dtype.name == 'category':
            categories = df[feature_x].unique()
            for cat in categories:
                barnames.append(cat)
                df_step = df[df[feature_x] == cat]
                counts.append(len(df_step))
        if feature_x == 'Month':
            newbarnames = ['January','February','March','April','May','June','July','August','September','October','November','December']
            newcounts = []
            for barname in newbarnames:
                if barname in barnames:
                    newcounts.append(counts[barnames.index(barname)])
            fig.add_trace(go.Bar(
                x=newbarnames,
                y=newcounts,
            ))
        else:
            fig.add_trace(go.Bar(
                x=barnames,
                y=counts,
            ))
        
        fig.update_layout(
            yaxis_zeroline=False,
            xaxis_zeroline=False,
            dragmode='select'
        )
        fig.update_xaxes(fixedrange=True)
        fig.update_yaxes(fixedrange=True)
        fig.update_layout(
            xaxis_title=feature_x,
        )
        print("returned fig")
        return fig

    app.run_server(debug=False, dev_tools_ui=False)