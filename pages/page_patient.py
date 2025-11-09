import pandas as pd
import dash
from dash import html, dcc, Input, Output
import plotly.express as px
import plotly.graph_objects as go
from db_config import get_engine
from geopy.distance import geodesic
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from scipy.spatial.distance import squareform
from scipy.cluster.hierarchy import dendrogram, linkage
from collections import Counter


dash.register_page(__name__, path="/page_patient", name="Parcours Patients")


engine = get_engine()

def load_data():
    personnes = pd.read_sql("SELECT id_personne, nom, prenom, latitude_personne, longitude_personne FROM public.personne", engine)
    
    groupes = pd.read_sql("""
        SELECT p.id_personne, gp.id_groupe, gp.nomgroupe
        FROM public.personne p
        JOIN public.appartient ap ON p.id_personne = ap.id_personne
        JOIN public.groupepersonne gp ON ap.id_groupe = gp.id_groupe
    """, engine)
    
    axes = pd.read_sql("SELECT id_axe, nomaxe FROM public.Axe", engine)
    
    ressources = pd.read_sql("""
        SELECT id_ressource, nom_ressource, description_ressource, typeressource, 
               telephone, email, horaires_ouverture, secteur, conventionnement,
               latitude_ressource, longitude_ressource, id_type
        FROM public.ressource
    """, engine)
    
    pathologies = pd.read_sql("""
        SELECT p.id_personne, t.nomtheme
        FROM public.etre_malade em
        JOIN public.Theme t ON em.id_theme = t.id_theme
        JOIN public.Personne p ON em.id_personne = p.id_personne
    """, engine)
    
    parcours = pd.read_sql("""
        SELECT p.id_parcours, p.id_personne, p.id_parcours_type, pt.nom_parcours_type
        FROM public.Parcours p
        LEFT JOIN public.Parcours_type pt ON p.id_parcours_type = pt.id_parcours_type
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
        FROM public.Utilise_ressource ur
        JOIN public.Parcours p ON ur.id_parcours = p.id_parcours
        JOIN public.Axe a ON ur.id_axe = a.id_axe
        JOIN public.ressource r ON ur.id_ressource = r.id_ressource
        LEFT JOIN public.Parcours_type pt ON p.id_parcours_type = pt.id_parcours_type
    """, engine)
    
    parcours_types = pd.read_sql("SELECT * FROM public.Parcours_type", engine)
    
    prevoit_ressources = pd.read_sql("""
        SELECT pt.id_parcours_type, pt.nom_parcours_type, 
               r.id_ressource, r.nom_ressource, 
               pr.ordre, pr.frequence, pr.nombre_de_visite
        FROM public.Prevoit_ressource pr
        JOIN public.Parcours_type pt ON pt.id_parcours_type = pr.id_parcours_type
        JOIN public.ressource r ON r.id_ressource = pr.id_ressource
        ORDER BY pt.id_parcours_type, pr.ordre
    """, engine)

    evenements["date_evenement"] = pd.to_datetime(evenements["date_evenement"])
    return personnes, groupes, axes, ressources, evenements, pathologies, parcours_types, prevoit_ressources, parcours

personnes_df, groupes_df, axes_df, ressources_df, evenements_df, pathologies_df, parcours_types_df, prevoit_ressources_df, parcours_df = load_data()

personnes_df["identifiant"] = personnes_df["nom"].str[0].str.upper() + personnes_df["prenom"].str[0].str.upper()


# ========== FONCTIONS DE CALCUL DE SIMILARITÉ ==========

