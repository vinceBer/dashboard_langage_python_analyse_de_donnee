# Importation des bibliothèques et des fonctions nécessaires
import dash
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output
import plotly.express as px
import numpy as np

# Importation des fonctions personnalisées depuis d'autres fichiers Python
from data_processing import load_data, french_athlete_performance, participants_per_year, age_histogram, gender_pie_chart, weight_category_bar_chart, best_performance_plot,meet_country_distribution,competition_timeline,compute_nombre_participants, compute_max_total, compute_max_goodlift
from fonction_ame import create_folium_map
from texts import text1, text2

# Chargement des données à partir des fichiers externes
powerlifting_data_cleaned, _, french_athletes, sheffield_participants = load_data()

nombre_participants = compute_nombre_participants(powerlifting_data_cleaned)
max_name, max_total_kg = compute_max_total(powerlifting_data_cleaned)
max_goodlift_name, max_goodlift_weight, max_goodlift_total_kg = compute_max_goodlift(powerlifting_data_cleaned)

# Initialisation de l'application Dash
app = dash.Dash(__name__, suppress_callback_exceptions=True)

# Définition de la mise en page de l'application
app.layout = html.Div([
    html.Link(rel='stylesheet', href='https://fonts.googleapis.com/icon?family=Material+Icons'),
    dcc.Location(id='url', refresh=False),
    html.Div([
        html.Div([
        html.H2('Powerlifting DashBoard'),
        html.Button([html.I(className='material-icons', children='home'), ' Accueil'], id='home-button', n_clicks=0, style={'marginBottom': '10px', 'width': '100%', 'fontSize': '20px', 'height': '60px'}),
        html.Button([html.I(className='material-icons', children='group'), ' Athlètes'], id='page-2-button', n_clicks=0, style={'marginBottom': '10px', 'width': '100%', 'fontSize': '20px', 'height': '60px'}),
        html.Button([html.I(className='material-icons', children=' fitness_center'), 'Records'], id='page-3-button', n_clicks=0, style={'marginBottom': '10px', 'width': '100%', 'fontSize': '20px', 'height': '60px'}),
        html.Button([html.I(className='material-icons', children=' info'), 'A propos'], id='page-4-button', n_clicks=0, style={'marginBottom': '10px', 'width': '100%', 'fontSize': '20px', 'height': '60px'}),
    ], style={'padding': '20px', 'backgroundColor': '#f0f0f0', 'width': '15%', 'height': '100vh', 'display': 'flex', 'flexDirection': 'column'}),
    html.Div(id='page-content', style={'width': '75%', 'display': 'inline-block', 'padding': '20px'})
], style={
        'display': 'flex',  
        'flex': '1', 
        'minHeight': '100vh'
    }),
])

# Callback pour gérer la navigation entre les pages
@app.callback(Output('url', 'pathname'), [Input('home-button', 'n_clicks'), Input('page-2-button', 'n_clicks'),Input('page-3-button', 'n_clicks'),Input('page-4-button', 'n_clicks')])
def navigate_to_page(home_clicks, page_2_clicks,page_3_clicks,page_4_clicks):
    ctx = dash.callback_context
    if not ctx.triggered: return '/'
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    if button_id == 'home-button': return '/'
    elif button_id == 'page-2-button': return '/page-2'
    elif button_id == 'page-3-button': return '/page-3'
    elif button_id == 'page-4-button': return '/page-4'

def create_info_box(title, content, background_color):
    return html.Div([
        html.H5(title),
        html.P(content)
    ], style={
        'width': '30%', 
        'display': 'inline-block', 
        'background': background_color, 
        'padding': '20px', 
        'color': 'white', 
        'textAlign': 'center',
        'margin': '10px'
    })

