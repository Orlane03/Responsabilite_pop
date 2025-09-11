import dash
from dash import html, dcc, Input, Output, State, dash_table
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from db_config import get_engine
import numpy as np
from geopy.distance import geodesic


dash.register_page(__name__, path="/comparaison-parcours", name="Comparer Parcours")


engine = get_engine()


parcours_patients_df = pd.read_sql("""
    SELECT
        p.id_parcours, p.id_personne, p.id_parcours_type,
        pt.nom_parcours_type,
        pers.nom, pers.prenom, pers.latitude_personne, pers.longitude_personne,
        ur.id_ressource, ur.date_consultation, ur.duree_consultation, ur.cout_consultation,
        r.nom_ressource as description_ressource, r.latitude_ressource, r.longitude_ressource,
        r.typeressource, a.nomaxe
    FROM parcours p
    JOIN parcours_type pt ON p.id_parcours_type = pt.id_parcours_type
    JOIN personne pers ON p.id_personne = pers.id_personne
    LEFT JOIN utilise_ressource ur ON p.id_parcours = ur.id_parcours
    LEFT JOIN ressource r ON ur.id_ressource = r.id_ressource
    LEFT JOIN axe a ON ur.id_axe = a.id_axe
    ORDER BY p.id_parcours, ur.date_consultation
""", engine)

parcours_patients_df = pd.read_sql("""
    SELECT
        p.id_parcours, p.id_personne, p.id_parcours_type,
        pt.nom_parcours_type,
        pers.nom, pers.prenom, pers.latitude_personne, pers.longitude_personne,
        ur.id_ressource, ur.date_consultation, ur.duree_consultation, ur.cout_consultation,
        r.nom_ressource as description_ressource, r.latitude_ressource, r.longitude_ressource,
        r.typeressource, a.nomaxe
    FROM parcours p
    JOIN parcours_type pt ON p.id_parcours_type = pt.id_parcours_type
    JOIN personne pers ON p.id_personne = pers.id_personne
    LEFT JOIN utilise_ressource ur ON p.id_parcours = ur.id_parcours
    LEFT JOIN ressource r ON ur.id_ressource = r.id_ressource
    LEFT JOIN axe a ON ur.id_axe = a.id_axe
    ORDER BY p.id_parcours, ur.date_consultation
""", engine)

parcours_types_df = pd.read_sql("""
    SELECT 
        pt.id_parcours_type, pt.nom_parcours_type,
        pr.id_ressource, pr.ordre, pr.frequence, pr.nombre_de_visite,
        r.nom_ressource as description_ressource, r.latitude_ressource, r.longitude_ressource,
        r.typeressource
    FROM parcours_type pt
    LEFT JOIN prevoit_ressource pr ON pt.id_parcours_type = pr.id_parcours_type
    LEFT JOIN ressource r ON pr.id_ressource = r.id_ressource
    ORDER BY pt.id_parcours_type, pr.ordre
""", engine)


ressources_df = pd.read_sql("""
    SELECT id_ressource, nom_ressource as description_ressource, typeressource
    FROM ressource
""", engine)


parcours_individuels = parcours_patients_df.groupby(['id_parcours', 'nom', 'prenom', 'nom_parcours_type']).first().reset_index()
parcours_individuels['label'] = parcours_individuels.apply(
    lambda x: f"{x['prenom']} {x['nom']} - {x['nom_parcours_type']} ({x['id_parcours']})", axis=1
)
parcours_types_unique = parcours_types_df[['id_parcours_type', 'nom_parcours_type']].drop_duplicates()

def calculer_distance_geo(lat1, lon1, lat2, lon2):
    if pd.isna(lat1) or pd.isna(lon1) or pd.isna(lat2) or pd.isna(lon2):
        return None
    try:
        return geodesic((lat1, lon1), (lat2, lon2)).kilometers
    except:
        return None

def get_ressource_description(ressource_id):
    """Récupère la description d'une ressource"""
    if ressources_df.empty:
        return f"Ressource {ressource_id}"
    
    ressource_info = ressources_df[ressources_df['id_ressource'] == ressource_id]
    if not ressource_info.empty:
        return ressource_info.iloc[0]['description_ressource']
    return f"Ressource {ressource_id}"

def analyser_parcours_individuel(parcours_id):
    data = parcours_patients_df[parcours_patients_df['id_parcours'] == parcours_id]
    if data.empty:
        return None
    
    ressources = data[data['id_ressource'].notna()]['id_ressource'].tolist()
    distances = []
    patient_lat, patient_lon = data['latitude_personne'].iloc[0], data['longitude_personne'].iloc[0]
    
    for _, row in data[data['id_ressource'].notna()].iterrows():
        dist = calculer_distance_geo(patient_lat, patient_lon, row['latitude_ressource'], row['longitude_ressource'])
        if dist is not None:
            distances.append(dist)
    
    couts_numeriques, couts_par_type = [], {}
    for _, row in data[data['cout_consultation'].notna()].iterrows():
        print(f"Valeur brute: {row['cout_consultation']}, Type: {type(row['cout_consultation'])}")
        try:
            cout_str = str(row['cout_consultation']).lower().strip()
            
            cout_str = cout_str.replace('euros', '').replace('€', '').replace(' ', '')
            cout_str = cout_str.replace(',', '.')
            
            cout_num = float(cout_str)
            couts_numeriques.append(cout_num)
            if row['typeressource']:
                couts_par_type[row['typeressource']] = couts_par_type.get(row['typeressource'], 0) + cout_num
        except Exception as e:
            print(f"Erreur conversion cout: {row['cout_consultation']} - {e}")
            continue
    
    
    visites_reelles = data[data['id_ressource'].notna()]['id_ressource'].value_counts().to_dict()
    
    return {
        'id_parcours': parcours_id,
        'ressources': ressources,
        'distances': distances,
        'distance_totale': sum(distances) if distances else 0,
        'distance_moyenne': np.mean(distances) if distances else 0,
        'cout_total': sum(couts_numeriques) if couts_numeriques else 0,
        'couts_par_type': couts_par_type,
        'types_ressources': list(set(data[data['typeressource'].notna()]['typeressource'].tolist())),
        'axes': list(set(data[data['nomaxe'].notna()]['nomaxe'].tolist())),
        'nb_ressources': len(set(ressources)),
        'visites_reelles': visites_reelles,
        'nb_visites_total_reel': len(ressources),
        'patient_info': {
            'nom': data['nom'].iloc[0] if 'nom' in data.columns else 'Inconnu',
            'prenom': data['prenom'].iloc[0] if 'prenom' in data.columns else 'Inconnu',
            'nom_parcours_type': data['nom_parcours_type'].iloc[0] if 'nom_parcours_type' in data.columns else 'Inconnu'
        }
    }

