import pandas as pd
import dash
from dash import html, dcc, Input, Output
import plotly.express as px
import plotly.graph_objects as go
from db_config import get_engine
from geopy.distance import geodesic
import numpy as np


dash.register_page(__name__, path="/page_patient", name="Parcours Patients")


engine = get_engine()

def load_data():
    personnes = pd.read_sql("SELECT id_personne, nom, prenom, latitude_personne, longitude_personne FROM personne", engine)
    
    groupes = pd.read_sql("""
        SELECT p.id_personne, gp.id_groupe, gp.nomgroupe
        FROM personne p
        JOIN appartient ap ON p.id_personne = ap.id_personne
        JOIN groupepersonne gp ON ap.id_groupe = gp.id_groupe
    """, engine)
    
    axes = pd.read_sql("SELECT id_axe, nomaxe FROM Axe", engine)
    
    ressources = pd.read_sql("""
        SELECT id_ressource, nom_ressource, description_ressource, typeressource, 
               telephone, email, horaires_ouverture, secteur, conventionnement,
               latitude_ressource, longitude_ressource, id_type
        FROM ressource
    """, engine)
    
    pathologies = pd.read_sql("""
        SELECT p.id_personne, t.nomtheme
        FROM etre_malade em
        JOIN Theme t ON em.id_theme = t.id_theme
        JOIN Personne p ON em.id_personne = p.id_personne
    """, engine)
    
    parcours = pd.read_sql("""
        SELECT p.id_parcours, p.id_personne, p.id_parcours_type, pt.nom_parcours_type
        FROM Parcours p
        LEFT JOIN Parcours_type pt ON p.id_parcours_type = pt.id_parcours_type
    """, engine)
    
    evenements = pd.read_sql("""
        SELECT ur.Date_Consultation AS date_evenement,
               ur.id_axe,
               ur.id_parcours,
               ur.id_ressource,
               p.id_personne,
               a.nomaxe,
               r.nom_ressource AS nom_ressource,
               r.latitude_ressource AS latitude,
               r.longitude_ressource AS longitude,
               ur.duree_consultation,
               pt.nom_parcours_type
        FROM Utilise_ressource ur
        JOIN Parcours p ON ur.id_parcours = p.id_parcours
        JOIN Axe a ON ur.id_axe = a.id_axe
        JOIN ressource r ON ur.id_ressource = r.id_ressource
        LEFT JOIN Parcours_type pt ON p.id_parcours_type = pt.id_parcours_type
    """, engine)
    
    parcours_types = pd.read_sql("SELECT * FROM Parcours_type", engine)
    
    prevoit_ressources = pd.read_sql("""
        SELECT pt.id_parcours_type, pt.nom_parcours_type, 
               r.id_ressource, r.nom_ressource, 
               pr.ordre, pr.frequence, pr.nombre_de_visite
        FROM Prevoit_ressource pr
        JOIN Parcours_type pt ON pt.id_parcours_type = pr.id_parcours_type
        JOIN ressource r ON r.id_ressource = pr.id_ressource
        ORDER BY pt.id_parcours_type, pr.ordre
    """, engine)

    evenements["date_evenement"] = pd.to_datetime(evenements["date_evenement"])
    return personnes, groupes, axes, ressources, evenements, pathologies, parcours_types, prevoit_ressources, parcours

personnes_df, groupes_df, axes_df, ressources_df, evenements_df, pathologies_df, parcours_types_df, prevoit_ressources_df, parcours_df = load_data()

personnes_df["identifiant"] = personnes_df["nom"].str[0].str.upper() + personnes_df["prenom"].str[0].str.upper()

