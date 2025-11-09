import dash
from dash import html, dcc
import dash_bootstrap_components as dbc

# Initialisation de l'application avec Dash Pages
app = dash.Dash(
    __name__,
    use_pages=True,
    suppress_callback_exceptions=True,
    external_stylesheets=[dbc.themes.BOOTSTRAP]
)
server = app.server

app.title = "Visualisation des parcours"

# Layout principal
app.layout = dbc.Container([
    html.H1("Tableau de bord des parcours", className="text-center my-4"),

    dbc.Nav([
        dbc.NavLink("Accueil", href="/", active="exact"),
        dbc.NavLink("Parcours Patients", href="/page_patient", active="exact"),
        dbc.NavLink("Ressources & Catégories", href="/page-ressources", active="exact"),
        dbc.NavLink("Comparer Parcours", href="/comparaison-parcours", active="exact"),
        dbc.NavLink("Groupes Similaires", href="/groupes_similaires", active="exact")
    ], pills=True, className="mb-4"),

    dash.page_container  # Contenu dynamique des pages
], fluid=True)

if __name__ == "__main__":
    app.run(debug=True)