def extract_parcours_features(patient_id, evenements_df, axes_df, ressources_df):
    """
    Extrait les caractéristiques d'un parcours patient pour l'analyse de similarité
    
    Returns:
        dict: Dictionnaire contenant les features du parcours
    """
    patient_events = evenements_df[evenements_df["id_personne"] == patient_id].copy()
    
    if patient_events.empty:
        return None
    
    features = {
        'patient_id': patient_id,
        'nb_total_visites': len(patient_events),
        'nb_ressources_uniques': patient_events['id_ressource'].nunique(),
        'nb_axes': patient_events['id_axe'].nunique(),
        'duree_totale': patient_events['duree_consultation'].sum(),
        'duree_moyenne': patient_events['duree_consultation'].mean(),
        
        # Répartition par axe
        'axes_distribution': patient_events.groupby('nomaxe').size().to_dict(),
        
        # Répartition par type de ressource
        'ressources_distribution': patient_events.groupby('nom_ressource').size().to_dict(),
        
        # Types de ressources utilisées
        'types_ressources': set(patient_events['nom_ressource'].unique()),
        
        # Parcours temporel
        'duree_parcours_jours': (patient_events['date_evenement'].max() - 
                                 patient_events['date_evenement'].min()).days,
        
        # Fréquence moyenne des visites
        'freq_visites': len(patient_events) / max(1, (patient_events['date_evenement'].max() - 
                                                       patient_events['date_evenement'].min()).days),
        
        # Séquence des axes (ordre chronologique)
        'sequence_axes': patient_events.sort_values('date_evenement')['nomaxe'].tolist(),
        
        # Séquence des ressources
        'sequence_ressources': patient_events.sort_values('date_evenement')['nom_ressource'].tolist(),
        
        # Distance géographique totale
        'distance_totale': calculate_total_distance(patient_events)
    }
    
    return features

def calculate_total_distance(patient_events):
    """Calcule la distance totale parcourue"""
    from geopy.distance import geodesic
    
    patient_events = patient_events.sort_values('date_evenement')
    points = list(zip(patient_events["latitude"], patient_events["longitude"]))
    valid_points = [(lat, lon) for lat, lon in points if pd.notna(lat) and pd.notna(lon) and lat != 0 and lon != 0]
    
    distance = 0
    for i in range(1, len(valid_points)):
        distance += geodesic(valid_points[i-1], valid_points[i]).km
    
    return distance

def calculate_sequence_similarity(seq1, seq2):
    """
    Calcule la similarité entre deux séquences (Jaccard + ordre)
    """
    if not seq1 or not seq2:
        return 0
    
    # Similarité Jaccard (éléments communs)
    set1, set2 = set(seq1), set(seq2)
    jaccard = len(set1.intersection(set2)) / len(set1.union(set2))
    
    # Similarité de séquence (ordre)
    # On utilise la distance d'édition normalisée
    max_len = max(len(seq1), len(seq2))
    common_subsequence = 0
    
    for i, elem in enumerate(seq1):
        if i < len(seq2) and elem == seq2[i]:
            common_subsequence += 1
    
    sequence_score = common_subsequence / max_len if max_len > 0 else 0
    
    # Moyenne pondérée
    return 0.6 * jaccard + 0.4 * sequence_score

def calculate_distribution_similarity(dist1, dist2):
    """
    Calcule la similarité entre deux distributions (cosine similarity)
    """
    if not dist1 or not dist2:
        return 0
    
    # Créer un vecteur combiné de toutes les clés
    all_keys = set(dist1.keys()).union(set(dist2.keys()))
    
    vec1 = [dist1.get(k, 0) for k in all_keys]
    vec2 = [dist2.get(k, 0) for k in all_keys]
    
    # Cosine similarity
    vec1 = np.array(vec1).reshape(1, -1)
    vec2 = np.array(vec2).reshape(1, -1)
    
    return cosine_similarity(vec1, vec2)[0][0]