layout = html.Div([
    html.H2("Visualisation des parcours patients par axe"),
    html.Div([
        html.Label("Sélectionner un groupe de patients"),
        dcc.Dropdown(
            id="groupe-dropdown",
            options=[{"label": row["nomgroupe"], "value": row["id_groupe"]} for _, row in groupes_df.drop_duplicates(["id_groupe"]).iterrows()],
            placeholder="Choisir un groupe"
        ),
        html.Label("Sélectionner une ou plusieurs personnes"),
        dcc.Dropdown(
            id="personne-dropdown",
            options=[{"label": f"{row['prenom']} {row['nom']}", "value": row["id_personne"]} for _, row in personnes_df.iterrows()],
            multi=True,
            placeholder="Choisir des personnes"
        ),
        
        html.Div([
            html.Label("Sélectionner un axe à visualiser"),
            dcc.RadioItems(
                id="axe-radio",
                options=[
                    {"label": " Tous les axes", "value": "all"},
                    *[{"label": f" {row['nomaxe']}", "value": row["id_axe"]} for _, row in axes_df.iterrows()]
                ],
                value="all",
                labelStyle={'display': 'block', 'marginBottom': '5px'}
            )
        ], style={'marginBottom': '20px'}),
        
        html.Label("Filtrer par période"),
        dcc.DatePickerRange(
            id="date-picker-range",
            min_date_allowed=evenements_df["date_evenement"].min().date(),
            max_date_allowed=evenements_df["date_evenement"].max().date(),
            start_date=evenements_df["date_evenement"].min().date(),
            end_date=evenements_df["date_evenement"].max().date()
        ),
        
        html.Label("Zone géographique"),
        dcc.RadioItems(
            id="zoom-mode",
            options=[
                {"label": "Auto-ajustement", "value": "auto"},
                {"label": "Vue régionale", "value": "regional"},
                {"label": "Vue locale", "value": "local"}
            ],
            value="auto",
            labelStyle={'display': 'block'}
        ),
        
        html.Label("Gestion des superpositions"),
        dcc.RadioItems(
            id="overlap-mode",
            options=[
                {"label": "Points décalés", "value": "offset"},
                {"label": "Clustering", "value": "cluster"},
                {"label": "Standard", "value": "standard"}
            ],
            value="offset",
            labelStyle={'display': 'block'}
        ),
        
        html.Label("Affichage de l'ordre des visites"),
        dcc.RadioItems(
            id="show-order",
            options=[
                {"label": "Masquer l'ordre", "value": "hide"},
                {"label": "Numéros sur la carte", "value": "numbers"},
                {"label": "Numéros + flèches", "value": "arrows"}
            ],
            value="numbers",
            labelStyle={'display': 'block'}
        )
    ], style={"width": "25%", "float": "left", "padding": "20px"}),

    html.Div([
        html.Div(id='info-patient'),
        html.Div(id="stats-axe", style={"marginBottom": 10}),
        html.Div(id="distance-output", style={"marginBottom": 10}),
        html.Div(id="temps-passe-output", style={"marginBottom": 10}),
        
        html.Div(id="cartes-container", children=[
            dcc.Graph(id="carte-ressources", style={"height": "600px"})
        ]),
        
        dcc.Graph(id="timeline-events", style={"height": "300px"}),
        dcc.Graph(id="analyse-frequence", style={"height": "300px"})
    ], style={"width": "70%", "float": "right", "padding": "20px"})
])

@dash.callback(
    Output("personne-dropdown", "value"),
    Output("personne-dropdown", "options"),
    Input("groupe-dropdown", "value"),
    prevent_initial_call=True
)
def update_personnes_par_groupe(groupe_id):
    all_options = [{"label": f"{row['prenom']} {row['nom']}", "value": row["id_personne"]} for _, row in personnes_df.iterrows()]
    
    if groupe_id:
        personnes_groupe = groupes_df[groupes_df["id_groupe"] == groupe_id]["id_personne"].tolist()
        filtered_options = [opt for opt in all_options if opt["value"] in personnes_groupe]
        return personnes_groupe, filtered_options
    
    return dash.no_update, all_options

def extract_minutes(duree_consultation):
    """CORRECTION: Adaptation pour votre colonne duree_consultation (probablement en minutes)"""
    if pd.isna(duree_consultation):
        return 0
    try:
        return int(float(duree_consultation))
    except:
        return 0

def calculate_zone_bounds(latitudes, longitudes, zoom_mode):
    """Calcule les limites géographiques et le zoom selon le mode sélectionné"""
    if not latitudes or not longitudes:
        return 43.5, -1.45, 10
    
    center_lat = sum(latitudes) / len(latitudes)
    center_lon = sum(longitudes) / len(longitudes)
    
    if zoom_mode == "auto":
        lat_range = max(latitudes) - min(latitudes)
        lon_range = max(longitudes) - min(longitudes)
        max_range = max(lat_range, lon_range)
        
        if max_range < 0.01:
            zoom_level = 15
        elif max_range < 0.05:
            zoom_level = 13
        elif max_range < 0.1:
            zoom_level = 11
        elif max_range < 0.5:
            zoom_level = 9
        else:
            zoom_level = 7
    elif zoom_mode == "regional":
        zoom_level = 8
    else:  
        zoom_level = 12
    
    return center_lat, center_lon, zoom_level