def analyser_parcours_type(parcours_type_id):
    data = parcours_types_df[parcours_types_df['id_parcours_type'] == parcours_type_id]
    if data.empty:
        return None
    ressources = data[data['id_ressource'].notna()]['id_ressource'].tolist()
    types_ressources = data[data['typeressource'].notna()]['typeressource'].tolist()
    nb_visites_total = data[data['nombre_de_visite'].notna()]['nombre_de_visite'].sum()
    
    
    visites_prevues = {}
    for _, row in data[data['id_ressource'].notna()].iterrows():
        if pd.notna(row['nombre_de_visite']):
            visites_prevues[row['id_ressource']] = int(row['nombre_de_visite'])
    
    return {
        'id_parcours_type': parcours_type_id,  
        'nom': data['nom_parcours_type'].iloc[0],
        'ressources': ressources,
        'types_ressources': list(set(types_ressources)),
        'nb_ressources': len(set(ressources)),
        'nb_visites_prevu': int(nb_visites_total) if pd.notna(nb_visites_total) else 0,
        'visites_prevues': visites_prevues,
        'frequences': data[data['frequence'].notna()]['frequence'].tolist()
    }

def comparer_single_parcours(analysis_ind, analysis_type):
    """Comparaison corrigée - La correspondance inclut la qualité des visites"""
    if not analysis_ind or not analysis_type:
        return None
        
    ressources_ind, ressources_type = set(analysis_ind['ressources']), set(analysis_type['ressources'])
    ressources_communes = ressources_ind.intersection(ressources_type)
    ressources_manquantes = ressources_type - ressources_ind
    ressources_excedent = ressources_ind - ressources_type
    
    
    visites_comparison = {}
    visites_manquees_details = []
    total_visites_manquees = 0
    total_points_correspondance = 0  
    total_points_possibles = 0
    
    
    for ressource in ressources_communes:
        visites_reelles = analysis_ind['visites_reelles'].get(ressource, 0)
        visites_prevues = analysis_type['visites_prevues'].get(ressource, 0)
        ecart = visites_reelles - visites_prevues
        
        
        if visites_prevues > 0:
            
            score_visite = min(100, (visites_reelles / visites_prevues) * 100)
            total_points_correspondance += score_visite
            total_points_possibles += 100
        else:
            
            total_points_correspondance += 50
            total_points_possibles += 50
        
        taux_realisation = (visites_reelles / visites_prevues * 100) if visites_prevues > 0 else 0
        
        visites_comparison[ressource] = {
            'reelles': visites_reelles,
            'prevues': visites_prevues,
            'ecart': ecart,
            'taux_realisation': taux_realisation,
            'score_correspondance': score_visite if visites_prevues > 0 else 50,
            'description': get_ressource_description(ressource)
        }
        
        
        if ecart < 0:
            visites_manquees = abs(ecart)
            total_visites_manquees += visites_manquees
            visites_manquees_details.append({
                'ressource_id': ressource,
                'description': get_ressource_description(ressource),
                'visites_manquees': visites_manquees,
                'visites_reelles': visites_reelles,
                'visites_prevues': visites_prevues
            })
    
    
    for ressource in ressources_manquantes:
        visites_prevues = analysis_type['visites_prevues'].get(ressource, 0)
        if visites_prevues > 0:
            total_visites_manquees += visites_prevues
            total_points_possibles += 100  
            visites_manquees_details.append({
                'ressource_id': ressource,
                'description': get_ressource_description(ressource),
                'visites_manquees': visites_prevues,
                'visites_reelles': 0,
                'visites_prevues': visites_prevues
            })
    
    
    if total_points_possibles > 0:
        taux_correspondance_corrige = total_points_correspondance / total_points_possibles
    else:
        taux_correspondance_corrige = 0
    
    
    taux_correspondance_simple = len(ressources_communes) / len(ressources_type) if ressources_type else 0
    
    
    ressources_communes_details = [
        {
            'id': r, 
            'description': get_ressource_description(r),
            'visites_reelles': analysis_ind['visites_reelles'].get(r, 0),
            'visites_prevues': analysis_type['visites_prevues'].get(r, 0),
            'score_correspondance': visites_comparison.get(r, {}).get('score_correspondance', 0)
        } 
        for r in ressources_communes
    ]
    
    ressources_manquantes_details = [
        {
            'id': r, 
            'description': get_ressource_description(r),
            'visites_prevues': analysis_type['visites_prevues'].get(r, 0),
            'score_correspondance': 0  
        } 
        for r in ressources_manquantes
    ]
    
    ressources_excedent_details = [
        {
            'id': r, 
            'description': get_ressource_description(r),
            'visites_reelles': analysis_ind['visites_reelles'].get(r, 0)
        } 
        for r in ressources_excedent
    ]
    
    return {
        'ressources_communes': list(ressources_communes),
        'ressources_communes_details': ressources_communes_details,
        'ressources_manquantes': list(ressources_manquantes),
        'ressources_manquantes_details': ressources_manquantes_details,
        'ressources_excedent': list(ressources_excedent),
        'ressources_excedent_details': ressources_excedent_details,
        
        
        'taux_correspondance_ressources': taux_correspondance_corrige,  
        'taux_correspondance_simple': taux_correspondance_simple,       
        'score_total_correspondance': total_points_correspondance,
        'score_total_possible': total_points_possibles,
        
        'distance_totale': analysis_ind['distance_totale'],
        'cout_total': analysis_ind['cout_total'],
        'couts_par_type': analysis_ind['couts_par_type'],
        'visites_comparison': visites_comparison,
        'visites_manquees_details': visites_manquees_details,
        'total_visites_manquees': total_visites_manquees,
        'nb_visites_total_reel': analysis_ind['nb_visites_total_reel'],
        'nb_visites_total_prevu': analysis_type['nb_visites_prevu']
    }


def generer_explication_correspondance(comparison_details):
    """Génère une explication claire de la logique de correspondance"""
    
    correspondance_corrigee = comparison_details['taux_correspondance_ressources']
    correspondance_simple = comparison_details['taux_correspondance_simple']
    
    explanation_items = []
    
    
    for ressource_details in comparison_details['ressources_communes_details']:
        reelles = ressource_details['visites_reelles']
        prevues = ressource_details['visites_prevues']
        score = ressource_details['score_correspondance']
        description = ressource_details['description'][:40] + "..."
        
        if reelles < prevues:
            explanation_items.append({
                'type': 'warning',
                'message': f"{description}: {reelles}/{prevues} visites → Score: {score:.0f}% (visites manquées)",
                'impact': f"-{100-score:.0f} points"
            })
        elif reelles == prevues:
            explanation_items.append({
                'type': 'success',
                'message': f"{description}: {reelles}/{prevues} visites → Score: 100% (parfait)",
                'impact': "+100 points"
            })
        else:
            explanation_items.append({
                'type': 'info',
                'message': f"{description}: {reelles}/{prevues} visites → Score: 100% (dépassé)",
                'impact': "+100 points"
            })
    
    
    for ressource_details in comparison_details['ressources_manquantes_details']:
        prevues = ressource_details['visites_prevues']
        description = ressource_details['description'][:40] + "..."
        explanation_items.append({
            'type': 'error',
            'message': f"{description}: 0/{prevues} visites → Score: 0% (ressource non visitée)",
            'impact': "-100 points"
        })
    
    return {
        'correspondance_corrigee': correspondance_corrigee,
        'correspondance_simple': correspondance_simple,
        'explanation_items': explanation_items,
        'resume': f"Correspondance simple (ressources): {correspondance_simple:.1%} vs Correspondance corrigée (avec qualité): {correspondance_corrigee:.1%}"
    }


