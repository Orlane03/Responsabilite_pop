import dash
from dash import html, dcc, Input, Output
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
from sklearn.cluster import KMeans
from db_config import get_engine


dash.register_page(__name__, path="/groupes_similaires", name="Groupes similaires")


engine = get_engine()


personnes_df = pd.read_sql("""
    SELECT p.id_personne, p.nom, p.prenom, pt.nom_parcours_type
    FROM Personne p
    LEFT JOIN Parcours pa ON p.id_personne = pa.id_personne
    LEFT JOIN Parcours_type pt ON pa.ID_Parcours_type = pt.ID_Parcours_type
""", engine)


personnes_df['identifiant'] = personnes_df['nom'].str[0].str.upper() + personnes_df['prenom'].str[0].str.upper()


personnes_df['nom_parcours_type'] = personnes_df['nom_parcours_type'].fillna("Non défini")

layout = html.Div([
    html.H2("Regrouper automatiquement les patients par parcours type"),
    
    dcc.Graph(id="cluster-graph"),
    html.Div(id="cluster-output")
])

@dash.callback(
    Output("cluster-graph", "figure"),
    Output("cluster-output", "children"),
    Input("cluster-graph", "id")
)
def regrouper_patients(_):
    
    critere = "nom_parcours_type"
    grouped = personnes_df.groupby(critere)["identifiant"].apply(list).reset_index()
    
    fig = px.bar(grouped, x=critere, y=grouped["identifiant"].apply(len),
                 labels={"x": critere, "y": "Nombre de patients"},
                 title=f"Nombre de patients par {critere}")
    
    
    listes = [html.Li(f"{row[critere]} : {', '.join(row['identifiant'])}") for _, row in grouped.iterrows()]
    
    return fig, html.Ul(listes)