def get_axe_style(axe_name):
    """Définit les styles visuels spécifiques à chaque axe"""
    import unicodedata
    import re
    
    if not axe_name:
        return {'color': '#95A5A6', 'symbol': 'circle', 'line_width': 3, 'size': 10}
    

    axe_original = str(axe_name)
    axe_clean = axe_original.strip().lower()

    axe_clean = unicodedata.normalize('NFKD', axe_clean)
    axe_clean = ''.join(c for c in axe_clean if not unicodedata.combining(c))
    
    axe_clean = re.sub(r'[^\w\s]', ' ', axe_clean)
    axe_clean = re.sub(r'\s+', ' ', axe_clean).strip()
    
    axe_styles = {

        'sante': {'color': '#FF0000', 'symbol': 'circle', 'line_width': 6, 'size': 20},
        'santé': {'color': '#FF0000', 'symbol': 'circle', 'line_width': 6, 'size': 20},
        'health': {'color': '#FF0000', 'symbol': 'circle', 'line_width': 6, 'size': 20},

        'soin': {'color': '#00CED1', 'symbol': 'circle', 'line_width': 5, 'size': 16},
        'soins': {'color': '#00CED1', 'symbol': 'circle', 'line_width': 5, 'size': 16},
        'care': {'color': '#00CED1', 'symbol': 'circle', 'line_width': 5, 'size': 16},
        

        'vie': {'color': '#0000FF', 'symbol': 'circle', 'line_width': 8, 'size': 25},
        'life': {'color': '#0000FF', 'symbol': 'circle', 'line_width': 8, 'size': 25},
    }
    
   
    if axe_clean in axe_styles:
        return axe_styles[axe_clean]
    
    
    for key, style in axe_styles.items():
        if key in axe_clean or axe_clean in key:
            return style
    

    return {'color': '#FF6600', 'symbol': 'circle', 'line_width': 5, 'size': 14}

def apply_offset_to_coordinates(lats, lons, patient_index, total_patients, overlap_mode="offset"):
    """
    NOUVEAU: Applique un décalage aux coordonnées pour éviter les superpositions
    """
    if overlap_mode == "standard" or len(lats) == 0:
        return lats, lons
    
    offset_distance = 0.001 
    
    if overlap_mode == "offset":
       
        angle = (patient_index * 2 * np.pi) / max(total_patients, 1)
        radius = offset_distance * (1 + patient_index * 0.5)
        
        offset_lat = radius * np.cos(angle)
        offset_lon = radius * np.sin(angle)
        
        return [lat + offset_lat for lat in lats], [lon + offset_lon for lon in lons]
    
    elif overlap_mode == "cluster":

        clustered_lats, clustered_lons = [], []
        
        for i, (lat, lon) in enumerate(zip(lats, lons)):
            cluster_offset_lat = offset_distance * (np.random.random() - 0.5) * 2
            cluster_offset_lon = offset_distance * (np.random.random() - 0.5) * 2
            
            clustered_lats.append(lat + cluster_offset_lat)
            clustered_lons.append(lon + cluster_offset_lon)
        
        return clustered_lats, clustered_lons
    
    return lats, lons

def create_legend_for_overlaps(overlap_mode):
    """
    NOUVEAU: Crée une légende explicative pour la gestion des superpositions
    """
    if overlap_mode == "offset":
        return html.Div([
            html.H4("Gestion des superpositions - Points décalés", style={"color": "#2C3E50"}),
            html.P("Les points de chaque patient sont légèrement décalés en spirale pour éviter les chevauchements tout en conservant leur position géographique approximative.", 
                   style={"fontSize": "12px", "color": "#7F8C8D"})
        ], style={"backgroundColor": "#E8F6F3", "padding": "10px", "borderRadius": "5px", "marginTop": "10px"})
    
    elif overlap_mode == "cluster":
        return html.Div([
            html.H4("Gestion des superpositions - Clustering", style={"color": "#2C3E50"}),
            html.P("Les points proches sont regroupés avec de légers décalages aléatoires pour améliorer la lisibilité.", 
                   style={"fontSize": "12px", "color": "#7F8C8D"})
        ], style={"backgroundColor": "#FDF2E9", "padding": "10px", "borderRadius": "5px", "marginTop": "10px"})
    
    else:
        return html.Div([
            html.H4("Affichage standard", style={"color": "#2C3E50"}),
            html.P("Les points sont affichés à leurs coordonnées exactes (superpositions possibles).", 
                   style={"fontSize": "12px", "color": "#7F8C8D"})
        ], style={"backgroundColor": "#F8F9FA", "padding": "10px", "borderRadius": "5px", "marginTop": "10px"})