def create_explanation_widget(comparison_details):
    """Crée un widget d'explication pour l'interface"""
    
    explanation = generer_explication_correspondance(comparison_details)
    
    
    comparison_cards = html.Div([
        html.Div([
            html.H4(f"{explanation['correspondance_simple']:.1%}", 
                   style={'fontSize': '28px', 'margin': '0', 'color': '#3498db'}),
            html.P("Correspondance Simple", style={'margin': '0', 'fontSize': '12px'}),
            html.P("(Ressources présentes)", style={'margin': '0', 'fontSize': '10px', 'fontStyle': 'italic'})
        ], style={'textAlign': 'center', 'padding': '10px', 'backgroundColor': '#d6eaf8', 'borderRadius': '8px', 'width': '45%', 'marginRight': '5%'}),
        
        html.Div([
            html.H4(f"{explanation['correspondance_corrigee']:.1%}", 
                   style={'fontSize': '28px', 'margin': '0', 'color': '#e67e22'}),
            html.P("Correspondance Corrigée", style={'margin': '0', 'fontSize': '12px'}),
            html.P("(Ressources + Qualité visites)", style={'margin': '0', 'fontSize': '10px', 'fontStyle': 'italic'})
        ], style={'textAlign': 'center', 'padding': '10px', 'backgroundColor': '#fdeaa7', 'borderRadius': '8px', 'width': '45%'}),
    ], style={'display': 'flex', 'justifyContent': 'space-between', 'marginBottom': '20px'})
    
    
    explanation_list = []
    for item in explanation['explanation_items']:
        color = {
            'success': '#27ae60',
            'warning': '#f39c12', 
            'error': '#e74c3c',
            'info': '#3498db'
        }.get(item['type'], '#95a5a6')
        
        explanation_list.append(
            html.Div([
                html.Span("●", style={'color': color, 'marginRight': '10px', 'fontSize': '16px'}),
                html.Span(item['message'], style={'fontSize': '14px'}),
                html.Span(f" {item['impact']}", style={'fontSize': '12px', 'color': color, 'fontWeight': 'bold', 'marginLeft': '10px'})
            ], style={'marginBottom': '5px'})
        )
    
    return html.Div([
        html.H4("🔍 Explication de la Correspondance", style={'color': '#2c3e50', 'marginBottom': '15px'}),
        comparison_cards,
        html.Div([
            html.H5("Détail du calcul:", style={'marginBottom': '10px'}),
            html.Div(explanation_list)
        ], style={'backgroundColor': '#f8f9fa', 'padding': '15px', 'borderRadius': '8px'}),
        html.P(explanation['resume'], 
               style={'fontWeight': 'bold', 'textAlign': 'center', 'marginTop': '10px', 'padding': '10px', 'backgroundColor': '#e8f6f3', 'borderRadius': '5px'})
    ])

def analyser_multi_comparaisons(parcours_individuels_ids, parcours_types_ids):
    """Analyse comparative multiple entre plusieurs patients et parcours types"""
    
    if not parcours_individuels_ids or not parcours_types_ids:
        return None
    
    
    if not isinstance(parcours_individuels_ids, list):
        parcours_individuels_ids = [parcours_individuels_ids]
    if not isinstance(parcours_types_ids, list):
        parcours_types_ids = [parcours_types_ids]
    
    results = {
        'patients_analyses': {},
        'types_analyses': {},
        'comparisons': [],
        'matrix_correspondance': {},
        'stats_globales': {}
    }
    
    
    for parcours_id in parcours_individuels_ids:
        analysis = analyser_parcours_individuel(parcours_id)
        if analysis:
            results['patients_analyses'][parcours_id] = analysis
    
    
    for type_id in parcours_types_ids:
        analysis = analyser_parcours_type(type_id)
        if analysis:
            results['types_analyses'][type_id] = analysis
    
    
    for parcours_id, patient_analysis in results['patients_analyses'].items():
        for type_id, type_analysis in results['types_analyses'].items():
            comparison = comparer_single_parcours(patient_analysis, type_analysis)
            if comparison:
                comparison_data = {
                    'patient_id': parcours_id,
                    'type_id': type_id,
                    'patient_label': f"{patient_analysis['patient_info']['prenom']} {patient_analysis['patient_info']['nom']}",
                    'type_label': type_analysis['nom'],
                    'taux_correspondance': comparison['taux_correspondance_ressources'],
                    'distance_totale': comparison['distance_totale'],
                    'cout_total': comparison['cout_total'],
                    'nb_ressources_communes': len(comparison['ressources_communes']),
                    'nb_ressources_manquantes': len(comparison['ressources_manquantes']),
                    'nb_ressources_excedent': len(comparison['ressources_excedent']),
                    'taux_visites': (comparison['nb_visites_total_reel'] / comparison['nb_visites_total_prevu'] * 100) if comparison['nb_visites_total_prevu'] > 0 else 0,
                    'total_visites_manquees': comparison['total_visites_manquees'],
                    'comparison_details': comparison
                }
                results['comparisons'].append(comparison_data)
    
    
    if results['comparisons']:
        correspondances = [c['taux_correspondance'] for c in results['comparisons']]
        distances = [c['distance_totale'] for c in results['comparisons']]
        couts = [c['cout_total'] for c in results['comparisons']]
        taux_visites = [c['taux_visites'] for c in results['comparisons']]
        visites_manquees = [c['total_visites_manquees'] for c in results['comparisons']]
        
        results['stats_globales'] = {
            'nb_comparaisons': len(results['comparisons']),
            'taux_correspondance_moyen': np.mean(correspondances),
            'taux_correspondance_max': max(correspondances),
            'taux_correspondance_min': min(correspondances),
            'distance_moyenne': np.mean(distances),
            'distance_max': max(distances),
            'distance_min': min(distances),
            'cout_moyen': np.mean(couts),
            'cout_max': max(couts),
            'cout_min': min(couts),
            'taux_visites_moyen': np.mean(taux_visites),
            'visites_manquees_moyenne': np.mean(visites_manquees),
            'visites_manquees_total': sum(visites_manquees),
            'meilleure_correspondance': max(results['comparisons'], key=lambda x: x['taux_correspondance'])
        }
        
        
        patient_labels = list(set([c['patient_label'] for c in results['comparisons']]))
        type_labels = list(set([c['type_label'] for c in results['comparisons']]))
        
        matrix = np.zeros((len(patient_labels), len(type_labels)))
        for comparison in results['comparisons']:
            i = patient_labels.index(comparison['patient_label'])
            j = type_labels.index(comparison['type_label'])
            matrix[i][j] = comparison['taux_correspondance']
        
        results['matrix_correspondance'] = {
            'matrix': matrix,
            'patient_labels': patient_labels,
            'type_labels': type_labels
        }
    
    return results

