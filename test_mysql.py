import pymysql
import pandas as pd
import dash
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime


# Étape 1 : Connexion à la base de données MySQL et récupération des données
def fetch_data_from_db():
    connection = pymysql.connect(
        host='localhost',  # Adresse du serveur
        user='root',  # Nom d'utilisateur MySQL
        password='',  # Mot de passe MySQL
        database='sensor_db'  # Nom de la base de données
    )
    query = "SELECT * FROM dht22 ORDER BY Datetime DESC LIMIT 200;"  # Récupérer les 200 dernières données
    df = pd.read_sql(query, connection)
    connection.close()
    return df


# Charger les données
df = fetch_data_from_db()
df['Datetime'] = pd.to_datetime(df['Datetime'])

# Étape 2 : Initialisation de l'application Dash
app = dash.Dash(__name__)
app.title = "Real-Time Sensor Dashboard"

# Couleurs personnalisées
colors = {
    'background': '#1e1e2f',
    'text': '#ffffff',
    'card_background': '#2a2a40',
    'card_hover': '#3a3a5a',
    'temperature_color': '#ff7f50',
    'humidity_color': '#1f78b4'
}

# CSS personnalisé pour le mode dark et une apparence professionnelle
app.layout = html.Div(
    style={'backgroundColor': colors['background'], 'color': colors['text'], 'fontFamily': 'Arial, sans-serif',
           'padding': '20px'},
    children=[
        # Titre dynamique avec un indicateur en temps réel
        html.Div([
            html.H1(
                "🌡️ Real-Time Sensor Data Dashboard 🌧️",
                style={'textAlign': 'center', 'marginBottom': '10px', 'color': colors['text']}
            ),
            html.Div(
                id='live-update-text',
                style={'textAlign': 'center', 'fontSize': '18px', 'color': '#bbbbbb', 'marginBottom': '30px'}
            ),
        ]),

        # Section Température
        html.Div([
            # Gauge de température
            html.Div([
                dcc.Graph(id='temperature-gauge', style={'height': '300px'}),
            ], style={'width': '25%', 'display': 'inline-block', 'padding': '10px'}),

            # Line Chart de température avec interactivité
            html.Div([
                dcc.Graph(
                    id='temperature-line-chart',
                    style={'height': '300px'},
                    config={'displayModeBar': True, 'scrollZoom': True}  # Activer le zoom et le déplacement
                ),
            ], style={'width': '50%', 'display': 'inline-block', 'padding': '10px'}),

            # Cartes stylisées pour les statistiques de température
            html.Div([
                html.Div(id='temperature-stats', style={'display': 'flex', 'flexDirection': 'column', 'gap': '10px'})
            ], style={'width': '20%', 'display': 'inline-block', 'padding': '10px', 'verticalAlign': 'top'}),
        ], style={'borderBottom': '1px solid #444', 'paddingBottom': '20px', 'display': 'flex',
                  'alignItems': 'stretch'}),

        # Section Humidité
        html.Div([
            # Gauge d'humidité
            html.Div([
                dcc.Graph(id='humidity-gauge', style={'height': '300px'}),
            ], style={'width': '25%', 'display': 'inline-block', 'padding': '10px'}),

            # Line Chart d'humidité avec interactivité
            html.Div([
                dcc.Graph(
                    id='humidity-line-chart',
                    style={'height': '300px'},
                    config={'displayModeBar': True, 'scrollZoom': True}  # Activer le zoom et le déplacement
                ),
            ], style={'width': '50%', 'display': 'inline-block', 'padding': '10px'}),

            # Cartes stylisées pour les statistiques d'humidité
            html.Div([
                html.Div(id='humidity-stats', style={'display': 'flex', 'flexDirection': 'column', 'gap': '10px'})
            ], style={'width': '20%', 'display': 'inline-block', 'padding': '10px', 'verticalAlign': 'top'}),
        ], style={'paddingTop': '20px', 'display': 'flex', 'alignItems': 'stretch'}),

        # Tableau de données interactif
        html.Div([
            dash_table.DataTable(
                id='data-table',
                columns=[{"name": i, "id": i} for i in df.columns],
                data=df.to_dict('records'),
                page_size=10,
                style_table={'overflowX': 'auto'},
                style_header={
                    'backgroundColor': colors['card_background'],
                    'color': colors['text'],
                    'fontWeight': 'bold'
                },
                style_cell={
                    'backgroundColor': colors['background'],
                    'color': colors['text'],
                    'border': '1px solid #444'
                },
            )
        ], style={'marginTop': '30px'}),

        # Intervalle de mise à jour
        dcc.Interval(id='interval-component', interval=1000, n_intervals=0),  # Mise à jour toutes les 1 seconde
    ]
)

# Style CSS pour les cartes
card_style = {
    'backgroundColor': colors['card_background'],
    'borderRadius': '10px',
    'padding': '15px',
    'boxShadow': '0 4px 8px 0 rgba(0, 0, 0, 0.2)',
    'transition': 'transform 0.2s, box-shadow 0.2s',
    'textAlign': 'center',
    'color': colors['text'],
    'fontSize': '18px'
}

card_hover_style = {
    'transform': 'scale(1.05)',
    'boxShadow': '0 8px 16px 0 rgba(0, 0, 0, 0.3)',
    'backgroundColor': colors['card_hover']
}