def calculate_parcours_similarity(features1, features2, weights=None):
    """
    Calcule un score de similarité global entre deux parcours
    
    Args:
        features1, features2: Dictionnaires de features des parcours
        weights: Dictionnaire de poids pour chaque critère
    
    Returns:
        float: Score de similarité entre 0 et 1
        dict: Détail des scores par critère
    """
    if features1 is None or features2 is None:
        return 0, {}
    
    # Poids par défaut
    if weights is None:
        weights = {
            'axes_distribution': 0.25,
            'ressources_distribution': 0.20,
            'sequence_axes': 0.20,
            'duree_parcours': 0.10,
            'nb_visites': 0.10,
            'distance': 0.10,
            'freq_visites': 0.05
        }
    
    scores = {}
    
    # 1. Similarité de distribution des axes
    scores['axes_distribution'] = calculate_distribution_similarity(
        features1['axes_distribution'], 
        features2['axes_distribution']
    )
    
    # 2. Similarité de distribution des ressources
    scores['ressources_distribution'] = calculate_distribution_similarity(
        features1['ressources_distribution'], 
        features2['ressources_distribution']
    )
    
    # 3. Similarité de séquence des axes
    scores['sequence_axes'] = calculate_sequence_similarity(
        features1['sequence_axes'], 
        features2['sequence_axes']
    )
    
    # 4. Similarité de durée de parcours
    duree1 = features1['duree_parcours_jours']
    duree2 = features2['duree_parcours_jours']
    max_duree = max(duree1, duree2)
    scores['duree_parcours'] = 1 - (abs(duree1 - duree2) / max_duree) if max_duree > 0 else 1
    
    # 5. Similarité du nombre de visites
    nb1 = features1['nb_total_visites']
    nb2 = features2['nb_total_visites']
    max_nb = max(nb1, nb2)
    scores['nb_visites'] = 1 - (abs(nb1 - nb2) / max_nb) if max_nb > 0 else 1
    
    # 6. Similarité de distance parcourue
    dist1 = features1['distance_totale']
    dist2 = features2['distance_totale']
    max_dist = max(dist1, dist2)
    scores['distance'] = 1 - (abs(dist1 - dist2) / max_dist) if max_dist > 0 else 1
    
    # 7. Similarité de fréquence de visites
    freq1 = features1['freq_visites']
    freq2 = features2['freq_visites']
    max_freq = max(freq1, freq2)
    scores['freq_visites'] = 1 - (abs(freq1 - freq2) / max_freq) if max_freq > 0 else 1
    
    # Score global pondéré
    global_score = sum(scores[k] * weights[k] for k in scores.keys())
    
    return global_score, scores

def find_similar_patients(patient_id, all_features, top_n=5, min_similarity=0.3):
    """
    Trouve les patients avec des parcours similaires
    
    Args:
        patient_id: ID du patient de référence
        all_features: Dictionnaire {patient_id: features}
        top_n: Nombre de patients similaires à retourner
        min_similarity: Seuil minimum de similarité
    
    Returns:
        list: Liste de tuples (patient_id, score, détail_scores)
    """
    if patient_id not in all_features:
        return []
    
    reference_features = all_features[patient_id]
    similarities = []
    
    for other_id, other_features in all_features.items():
        if other_id != patient_id:
            score, details = calculate_parcours_similarity(reference_features, other_features)
            if score >= min_similarity:
                similarities.append((other_id, score, details))
    
    # Trier par score décroissant
    similarities.sort(key=lambda x: x[1], reverse=True)
    
    return similarities[:top_n]

def cluster_similar_parcours(all_features, similarity_threshold=0.6):
    """
    Regroupe les parcours similaires en clusters
    
    Args:
        all_features: Dictionnaire {patient_id: features}
        similarity_threshold: Seuil pour considérer deux parcours similaires
    
    Returns:
        list: Liste de clusters (liste de patient_ids)
    """
    patient_ids = list(all_features.keys())
    n = len(patient_ids)
    
    # Matrice de similarité
    similarity_matrix = np.zeros((n, n))
    
    for i in range(n):
        for j in range(i+1, n):
            score, _ = calculate_parcours_similarity(
                all_features[patient_ids[i]], 
                all_features[patient_ids[j]]
            )
            similarity_matrix[i][j] = score
            similarity_matrix[j][i] = score
    
    # Clustering simple basé sur le seuil
    visited = set()
    clusters = []
    
    for i in range(n):
        if i not in visited:
            cluster = [patient_ids[i]]
            visited.add(i)
            
            for j in range(i+1, n):
                if j not in visited and similarity_matrix[i][j] >= similarity_threshold:
                    cluster.append(patient_ids[j])
                    visited.add(j)
            
            if len(cluster) > 1:  # Ne garder que les clusters avec plusieurs patients
                clusters.append(cluster)
    
    return clusters

