import dash
import pandas as pd
import plotly.graph_objects as go
from dash import dash_table
from dash import dcc, html
from pymongo import MongoClient

def extract_data_from_mongodb():
    """
    Extracts data from the MongoDB stocks database.
    """
    try:
        client = MongoClient("mongodb://localhost:27017/")
        db = client["yfinance"]
        collection = db["stocks"]
        data = list(collection.find({}))
        return list(data)
    except Exception as e:
        raise RuntimeError(f"Error extracting data from MongoDB: {e}")

def create_change_indicator(data):
    """
    Creates a visual change indicator.
    """
    try:
        change = data['yesterday_change']
        change_formatted = f"{change:.2f}"
        integer_part, decimal_part = change_formatted.split('.')
        integer_part = integer_part.zfill(2)    
        change_formatted = f"{integer_part}.{decimal_part}"

        color, triangle = ('green', '▲') if change >= 0 else ('red', '▼')

        return html.Div([
            html.Span(
                triangle,  
                style={'color': color, 'fontSize': '24px', 'fontFamily': 'Consolas, monospace', 'marginRight': '5px'}   
            ),
            html.Span(
                f"{change_formatted}%",  
                style={'color': color, 'fontSize': '16px', 'fontFamily': 'Consolas, monospace'}
            ),
        ], style={'display': 'flex', 'alignItems': 'center'})
    except Exception as e:
        raise RuntimeError(f"Error creating visual change indicator: {e}")

def create_metric_chart(metric, y_name):
    """
    Creates a metric line chart.
    """
    try:
        ## line chart
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=[-4, -3, -2, -1, 0],
            y=[
                metric['close_4'],
                metric['close_3'],
                metric['close_2'],
                metric['close_yesterday'],
                metric['close_today']
            ],
            mode='lines+markers',
            line=dict(color='#00FF00', width=2),    
            marker=dict(size=6, color='white', line=dict(width=1, color='#00FF00')),
            name=y_name
        ))
        ## price has a moving average
        if 'close_moving_avg_5d' in metric:
            fig.add_trace(go.Scatter(
                x=[-4, -3, -2, -1, 0],
                y=[metric['close_moving_avg_5d']] * 5,
                mode='lines',
                line=dict(color='#FFAA00', width=1.5, dash='dash'), 
                name='MA 5D'
            ))
        ## layout
        fig.update_layout(
            paper_bgcolor='#1E1E1E',
            plot_bgcolor='#1E1E1E',
            margin=dict(l=20, r=40, t=20, b=20),
            xaxis=dict(
                title="T",
                tickvals=[-4, -3, -2, -1, 0],
                tickfont=dict(color='white', family='Consolas'),
                gridcolor='#444',
                zerolinecolor='white',
                linecolor='white',
                tickcolor='white',
                titlefont=dict(size=12, color='white', family='Consolas'),
                tickangle=0
            ),
            yaxis=dict(
                title=y_name,
                tickfont=dict(color='white', family='Consolas'),
                gridcolor='#444',
                zerolinecolor='white',
                linecolor='white',
                tickcolor='white',
                titlefont=dict(size=12, color='white', family='Consolas')
            ),
            height=200,
            width=300,
            legend=dict(
                orientation='h',
                x=0.5,
                y=1.1,
                traceorder='normal',
                font=dict(
                    size=7.5,
                    color='white',
                    family='Consolas'
                ),
                bordercolor='white',
                borderwidth=1,
                xanchor='center',
                yanchor='bottom'
            )
        )
        return dcc.Graph(figure=fig, style={'border': '2px solid #000000', 'borderRadius': '5px'})
    except Exception as e:
        raise RuntimeError(f"Error creating metric line chart: {e}")