# Callback pour afficher le contenu des différentes pages
@app.callback(Output('page-content', 'children'), [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/page-2':
         # Contenu de la page 2 avec des graphiques et des dropdowns interactifs
        return html.Div([
            html.H3('Répartition des athlètes'),
            dcc.Graph(id='age-histogram', figure=age_histogram(powerlifting_data_cleaned)),
            dcc.Graph(id='gender-pie-chart', figure=gender_pie_chart(powerlifting_data_cleaned)),
            dcc.Dropdown(id='weight-category-dropdown', options=[{'label': 'Male', 'value': 'M'}, {'label': 'Female', 'value': 'F'}], value='M', style={'width': '50%'}),
            dcc.Graph(id='weight-category-bar-chart')
        ])
    elif pathname == '/page-3':
         # Contenu de la page 3 avec des dropdowns et un graphique interactif
        return html.Div([
            html.H3('Les records'),
            dcc.Dropdown(id='gender-dropdown', options=[{'label': 'Male', 'value': 'M'}, {'label': 'Female', 'value': 'F'}], value='M', style={'width': '50%'}),
            dcc.Dropdown(id='lift-dropdown', options=[{'label': lift, 'value': lift} for lift in ['Squat', 'Bench', 'Deadlift', 'TotalKg']], value='Squat', style={'width': '50%'}),
            dcc.Input(id='year-input', type='number', value=2018, style={'width': '50%'}),
            dcc.Graph(id='best-performance-plot')
    ])
    elif pathname == '/page-4':
        # Contenu de la page 4 avec des graphiques et des informations sur le powerlifting
        return html.Div([
            html.H3('informations supplémentaires'),
            dcc.Graph(id='meet-country-distribution', figure=meet_country_distribution(powerlifting_data_cleaned)),
            dcc.Graph(id='competition-timeline', figure=competition_timeline(powerlifting_data_cleaned)),
            html.H4('Introduction au powerlifting'),
            html.P(text1),
            html.H4('Information sur le Dataset'),
            html.P(text2)
    ])
    else:
        # Page d'accueil avec une carte interactive et un tableau de données
        return html.Div([html.Div([  
                create_info_box("Nombre de Participants", nombre_participants, 'red'),
                create_info_box("Le plus gros total", f"{max_name}: {max_total_kg} kg", 'blue'),
                create_info_box("Meilleur(e) Athlète goodlift points",
                                f"{max_goodlift_name} Poids: {max_goodlift_weight} kg Total: {max_goodlift_total_kg} kg", 'green'),
            ], style={'display': 'flex', 'justifyContent': 'space-around'}),

            html.Div([html.H5('Nombre de Participant par pays '),
            html.Iframe(srcDoc=create_folium_map(), width='100%', height='500px')], className='card'),
            html.Div([html.Div([html.H5('Performance des Athlètes Francais aux compétitions internationales'),
            dcc.Graph(id='french-athlete-performance', figure=french_athlete_performance(french_athletes), style={'height': '500px'})], className='card', style={'flex': '1'}),
            html.Div([html.H5('Résultats de Participant à Sheffield, la compétition la plus préstigieuse'), 
            dash_table.DataTable(id='sheffield-table', columns=[{'name': col, 'id': col} for col in sheffield_participants.columns], data=sheffield_participants.to_dict('records'), style_table={'overflowX': 'auto', 'maxHeight': '500px', 'overflowY': 'auto'}, style_cell={'textAlign': 'left'}, style_header={'backgroundColor': 'rgb(230, 230, 230)', 'fontWeight': 'bold'})], className='card', style={'flex': '1'})], style={'display': 'flex', 'gap': '20px'})])


# Callback pour mettre à jour le graphique en barres en fonction de la sélection du genre
@app.callback(Output('weight-category-bar-chart', 'figure'), [Input('weight-category-dropdown', 'value')])
def update_weight_category_bar_chart(selected_gender):
    return weight_category_bar_chart(powerlifting_data_cleaned, selected_gender)

# Callback pour mettre à jour le graphique en fonction des sélections du genre, de l'ascenseur et de l'année
@app.callback(Output('best-performance-plot', 'figure'), [Input('gender-dropdown', 'value'), Input('lift-dropdown', 'value'), Input('year-input', 'value')])
def update_best_performance_plot(selected_gender, selected_lift, selected_year):
    return best_performance_plot(powerlifting_data_cleaned, selected_gender, selected_lift, selected_year)


# Configuration des styles externes et des scripts pour l'application
external_stylesheets = [{'href': 'https://fonts.googleapis.com/icon?family=Material+Icons', 'rel': 'stylesheet'}, {'href': 'https://cdnjs.cloudflare.com/ajax/libs/materialize/1.0.0/css/materialize.min.css', 'rel': 'stylesheet'}]
external_scripts = [{'src': 'https://cdnjs.cloudflare.com/ajax/libs/materialize/1.0.0/js/materialize.min.js'}]
app.css.config.serve_locally = False
app.scripts.config.serve_locally = False
app.external_stylesheets = external_stylesheets
app.external_scripts = external_scripts

# Point d'entrée de l'application, exécute l'application en mode de débogage
if __name__ == '__main__':
    # Lancer l'application en mode de débogage
    app.run_server(debug=True)