layout = html.Div([
    html.H1("Comparaison Multi-Parcours Patients vs Types", 
            style={'textAlign': 'center', 'color': '#2c3e50', 'marginBottom': '30px'}),
    
    
    html.Div([
        
        html.Div([
            html.Label("Sélectionner les patients à comparer:", 
                      style={'fontWeight': 'bold', 'marginBottom': '10px'}),
            dcc.Dropdown(
                id="multi-parcours-individuels-dropdown",
                options=[{"label": row['label'], "value": row["id_parcours"]} 
                         for _, row in parcours_individuels.iterrows()],
                placeholder="Choisir plusieurs parcours de patients...",
                multi=True,
                style={'marginBottom': '15px'}
            ),
        ], style={'width': '48%', 'display': 'inline-block', 'verticalAlign': 'top'}),
        
        
        html.Div([
            html.Label("Sélectionner les parcours types de référence:", 
                      style={'fontWeight': 'bold', 'marginBottom': '10px'}),
            dcc.Dropdown(
                id="multi-parcours-types-dropdown",
                options=[{"label": row['nom_parcours_type'], "value": row["id_parcours_type"]} 
                         for _, row in parcours_types_unique.iterrows()],
                placeholder="Choisir plusieurs parcours types...",
                multi=True,
                style={'marginBottom': '15px'}
            ),
        ], style={'width': '48%', 'float': 'right', 'display': 'inline-block', 'verticalAlign': 'top'}),
    ], style={'marginBottom': '20px'}),
    
    
    html.Div([
        html.Div([
            html.Button(" Tous les Patients", 
                       id="quick-select-all-patients", 
                       n_clicks=0,
                       style={
                           'backgroundColor': '#2ecc71', 'color': 'white', 'border': 'none',
                           'padding': '8px 16px', 'fontSize': '14px', 'borderRadius': '3px',
                           'marginRight': '5px', 'cursor': 'pointer'
                       }),
            html.Button(" Tous les Types", 
                       id="quick-select-all-types", 
                       n_clicks=0,
                       style={
                           'backgroundColor': '#e67e22', 'color': 'white', 'border': 'none',
                           'padding': '8px 16px', 'fontSize': '14px', 'borderRadius': '3px',
                           'cursor': 'pointer'
                       })
        ], style={'textAlign': 'center', 'marginBottom': '15px'}),
        
        html.Div([
            html.Button(" Analyser les Comparaisons", 
                       id="multi-analyser-btn", 
                       n_clicks=0,
                       style={
                           'backgroundColor': '#3498db', 'color': 'white', 'border': 'none',
                           'padding': '12px 24px', 'fontSize': '16px', 'borderRadius': '5px',
                           'marginRight': '10px', 'cursor': 'pointer'
                       }),
            html.Button(" Réinitialiser", 
                       id="multi-reset-btn", 
                       n_clicks=0,
                       style={
                           'backgroundColor': '#95a5a6', 'color': 'white', 'border': 'none',
                           'padding': '12px 24px', 'fontSize': '16px', 'borderRadius': '5px',
                           'cursor': 'pointer'
                       })
        ], style={'textAlign': 'center'})
    ], style={'marginBottom': '30px'}),
    
    
    html.Div(id="multi-results-container"),
    
    
    dcc.Tabs(id="visualizations-tabs", value='overview', children=[
        dcc.Tab(label=' Vue d\'ensemble', value='overview'),
        dcc.Tab(label=' Heatmap Correspondances', value='heatmap'),
        dcc.Tab(label=' Nuage de Points', value='scatter'),
        dcc.Tab(label=' Tableau Détaillé', value='detailed-table'),
        dcc.Tab(label=' Visites Manquées', value='missed-visits'),
        dcc.Tab(label=' Analyses Avancées', value='advanced')
    ], style={'marginTop': '20px'}),
    
    html.Div(id="tab-content")
])

@dash.callback(
    Output("multi-results-container", "children"),
    Output("tab-content", "children"),
    Input("multi-analyser-btn", "n_clicks"),
    Input("visualizations-tabs", "value"),
    State("multi-parcours-individuels-dropdown", "value"),
    State("multi-parcours-types-dropdown", "value")
)
def update_multi_analysis(n_clicks, active_tab, parcours_ind_ids, parcours_type_ids):
    if n_clicks == 0 or not parcours_ind_ids or not parcours_type_ids:
        
        total_ressources = len(ressources_df)
        total_patients = len(parcours_individuels)
        total_types = len(parcours_types_unique)
        
        return (
            html.Div([
                html.H3(" Bienvenue dans l'outil de comparaison multi-parcours", 
                       style={'color': '#7f8c8d', 'textAlign': 'center'}),
                html.Div([
                    html.Div([
                        html.H4(f"{total_ressources}", style={'fontSize': '36px', 'margin': '0', 'color': '#3498db'}),
                        html.P("Ressources disponibles", style={'margin': '0', 'fontWeight': 'bold'})
                    ], style={'textAlign': 'center', 'padding': '15px', 'backgroundColor': '#ecf0f1', 'borderRadius': '8px', 'margin': '5px'}),
                    
                    html.Div([
                        html.H4(f"{total_patients}", style={'fontSize': '36px', 'margin': '0', 'color': '#e74c3c'}),
                        html.P("Patients suivis", style={'margin': '0', 'fontWeight': 'bold'})
                    ], style={'textAlign': 'center', 'padding': '15px', 'backgroundColor': '#ecf0f1', 'borderRadius': '8px', 'margin': '5px'}),
                    
                    html.Div([
                        html.H4(f"{total_types}", style={'fontSize': '36px', 'margin': '0', 'color': '#27ae60'}),
                        html.P("Parcours types", style={'margin': '0', 'fontWeight': 'bold'})
                    ], style={'textAlign': 'center', 'padding': '15px', 'backgroundColor': '#ecf0f1', 'borderRadius': '8px', 'margin': '5px'}),
                ], style={'display': 'flex', 'justifyContent': 'space-around', 'flexWrap': 'wrap', 'margin': '20px 0'}),
                
                html.P("Sélectionnez plusieurs patients et parcours types, puis cliquez sur 'Analyser' pour commencer.",
                      style={'textAlign': 'center', 'fontSize': '16px'})
            ], style={'padding': '40px', 'backgroundColor': '#ecf0f1', 'borderRadius': '10px', 'margin': '20px'}),
            html.Div()
        )
    
    results = analyser_multi_comparaisons(parcours_ind_ids, parcours_type_ids)
    
    if not results or not results['comparisons']:
        return (
            html.Div(" Erreur lors de l'analyse ou aucune comparaison possible.", 
                    style={'color': 'red', 'textAlign': 'center', 'fontSize': '18px'}),
            html.Div()
        )
    
    stats = results['stats_globales']
    best_match = stats['meilleure_correspondance']
    
    summary = html.Div([
        html.H2(" Résumé de l'Analyse", style={'color': '#2c3e50'}),
        html.Div([
            html.Div([
                html.H4(f"{len(parcours_ind_ids)}", style={'fontSize': '36px', 'margin': '0', 'color': '#3498db'}),
                html.P("Patients", style={'margin': '0', 'fontWeight': 'bold'})
            ], style={'textAlign': 'center', 'padding': '15px', 'backgroundColor': '#ecf0f1', 'borderRadius': '8px', 'margin': '5px'}),
            
            html.Div([
                html.H4(f"{len(parcours_type_ids)}", style={'fontSize': '36px', 'margin': '0', 'color': '#e74c3c'}),
                html.P("Parcours Types", style={'margin': '0', 'fontWeight': 'bold'})
            ], style={'textAlign': 'center', 'padding': '15px', 'backgroundColor': '#ecf0f1', 'borderRadius': '8px', 'margin': '5px'}),
            
            html.Div([
                html.H4(f"{stats['nb_comparaisons']}", style={'fontSize': '36px', 'margin': '0', 'color': '#27ae60'}),
                html.P("Comparaisons", style={'margin': '0', 'fontWeight': 'bold'})
            ], style={'textAlign': 'center', 'padding': '15px', 'backgroundColor': '#ecf0f1', 'borderRadius': '8px', 'margin': '5px'}),
            
            html.Div([
                html.H4(f"{stats['taux_correspondance_moyen']:.1%}", style={'fontSize': '36px', 'margin': '0', 'color': '#f39c12'}),
                html.P("Corresp. Moyenne", style={'margin': '0', 'fontWeight': 'bold'})
            ], style={'textAlign': 'center', 'padding': '15px', 'backgroundColor': '#ecf0f1', 'borderRadius': '8px', 'margin': '5px'}),
            
            html.Div([
                html.H4(f"{int(stats['visites_manquees_total'])}", style={'fontSize': '36px', 'margin': '0', 'color': '#e74c3c'}),
                html.P("Visites Manquées", style={'margin': '0', 'fontWeight': 'bold'})
            ], style={'textAlign': 'center', 'padding': '15px', 'backgroundColor': '#ecf0f1', 'borderRadius': '8px', 'margin': '5px'}),
        ], style={'display': 'flex', 'justifyContent': 'space-around', 'flexWrap': 'wrap', 'marginBottom': '20px'}),
        
        html.Div([
            html.H4(" Meilleure Correspondance:", style={'color': '#27ae60'}),
            html.P(f"{best_match['patient_label']} ↔ {best_match['type_label']}", style={'fontSize': '16px', 'fontWeight': 'bold'}),
            html.P(f"Taux de correspondance: {best_match['taux_correspondance']:.1%}", style={'fontSize': '14px'})
        ], style={'backgroundColor': '#d5f4e6', 'padding': '15px', 'borderRadius': '8px', 'marginBottom': '20px'})
    ])
    
    
    tab_content = generate_tab_content(active_tab, results)
    
    return summary, tab_content

