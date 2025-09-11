import dash
from dash import html
import dash_bootstrap_components as dbc

dash.register_page(__name__, path="/", name="Accueil")

layout = dbc.Container([
    html.H1("Bienvenue sur le Tableau de bord des Parcours", className="text-center my-4"),

    dbc.Row([
        dbc.Col([
            html.Img(src="https://cdn-icons-png.flaticon.com/512/2920/2920277.png", height="120px"),
            html.H4("Visualiser les parcours", className="text-center mt-3"),
            html.P("Suivre le trajet des patients sur la carte et la ligne du temps."),
            dbc.Button("Voir les parcours", href="/page_patient", color="primary", className="w-100")
        ], width=4),

        dbc.Col([
            html.Img(src="https://cdn-icons-png.flaticon.com/512/3242/3242257.png", height="120px"),
            html.H4("Comparer les patients", className="text-center mt-3"),
            html.P("Comparer deux patients ou plus sur les ressources utilisées."),
            dbc.Button("Comparer", href="/comparaison_patients", color="secondary", className="w-100")
        ], width=4),

        dbc.Col([
            html.Img(src="https://cdn-icons-png.flaticon.com/512/1055/1055644.png", height="120px"),
            html.H4("Groupes similaires", className="text-center mt-3"),
            html.P("Découvrir automatiquement les groupes de patients aux parcours proches."),
            dbc.Button("Découvrir les groupes", href="/groupes_similaires", color="success", className="w-100")
        ], width=4),
    ], className="mb-5"),

    dbc.Row([
        dbc.Col([
            html.Img(src="https://cdn-icons-png.flaticon.com/512/846/846449.png", height="100px"),
            html.H4("Explorer les ressources", className="text-center mt-3"),
            html.P("Liste des ressources disponibles et leur catégorisation."),
            dbc.Button("Explorer", href="/page-ressources", color="info", className="w-100")
        ], width=4),
    ], className="mb-4 justify-content-center")
])