def create_map_for_axe(df, axe_id, axe_name, patient_ids, zoom_mode, show_order, overlap_mode="offset"):
    """Crée une carte spécifique pour un axe donné avec gestion de l'ordre des visites et des superpositions"""
    axe_df = df[df["id_axe"] == axe_id].copy()
    
    if axe_df.empty:
        fig = go.Figure()
        fig.update_layout(
            title=f"Axe: {axe_name} - Aucune donnée",
            mapbox_style="open-street-map",
            mapbox=dict(center=dict(lat=43.5, lon=-1.45), zoom=10),
            height=500
        )
        return fig
    
    fig = go.Figure()
    axe_style = get_axe_style(axe_name)
    latitudes, longitudes = [], []
    traces_ajoutees = 0
    
    for i, patient_id in enumerate(patient_ids):
        patient_axe_df = axe_df[axe_df["id_personne"] == patient_id].copy()
        if patient_axe_df.empty:
            continue
            
        patient_axe_df = patient_axe_df.sort_values('date_evenement')
        
        try:
            person_info = personnes_df[personnes_df["id_personne"] == patient_id].iloc[0]
        except IndexError:
            continue
        
        lats_raw = patient_axe_df["latitude"].tolist()
        lons_raw = patient_axe_df["longitude"].tolist()
        ressources = patient_axe_df["nom_ressource"].tolist()
        dates = patient_axe_df["date_evenement"].tolist()
        
        valid_coords = []
        valid_ressources = []
        valid_dates = []
        
        for j, (lat, lon, res, date) in enumerate(zip(lats_raw, lons_raw, ressources, dates)):
            if (pd.notna(lat) and pd.notna(lon) and 
                lat != 0 and lon != 0 and 
                isinstance(lat, (int, float)) and isinstance(lon, (int, float)) and
                -90 <= lat <= 90 and -180 <= lon <= 180):
                valid_coords.append((lat, lon))
                valid_ressources.append(res)
                valid_dates.append(date)
        
        if valid_coords:
            lats, lons = zip(*valid_coords)
            
            adjusted_lats, adjusted_lons = apply_offset_to_coordinates(
                list(lats), list(lons), i, len(patient_ids), overlap_mode
            )
            
            base_hover_text = []
            for j, (r, d, orig_lat, orig_lon) in enumerate(zip(valid_ressources, valid_dates, lats, lons)):
                order_text = f"<br>Ordre: {j+1}" if show_order != "hide" else ""
                coord_text = f"<br>Coordonnées: {orig_lat:.4f}, {orig_lon:.4f}"
                text = f"Patient: {person_info['prenom']} {person_info['nom']}<br>Axe: {axe_name}<br>Ressource: {r}<br>Date: {d}{order_text}{coord_text}"
                base_hover_text.append(text)
            
            if len(valid_coords) == 1:
                marker_dict = dict(
                    size=axe_style['size'] * 1.5,
                    color=axe_style['color'],
                    symbol=axe_style['symbol'],
                    opacity=0.8 
                )
                
                fig.add_trace(go.Scattermapbox(
                    lat=adjusted_lats,
                    lon=adjusted_lons,
                    mode="markers",
                    marker=marker_dict,
                    text=base_hover_text,
                    hoverinfo="text",
                    name=f"{person_info['prenom']} {person_info['nom']} - {axe_name} (Point unique)",
                    showlegend=True
                ))
                
                if show_order in ["numbers", "arrows"]:
                    fig.add_trace(go.Scattermapbox(
                        lat=adjusted_lats,
                        lon=adjusted_lons,
                        mode="text",
                        text=["1"],
                        textfont=dict(size=14, color="white"),
                        textposition="middle center",
                        showlegend=False,
                        hoverinfo="skip"
                    ))
                    
            else:
                line_dict = {
                    'width': axe_style['line_width'], 
                    'color': axe_style['color']
                }
                
                mode = "markers+lines"
                if show_order == "arrows":
                    mode = "markers+lines"
                
                fig.add_trace(go.Scattermapbox(
                    lat=adjusted_lats,
                    lon=adjusted_lons,
                    mode=mode,
                    marker=dict(
                        size=axe_style['size'], 
                        color=axe_style['color'],
                        symbol=axe_style['symbol'],
                        opacity=0.8 
                    ),
                    line=line_dict,
                    text=base_hover_text,
                    hoverinfo="text",
                    name=f"{person_info['prenom']} {person_info['nom']} - {axe_name}",
                    showlegend=True
                ))
                
                if show_order in ["numbers", "arrows"]:
                    fig.add_trace(go.Scattermapbox(
                        lat=adjusted_lats,
                        lon=adjusted_lons,
                        mode="text",
                        text=[str(j+1) for j in range(len(adjusted_lats))],
                        textfont=dict(size=12, color="white"),
                        textposition="middle center",
                        showlegend=False,
                        hoverinfo="skip"
                    ))
                
                
                if show_order == "arrows" and len(adjusted_lats) > 1:
                    for j in range(len(adjusted_lats) - 1):
                        
                        mid_lat = (adjusted_lats[j] + adjusted_lats[j+1]) / 2
                        mid_lon = (adjusted_lons[j] + adjusted_lons[j+1]) / 2
                        
                        
                        fig.add_trace(go.Scattermapbox(
                            lat=[mid_lat],
                            lon=[mid_lon],
                            mode="text",
                            text=["→"],
                            textfont=dict(size=16, color=axe_style['color']),
                            textposition="middle center",
                            showlegend=False,
                            hoverinfo="skip"
                        ))
            
            traces_ajoutees += 1
            
            latitudes.extend(lats)
            longitudes.extend(lons)
    
    
    if latitudes and longitudes:
        if len(set(latitudes)) == 1 and len(set(longitudes)) == 1:
            center_lat, center_lon = latitudes[0], longitudes[0]
            zoom_level = 16
        else:
            center_lat, center_lon, zoom_level = calculate_zone_bounds(latitudes, longitudes, zoom_mode)
    else:
        center_lat, center_lon, zoom_level = 43.5, -1.45, 10
    
    order_text = ""
    if show_order == "numbers":
        order_text = " (avec numéros d'ordre)"
    elif show_order == "arrows":
        order_text = " (avec numéros et flèches)"
    
    overlap_text = ""
    if overlap_mode == "offset":
        overlap_text = " - Points décalés"
    elif overlap_mode == "cluster":
        overlap_text = " - Mode clustering"
    
    fig.update_layout(
        title=f"Parcours - Axe: {axe_name} ({len(axe_df)} visites, {traces_ajoutees} traces){order_text}{overlap_text}",
        mapbox_style="open-street-map",
        mapbox=dict(
            center=dict(lat=center_lat, lon=center_lon),
            zoom=zoom_level
        ),
        height=500,
        margin=dict(l=0, r=0, t=30, b=0)
    )
    
    return fig