def generate_tab_content(active_tab, results):
    """Génère le contenu pour chaque onglet"""
    
    if active_tab == 'overview':
        return generate_overview_content(results)
    elif active_tab == 'heatmap':
        return generate_heatmap_content(results)
    elif active_tab == 'scatter':
        return generate_scatter_content(results)
    elif active_tab == 'detailed-table':
        return generate_detailed_table_content(results)
    elif active_tab == 'missed-visits':
        return generate_missed_visits_content(results)
    elif active_tab == 'advanced':
        return generate_advanced_content(results)
    else:
        return html.Div()

def generate_overview_content(results):
    """Génère le contenu de la vue d'ensemble"""
    stats = results['stats_globales']
    
    
    fig_stats = go.Figure()
    fig_stats.add_trace(go.Bar(
        x=['Correspondance Moyenne', 'Correspondance Max', 'Distance Moyenne', 'Coût Moyen'],
        y=[stats['taux_correspondance_moyen']*100, stats['taux_correspondance_max']*100, 
           stats['distance_moyenne'], stats['cout_moyen']],
        marker_color=['#3498db', '#27ae60', '#f39c12', '#e74c3c'],
        text=[f"{stats['taux_correspondance_moyen']:.1%}", f"{stats['taux_correspondance_max']:.1%}",
              f"{stats['distance_moyenne']:.1f} km", f"{stats['cout_moyen']:.0f}€"]
    ))
    fig_stats.update_layout(title=" Statistiques Principales", showlegend=False)
    fig_stats.update_traces(textposition='outside')
    
    return html.Div([
        dcc.Graph(figure=fig_stats),
        html.Div([
            html.H4(" Statistiques Détaillées"),
            html.P(f"• Taux de correspondance: {stats['taux_correspondance_min']:.1%} - {stats['taux_correspondance_max']:.1%}"),
            html.P(f"• Distance: {stats['distance_min']:.1f} - {stats['distance_max']:.1f} km"),
            html.P(f"• Coût: {stats['cout_min']:.0f} - {stats['cout_max']:.0f}€"),
            html.P(f"• Taux de visites moyen: {stats['taux_visites_moyen']:.1f}%"),
            html.P(f"• Visites manquées total: {int(stats['visites_manquees_total'])} visites")
        ], style={'backgroundColor': '#f8f9fa', 'padding': '20px', 'borderRadius': '8px'})
    ])

def generate_heatmap_content(results):
    """Génère la heatmap des correspondances"""
    matrix_data = results['matrix_correspondance']
    
    fig_heatmap = px.imshow(
        matrix_data['matrix'],
        x=matrix_data['type_labels'],
        y=matrix_data['patient_labels'],
        color_continuous_scale='RdYlGn',
        aspect='auto',
        title=" Matrice des Correspondances (Patient vs Parcours Type)"
    )
    
    fig_heatmap.update_layout(
        xaxis_title="Parcours Types",
        yaxis_title="Patients",
        height=500
    )
    
    return html.Div([
        dcc.Graph(figure=fig_heatmap),
        html.P(" Correspondance entre le patient et le parcours type.",
               style={'fontStyle': 'italic', 'textAlign': 'center', 'marginTop': '10px'})
    ])

def generate_scatter_content(results):
    """Génère le nuage de points avec taux de correspondance"""
    comparisons = results['comparisons']
    
    
    fig_scatter = px.scatter(
        x=[c['distance_totale'] for c in comparisons],
        y=[c['cout_total'] for c in comparisons],
        size=[c['taux_correspondance']*100 for c in comparisons],
        color=[c['taux_correspondance']*100 for c in comparisons],
        hover_name=[f"{c['patient_label']} vs {c['type_label']}" for c in comparisons],
        hover_data={
            'Correspondance': [f"{c['taux_correspondance']:.1%}" for c in comparisons],
            'Visites manquées': [c['total_visites_manquees'] for c in comparisons],
            'Taux visites': [f"{c['taux_visites']:.1f}%" for c in comparisons]
        },
        labels={'x': 'Distance Totale (km)', 'y': 'Coût Total (€)', 'color': 'Correspondance (%)'},
        title=" Nuage de Points: Coût vs Distance (taille = correspondance)",
        color_continuous_scale='RdYlGn',
        size_max=50
    )
    
    fig_scatter.update_layout(height=600)
    
    
    fig_scatter2 = px.scatter(
        x=[c['taux_correspondance']*100 for c in comparisons],
        y=[c['total_visites_manquees'] for c in comparisons],
        size=[c['cout_total'] for c in comparisons],
        color=[c['taux_visites'] for c in comparisons],
        hover_name=[f"{c['patient_label']} vs {c['type_label']}" for c in comparisons],
        labels={'x': 'Taux de Correspondance (%)', 'y': 'Visites Manquées', 'color': 'Taux Visites (%)'},
        title=" Correspondance vs Visites Manquées (taille = coût)",
        color_continuous_scale='RdYlBu_r',
        size_max=40
    )
    
    fig_scatter2.update_layout(height=500)
    
    return html.Div([
        dcc.Graph(figure=fig_scatter),
        dcc.Graph(figure=fig_scatter2),
        html.Div([
            html.P(" Dans le premier graphique, les points en vert avec une grande taille représentent les meilleures correspondances."),
            html.P(" Dans le second graphique, l'objectif est d'avoir peu de visites manquées avec un haut taux de correspondance.")
        ], style={'backgroundColor': '#e8f6f3', 'padding': '15px', 'borderRadius': '8px', 'marginTop': '10px'})
    ])