# Callback pour mettre à jour les graphiques, les indicateurs et le texte en temps réel
@app.callback(
    [Output('temperature-gauge', 'figure'),
     Output('temperature-line-chart', 'figure'),
     Output('temperature-stats', 'children'),
     Output('humidity-gauge', 'figure'),
     Output('humidity-line-chart', 'figure'),
     Output('humidity-stats', 'children'),
     Output('data-table', 'data'),
     Output('live-update-text', 'children')],
    [Input('interval-component', 'n_intervals')]
)
def update_graphs(n):
    # Récupérer les données
    df = fetch_data_from_db()
    df['Datetime'] = pd.to_datetime(df['Datetime'])

    latest_temperature = df['Temperature'].iloc[0]
    latest_humidity = df['Humidity'].iloc[0]

    # Calcul des statistiques de température
    avg_temp = df['Temperature'].mean()
    max_temp = df['Temperature'].max()

    # Calcul des statistiques d'humidité
    avg_humidity = df['Humidity'].mean()
    max_humidity = df['Humidity'].max()

    # Gauge Chart pour la température
    temp_gauge = go.Figure(go.Indicator(
        mode="gauge+number",
        value=latest_temperature,
        title={'text': "Temperature (°C)", 'font': {'color': colors['text']}},
        gauge={
            'axis': {'range': [0, 50], 'tickcolor': colors['text']},
            'bar': {'color': colors['temperature_color']},
            'bgcolor': colors['background'],
            'borderwidth': 2,
            'bordercolor': "#444"
        }
    ))
    temp_gauge.update_layout(paper_bgcolor=colors['background'], font={'color': colors['text'], 'family': 'Arial'})

    # Graphique de la température avec infobulles
    temp_line_fig = px.line(
        df,
        x='Datetime',
        y='Temperature',
        title="Temperature Over Time",
        labels={'Datetime': "Date and Time", 'Temperature': "Temperature (°C)"},
        hover_data={'Temperature': ':.2f', 'Datetime': '%Y-%m-%d %H:%M:%S'}  # Infobulles détaillées
    )
    temp_line_fig.update_traces(line=dict(color=colors['temperature_color']))
    temp_line_fig.update_yaxes(range=[min(df['Temperature']) - 0.5, max(df['Temperature']) + 0.5])  # Échelle dynamique
    temp_line_fig.update_layout(
        template="plotly_dark",
        paper_bgcolor=colors['background'],
        plot_bgcolor=colors['background'],
        font={'color': colors['text']}
    )

    # Cartes stylisées pour les statistiques de température
    temp_stats = [
        html.Div([
            html.Div("Average", style={'fontSize': '16px', 'color': '#bbbbbb'}),
            html.Div(f"{avg_temp:.2f} °C", style={'fontSize': '24px', 'fontWeight': 'bold'})
        ], style={**card_style, ':hover': card_hover_style}),
        html.Div([
            html.Div("Peak", style={'fontSize': '16px', 'color': '#bbbbbb'}),
            html.Div(f"{max_temp:.2f} °C", style={'fontSize': '24px', 'fontWeight': 'bold'})
        ], style={**card_style, ':hover': card_hover_style})
    ]

    # Gauge Chart pour l'humidité
    humidity_gauge = go.Figure(go.Indicator(
        mode="gauge+number",
        value=latest_humidity,
        title={'text': "Humidity (%)", 'font': {'color': colors['text']}},
        gauge={
            'axis': {'range': [0, 100], 'tickcolor': colors['text']},
            'bar': {'color': colors['humidity_color']},
            'bgcolor': colors['background'],
            'borderwidth': 2,
            'bordercolor': "#444"
        }
    ))
    humidity_gauge.update_layout(paper_bgcolor=colors['background'], font={'color': colors['text'], 'family': 'Arial'})

    # Graphique de l'humidité avec infobulles
    humidity_line_fig = px.line(
        df,
        x='Datetime',
        y='Humidity',
        title="Humidity Over Time",
        labels={'Datetime': "Date and Time", 'Humidity': "Humidity (%)"},
        hover_data={'Humidity': ':.2f', 'Datetime': '%Y-%m-%d %H:%M:%S'}  # Infobulles détaillées
    )
    humidity_line_fig.update_traces(line=dict(color=colors['humidity_color']))
    humidity_line_fig.update_yaxes(range=[min(df['Humidity']) - 1, max(df['Humidity']) + 1])  # Échelle dynamique
    humidity_line_fig.update_layout(
        template="plotly_dark",
        paper_bgcolor=colors['background'],
        plot_bgcolor=colors['background'],
        font={'color': colors['text']}
    )

    # Cartes stylisées pour les statistiques d'humidité
    humidity_stats = [
        html.Div([
            html.Div("Average", style={'fontSize': '16px', 'color': '#bbbbbb'}),
            html.Div(f"{avg_humidity:.2f} %", style={'fontSize': '24px', 'fontWeight': 'bold'})
        ], style={**card_style, ':hover': card_hover_style}),
        html.Div([
            html.Div("Peak", style={'fontSize': '16px', 'color': '#bbbbbb'}),
            html.Div(f"{max_humidity:.2f} %", style={'fontSize': '24px', 'fontWeight': 'bold'})
        ], style={**card_style, ':hover': card_hover_style})
    ]

    # Mise à jour du tableau de données
    table_data = df.to_dict('records')

    # Texte dynamique pour le titre
    last_update_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    live_update_text = f"Last Updated: {last_update_time} (Refreshing every 1 second)"

    return temp_gauge, temp_line_fig, temp_stats, humidity_gauge, humidity_line_fig, humidity_stats, table_data, live_update_text


# Étape 4 : Exécution de l'application
if __name__ == '__main__':
    app.run_server(debug=True, port=8051)