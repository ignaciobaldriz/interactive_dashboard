import pandas as pd
import plotly
import plotly.express as px

import dash
import dash_table

import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html

from dash.dependencies import Input, Output
from dash.exceptions import PreventUpdate


# "pip install alpha_vantage" (if you haven't done so)
from alpha_vantage.timeseries import TimeSeries
from alpha_vantage.techindicators import TechIndicators  

# --------------------------------------------------

# Import the API stock market data from Google 

key = 'L8CWO5SA7MMRM7YP'
ts = TimeSeries(key, output_format='pandas')
ti = TechIndicators(key, output_format = 'pandas')


# --------------------------------------------------

# Define a function that transform the default imported data base into a Plotlyb apropiate format

def alphaVantageDF_to_plotlyDF(company_data):
    df = company_data.copy()
    df = df.transpose()
    df.rename(index={"1. open":"open", "2. high":"high", "3. low":"low",
                     "4. close":"close","5. volume":"volume"},inplace=True)
    df=df.reset_index().rename(columns={'index': 'indicator'})
    df = pd.melt(df,id_vars=['indicator'],var_name='date',value_name='rate')
    df = df[df['indicator']!='volume']
     
    return(df)

# ---------------------------------------------------


app = dash.Dash(__name__, external_stylesheets = [dbc.themes.SANDSTONE],
                meta_tags=[{'name': 'viewport',
                            'content': 'width=device-width, initial-scale=1.0'}]
                )
server = app.server

app.layout = html.Div([
    
    dbc.Row(
        dbc.Col( html.H3("Daily Stock Market Update", className = 'text-center text-light'),
                width = {'size':12, 'offset':0}, style={"background-color": "gray"},
        ),   
    ),

    dbc.Row(
        dbc.Col( html.H4("Report Case: Google", className = 'text-center text-light'),
                width = {'size':12, 'offset':0}, style = {"background-color": "gray"}
        ),   
    ),

    dbc.Row(
        [
            dbc.Col(
                html.Div([
                    # Interval object: to update the app in real time
                    dcc.Interval(
                        id='google_interval',
                        n_intervals=0,       # number of times the interval was activated at the begining of the app
                        interval=900*1000,   # update every 15 minutes
                        ),
                
                    # Graph object
                    dcc.Graph(id="google_graph", figure={'layout':{'plot_bgcolor': '#d8d5ee', 'paper_bgcolor': '#d8d5ee'}}),   # empty graph to be populated by line chart
            ]),
            
            #width={'offset': 2},
            style={'marginLeft': 10, 'marginRight': 10, 'marginTop': 10, 'marginBottom': 10},
            xs=10, sm=10, md=5, lg=5, xl=5
            ),

            dbc.Col(
                html.Div([
                    # Interval object: to update the app in real time
                    dcc.Interval(
                        id='google_interval_volume',
                        n_intervals=0,       # number of times the interval was activated at the begining of the app
                        interval=900*1000,   # update every 15 minutes
                        ),
                
                    # Graph object
                    dcc.Graph(id="google_graph_volume", figure={'layout':{'plot_bgcolor': '#d8d5ee', 'paper_bgcolor': '#d8d5ee'}}),   # empty graph to be populated by line chart
            ]),
            
            #width={'offset': 1},
            style={'marginLeft': 10, 'marginRight': 10, 'marginTop': 10, 'marginBottom': 10},
            xs=10, sm=10, md=5, lg=5, xl=5

            ),

        ]
    ),

    dbc.Row(
        dbc.Col( html.P(""),
                width = {'size':12},
        ),   
    ),

    dbc.Row(
        dbc.Col(
            html.Div([
                # Interval object: to update the app in real time
                dcc.Interval(
                    id='google_interval_bbands',
                    n_intervals=0,       # number of times the interval was activated at the begining of the app
                    interval=900*1000,   # update every 15 minutes
                ),
                
                # Graph object
                dcc.Graph(id="google_graph_bbands", figure={'layout':{'plot_bgcolor': '#d8d5ee', 'paper_bgcolor': '#d8d5ee'}}),   # empty graph to be populated by line chart
            ]),
            width={'size': 11}, 
            style={'marginLeft': 10, 'marginRight': 10, 'marginTop': 10, 'marginBottom': 10}
        ),
    ),

    dbc.Row(
        dbc.Col( html.P(""),
                width = {'size':12},
        ),   
    ),


])

# --------------------------------------------------

@app.callback(
     [Output(component_id='google_graph', component_property='figure'),
      Output(component_id='google_graph_volume', component_property='figure'),
      Output(component_id='google_graph_bbands', component_property='figure')],
     [Input(component_id='google_interval', component_property='n_intervals'),
      Input(component_id='google_interval_volume', component_property='n_intervals'),
      Input(component_id='google_interval_bbands', component_property='n_intervals')]
 )

def update_graph(n_google, n_google_volume, n_google_bbands):
     "Pull financial data from Alpha Vantage and update graph every 15 minutes"
     
     # Code from Alpha Vantage documentation to streaming data
     google_data, google_meta_data = ts.get_intraday(symbol='GOOGL',interval='5min',outputsize='compact')
     
     google_bbands, google_bbands_meta_data = ti.get_bbands(symbol='GOOGL', interval='60min', time_period=60)     

     # Transform the data to an acceptable format for the Plotly librarie
     df_google = alphaVantageDF_to_plotlyDF(google_data)

     # Line chart graph 
     google_line_chart = px.line(
                         data_frame=df_google,
                         x='date',
                         y='rate',
                         color='indicator',
                         title="Stock prices over time",

                         )


     # Transactions volume for Google
     google_volume_line_chart = px.line(
                               data_frame = google_data['5. volume'],
                               title="Total amount of traiding activity over time")

     # B Band indicator for Google
     google_bbands_line_chart = px.line(
                               data_frame = google_bbands,
                               title="Bollinger Band indicator")



     return (google_line_chart, google_volume_line_chart, google_bbands_line_chart)
 
# --------------------------------------------------------------------------------


if __name__ == '__main__':
    app.run_server(debug=False)

# --------------------------------------------------------------------------------

# References:
# https://medium.com/analytics-vidhya/python-dash-data-visualization-dashboard-template-6a5bff3c2b76
# https://www.youtube.com/watch?v=b-M2KQ6_bM4