def generate_detailed_table_content(results):
    """Génère le tableau détaillé avec correspondances des ressources"""
    comparisons = results['comparisons']
    
    table_data = []
    for c in comparisons:
        details = c['comparison_details']
        
        
        ressources_communes_str = ", ".join([
            f"{r['description'][:30]}... ({r['visites_reelles']}/{r['visites_prevues']})" 
            for r in details['ressources_communes_details'][:3]  
        ])
        if len(details['ressources_communes_details']) > 3:
            ressources_communes_str += f" +{len(details['ressources_communes_details'])-3} autres"
        
        ressources_manquantes_str = ", ".join([
            f"{r['description'][:30]}... ({r['visites_prevues']})" 
            for r in details['ressources_manquantes_details'][:3]
        ])
        if len(details['ressources_manquantes_details']) > 3:
            ressources_manquantes_str += f" +{len(details['ressources_manquantes_details'])-3} autres"
        
        table_data.append({
            'Patient': c['patient_label'],
            'Parcours Type': c['type_label'],
            'Correspondance': f"{c['taux_correspondance']:.1%}",
            'Distance (km)': f"{c['distance_totale']:.1f}",
            'Coût (€)': f"{c['cout_total']:.0f}",
            'Ressources Communes': f"{c['nb_ressources_communes']}",
            'Détails Ressources Communes': ressources_communes_str if ressources_communes_str else "Aucune",
            'Ressources Manquantes': f"{c['nb_ressources_manquantes']}",
            'Détails Ressources Manquantes': ressources_manquantes_str if ressources_manquantes_str else "Aucune",
            'Taux Visites': f"{c['taux_visites']:.1f}%",
            'Visites Manquées': f"{c['total_visites_manquees']}"
        })
    
    if not table_data:
        return html.Div("Aucune donnée à afficher.", style={'textAlign': 'center'})
    
    return html.Div([
        html.H4(" Tableau Détaillé des Comparaisons"),
        html.P(" Format des ressources: Description (Visites réelles/Visites prévues)", 
               style={'fontStyle': 'italic', 'marginBottom': '10px'}),
        dash_table.DataTable(
            data=table_data,
            columns=[
                {"name": "Patient", "id": "Patient"},
                {"name": "Parcours Type", "id": "Parcours Type"},
                {"name": "Correspondance", "id": "Correspondance"},
                {"name": "Distance (km)", "id": "Distance (km)"},
                {"name": "Coût (€)", "id": "Coût (€)"},
                {"name": "Res. Communes", "id": "Ressources Communes"},
                {"name": "Détails Ressources Communes", "id": "Détails Ressources Communes"},
                {"name": "Res. Manquantes", "id": "Ressources Manquantes"},
                {"name": "Détails Ressources Manquantes", "id": "Détails Ressources Manquantes"},
                {"name": "Taux Visites", "id": "Taux Visites"},
                {"name": "Visites Manquées", "id": "Visites Manquées"}
            ],
            style_cell={
                'textAlign': 'left', 
                'padding': '8px',
                'whiteSpace': 'normal',
                'height': 'auto',
                'fontSize': '12px',
                'minWidth': '80px', 'width': '100px', 'maxWidth': '180px'
            },
            style_header={
                'backgroundColor': '#3498db', 
                'color': 'white', 
                'fontWeight': 'bold',
                'textAlign': 'center'
            },
            style_data_conditional=[
                {
                    'if': {'row_index': 'odd'},
                    'backgroundColor': '#f8f9fa'
                },
                {
                    'if': {'filter_query': '{Correspondance} > 80%'},
                    'backgroundColor': '#d5f4e6',
                },
                {
                    'if': {'filter_query': '{Correspondance} < 50%'},
                    'backgroundColor': '#fadbd8',
                }
            ],
            style_data={
                'whiteSpace': 'normal',
                'height': 'auto',
                'lineHeight': '15px'
            },
            sort_action="native",
            filter_action="native",
            page_action="native",
            page_current=0,
            page_size=10,
            tooltip_data=[
                {
                    column: {'value': str(row[column]), 'type': 'markdown'}
                    for column in row.keys()
                } for row in table_data
            ],
            tooltip_duration=None
        )
    ])