def analyze_cluster_characteristics(cluster_patient_ids, all_features, evenements_df, axes_df):
    """
    Analyse les caractéristiques communes d'un cluster de patients
    
    Returns:
        dict: Caractéristiques du cluster
    """
    cluster_features = [all_features[pid] for pid in cluster_patient_ids if pid in all_features]
    
    if not cluster_features:
        return {}
    
    # Axes les plus fréquents
    all_axes = []
    for f in cluster_features:
        all_axes.extend(f['sequence_axes'])
    axes_counter = Counter(all_axes)
    
    # Ressources les plus fréquentes
    all_ressources = []
    for f in cluster_features:
        all_ressources.extend(f['sequence_ressources'])
    ressources_counter = Counter(all_ressources)
    
    # Statistiques moyennes
    avg_visites = np.mean([f['nb_total_visites'] for f in cluster_features])
    avg_duree = np.mean([f['duree_parcours_jours'] for f in cluster_features])
    avg_distance = np.mean([f['distance_totale'] for f in cluster_features])
    
    return {
        'taille_cluster': len(cluster_patient_ids),
        'axes_frequents': axes_counter.most_common(3),
        'ressources_frequentes': ressources_counter.most_common(5),
        'moyenne_visites': avg_visites,
        'moyenne_duree_jours': avg_duree,
        'moyenne_distance_km': avg_distance,
        'patient_ids': cluster_patient_ids
    }

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
    
    html.Hr(style={'marginTop': '30px', 'marginBottom': '20px'}),

html.H3("🔍 Analyse de similarité", 
        style={'color': '#2C3E50', 'marginBottom': '15px', 'fontSize': '18px'}),