def create_metric_table(metric):
    """
    Creates a metric table for price.
    """
    try:
        data = {
            'Metric': ['Close Today', 'Open Today', 'Low Today', 'High Today', 'Low 52wk', 'High 52wk'],
            'Price': [metric['close_today'], metric['open_today'], metric['low_today'], metric['high_today'], metric['low_52wk'], metric['high_52wk']]
        }
        df = pd.DataFrame(data)
        table = dash_table.DataTable(
            data=df.to_dict('records'),
            columns=[
                {'name': 'Metric', 'id': 'Metric'},
                {'name': 'Price', 'id': 'Price'}
            ],
            style_table={'height': '250px', 'width': '250px', 'overflowY': 'auto'},
            style_cell={
                'padding': '6px',
                'textAlign': 'center',
                'color': 'white',
                'backgroundColor': '#1E1E1E',
                'border': '1px solid #444',
                'height': '30px',
                'width': '120px',
                'fontFamily': 'Consolas',
                'fontSize': '12px'
            },
            style_header={
                'backgroundColor': '#222',
                'fontWeight': 'bold',
                'color': 'white',
                'fontFamily': 'Consolas',
                'fontSize': '12px'
            },
            style_data={
                'backgroundColor': '#222',
                'color': 'white',
                'fontFamily': 'Consolas',
                'fontSize': '12px'
            }
        )
        return table
    except Exception as e:
        raise RuntimeError(f"Error creating metric table for price: {e}")

def create_header():
    """
    Creates the dashboard header.
    """
    return html.H1("stocks overview", style={
                'textAlign': 'center',
                'fontFamily': 'Consolas, monospace',
                'fontSize': '36px',
                'color': '#FAFAFA',
                'marginBottom': '20px',
                'backgroundColor': '#1E1E1E',
                'padding': '20px',
                'borderRadius': '10px',
                'boxShadow': '0 4px 10px rgba(0, 0, 0, 0.1)'
            })

def dash_app():
    """
    Creates and launches the Dash dashboard app.
    """
    ## obtaining data from mongodb
    data = extract_data_from_mongodb()

    ## starting the dash app for creating the dashboard
    app = dash.Dash(__name__)

    app.layout = html.Div([
        html.Div([
            ## adding the header
            create_header(),
            html.Div([
                html.Div([
                    html.Div([
                        ## adding the company stock name and logo
                        html.H3(f"({i['ticker']: <5})", style={
                            'fontFamily': 'Consolas, monospace',
                            'fontSize': '20px',
                            'color': '#555',
                            'display': 'inline-block',
                            'width': '90px',
                            'textAlign': 'left',
                            'marginRight': '15px',
                            'fontWeight': '500'
                        }),
                        html.Div([
                            html.Img(src=i['company_logo_url'], height="35px", width="35px")
                        ], style={'display': 'inline-block', 'verticalAlign': 'middle'})
                    ], style={'display': 'flex', 'alignItems': 'center', 'flexWrap': 'nowrap'}),

                    ## adding yesterday's price change indicator
                    create_change_indicator(i['price']),

                    ## adding the line chart for closed price
                    html.Div([
                        create_metric_chart(i['price'], 'Closed Price')
                    ], style={'marginTop': '20px'}),

                    ## adding the table for price metrics
                    create_metric_table(i['price']),

                    ## adding yesterday's volume change indicator
                    create_change_indicator(i['volume']),
                    
                    ## adding the line chart for closed volume
                    html.Div([
                        create_metric_chart(i['volume'], 'Closed Volume')
                    ], style={'marginTop': '20px'}),

                ], style={
                    'display': 'flex', 
                    'flexDirection': 'row', 
                    'alignItems': 'center',
                    'marginBottom': '20px', 
                    'flexWrap': 'wrap', 
                    'justifyContent': 'space-between', 
                    'gap': '20px',
                    'padding': '20px',
                    'backgroundColor': '#f0f0f0',
                    'borderRadius': '10px',
                    'boxShadow': '0 4px 10px rgba(0, 0, 0, 0.1)',
                    'height': 'auto'
                })
                ## for every stock in the data
                for i in data
            ], style={
                'display': 'flex',
                'flexDirection': 'column',
                'alignItems': 'center',
                'backgroundColor': '#FAF0E6',
                'paddingTop': '20px',
                'paddingBottom': '20px',
                'paddingLeft': '5px',
                'paddingRight': '5px',
                'borderRadius': '5px',
                'boxShadow': '0 4px 10px rgba(0, 0, 0, 0.1)'
            })
        ])
    ])

    ## running the app
    app.run_server(debug=True)