def generate_missed_visits_content(results):
    """Génère le contenu spécifique aux visites manquées"""
    comparisons = results['comparisons']
    
    
    all_missed_visits = []
    for c in comparisons:
        details = c['comparison_details']
        for missed in details['visites_manquees_details']:
            all_missed_visits.append({
                'patient': c['patient_label'],
                'parcours_type': c['type_label'],
                'ressource_description': missed['description'],
                'visites_manquees': missed['visites_manquees'],
                'visites_reelles': missed['visites_reelles'],
                'visites_prevues': missed['visites_prevues'],
                'taux_realisation': (missed['visites_reelles'] / missed['visites_prevues'] * 100) if missed['visites_prevues'] > 0 else 0
            })
    
    if not all_missed_visits:
        return html.Div([
            html.H4(" Aucune Visite Manquée Détectée"),
            html.P("Toutes les visites prévues ont été réalisées pour les comparaisons sélectionnées.",
                  style={'textAlign': 'center', 'fontStyle': 'italic'})
        ], style={'textAlign': 'center', 'padding': '40px'})
    
    
    patients_missed = {}
    for missed in all_missed_visits:
        patient = missed['patient']
        if patient not in patients_missed:
            patients_missed[patient] = 0
        patients_missed[patient] += missed['visites_manquees']
    
    
    patient_data = []
    for patient, count in patients_missed.items():
        patient_data.append({'Patient': patient, 'Visites_Manquees': count})
    
    fig_missed_by_patient = px.bar(
        patient_data,
        x='Patient',
        y='Visites_Manquees',
        title=" Visites Manquées par Patient",
        labels={'Visites_Manquees': 'Nombre de Visites Manquées'},
        color='Visites_Manquees',
        color_continuous_scale='Reds'
    )
    fig_missed_by_patient.update_layout(showlegend=False)
    
    
    ressources_missed = {}
    for missed in all_missed_visits:
        ressource = missed['ressource_description'][:50] + "..." if len(missed['ressource_description']) > 50 else missed['ressource_description']
        if ressource not in ressources_missed:
            ressources_missed[ressource] = 0
        ressources_missed[ressource] += missed['visites_manquees']
    
    
    top_missed_resources = sorted(ressources_missed.items(), key=lambda x: x[1], reverse=True)[:10]
    
    
    resource_df = pd.DataFrame({
        'Ressource': [item[0] for item in top_missed_resources],
        'Visites_Manquees': [item[1] for item in top_missed_resources]
    })
    
    fig_missed_resources = px.bar(
        resource_df,  
        x='Visites_Manquees',
        y='Ressource',
        orientation='h',
        title=" Top 10 des Ressources les Plus Manquées",
        labels={'Visites_Manquees': 'Nombre de Visites Manquées'},
        color='Visites_Manquees',
        color_continuous_scale='Oranges'
    )
    fig_missed_resources.update_layout(showlegend=False, height=500)
    
    
    missed_table_data = []
    for missed in all_missed_visits:
        missed_table_data.append({
            'Patient': missed['patient'],
            'Parcours Type': missed['parcours_type'],
            'Ressource': missed['ressource_description'][:60] + "..." if len(missed['ressource_description']) > 60 else missed['ressource_description'],
            'Visites Manquées': missed['visites_manquees'],
            'Visites Réelles': missed['visites_reelles'],
            'Visites Prévues': missed['visites_prevues'],
            'Taux Réalisation': f"{missed['taux_realisation']:.1f}%"
        })
    
    
    total_missed = sum([missed['visites_manquees'] for missed in all_missed_visits])
    total_expected = sum([missed['visites_prevues'] for missed in all_missed_visits])
    avg_realization = (1 - total_missed / total_expected) * 100 if total_expected > 0 else 100
    
    stats_card = html.Div([
        html.H4(" Statistiques des Visites Manquées"),
        html.Div([
            html.Div([
                html.H3(f"{total_missed}", style={'color': '#e74c3c', 'margin': '0'}),
                html.P("Visites Manquées Total", style={'margin': '0'})
            ], style={'textAlign': 'center', 'padding': '15px', 'backgroundColor': '#fadbd8', 'borderRadius': '8px', 'margin': '5px'}),
            
            html.Div([
                html.H3(f"{total_expected}", style={'color': '#3498db', 'margin': '0'}),
                html.P("Visites Prévues Total", style={'margin': '0'})
            ], style={'textAlign': 'center', 'padding': '15px', 'backgroundColor': '#d6eaf8', 'borderRadius': '8px', 'margin': '5px'}),
            
            html.Div([
                html.H3(f"{avg_realization:.1f}%", style={'color': '#27ae60', 'margin': '0'}),
                html.P("Taux de Réalisation Global", style={'margin': '0'})
            ], style={'textAlign': 'center', 'padding': '15px', 'backgroundColor': '#d5f4e6', 'borderRadius': '8px', 'margin': '5px'}),
        ], style={'display': 'flex', 'justifyContent': 'space-around', 'marginBottom': '20px'})
    ])
    
    return html.Div([
        stats_card,
        dcc.Graph(figure=fig_missed_by_patient),
        dcc.Graph(figure=fig_missed_resources),
        html.H4(" Détail des Visites Manquées", style={'marginTop': '30px'}),
        dash_table.DataTable(
            data=missed_table_data,
            columns=[{"name": i, "id": i} for i in missed_table_data[0].keys()] if missed_table_data else [],
            style_cell={'textAlign': 'left', 'padding': '10px', 'fontSize': '12px'},
            style_header={'backgroundColor': '#e74c3c', 'color': 'white', 'fontWeight': 'bold'},
            style_data_conditional=[
                {
                    'if': {'row_index': 'odd'},
                    'backgroundColor': '#f8f9fa'
                },
                {
                    'if': {'filter_query': '{Taux Réalisation} = "0.0%"'},
                    'backgroundColor': '#fadbd8',
                },
                {
                    'if': {'filter_query': '{Taux Réalisation} > "50.0%"'},
                    'backgroundColor': '#fdf2e9',
                }
            ],
            sort_action="native",
            filter_action="native",
            page_action="native",
            page_current=0,
            page_size=15
        )
    ])