html.Div([
    html.Label("Type d'analyse"),
    dcc.RadioItems(
        id="similarity-mode",
        options=[
            {"label": "Désactivée", "value": "none"},
            {"label": "Patients similaires", "value": "similar_patients"},
            {"label": "Clusters automatiques", "value": "auto_clusters"}
        ],
        value="none",
        labelStyle={'display': 'block', 'marginBottom': '5px'}
    ),
    
    html.Div(id="similarity-controls", children=[
        html.Label("Nombre de similaires", style={'marginTop': '10px', 'fontSize': '12px'}),
        dcc.Slider(
            id="similarity-top-n",
            min=1, max=10, step=1, value=5,
            marks={i: str(i) for i in [1, 5, 10]},
            tooltip={"placement": "bottom", "always_visible": True}
        ),
        
        html.Label("Seuil minimum", style={'marginTop': '10px', 'fontSize': '12px'}),
        dcc.Slider(
            id="similarity-threshold",
            min=0.1, max=1.0, step=0.05, value=0.3,
            marks={i/10: f'{i/10:.1f}' for i in [1, 5, 10]},
            tooltip={"placement": "bottom", "always_visible": True}
        ),
        
        html.Details([
            html.Summary(" Poids des critères", style={'cursor': 'pointer', 'fontWeight': 'bold', 'marginTop': '10px'}),
            html.Div([
                html.Div([
                    html.Label("Axes:", style={'display': 'inline-block', 'width': '120px', 'fontSize': '11px'}),
                    dcc.Input(id='weight-axes', type='number', value=0.25, min=0, max=1, step=0.05, 
                             style={'width': '60px'})
                ], style={'marginBottom': '3px'}),
                html.Div([
                    html.Label("Ressources:", style={'display': 'inline-block', 'width': '120px', 'fontSize': '11px'}),
                    dcc.Input(id='weight-ressources', type='number', value=0.20, min=0, max=1, step=0.05,
                             style={'width': '60px'})
                ], style={'marginBottom': '3px'}),
                html.Div([
                    html.Label("Séquence:", style={'display': 'inline-block', 'width': '120px', 'fontSize': '11px'}),
                    dcc.Input(id='weight-sequence', type='number', value=0.20, min=0, max=1, step=0.05,
                             style={'width': '60px'})
                ], style={'marginBottom': '3px'}),
                html.Div([
                    html.Label("Durée:", style={'display': 'inline-block', 'width': '120px', 'fontSize': '11px'}),
                    dcc.Input(id='weight-duree', type='number', value=0.10, min=0, max=1, step=0.05,
                             style={'width': '60px'})
                ], style={'marginBottom': '3px'}),
                html.Div([
                    html.Label("Nb visites:", style={'display': 'inline-block', 'width': '120px', 'fontSize': '11px'}),
                    dcc.Input(id='weight-visites', type='number', value=0.10, min=0, max=1, step=0.05,
                             style={'width': '60px'})
                ], style={'marginBottom': '3px'}),
                html.Div([
                    html.Label("Distance:", style={'display': 'inline-block', 'width': '120px', 'fontSize': '11px'}),
                    dcc.Input(id='weight-distance', type='number', value=0.10, min=0, max=1, step=0.05,
                             style={'width': '60px'})
                ], style={'marginBottom': '3px'}),
                html.Div([
                    html.Label("Fréquence:", style={'display': 'inline-block', 'width': '120px', 'fontSize': '11px'}),
                    dcc.Input(id='weight-freq', type='number', value=0.05, min=0, max=1, step=0.05,
                             style={'width': '60px'})
                ]),
                html.Div(id='weight-total', style={'marginTop': '8px', 'fontSize': '11px', 'fontWeight': 'bold'})
            ], style={'marginTop': '10px', 'padding': '10px', 'backgroundColor': '#F8F9FA', 'borderRadius': '5px'})
        ])
    ], style={'marginTop': '10px'})
]),

    html.Div([
        html.Div(id='info-patient'),
        html.Div(id="similarity-results", style={"marginTop": "20px", "marginBottom": "20px"}),
        html.Div(id="stats-axe", style={"marginBottom": 10}),
        html.Div(id="distance-output", style={"marginBottom": 10}),
        html.Div(id="temps-passe-output", style={"marginBottom": 10}),
        
        html.Div(id="cartes-container", children=[
            dcc.Graph(id="carte-ressources", style={"height": "600px"})
        ]),
        
        dcc.Graph(id="timeline-events", style={"height": "300px"}),
        dcc.Graph(id="analyse-frequence", style={"height": "300px"}),
        dcc.Graph(id="similarity-heatmap", style={"height": "500px", "marginTop": "20px"}),
        dcc.Graph(id="similarity-dendrogram", style={"height": "400px", "marginTop": "20px"})
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
# ========== CALLBACKS POUR L'ANALYSE DE SIMILARITÉ ==========

@dash.callback(
    Output('weight-total', 'children'),
    Output('weight-total', 'style'),
    Input('weight-axes', 'value'),
    Input('weight-ressources', 'value'),
    Input('weight-sequence', 'value'),
    Input('weight-duree', 'value'),
    Input('weight-visites', 'value'),
    Input('weight-distance', 'value'),
    Input('weight-freq', 'value')
)
def validate_weights(w_axes, w_ress, w_seq, w_duree, w_vis, w_dist, w_freq):
    """Valide que la somme des poids = 1"""
    total = sum([w_axes or 0, w_ress or 0, w_seq or 0, w_duree or 0, w_vis or 0, w_dist or 0, w_freq or 0])
    
    if abs(total - 1.0) < 0.01:
        return f"✓ Total des poids: {total:.2f}", {'marginTop': '10px', 'fontWeight': 'bold', 'color': '#27AE60'}
    else:
        return f"⚠ Total des poids: {total:.2f} (doit être = 1.0)", {'marginTop': '10px', 'fontWeight': 'bold', 'color': '#E74C3C'}

@dash.callback(
    Output('similarity-controls', 'style'),
    Input('similarity-mode', 'value')
)
def toggle_similarity_controls(mode):
    """Affiche/masque les contrôles de similarité"""
    if mode == "none":
        return {'display': 'none'}
    return {'marginTop': '15px'}

@dash.callback(
    Output("similarity-results", "children"),
    Output("similarity-heatmap", "figure"),
    Output("similarity-dendrogram", "figure"),
    Input("personne-dropdown", "value"),
    Input("similarity-mode", "value"),
    Input("similarity-top-n", "value"),
    Input("similarity-threshold", "value"),
    Input("date-picker-range", "start_date"),
    Input("date-picker-range", "end_date"),
    Input('weight-axes', 'value'),
    Input('weight-ressources', 'value'),
    Input('weight-sequence', 'value'),
    Input('weight-duree', 'value'),
    Input('weight-visites', 'value'),
    Input('weight-distance', 'value'),
    Input('weight-freq', 'value')
)
def analyze_similarity(patient_ids, mode, top_n, threshold, start_date, end_date,
                      w_axes, w_ress, w_seq, w_duree, w_vis, w_dist, w_freq):
    """Analyse de similarité des parcours"""
    
    empty_fig = go.Figure()
    empty_fig.update_layout(title="Aucune analyse de similarité activée")
    
    if mode == "none":
        return html.Div(), empty_fig, empty_fig
    
    # Filtrer les données
    df = evenements_df.copy()
    df = df[(df["date_evenement"] >= pd.to_datetime(start_date)) & 
            (df["date_evenement"] <= pd.to_datetime(end_date))]
    
    # Construire les poids
    weights = {
        'axes_distribution': w_axes or 0.25,
        'ressources_distribution': w_ress or 0.20,
        'sequence_axes': w_seq or 0.20,
        'duree_parcours': w_duree or 0.10,
        'nb_visites': w_vis or 0.10,
        'distance': w_dist or 0.10,
        'freq_visites': w_freq or 0.05
    }
    
    # Extraire les features pour tous les patients concernés
    if mode == "similar_patients":
        if not patient_ids:
            return html.Div("⚠ Veuillez sélectionner au moins un patient"), empty_fig, empty_fig
        
        if not isinstance(patient_ids, list):
            patient_ids = [patient_ids]
        
        # Features pour les patients sélectionnés
        all_features = {}
        for pid in patient_ids:
            features = extract_parcours_features(pid, df, axes_df, ressources_df)
            if features:
                all_features[pid] = features
        
        # Trouver des patients similaires
        all_patient_ids = df['id_personne'].unique()
        for pid in all_patient_ids:
            if pid not in all_features:
                features = extract_parcours_features(pid, df, axes_df, ressources_df)
                if features:
                    all_features[pid] = features
        
        # Résultats de similarité
        results_components = []
        all_similarities = {}
        
        for ref_patient_id in patient_ids:
            if ref_patient_id not in all_features:
                continue
                
            person_info = personnes_df[personnes_df["id_personne"] == ref_patient_id].iloc[0]
            ref_name = f"{person_info['prenom']} {person_info['nom']}"
            
            similar = find_similar_patients(ref_patient_id, all_features, top_n, threshold)
            all_similarities[ref_patient_id] = similar
            
            if not similar:
                results_components.append(html.Div([
                    html.H4(f"Patient de référence: {ref_name}", style={'color': '#2C3E50'}),
                    html.P(f"Aucun patient similaire trouvé (seuil: {threshold})", 
                          style={'color': '#E74C3C'})
                ], style={'marginBottom': '20px', 'padding': '15px', 'backgroundColor': '#FFF3CD', 
                         'borderRadius': '5px'}))
                continue
            
            # Tableau des patients similaires
            similar_rows = []
            for other_id, score, details in similar:
                other_person = personnes_df[personnes_df["id_personne"] == other_id].iloc[0]
                other_name = f"{other_person['prenom']} {other_person['nom']}"
                
                detail_items = [html.Li(f"{k}: {v:.2%}", style={'fontSize': '11px'}) 
                               for k, v in details.items()]
                
                similar_rows.append(html.Tr([
                    html.Td(other_name, style={'fontWeight': 'bold'}),
                    html.Td(f"{score:.1%}", style={'color': '#27AE60' if score > 0.7 else '#F39C12'}),
                    html.Td(html.Ul(detail_items, style={'marginBottom': '0'}))
                ]))
            
            results_components.append(html.Div([
                html.H4(f" Patient de référence: {ref_name}", 
                       style={'color': '#2C3E50', 'marginBottom': '15px'}),
                html.P([
                    html.Strong(f"{len(similar)} patients similaires trouvés"),
                    f" (score ≥ {threshold:.0%})"
                ], style={'color': '#7F8C8D'}),
                
                html.Table([
                    html.Thead(html.Tr([
                        html.Th("Patient", style={'backgroundColor': '#3498DB', 'color': 'white', 'padding': '10px'}),
                        html.Th("Score", style={'backgroundColor': '#3498DB', 'color': 'white', 'padding': '10px'}),
                        html.Th("Détail des critères", style={'backgroundColor': '#3498DB', 'color': 'white', 'padding': '10px'})
                    ])),
                    html.Tbody(similar_rows)
                ], style={'width': '100%', 'borderCollapse': 'collapse', 'border': '1px solid #BDC3C7'})
            ], style={'marginBottom': '30px', 'padding': '20px', 'backgroundColor': '#ECF0F1', 
                     'borderRadius': '8px', 'border': '2px solid #3498DB'}))
        
        # Créer la heatmap de similarité
        if len(all_features) > 1:
            patient_list = list(all_features.keys())
            n = len(patient_list)
            similarity_matrix = np.zeros((n, n))
            
            for i in range(n):
                for j in range(n):
                    if i != j:
                        score, _ = calculate_parcours_similarity(
                            all_features[patient_list[i]], 
                            all_features[patient_list[j]],
                            weights
                        )
                        similarity_matrix[i][j] = score
                    else:
                        similarity_matrix[i][j] = 1.0
            
            # Noms pour les axes
            patient_names = []
            for pid in patient_list:
                p = personnes_df[personnes_df["id_personne"] == pid].iloc[0]
                patient_names.append(f"{p['prenom']} {p['nom']}")
            
            heatmap_fig = go.Figure(data=go.Heatmap(
                z=similarity_matrix,
                x=patient_names,
                y=patient_names,
                colorscale='RdYlGn',
                text=similarity_matrix,
                texttemplate='%{text:.2f}',
                textfont={"size": 10},
                colorbar=dict(title="Similarité")
            ))
            
            heatmap_fig.update_layout(
                title=f"Matrice de similarité des parcours (n={n})",
                xaxis_title="Patients",
                yaxis_title="Patients",
                height=500
            )
        else:
            heatmap_fig = empty_fig
        
        return html.Div(results_components), heatmap_fig, empty_fig
    
    elif mode == "auto_clusters":
        # Clustering automatique sur tous les patients
        all_patient_ids = df['id_personne'].unique()
        
        all_features = {}
        for pid in all_patient_ids:
            features = extract_parcours_features(pid, df, axes_df, ressources_df)
            if features:
                all_features[pid] = features
        
        if len(all_features) < 2:
            return html.Div("⚠ Pas assez de patients pour effectuer un clustering"), empty_fig, empty_fig
        
        # Trouver les clusters
        clusters = cluster_similar_parcours(all_features, threshold)
        
        if not clusters:
            return html.Div([
                html.H4("Aucun cluster identifié", style={'color': '#E74C3C'}),
                html.P(f"Essayez de réduire le seuil de similarité (actuellement: {threshold:.0%})")
            ], style={'padding': '20px', 'backgroundColor': '#FFF3CD', 'borderRadius': '5px'}), empty_fig, empty_fig
        
        # Analyser chaque cluster
        cluster_components = []
        cluster_components.append(html.H3(f"🔍 {len(clusters)} groupes de parcours similaires identifiés", 
                                         style={'color': '#2C3E50', 'marginBottom': '20px'}))
        
        for i, cluster in enumerate(clusters, 1):
            characteristics = analyze_cluster_characteristics(cluster, all_features, df, axes_df)
            
            # Noms des patients du cluster
            patient_names = []
            for pid in cluster:
                p = personnes_df[personnes_df["id_personne"] == pid].iloc[0]
                patient_names.append(f"{p['prenom']} {p['nom']}")
            
            cluster_components.append(html.Div([
                html.H4(f"Cluster {i} - {characteristics['taille_cluster']} patients", 
                       style={'color': '#3498DB', 'marginBottom': '15px'}),
                
                html.Div([
                    html.Strong("👥 Patients: "),
                    html.Span(", ".join(patient_names))
                ], style={'marginBottom': '10px'}),
                
                html.Div([
                    html.H5(" Caractéristiques communes:", style={'color': '#2C3E50', 'marginTop': '15px'}),
                    html.Ul([
                        html.Li(f"Moyenne de {characteristics['moyenne_visites']:.1f} visites par patient"),
                        html.Li(f"Durée moyenne du parcours: {characteristics['moyenne_duree_jours']:.0f} jours"),
                        html.Li(f"Distance moyenne parcourue: {characteristics['moyenne_distance_km']:.1f} km"),
                    ])
                ]),
                
                html.Div([
                    html.H5(" Axes les plus fréquents:", style={'color': '#2C3E50'}),
                    html.Ul([
                        html.Li(f"{axe} ({count} fois)", style={'color': '#27AE60'})
                        for axe, count in characteristics['axes_frequents']
                    ])
                ]),
                
                html.Div([
                    html.H5(" Ressources les plus utilisées:", style={'color': '#2C3E50'}),
                    html.Ul([
                        html.Li(f"{ressource} ({count} fois)")
                        for ressource, count in characteristics['ressources_frequentes']
                    ])
                ])
                
            ], style={'marginBottom': '25px', 'padding': '20px', 'backgroundColor': '#E8F6F3', 
                     'borderRadius': '8px', 'border': '2px solid #3498DB'}))
        
        # Créer la matrice de similarité pour tous les patients
        patient_list = list(all_features.keys())
        n = len(patient_list)
        similarity_matrix = np.zeros((n, n))
        
        for i in range(n):
            for j in range(n):
                if i != j:
                    score, _ = calculate_parcours_similarity(
                        all_features[patient_list[i]], 
                        all_features[patient_list[j]],
                        weights
                    )
                    similarity_matrix[i][j] = score
                else:
                    similarity_matrix[i][j] = 1.0
        
        # Noms pour les axes
        patient_names = []
        for pid in patient_list:
            p = personnes_df[personnes_df["id_personne"] == pid].iloc[0]
            patient_names.append(f"{p['prenom'][0]}.{p['nom']}")
        
        heatmap_fig = go.Figure(data=go.Heatmap(
            z=similarity_matrix,
            x=patient_names,
            y=patient_names,
            colorscale='RdYlGn',
            text=similarity_matrix,
            texttemplate='%{text:.2f}',
            textfont={"size": 8},
            colorbar=dict(title="Score de<br>similarité")
        ))
        
        heatmap_fig.update_layout(
            title=f"Matrice de similarité - Tous les patients (n={n})",
            xaxis_title="Patients",
            yaxis_title="Patients",
            height=600,
            xaxis={'tickangle': -45}
        )
        
        # Créer un dendrogramme simple
        from scipy.cluster.hierarchy import dendrogram, linkage
        from scipy.spatial.distance import squareform
        
        # Convertir la matrice de similarité en matrice de distance
        distance_matrix = 1 - similarity_matrix
        
        # Linkage hierarchique
        condensed_dist = squareform(distance_matrix)
        linkage_matrix = linkage(condensed_dist, method='average')
        
        # Créer le dendrogramme
        dend = dendrogram(linkage_matrix, labels=patient_names, no_plot=True)
        
        dendro_fig = go.Figure()
        
        # Ajouter les branches
        icoord = np.array(dend['icoord'])
        dcoord = np.array(dend['dcoord'])
        
        for i in range(len(icoord)):
            dendro_fig.add_trace(go.Scatter(
                x=icoord[i],
                y=dcoord[i],
                mode='lines',
                line=dict(color='rgb(100,100,100)', width=1.5),
                hoverinfo='skip',
                showlegend=False
            ))
        
        dendro_fig.update_layout(
            title="Dendrogramme de similarité des parcours",
            xaxis={'title': 'Patients', 'ticktext': dend['ivl'], 
                   'tickvals': list(range(5, len(dend['ivl'])*10+5, 10)),
                   'tickangle': -45},
            yaxis={'title': 'Distance (1 - similarité)'},
            height=400,
            showlegend=False
        )
        
        return html.Div(cluster_components), heatmap_fig, dendro_fig
    
    return html.Div(), empty_fig, empty_fig