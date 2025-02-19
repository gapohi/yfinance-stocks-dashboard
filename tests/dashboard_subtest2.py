import dash
from dash import dash_table
from dash import dcc, html
import pandas as pd
import plotly.graph_objects as go
from pymongo import MongoClient

app = dash.Dash(__name__)

# Función para obtener los datos desde MongoDB
def fetch_data_from_mongodb():
    client = MongoClient("mongodb://localhost:27017/")
    db = client["yfinance"]
    collection = db["prices"]
    data = list(collection.find({}))
    return list(data)

data = fetch_data_from_mongodb()

def create_change_indicator(data):
    change = data['yesterday_change']
    
    # Redondear el cambio a 2 decimales
    change_formatted = f"{change:.2f}"

    # Separar la parte entera y decimal
    integer_part, decimal_part = change_formatted.split('.')
    
    # Asegurarse de que la parte entera tenga siempre 2 dígitos
    integer_part = integer_part.zfill(2)  # Asegurarse de que la parte entera tenga 2 dígitos
    change_formatted = f"{integer_part}.{decimal_part}"  # Volver a juntar

    color = 'green' if change >= 0 else 'red'
    triangle = "▲" if change >= 0 else "▼"

    return html.Div([
        html.Span(
            triangle,  
            style={'color': color, 'fontSize': '24px', 'marginRight': '5px'}  # Triángulo con tamaño constante
        ),
        html.Span(
            f"{change_formatted}%",  
            style={'color': color, 'fontSize': '16px'}  # Texto con tamaño más pequeño
        ),
    ], style={'display': 'flex', 'alignItems': 'center'})


def create_metric_chart(metric, y_name):
    fig = go.Figure()

    # Línea principal (precio o métrica principal)
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
        line=dict(color='#00FF00', width=2),  # Verde neón
        marker=dict(size=6, color='white', line=dict(width=1, color='#00FF00')),
        name=y_name
    ))

    # Línea de la media móvil si metric es 'price'
    if 'close_moving_avg_5d' in metric:
        fig.add_trace(go.Scatter(
            x=[-4, -3, -2, -1, 0],
            y=[metric['close_moving_avg_5d']] * 5,  # Línea horizontal con el mismo valor
            mode='lines',
            line=dict(color='#FFAA00', width=1.5, dash='dash'),  # Línea naranja punteada
            name='MA 5D'
        ))

    fig.update_layout(
        paper_bgcolor='#1E1E1E',
        plot_bgcolor='#1E1E1E',
        margin=dict(l=20, r=40, t=20, b=20),  # Se aumenta el margen derecho para la leyenda
        xaxis=dict(
            title="T",
            tickvals=[-4, -3, -2, -1, 0],
            tickfont=dict(color='white'),
            gridcolor='#444',
            zerolinecolor='white',
            linecolor='white',
            tickcolor='white',
            titlefont=dict(size=12, color='white'),
            tickangle=0  # No rotar los números del eje X
        ),
        yaxis=dict(
            title=y_name,
            tickfont=dict(color='white'),
            gridcolor='#444',
            zerolinecolor='white',
            linecolor='white',
            tickcolor='white',
            titlefont=dict(size=12, color='white')
        ),
        height=200,  # Tamaño de altura ajustado
        width=300,   # Tamaño de ancho ajustado
        legend=dict(
            orientation='h',  # Leyenda en horizontal
            x=0.5,  # Centrada en el gráfico
            y=1.1,  # Colocada justo encima del gráfico
            traceorder='normal',
            font=dict(
                size=7.5,  # Tamaño de la fuente más pequeño
                color='white'
            ),
            bordercolor='white',
            borderwidth=1,
            xanchor='center',  # Alinear la leyenda al centro
            yanchor='bottom'  # Alinear la leyenda al fondo
        )
    )

    return dcc.Graph(figure=fig, style={'border': '2px solid #000000', 'borderRadius': '5px'})

def create_metric_table(metric):
    # Crear los datos de la tabla
    data = {
        'Metric': ['Open Today', 'Low Today', 'High Today', 'Low 52wk', 'High 52wk'],
        'Price': [metric['open_today'], metric['low_today'], metric['high_today'], metric['low_52wk'], metric['high_52wk']]
    }

    # Convertir a un DataFrame
    df = pd.DataFrame(data)

    # Crear la tabla
    table = dash_table.DataTable(
        data=df.to_dict('records'),
        columns=[
            {'name': 'Metric', 'id': 'Metric'},
            {'name': 'Price', 'id': 'Price'}
        ],
        style_table={'height': '200px', 'width': '250px', 'overflowY': 'auto'},  # Tamaño ajustado para la tabla
        style_cell={
            'padding': '6px',  # Menos padding
            'textAlign': 'center',
            'color': 'white',
            'backgroundColor': '#1E1E1E',
            'border': '1px solid #444',
            'height': '30px',  # Altura aún más pequeña
            'width': '120px'   # Ancho más pequeño para las celdas
        },
        style_header={
            'backgroundColor': '#333',
            'fontWeight': 'bold',
            'color': 'white'
        },
        style_data={
            'backgroundColor': '#222',
            'color': 'white'
        }
    )

    return table


app.layout = html.Div([
    html.H1("Stocks Overview"),  # Título de la aplicación
    
    # Lista de apartados de cada empresa
    html.Div([
        html.Div([
            # Nombre y ticker de la empresa
            html.Div([
                # Ticker con un tamaño fijo
                html.H3(f"({i['ticker']: <5})", style={'display': 'inline-block', 'width': '80px', 'textAlign': 'left', 'marginRight': '10px'}),  # Ajustamos el margen derecho

                # Logo de la empresa
                html.Div([
                    html.Img(src=i['company_logo_url'], height="30px", width="30px")  # Logo de la empresa
                ], style={'display': 'inline-block', 'verticalAlign': 'middle'})
            ], style={'display': 'flex', 'alignItems': 'center', 'flexWrap': 'nowrap'}),


            # Comprobar el cambio de precio y definir el color y el triángulo
            create_change_indicator(i['price']),

            html.Div([
                create_metric_chart(i['price'], 'Closed Price')
            ]),

            create_metric_table(i['price']),

            create_change_indicator(i['volume']),

            html.Div([
                create_metric_chart(i['volume'], 'Closed Volume')
            ]),
        ], style={'display': 'flex', 'flexDirection': 'row', 'alignItems': 'center', 'marginBottom': '30px', 'flexWrap': 'wrap', 'justifyContent': 'space-between', 'gap': '60px'})
        for i in data  # Iteramos sobre los datos obtenidos de MongoDB
    ])
])


# Ejecutar la aplicación
app.run_server(debug=True)