def generate_advanced_content(results):
    """Génère les analyses avancées"""
    if len(results['patients_analyses']) < 2:
        return html.Div([
            html.H4("Analyse Avancée Non Disponible"),
            html.P("L'analyse avancée nécessite la sélection d'au moins 2 patients pour la comparaison."),
            html.P("Veuillez sélectionner plusieurs patients dans le menu déroulant ci-dessus.")
        ], style={'textAlign': 'center', 'padding': '40px', 'backgroundColor': '#f8f9fa'})
    
    comparisons = results['comparisons']
    
    
    fig_scatter_advanced = px.scatter(
        x=[c['distance_totale'] for c in comparisons],
        y=[c['cout_total'] for c in comparisons],
        size=[c['taux_correspondance']*100 for c in comparisons],
        color=[c['taux_correspondance']*100 for c in comparisons],
        hover_name=[f"{c['patient_label']} vs {c['type_label']}" for c in comparisons],
        hover_data={
            'Correspondance': [f"{c['taux_correspondance']:.1%}" for c in comparisons],
            'Visites manquées': [c['total_visites_manquees'] for c in comparisons],
            'Ressources communes': [c['nb_ressources_communes'] for c in comparisons],
            'Ressources manquantes': [c['nb_ressources_manquantes'] for c in comparisons]
        },
        labels={
            'x': 'Distance Totale (km)', 
            'y': 'Coût Total (€)', 
            'color': 'Correspondance (%)',
            'size': 'Correspondance (%)'
        },
        title=" Performance des Parcours: Coût vs Distance (Taille = Qualité de correspondance)",
        color_continuous_scale='RdYlGn',
        size_max=50
    )
    
    fig_scatter_advanced.update_layout(
        height=500,
        xaxis_title="Distance parcourue (km) → Moins c'est mieux",
        yaxis_title="Coût total (€) → Moins c'est mieux",
        coloraxis_colorbar_title="Correspondance (%)"
    )
    
    
    avg_distance = np.mean([c['distance_totale'] for c in comparisons])
    avg_cost = np.mean([c['cout_total'] for c in comparisons])
    
    fig_scatter_advanced.add_hline(
        y=avg_cost, 
        line_dash="dash", 
        line_color="red",
        annotation_text=f"Moyenne coût: {avg_cost:.0f}€",
        annotation_position="bottom right"
    )
    
    fig_scatter_advanced.add_vline(
        x=avg_distance, 
        line_dash="dash", 
        line_color="blue",
        annotation_text=f"Moyenne distance: {avg_distance:.1f}km",
        annotation_position="top right"
    )
    
    
    fig_efficiency = px.scatter(
        x=[c['taux_correspondance']*100 for c in comparisons],
        y=[(c['nb_ressources_communes'] / (c['nb_ressources_communes'] + c['nb_ressources_manquantes'] + 0.001)) * 100 for c in comparisons],
        size=[c['comparison_details']['nb_visites_total_reel'] for c in comparisons],
        color=[c['taux_visites'] for c in comparisons],
        hover_name=[f"{c['patient_label']} vs {c['type_label']}" for c in comparisons],
        hover_data={
            'Visites totales': [c['comparison_details']['nb_visites_total_reel'] for c in comparisons],
            'Ressources utilisées': [c['nb_ressources_communes'] for c in comparisons],
            'Ressources manquées': [c['nb_ressources_manquantes'] for c in comparisons]
        },
        labels={
            'x': 'Taux de Correspondance (%) → Plus c\'est mieux',
            'y': 'Efficacité Ressources (%) → Plus c\'est mieux',
            'color': 'Taux Visites (%)',
            'size': 'Nombre visites'
        },
        title=" Efficacité: Correspondance vs Utilisation des Ressources",
        color_continuous_scale='Viridis'
    )
    
    fig_efficiency.update_layout(height=500)
    
    
    fig_distribution = px.box(
        x=[c['taux_correspondance']*100 for c in comparisons],
        points="all",
        title=" Distribution des Taux de Correspondance",
        labels={'x': 'Taux de Correspondance (%)'}
    )
    
    fig_distribution.update_layout(
        height=400,
        showlegend=False,
        xaxis_title="Taux de Correspondance (%) → Objectif: >80%"
    )
    
    
    fig_distribution.add_vline(
        x=80, 
        line_dash="dot", 
        line_color="green",
        annotation_text="Objectif: 80%", 
        annotation_position="top"
    )
    
    
    type_stats = {}
    for c in comparisons:
        type_name = c['type_label']
        if type_name not in type_stats:
            type_stats[type_name] = []
        type_stats[type_name].append(c['taux_correspondance']*100)
    
    fig_box = go.Figure()
    for type_name, correspondances in type_stats.items():
        fig_box.add_trace(go.Box(
            y=correspondances, 
            name=type_name,
            boxpoints='all',
            jitter=0.3,
            pointpos=-1.8
        ))
    
    fig_box.update_layout(
        title=" Performance par Type de Parcours",
        yaxis_title="Taux de Correspondance (%)",
        height=500,
        xaxis_title="Types de Parcours"
    )
    
    
    metrics_data = {
        'Correspondance': [c['taux_correspondance'] for c in comparisons],
        'Distance': [c['distance_totale'] for c in comparisons],
        'Coût': [c['cout_total'] for c in comparisons],
        'Taux_Visites': [c['taux_visites']/100 for c in comparisons],
        'Ressources_Communes': [c['nb_ressources_communes'] for c in comparisons],
        'Visites_Manquées': [c['total_visites_manquees'] for c in comparisons]
    }
    
    correlation_df = pd.DataFrame(metrics_data)
    correlation_matrix = correlation_df.corr()
    
    fig_corr = px.imshow(
        correlation_matrix.values,
        x=correlation_matrix.columns,
        y=correlation_matrix.columns,
        color_continuous_scale='RdBu_r',
        title=" Matrice de Corrélation entre les Métriques",
        aspect='auto',
        text_auto='.2f'
    )
    fig_corr.update_layout(height=400)
    
    
    recommendations = generate_recommendations(results)
    
    return html.Div([
        html.Div([
            html.H4(" Analyse Comparative des Performances", style={'color': '#2c3e50', 'textAlign': 'center'}),
            html.P("Visualisation des relations entre coût, distance et qualité de correspondance", 
                  style={'textAlign': 'center', 'fontStyle': 'italic'})
        ], style={'marginBottom': '20px'}),
        
        dcc.Graph(figure=fig_scatter_advanced),
        
        html.Div([
            html.Div([
                dcc.Graph(figure=fig_distribution),
            ], style={'width': '48%', 'display': 'inline-block'}),
            
            html.Div([
                dcc.Graph(figure=fig_efficiency),
            ], style={'width': '48%', 'float': 'right', 'display': 'inline-block'})
        ]),
        
        dcc.Graph(figure=fig_box),
        dcc.Graph(figure=fig_corr),
        
        html.Div([
            html.H4(" Recommandations Automatiques", style={'color': '#2c3e50'}),
            html.Div(recommendations, style={'backgroundColor': '#e8f6f3', 'padding': '15px', 'borderRadius': '8px'})
        ], style={'marginTop': '30px'})
    ])

def generate_recommendations(results):
    """Génère des recommandations automatiques basées sur l'analyse"""
    stats = results['stats_globales']
    comparisons = results['comparisons']
    recommendations = []
    
    
    if stats['taux_correspondance_moyen'] < 0.7:
        recommendations.append("Le taux de correspondance moyen est faible (<70%). Considérez réviser les parcours types ou adapter les parcours patients.")
    elif stats['taux_correspondance_moyen'] > 0.9:
        recommendations.append(" Excellent taux de correspondance moyen (>90%). Les parcours sont bien alignés.")
    
    
    if stats['visites_manquees_total'] > 0:
        most_missed = max(comparisons, key=lambda x: x['total_visites_manquees'])
        recommendations.append(f" {int(stats['visites_manquees_total'])} visites manquées au total. Le cas le plus critique: {most_missed['patient_label']} avec {most_missed['total_visites_manquees']} visites manquées.")
    
    
    cout_variance = np.var([c['cout_total'] for c in comparisons])
    if cout_variance > (stats['cout_moyen'] * 0.5) ** 2:
        recommendations.append(" Grande variabilité des coûts détectée. Analysez les facteurs de coût pour optimiser.")
    
    
    if stats['distance_moyenne'] > 50:
        recommendations.append(" Distance moyenne élevée (>50km). Considérez l'optimisation géographique des parcours.")
    
    
    if stats['taux_visites_moyen'] < 80:
        recommendations.append(" Taux de réalisation des visites faible (<80%). Revoyez la planification des parcours.")
    
    
    best_match = stats['meilleure_correspondance']
    recommendations.append(f" Meilleure pratique identifiée : {best_match['patient_label']} avec {best_match['type_label']} ({best_match['taux_correspondance']:.1%} de correspondance).")
    
    if not recommendations:
        recommendations.append(" Aucune anomalie majeure détectée. Les parcours semblent bien optimisés.")
    
    return [html.P(rec, style={'margin': '5px 0'}) for rec in recommendations]

@dash.callback(
    Output("multi-parcours-individuels-dropdown", "value"),
    Output("multi-parcours-types-dropdown", "value"),
    Input("multi-reset-btn", "n_clicks")
)
def reset_multi_selections(n_clicks):
    """Réinitialise les sélections multiples"""
    if n_clicks > 0:
        return [], []
    return dash.no_update, dash.no_update


@dash.callback(
    Output("multi-parcours-individuels-dropdown", "value", allow_duplicate=True),
    Output("multi-parcours-types-dropdown", "value", allow_duplicate=True),
    Input("quick-select-all-patients", "n_clicks"),
    Input("quick-select-all-types", "n_clicks"),
    State("multi-parcours-individuels-dropdown", "options"),
    State("multi-parcours-types-dropdown", "options"),
    prevent_initial_call=True
)
def quick_selections(n_clicks_patients, n_clicks_types, patient_options, type_options):
    """Sélections rapides pour tous les patients ou tous les types"""
    ctx = dash.callback_context
    if not ctx.triggered:
        return dash.no_update, dash.no_update
    
    trigger = ctx.triggered[0]['prop_id'].split('.')[0]
    
    if trigger == "quick-select-all-patients" and n_clicks_patients > 0:
        all_patient_values = [opt['value'] for opt in patient_options]
        return all_patient_values, dash.no_update
    elif trigger == "quick-select-all-types" and n_clicks_types > 0:
        all_type_values = [opt['value'] for opt in type_options]
        return dash.no_update, all_type_values
    
    return dash.no_update, dash.no_update