@dash.callback(
    Output("cartes-container", "children"),
    Output("timeline-events", "figure"),
    Output("info-patient", "children"),
    Output("distance-output", "children"),
    Output("temps-passe-output", "children"),
    Output("stats-axe", "children"),
    Output("analyse-frequence", "figure"),
    Input("personne-dropdown", "value"),
    Input("axe-radio", "value"),
    Input("date-picker-range", "start_date"),
    Input("date-picker-range", "end_date"),
    Input("zoom-mode", "value"),
    Input("show-order", "value"),
    Input("overlap-mode", "value") 
)
def update_visuals(patient_ids, selected_axe, start_date, end_date, zoom_mode, show_order, overlap_mode):
    
    timeline_fig = go.Figure()
    frequence_fig = go.Figure()
    info = ""
    distance_info = ""
    duree_info = ""
    stats_axe = ""
    
    if not patient_ids:
        empty_carte = dcc.Graph(
            figure=go.Figure().update_layout(
                mapbox_style="open-street-map",
                mapbox=dict(center=dict(lat=43.5, lon=-1.45), zoom=10)
            ),
            style={"height": "600px"}
        )
        return [empty_carte], timeline_fig, info, distance_info, duree_info, stats_axe, frequence_fig

    if not isinstance(patient_ids, list):
        patient_ids = [patient_ids]

    
    df = evenements_df.copy()
    df = df[(df["date_evenement"] >= pd.to_datetime(start_date)) & (df["date_evenement"] <= pd.to_datetime(end_date))]
    df = df[df["id_personne"].isin(patient_ids)]

    if df.empty:
        empty_carte = dcc.Graph(
            figure=go.Figure().update_layout(mapbox_style="open-street-map"),
            style={"height": "600px"}
        )
        return [empty_carte], timeline_fig, "Aucune donnée pour la sélection", "", "", "", frequence_fig

    
    cartes_components = []
    
    if selected_axe == "all":
        
        fig = go.Figure()
        latitudes, longitudes = [], []
        
        for i, patient_id in enumerate(patient_ids):
            patient_df = df[df["id_personne"] == patient_id].copy()
            if patient_df.empty:
                continue
                
            
            person_info = personnes_df[personnes_df["id_personne"] == patient_id].iloc[0]
            
            
            for axe_id in patient_df["id_axe"].unique():
                axe_df_patient = patient_df[patient_df["id_axe"] == axe_id].sort_values('date_evenement')
                axe_name = axes_df[axes_df["id_axe"] == axe_id]["nomaxe"].iloc[0]
                
                axe_style = get_axe_style(axe_name)
                
                lats = axe_df_patient["latitude"].tolist()
                lons = axe_df_patient["longitude"].tolist()
                ressources = axe_df_patient["nom_ressource"].tolist()
                dates = axe_df_patient["date_evenement"].tolist()
                
                
                valid_coords = []
                valid_ressources = []
                valid_dates = []
                
                for j, (lat, lon, res, date) in enumerate(zip(lats, lons, ressources, dates)):
                    if pd.notna(lat) and pd.notna(lon) and lat != 0 and lon != 0:
                        valid_coords.append((lat, lon))
                        valid_ressources.append(res)
                        valid_dates.append(date)
                
                if valid_coords:
                    valid_lats, valid_lons = zip(*valid_coords)
                    
                    
                    adjusted_lats, adjusted_lons = apply_offset_to_coordinates(
                        list(valid_lats), list(valid_lons), i, len(patient_ids), overlap_mode
                    )
                    
                    
                    hover_text = []
                    for j, (r, d, orig_lat, orig_lon) in enumerate(zip(valid_ressources, valid_dates, valid_lats, valid_lons)):
                        order_text = f"<br>Ordre dans l'axe: {j+1}" if show_order != "hide" else ""
                        coord_text = f"<br>Coordonnées: {orig_lat:.4f}, {orig_lon:.4f}"
                        text = f"Patient: {person_info['prenom']} {person_info['nom']}<br>Axe: {axe_name}<br>Ressource: {r}<br>Date: {d}{order_text}{coord_text}"
                        hover_text.append(text)
                    
                    line_dict = {
                        'width': axe_style['line_width'], 
                        'color': axe_style['color']
                    }
                    
                    fig.add_trace(go.Scattermapbox(
                        lat=adjusted_lats,
                        lon=adjusted_lons,
                        mode="markers+lines",
                        marker=dict(
                            size=axe_style['size'], 
                            color=axe_style['color'],
                            symbol=axe_style['symbol'],
                            opacity=0.8  
                        ),
                        line=line_dict,
                        text=hover_text,
                        hoverinfo="text",
                        name=f"{person_info['prenom']} {person_info['nom']} - {axe_name}",
                        showlegend=True
                    ))
                    
                    
                    if show_order in ["numbers", "arrows"]:
                        fig.add_trace(go.Scattermapbox(
                            lat=adjusted_lats,
                            lon=adjusted_lons,
                            mode="text",
                            text=[str(j+1) for j in range(len(adjusted_lats))],
                            textfont=dict(size=10, color="white"),
                            textposition="middle center",
                            showlegend=False,
                            hoverinfo="skip"
                        ))
                    
                    
                    latitudes.extend(valid_lats)
                    longitudes.extend(valid_lons)
        
        center_lat, center_lon, zoom_level = calculate_zone_bounds(latitudes, longitudes, zoom_mode)
        
        order_text = ""
        if show_order == "numbers":
            order_text = " - Numéros d'ordre affichés"
        elif show_order == "arrows":
            order_text = " - Numéros d'ordre affichés"
        
        overlap_text = ""
        if overlap_mode == "offset":
            overlap_text = " - Points décalés"
        elif overlap_mode == "cluster":
            overlap_text = " - Mode clustering"
        
        fig.update_layout(
            title=f"Vue d'ensemble - Tous les parcours par axe{order_text}{overlap_text}",
            mapbox_style="open-street-map",
            mapbox=dict(
                center=dict(lat=center_lat, lon=center_lon),
                zoom=zoom_level
            ),
            height=600,
            margin=dict(l=0, r=0, t=30, b=0)
        )
        
        cartes_components.append(dcc.Graph(figure=fig, style={"height": "600px"}))
        
        
        cartes_components.append(create_legend_for_overlaps(overlap_mode))
        
        
        legende_axes = html.Div([
            html.H4("Légende des axes de parcours:", style={"marginBottom": "10px", "color": "#2C3E50"}),
            html.Div([
                html.Div([
                    html.Span("●", style={"color": "#FF0000", "fontSize": "24px", "marginRight": "8px"}),
                    html.Span("SANTÉ", style={"fontWeight": "bold", "marginRight": "10px", "color": "#FF0000"}),
                    html.Span("(cercles rouges très gros)", style={"fontStyle": "italic", "color": "#7F8C8D"})
                ], style={"marginBottom": "5px"}),
                html.Div([
                    html.Span("●", style={"color": "#00CED1", "fontSize": "20px", "marginRight": "8px"}),
                    html.Span("SOINS", style={"fontWeight": "bold", "marginRight": "10px", "color": "#00CED1"}),
                    html.Span("(cercles turquoise gros)", style={"fontStyle": "italic", "color": "#7F8C8D"})
                ], style={"marginBottom": "5px"}),
                html.Div([
                    html.Span("●", style={"color": "#0000FF", "fontSize": "28px", "marginRight": "8px"}),
                    html.Span("VIE", style={"fontWeight": "bold", "marginRight": "10px", "color": "#0000FF"}),
                    html.Span("(cercles bleus énormes)", style={"fontStyle": "italic", "color": "#7F8C8D"})
                ])
            ], style={
                "backgroundColor": "#ECF0F1", 
                "padding": "15px", 
                "borderRadius": "8px",
                "border": "1px solid #BDC3C7"
            })
        ], style={"marginTop": "15px"})
        cartes_components.append(legende_axes)
        
        
        if show_order != "hide":
            legende_ordre = html.Div([
                html.H4("Ordre des visites:", style={"marginBottom": "10px", "color": "#2C3E50"}),
                html.Div([
                    html.Div("• Les numéros blancs sur chaque point indiquent l'ordre chronologique des visites", 
                             style={"marginBottom": "5px"}),
                    html.Div("• L'ordre est calculé par patient et par axe selon la date de consultation",
                             style={"marginBottom": "5px"}),
                    html.Div("• Les lignes relient les visites dans l'ordre chronologique" if show_order == "arrows" else "",
                             style={"fontStyle": "italic", "color": "#7F8C8D"})
                ], style={
                    "backgroundColor": "#F8F9FA", 
                    "padding": "10px", 
                    "borderRadius": "5px",
                    "border": "1px solid #DEE2E6"
                })
            ], style={"marginTop": "10px"})
            cartes_components.append(legende_ordre)
        
        stats_axe = f"Vue d'ensemble - {len(df)} visites totales sur tous les axes"
        
    else:
        
        axe_name = axes_df[axes_df["id_axe"] == selected_axe]["nomaxe"].iloc[0]
        fig = create_map_for_axe(df, selected_axe, axe_name, patient_ids, zoom_mode, show_order, overlap_mode)
        cartes_components.append(dcc.Graph(figure=fig, style={"height": "600px"}))
        
        
        cartes_components.append(create_legend_for_overlaps(overlap_mode))
        
        
        if show_order != "hide":
            info_ordre = html.Div([
                html.P(f"Ordre des visites pour l'axe '{axe_name}':", 
                       style={"fontWeight": "bold", "marginBottom": "10px"}),
                html.Div(id="details-ordre-axe")
            ], style={"marginTop": "15px", "padding": "10px", "backgroundColor": "#F8F9FA", "borderRadius": "5px"})
            
            
            details_ordre = []
            axe_df = df[df["id_axe"] == selected_axe]
            
            for patient_id in patient_ids:
                patient_axe_df = axe_df[axe_df["id_personne"] == patient_id].sort_values('date_evenement')
                if not patient_axe_df.empty:
                    person_info = personnes_df[personnes_df["id_personne"] == patient_id].iloc[0]
                    patient_name = f"{person_info['prenom']} {person_info['nom']}"
                    
                    ordre_list = []
                    for i, (_, row) in enumerate(patient_axe_df.iterrows()):
                        
                        coord_info = ""
                        if overlap_mode != "standard":
                            coord_info = f" [Coord. orig.: {row['latitude']:.4f}, {row['longitude']:.4f}]"
                        ordre_list.append(f"{i+1}. {row['nom_ressource']} ({row['date_evenement'].strftime('%d/%m/%Y')}){coord_info}")
                    
                    details_ordre.append(html.Div([
                        html.Strong(f"{patient_name}:"),
                        html.Ul([html.Li(item, style={"fontSize": "12px"}) for item in ordre_list])
                    ], style={"marginBottom": "10px"}))
            
            info_ordre.children.append(html.Div(details_ordre))
            cartes_components.append(info_ordre)
        
        
        axe_df = df[df["id_axe"] == selected_axe]
        nb_visites = len(axe_df)
        nb_ressources_uniques = axe_df["id_ressource"].nunique()
        order_info = f" (ordre: {show_order})" if show_order != "hide" else ""
        overlap_info = f" (superposition: {overlap_mode})" if overlap_mode != "standard" else ""
        stats_axe = f"Axe {axe_name}: {nb_visites} visites, {nb_ressources_uniques} ressources différentes{order_info}{overlap_info}"

    
    for i, patient_id in enumerate(patient_ids):
        person_info = personnes_df[personnes_df["id_personne"] == patient_id].iloc[0]
        identifiant = person_info["identifiant"]
        nom = person_info["nom"]
        prenom = person_info["prenom"]

        
        patho = pathologies_df[pathologies_df['id_personne'] == patient_id]['nomtheme'].tolist()
        patho_str = f"{nom} ({identifiant}) : {', '.join(patho)}" if patho else f"{nom} ({identifiant}) : Pas de pathologie"

        group_row = groupes_df[groupes_df['id_personne'] == patient_id]
        group_str = f" | Groupe : {group_row['nomgroupe'].iloc[0]}" if not group_row.empty else " | Aucun groupe"

        if i > 0:
            info += " || "
        info += patho_str + group_str

        
        patient_df = df[df["id_personne"] == patient_id]
        
        total_minutes = sum(extract_minutes(duree) for duree in patient_df["duree_consultation"])
        if i > 0:
            duree_info += " | "
        duree_info += f"{nom} ({identifiant}) : {int(total_minutes)} min"

        
        dist_total = 0
        axes_to_consider = [selected_axe] if selected_axe != "all" else patient_df["id_axe"].unique()
        
        for axe_id in axes_to_consider:
            axe_df_calc = patient_df[patient_df["id_axe"] == axe_id].sort_values('date_evenement')
            points = list(zip(axe_df_calc["latitude"], axe_df_calc["longitude"]))
            valid_points = [(lat, lon) for lat, lon in points if pd.notna(lat) and pd.notna(lon) and lat != 0 and lon != 0]
            for j in range(1, len(valid_points)):
                dist_total += geodesic(valid_points[j-1], valid_points[j]).km
        
        if i > 0:
            distance_info += " | "
        distance_info += f"{nom} ({identifiant}) : {round(dist_total, 2)} km"
        
        
        if overlap_mode != "standard" and i == len(patient_ids) - 1:
            distance_info += " (distances calculées sur coordonnées originales)"

    
    if not df.empty:
        df["identifiant"] = df["id_personne"].map(
            {pid: personnes_df[personnes_df["id_personne"] == pid].iloc[0]["identifiant"] 
             for pid in patient_ids}
        )
        
        
        timeline_df = df[df["id_axe"] == selected_axe] if selected_axe != "all" else df
        
        if not timeline_df.empty:
            
            if show_order != "hide":
                timeline_df_with_order = timeline_df.copy()
                timeline_df_with_order['ordre'] = 0
                
                for patient_id in patient_ids:
                    for axe_id in timeline_df_with_order[timeline_df_with_order["id_personne"] == patient_id]["id_axe"].unique():
                        mask = (timeline_df_with_order["id_personne"] == patient_id) & (timeline_df_with_order["id_axe"] == axe_id)
                        patient_axe_data = timeline_df_with_order[mask].sort_values('date_evenement')
                        for i, idx in enumerate(patient_axe_data.index):
                            timeline_df_with_order.loc[idx, 'ordre'] = i + 1
                
                timeline_df = timeline_df_with_order
                hover_data_list = ["nom_ressource", "duree_consultation", "ordre"]
            else:
                hover_data_list = ["nom_ressource", "duree_consultation"]
            
            title = f"Chronologie des événements - {'Axe ' + axes_df[axes_df['id_axe'] == selected_axe]['nomaxe'].iloc[0] if selected_axe != 'all' else 'Tous les axes'}"
            if show_order != "hide":
                title += " (avec ordre des visites)"
                
            timeline_fig = px.scatter(
                timeline_df, x="date_evenement", y="nomaxe",
                color="identifiant",
                hover_data=hover_data_list,
                title=title
            )
            timeline_fig.update_layout(height=300)

    
    if not df.empty:
        
        freq_df = df[df["id_axe"] == selected_axe] if selected_axe != "all" else df
        
        if not freq_df.empty:
            freq_data = freq_df.groupby(['nomaxe', 'identifiant']).size().reset_index(name='nb_visites')
            title = f"Fréquence des visites - {'Axe ' + axes_df[axes_df['id_axe'] == selected_axe]['nomaxe'].iloc[0] if selected_axe != 'all' else 'Tous les axes'}"
            
            if overlap_mode != "standard" and len(patient_ids) > 1:
                title += f" (Mode: {overlap_mode})"
            
            frequence_fig = px.bar(
                freq_data, x="nomaxe", y="nb_visites", color="identifiant",
                title=title
            )
            frequence_fig.update_layout(height=300)

    return cartes_components, timeline_fig, info, distance_info, duree_info, stats_axe, frequence_fig