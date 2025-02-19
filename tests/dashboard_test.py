import dash
from dash import dcc, html
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
    color = 'green' if change >= 0 else 'red'
    triangle = "▲" if change >= 0 else "▼"

    return html.Div([
        html.Span(
            triangle,  
            style={'color': color, 'fontSize': '24px', 'marginRight': '10px'}
        ),
        html.Span(
            f"{change}%",  
            style={'color': color, 'fontSize': '18px'}
        ),
    ], style={'display': 'flex', 'alignItems': 'center', 'marginLeft': '20px'})

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
        height=180,
        width=280,
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

    return dcc.Graph(figure=fig, style={'marginLeft': '20px', 'border': '2px solid #000000', 'borderRadius': '5px'})

app.layout = html.Div([
    html.H1("Stocks Overview"),  # Título de la aplicación
    
    # Lista de apartados de cada empresa
    html.Div([
        html.Div([
            # Nombre y ticker de la empresa
            html.H3(f"({i['ticker'][:4]})"),  

            # Logo de la empresa con margen después del ticker
            html.Div([
                html.Img(src=i['company_logo_url'], height="50px"),  # Logo de la empresa
            ], style={'marginLeft': '20px', 'marginRight': '20px'}),  # Añadir espacio después del logo

            # Comprobar el cambio de precio y definir el color y el triángulo
            create_change_indicator(i['price']),

            html.Div([
                create_metric_chart(i['price'], 'Closed Price')
            ], style={'marginLeft': '20px'}),

            create_change_indicator(i['volume']),

            html.Div([
                create_metric_chart(i['volume'], 'Closed Volume')
            ], style={'marginLeft': '20px'}),

        ], style={'display': 'flex', 'alignItems': 'center', 'marginBottom': '30px'})
        #], style={'display': 'flex', 'flexDirection': 'row', 'alignItems': 'flex-start', 'marginBottom': '30px', 'flexWrap': 'wrap', 'justifyContent': 'space-between'})
        for i in data  # Iteramos sobre los datos obtenidos de MongoDB
    ])
])

# Ejecutar la aplicación
app.run_server(debug=True)