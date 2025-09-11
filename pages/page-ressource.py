import pandas as pd
import dash
from dash import html, dcc, Input, Output, dash_table
import plotly.express as px
import plotly.graph_objects as go
import json
import psycopg2
from db_config import get_engine 


dash.register_page(__name__, path="/page-ressources", name="Ressources Médicales")


STRUCTURE_RECOURS = {
    "Prévention": {
        "color": "#007bff",  
        "description": "Actions de prévention et promotion de la santé",
    },
    "1er recours": {
        "color": "#28a745",
        "description": "Accès direct aux soins primaires",
    },
    "2ème recours": {
        "color": "#ffc107", 
        "description": "Accès aux spécialistes (sur orientation)",
    },
    "3ème recours": {
        "color": "#dc3545",
        "description": "Accès aux structures de soin spécialisées",
    }
}


def load_data_from_postgres():
    """Charge les données depuis PostgreSQL"""
    try:
        engine = get_engine()
        
        
        query = """
        SELECT 
            r.id_ressource,  -- CORRIGÉ: remplacé r.ressource par r.id_ressource
            r.nom_ressource,
            r.description_ressource,
            r.typeressource,
            r.telephone,
            r.email,
            r.horaires_ouverture,
            r.secteur,
            r.conventionnement,
            r.latitude_ressource,
            r.longitude_ressource,
            tps.nom_type as type_praticien,
            tps.description_type,
            nr.nom_niveau as niveau_recours,
            nr.ordre_niveau,
            nr.description_niveau,
            -- Jointure avec spécialités
            STRING_AGG(s.Nom_specialite, ', ') as specialites,
            -- Jointure avec avis (moyenne des notes)
            COALESCE(AVG(ar.note), 0) as note_moyenne,
            COUNT(ar.id_avis) as nombre_avis
        FROM Ressource r
        LEFT JOIN type_praticien_Structure tps ON r.id_type = tps.id_type
        LEFT JOIN niveau_recours nr ON tps.id_niveau_recours = nr.id_niveau_recours
        LEFT JOIN Ressource_specialite rs ON r.id_ressource = rs.id_ressource
        LEFT JOIN specialite s ON rs.id_specialite = s.id_specialite
        LEFT JOIN avis_Ressource ar ON r.id_ressource = ar.id_ressource
        GROUP BY 
            r.id_ressource, r.nom_ressource, r.description_ressource, r.typeressource,
            r.telephone, r.email, r.horaires_ouverture, r.secteur, r.conventionnement,
            r.latitude_ressource, r.longitude_ressource, tps.nom_type, tps.description_type,  -- CORRIGÉ: tps.Description_Type -> tps.description_type
            nr.nom_niveau, nr.ordre_niveau, nr.description_niveau
        ORDER BY nr.ordre_niveau, tps.nom_type, r.nom_ressource
        """
        
        df = pd.read_sql(query, engine)
        
        
        df['Praticien_Complet'] = df['nom_ressource']
        df['note_moyenne'] = pd.to_numeric(df['note_moyenne'], errors='coerce').fillna(0)  
        df['nombre_avis'] = pd.to_numeric(df['nombre_avis'], errors='coerce').fillna(0)    
        
        
        df['ville'] = 'Bayonne'
        df['Departement'] = '64'
        df['Nom_Département'] = 'Pyrénées-Atlantiques'
        
        return df
        
    except Exception as e:
        print(f"Erreur lors du chargement des données : {e}")
        
        return pd.DataFrame(columns=[
            'id_ressource', 'nom_ressource', 'description_ressource', 'typeressource',
            'telephone', 'email', 'horaires_ouverture', 'secteur', 'conventionnement',
            'latitude_ressource', 'longitude_ressource', 'type_praticien', 'description_type',
            'niveau_recours', 'ordre_niveau', 'description_niveau', 'specialites',
            'note_moyenne', 'nombre_avis', 'Praticien_Complet', 'ville', 'Departement', 'Nom_Département'
        ])

def load_patients_data():
    """Charge les données des patients et leurs parcours"""
    try:
        engine = get_engine()
        
        query = """
        SELECT 
            p.id_personne,
            p.nom,
            p.prenom,
            p.datenaissance,
            p.sex,
            p.ville,
            p.csp,
            p.latitude_personne,
            p.longitude_personne,
            -- Parcours
            pc.id_parcours,
            pc.datedebut_parcours,
            pc.datefin_parcours,
            pt.nom_parcours_type,
            -- Pathologies
            STRING_AGG(DISTINCT t.nomtheme, ', ') as Pathologies,
            -- nombre de consultations
            COUNT(ur.date_consultation) as nombre_Consultations
        FROM Personne p
        LEFT JOIN Parcours pc ON p.id_personne = pc.id_personne
        LEFT JOIN Parcours_type pt ON pc.id_parcours_type = pt.id_parcours_type
        LEFT JOIN est_associe_a ea ON pc.id_parcours = ea.id_parcours
        LEFT JOIN Theme t ON ea.id_theme = t.id_theme
        LEFT JOIN Utilise_ressource ur ON pc.id_parcours = ur.id_parcours
        GROUP BY 
            p.id_personne, p.nom, p.prenom, p.datenaissance, p.sex, p.ville, p.csp,
            p.latitude_personne, p.longitude_personne, pc.id_parcours,
            pc.datedebut_parcours, pc.datefin_parcours, pt.nom_parcours_type
        ORDER BY p.nom, p.prenom
        """
        
        patients_df = pd.read_sql(query, engine)
        return patients_df
        
    except Exception as e:
        print(f"Erreur lors du chargement des patients : {e}")
        return pd.DataFrame()

def load_consultations_data():
    """Charge les données des consultations"""
    try:
        engine = get_engine()
        
        query = """
        SELECT 
            ur.date_consultation,
            ur.heure_consultation,
            ur.duree_consultation,
            ur.cout_consultation,
            ur.type_consultation,
            ur.motif_consultation,
            ur.satisfaction_patient,
            -- Ressource
            r.nom_ressource,
            tps.nom_type as type_praticien,
            nr.nom_niveau as niveau_recours,
            -- Patient
            p.nom as Patient_Nom,
            p.prenom as Patient_prenom,
            -- axe
            a.nomaxe,
            -- Parcours
            pt.nom_parcours_type
        FROM Utilise_ressource ur
        LEFT JOIN Ressource r ON ur.id_ressource = r.id_ressource
        LEFT JOIN type_praticien_Structure tps ON r.id_type = tps.id_type
        LEFT JOIN niveau_recours nr ON tps.id_niveau_recours = nr.id_niveau_recours
        LEFT JOIN Parcours pc ON ur.id_parcours = pc.id_parcours
        LEFT JOIN Personne p ON pc.id_personne = p.id_personne
        LEFT JOIN axe a ON ur.id_axe = a.id_axe
        LEFT JOIN Parcours_type pt ON pc.id_parcours_type = pt.id_parcours_type
        ORDER BY ur.date_consultation DESC
        """
        
        consultations_df = pd.read_sql(query, engine)
        return consultations_df
        
    except Exception as e:
        print(f"Erreur lors du chargement des consultations : {e}")
        return pd.DataFrame()


medecins_df = load_data_from_postgres()
patients_df = load_patients_data()
consultations_df = load_consultations_data()


COORDS_BAYONNE = {"lat": 43.4928, "lon": -1.4748}
ZOOM_BAYONNE = 11

def creer_donnees_tableau_hierarchique():
    """Crée la structure de données pour le tableau hiérarchique"""
    if medecins_df.empty:
        return pd.DataFrame()
    
    donnees_tableau = []
    
    for _, ressource in medecins_df.iterrows():
        donnees_tableau.append({
            'id_ressource': ressource.get('id_ressource', ''),
            'niveau_recours': ressource.get('niveau_recours', 'Non classifié'),
            'type_praticien': ressource.get('type_praticien', 'Autre'),
            'Praticien': ressource.get('nom_ressource', 'nom non disponible'),
            'typeressource': ressource.get('typeressource', ''),
            'secteur': ressource.get('secteur', ''),
            'conventionnement': ressource.get('conventionnement', ''),
            'telephone': ressource.get('telephone', ''),
            'email': ressource.get('email', ''),
            'Horaires': ressource.get('horaires_ouverture', ''),
            'specialites': ressource.get('specialites', ''),
            'note_moyenne': ressource.get('note_moyenne', 0),     
            'Nombre_avis': ressource.get('nombre_avis', 0),       
            'ville': ressource.get('ville', 'Bayonne'),
            'Département': ressource.get('Departement', '64'),
            'Nom_Département': ressource.get('Nom_Département', 'Pyrénées-Atlantiques')
        })
    
    return pd.DataFrame(donnees_tableau)

def creer_vue_hierarchique_resume(df_filtre):
    """Crée une vue hiérarchique résumée sous forme d'arbre"""
    if df_filtre.empty:
        return html.Div("Aucune ressource disponible")
    
    structure = {}
    
    for niveau_recours in df_filtre['niveau_recours'].unique():
        if niveau_recours not in structure:
            structure[niveau_recours] = {}
        
        df_niveau = df_filtre[df_filtre['niveau_recours'] == niveau_recours]
        
        for type_praticien in df_niveau['type_praticien'].unique():
            df_type = df_niveau[df_niveau['type_praticien'] == type_praticien]
            ressources = df_type[['nom_ressource', 'note_moyenne', 'nombre_avis']].to_dict('records')
            structure[niveau_recours][type_praticien] = ressources
    
    elements_html = []
    
    for niveau, types_dict in structure.items():
        couleur = STRUCTURE_RECOURS.get(niveau, {}).get('color', '#000')
        
        elements_html.append(
            html.Details([
                html.Summary(
                    f"{niveau} ({sum(len(ressources) for ressources in types_dict.values())} ressources)",
                    style={"fontWeight": "bold", "color": couleur, "cursor": "pointer"}
                ),
                
                html.Div([
                    html.Details([
                        html.Summary(
                            f"{type_prat} ({len(ressources)} ressources)",
                            style={"marginLeft": "20px", "fontWeight": "bold", "cursor": "pointer"}
                        ),
                        html.Div([
                            html.Div([
                                html.Span(f"• {ressource['nom_ressource']}", style={"fontWeight": "bold"}),
                                html.Span(f" (note: {ressource['note_moyenne']:.1f}/5, {ressource['nombre_avis']} avis)" 
                                        if ressource['nombre_avis'] > 0 else " (Pas d'avis)",
                                        style={"fontSize": "0.9em", "color": "#666", "marginLeft": "10px"})
                            ], style={"marginLeft": "40px", "margin": "2px 0"})
                            for ressource in ressources[:10]
                        ] + ([html.P(f"... et {len(ressources)-10} autres", 
                                   style={"marginLeft": "40px", "fontStyle": "italic", "color": "#666"})]
                            if len(ressources) > 10 else []))
                    ], open=False)
                    for type_prat, ressources in types_dict.items()
                ], style={"marginLeft": "10px"})
            ], open=True)
        )
    
    return html.Div([
        html.H4("Vue Hiérarchique des Ressources"),
        html.Div(elements_html)
    ])

def creer_rapport_territorial(df_filtre, zone_titre):
    """Crée un rapport sur la couverture territoriale"""
    if df_filtre.empty:
        return html.Div("Aucune donnée pour l'analyse territoriale")
    
    
    repartition_niveau = df_filtre['niveau_recours'].value_counts()
    
    
    repartition_type = df_filtre['typeressource'].value_counts()
    
    
    ressources_avec_avis = df_filtre[df_filtre['nombre_avis'] > 0]
    note_moyenne_globale = ressources_avec_avis['note_moyenne'].mean() if not ressources_avec_avis.empty else 0
    
    return html.Div([
        html.H4("Analyse Territoriale - Bayonne/Pays Basque"),
        html.P(f"Zone analysée : {zone_titre}"),
        
        html.Div([
            html.H5("Répartition par niveau de recours"),
            *[html.P(f"• {niveau} : {count} ressources", 
                     style={"color": STRUCTURE_RECOURS.get(niveau, {}).get("color", "#000")}) 
              for niveau, count in repartition_niveau.items()]
        ]),
        
        html.Div([
            html.H5("Types de ressources"),
            *[html.P(f"• {type_res} : {count}") 
              for type_res, count in repartition_type.items()]
        ]),
        
        html.Div([
            html.H5("Qualité des services"),
            html.P(f"• note moyenne générale : {note_moyenne_globale:.1f}/5"),
            html.P(f"• Ressources avec avis : {len(ressources_avec_avis)}/{len(df_filtre)}"),
            html.P(f"• Total avis collectés : {df_filtre['nombre_avis'].sum()}")
        ])
    ], style={"padding": "15px", "backgroundColor": "#f0f8ff", "borderRadius": "5px", "marginBottom": "15px"})

def creer_statistiques_consultations():
    """Crée les statistiques des consultations"""
    if consultations_df.empty:
        return html.Div("Aucune donnée de consultation disponible")
    
    total_consultations = len(consultations_df)
    cout_moyen = consultations_df['cout_consultation'].mean()
    satisfaction_moyenne = consultations_df['satisfaction_patient'].mean()
    
    
    repartition_axe = consultations_df['nomaxe'].value_counts()
    
    
    repartition_niveau = consultations_df['niveau_recours'].value_counts()
    
    return html.Div([
        html.H4("Statistiques des Consultations"),
        
        html.Div([
            html.Div([
                html.P(f"Total consultations : {total_consultations}"),
                html.P(f"Coût moyen : {cout_moyen:.2f} €"),
                html.P(f"Satisfaction moyenne : {satisfaction_moyenne:.1f}/5")
            ], style={"width": "30%", "display": "inline-block"}),
            
            html.Div([
                html.H5("Par axe :"),
                *[html.P(f"• {axe} : {count}") for axe, count in repartition_axe.items()]
            ], style={"width": "30%", "display": "inline-block", "marginLeft": "5%"}),
            
            html.Div([
                html.H5("Par niveau :"),
                *[html.P(f"• {niveau} : {count}") for niveau, count in repartition_niveau.items()]
            ], style={"width": "30%", "float": "right"})
        ])
    ], style={"padding": "15px", "backgroundColor": "#f8f9fa", "borderRadius": "5px", "marginBottom": "20px"})


def create_safe_dropdown_options():
    """Crée les options de dropdown de manière sécurisée"""
    options = [{"label": "Tous les niveaux", "value": "all"}]
    
    if not medecins_df.empty and 'niveau_recours' in medecins_df.columns:
        niveaux_uniques = medecins_df['niveau_recours'].dropna().unique()
        for niveau in niveaux_uniques:
            count = len(medecins_df[medecins_df['niveau_recours'] == niveau])
            options.append({"label": f"{niveau} ({count})", "value": niveau})
    
    return options

def create_safe_type_ressource_options():
    """Crée les options de type de ressource de manière sécurisée"""
    options = [{"label": "Tous", "value": "all"}]
    
    if not medecins_df.empty and 'typeressource' in medecins_df.columns:
        types_uniques = medecins_df['typeressource'].dropna().unique()
        for type_res in types_uniques:
            options.append({"label": type_res, "value": type_res})
    
    return options


layout = html.Div([
    html.H2("Système d'Information des Parcours de Santé - Région de Bayonne", 
            style={"textAlign": "center", "marginBottom": "30px"}),
    
    
    html.Div([
        html.P(f"Données chargées : {len(medecins_df)} ressources, {len(patients_df)} patients, {len(consultations_df)} consultations" 
               if not medecins_df.empty else "Erreur de chargement des données", 
               style={"backgroundColor": "#e8f5e8" if not medecins_df.empty else "#f5e8e8", 
                      "padding": "10px", "borderRadius": "5px", "marginBottom": "20px"})
    ]),
    
    
    dcc.Tabs(id="tabs-visualisation", value='tab-carte', children=[
        dcc.Tab(label='Carte Interactive', value='tab-carte'),
        dcc.Tab(label='Ressources Détaillées', value='tab-tableau'),
        dcc.Tab(label='Parcours Patients', value='tab-parcours'),
        dcc.Tab(label='Pathologies', value='tab-pathologies'),
        dcc.Tab(label='Satisfaction', value='tab-satisfaction'),
    ]),
    
    
    html.Div(id="controles-filtres", children=[
        html.Div([
            html.Label("Niveau de recours :", style={"fontWeight": "bold"}),
            dcc.Dropdown(
                id="niveau-recours-dropdown",
                options=create_safe_dropdown_options(),
                value="all",
                style={"width": "100%"}
            )
        ], style={"width": "30%", "display": "inline-block"}),
        
        html.Div([
            html.Label("Type de praticien :", style={"fontWeight": "bold"}),
            dcc.Dropdown(
                id="type-praticien-dropdown",
                options=[{"label": "Tous les types", "value": "all"}],
                value="all",
                style={"width": "100%"}
            )
        ], style={"width": "30%", "display": "inline-block", "marginLeft": "3%"}),
        
        html.Div([
            html.Label("Type de ressource :", style={"fontWeight": "bold"}),
            dcc.Dropdown(
                id="type-ressource-dropdown",
                options=create_safe_type_ressource_options(),
                value="all",
                style={"width": "100%"}
            )
        ], style={"width": "30%", "float": "right"})
    ], style={"marginBottom": "20px"}),
    
    
    html.Div(id="contenu-visualisation")
])


@dash.callback(
    Output("type-praticien-dropdown", "options"),
    Output("type-praticien-dropdown", "value"),
    [Input("niveau-recours-dropdown", "value")]
)
def update_type_options(niveau_recours):
    if medecins_df.empty:
        return [{"label": "Tous les types", "value": "all"}], "all"
    
    options = [{"label": "Tous les types", "value": "all"}]
    
    if niveau_recours == "all":
        df_filtered = medecins_df
    else:
        df_filtered = medecins_df[medecins_df['niveau_recours'] == niveau_recours]
    
    if not df_filtered.empty and 'type_praticien' in df_filtered.columns:
        type_counts = df_filtered['type_praticien'].value_counts()
        
        for type_prat, count in type_counts.items():
            if pd.notna(type_prat):
                options.append({
                    "label": f"{type_prat} ({count})",
                    "value": type_prat
                })
    
    return options, "all"

def diagnose_date_format():
    """Diagnostique le format des colonnes de dates"""
    try:
        engine = get_engine()
        
        query_types = """
        SELECT 
            column_name,
            data_type,
            is_nullable
        FROM information_schema.columns 
        WHERE table_name = 'parcours' 
        AND column_name IN ('datedebut_parcours', 'datefin_parcours')
        """
        
        types_df = pd.read_sql(query_types, engine)
        print("Types des colonnes de dates :")
        print(types_df)
        query_sample = """
        SELECT 
            id_parcours,
            datedebut_parcours,
            datefin_parcours,
            pg_typeof(datedebut_parcours) as type_debut,
            pg_typeof(datefin_parcours) as type_fin
        FROM parcours 
        WHERE datedebut_parcours IS NOT NULL 
        LIMIT 5
        """
        
        sample_df = pd.read_sql(query_sample, engine)
        print("\nExemples de données :")
        print(sample_df)
        
        return types_df, sample_df
        
    except Exception as e:
        print(f"Erreur lors du diagnostic : {e}")
        return None, None

def get_parcours_stats():
    """Récupère les statistiques des parcours patients"""
    try:
        engine = get_engine()
        
        query = """
        SELECT 
            pt.nom_parcours_type,
            COUNT(DISTINCT pc.id_parcours) as nombre_parcours,
            COUNT(DISTINCT pc.id_personne) as nombre_patients,
            -- Calcul de la durée moyenne seulement sur les parcours terminés
            AVG(CASE 
                WHEN pc.datefin_parcours IS NOT NULL AND pc.datedebut_parcours IS NOT NULL 
                THEN EXTRACT(DAY FROM (pc.datefin_parcours::timestamp - pc.datedebut_parcours::timestamp))
                ELSE NULL 
            END) as duree_moyenne,
            COUNT(ur.date_consultation) as total_consultations
        FROM Parcours_type pt
        LEFT JOIN parcours pc ON pt.id_parcours_type = pc.id_parcours_type
        LEFT JOIN personne p ON pc.id_personne = p.id_personne
        LEFT JOIN utilise_ressource ur ON pc.id_parcours = ur.id_parcours
        GROUP BY pt.id_parcours_type, pt.nom_parcours_type
        ORDER BY nombre_parcours DESC
        """
        
        parcours_stats = pd.read_sql(query, engine)
        return parcours_stats
        
    except Exception as e:
        print(f"Erreur avec conversion timestamp : {e}")
        
        
        try:
            query_simple = """
            SELECT 
                pt.nom_parcours_type,
                COUNT(DISTINCT pc.id_parcours) as nombre_parcours,
                COUNT(DISTINCT pc.id_personne) as nombre_patients,
                NULL as duree_moyenne,  -- Pas de calcul de durée
                COUNT(ur.date_consultation) as total_consultations
            FROM Parcours_type pt
            LEFT JOIN parcours pc ON pt.id_parcours_type = pc.id_parcours_type
            LEFT JOIN personne p ON pc.id_personne = p.id_personne
            LEFT JOIN utilise_ressource ur ON pc.id_parcours = ur.id_parcours
            GROUP BY pt.id_parcours_type, pt.nom_parcours_type
            ORDER BY nombre_parcours DESC
            """
            
            parcours_stats = pd.read_sql(query_simple, engine)
            print("Utilisation de la version simplifiée sans calcul de durée")
            return parcours_stats
            
        except Exception as e2:
            print(f"Erreur même avec requête simplifiée : {e2}")
            return pd.DataFrame()

def get_satisfaction_stats():
    """Récupère les statistiques de satisfaction"""
    try:
        engine = get_engine()
        
        query = """
        SELECT 
            r.nom_ressource,
            tps.nom_type,
            nr.nom_niveau,
            AVG(ur.satisfaction_patient) as satisfaction_moyenne,
            COUNT(ur.satisfaction_patient) as nombre_evaluations,
            AVG(ur.cout_consultation) as cout_moyen
        FROM Utilise_ressource ur
        JOIN Ressource r ON ur.id_ressource = r.id_ressource
        JOIN type_praticien_Structure tps ON r.id_type = tps.id_type
        JOIN niveau_recours nr ON tps.id_niveau_recours = nr.id_niveau_recours
        WHERE ur.satisfaction_patient IS NOT NULL
        GROUP BY r.id_ressource, r.nom_ressource, tps.nom_type, nr.nom_niveau
        HAVING COUNT(ur.satisfaction_patient) >= 1
        ORDER BY satisfaction_moyenne DESC, nombre_evaluations DESC
        """
        
        satisfaction_df = pd.read_sql(query, engine)
        return satisfaction_df
        
    except Exception as e:
        print(f"Erreur lors du chargement des stats satisfaction : {e}")
        return pd.DataFrame()

def create_pathologies_overview():
    """Crée un aperçu des pathologies traitées"""
    try:
        engine = get_engine()
        
        query = """
        SELECT 
            t.nomtheme,
            t.description_theme,
            t.niveau_theme,
            COUNT(DISTINCT em.id_personne) as nombre_patients,
            COUNT(DISTINCT ea.id_parcours) as nombre_parcours,
            AVG(ur.satisfaction_patient) as satisfaction_moyenne
        FROM Theme t
        LEFT JOIN etre_malade em ON t.id_theme = em.id_theme
        LEFT JOIN est_associe_a ea ON t.id_theme = ea.id_theme
        LEFT JOIN Utilise_ressource ur ON ea.id_parcours = ur.id_parcours
        WHERE t.nomtheme IS NOT NULL
        GROUP BY t.id_theme, t.nomtheme, t.description_theme, t.niveau_theme
        ORDER BY nombre_patients DESC
        """
        
        pathologies_df = pd.read_sql(query, engine)
        return pathologies_df
        
    except Exception as e:
        print(f"Erreur lors du chargement des pathologies : {e}")
        return pd.DataFrame()


parcours_stats = get_parcours_stats()
satisfaction_stats = get_satisfaction_stats()
pathologies_overview = create_pathologies_overview()

def render_carte(df_filtre):
    """Rendu de la carte avec toutes les ressources disponibles"""
    
    df_carte = medecins_df if not medecins_df.empty else df_filtre
    
    if df_carte.empty:
        return html.Div("Aucune donnée à afficher sur la carte")
    
    
    print(f"Total ressources dans medecins_df: {len(df_carte)}")
    print(f"Colonnes disponibles: {df_carte.columns.tolist()}")
    
    
    coord_info = df_carte[['nom_ressource', 'latitude_ressource', 'longitude_ressource']].copy()
    coord_info['coords_valides'] = coord_info[['latitude_ressource', 'longitude_ressource']].notna().all(axis=1)
    
    print("\nCoordonnées par ressource:")
    for _, row in coord_info.iterrows():
        print(f"- {row['nom_ressource']}: lat={row['latitude_ressource']}, lon={row['longitude_ressource']}, valide={row['coords_valides']}")
    
    
    df_carte_valide = df_carte.dropna(subset=['latitude_ressource', 'longitude_ressource'])
    
    print(f"\nRessources avec coordonnées valides: {len(df_carte_valide)}")
    
    if df_carte_valide.empty:
        return html.Div("Aucune ressource avec coordonnées géographiques valides")
    
    
    lat_min, lat_max = df_carte_valide['latitude_ressource'].min(), df_carte_valide['latitude_ressource'].max()
    lon_min, lon_max = df_carte_valide['longitude_ressource'].min(), df_carte_valide['longitude_ressource'].max()
    
    
    centre_lat = (lat_min + lat_max) / 2
    centre_lon = (lon_min + lon_max) / 2
    
    
    lat_range = lat_max - lat_min
    lon_range = lon_max - lon_min
    max_range = max(lat_range, lon_range)
    
    
    if max_range > 1:
        zoom_adapte = 8
    elif max_range > 0.5:
        zoom_adapte = 10
    elif max_range > 0.1:
        zoom_adapte = 12
    elif max_range > 0.05:
        zoom_adapte = 13
    else:
        zoom_adapte = 14
    
    print(f"\nCentre calculé: lat={centre_lat:.4f}, lon={centre_lon:.4f}")
    print(f"Plage lat: {lat_range:.4f}, lon: {lon_range:.4f}")
    print(f"Zoom adapté: {zoom_adapte}")
    
    
    color_map = {niveau: config["color"] for niveau, config in STRUCTURE_RECOURS.items()}
    
    
    niveaux_uniques = df_carte_valide['niveau_recours'].unique()
    for niveau in niveaux_uniques:
        if niveau not in color_map:
            color_map[niveau] = "#999999"  
    
    
    df_carte_valide = df_carte_valide.copy()
    df_carte_valide['taille_marqueur'] = 15  
    fig = px.scatter_mapbox(
        df_carte_valide,
        lat="latitude_ressource",
        lon="longitude_ressource",
        size="taille_marqueur",  
        color="niveau_recours",
        hover_name="nom_ressource",
        hover_data={
            "type_praticien": True, 
            "typeressource": True,
            "secteur": True,
            "note_moyenne": ":.1f",
            "nombre_avis": True,
            "latitude_ressource": ":.4f",  
            "longitude_ressource": ":.4f",
            "taille_marqueur": False
        },
        color_discrete_map=color_map,
        size_max=20, 
        zoom=zoom_adapte,  
        center={"lat": centre_lat, "lon": centre_lon},  
        title=f"Ressources Médicales ({len(df_carte_valide)}/{len(df_carte)} ressources affichées)",
        mapbox_style="open-street-map",
        height=700
    )
    
    fig.update_layout(
        title={
            'text': f"Carte Interactive - {len(df_carte_valide)} ressources médicales sur {len(df_carte)} total",
            'x': 0.5,
            'xanchor': 'center'
        },
        margin=dict(l=0, r=0, t=50, b=0)
    )
    
    
    stats = creer_statistiques_synthese(df_carte_valide)
    rapport = creer_rapport_territorial(df_carte_valide, "Bayonne/Pays Basque")
    
    
    legende_niveaux = html.Div([
        html.H5("Légende des Niveaux de Recours"),
        html.Div([
            html.Div([
                html.Span("●", style={"color": config["color"], "fontSize": "18px", "marginRight": "8px"}),
                html.Span(f"{niveau}: {config['description']}")
            ], style={"margin": "5px 0"})
            for niveau, config in STRUCTURE_RECOURS.items()
        ])
    ], style={
        "backgroundColor": "#f8f9fa", 
        "padding": "15px", 
        "borderRadius": "5px", 
        "marginBottom": "20px"
    })
    
    return html.Div([
        html.H3("Cartographie Complète des Ressources Médicales", 
               style={"textAlign": "center", "marginBottom": "20px"}),
        
        legende_niveaux,
        stats,
        rapport,
        
        dcc.Graph(figure=fig),
        
        html.Div([
            html.H5("Instructions"),
            html.P("Survolez les marqueurs pour voir les détails. La taille indique la note moyenne.")
        ], style={
            "backgroundColor": "#e9ecef", 
            "padding": "10px", 
            "borderRadius": "5px", 
            "marginTop": "15px"
        })
    ])


def render_tableau(df_filtre):
    """Rendu du tableau des ressources avec tableau et vue hiérarchique en bas"""
    if df_filtre.empty:
        return html.Div("Aucune donnée pour le tableau")
    
    donnees_tableau = creer_donnees_tableau_hierarchique()
    donnees_filtrees = donnees_tableau[donnees_tableau['id_ressource'].isin(df_filtre['id_ressource'])]
    
    if donnees_filtrees.empty:
        return html.P("Aucune donnée pour le tableau")
    
    
    tableau = dash_table.DataTable(
        id='tableau-ressources',
        data=donnees_filtrees.to_dict('records'),
        columns=[
            {"name": "Niveau", "id": "niveau_recours", "type": "text"},
            {"name": "Type", "id": "type_praticien", "type": "text"},
            {"name": "Nom", "id": "Praticien", "type": "text"},
            {"name": "Type Ressource", "id": "typeressource", "type": "text"},
            {"name": "secteur", "id": "secteur", "type": "text"},
            {"name": "conventionnement", "id": "conventionnement", "type": "text"},
            {"name": "Téléphone", "id": "telephone", "type": "text"},
            {"name": "note", "id": "note_moyenne", "type": "numeric", "format": {"specifier": ".1f"}},
            {"name": "Nb avis", "id": "nombre_avis", "type": "numeric"},
        ],
        style_table={'overflowX': 'auto'},
        style_cell={
            'textAlign': 'left',
            'padding': '8px',
            'fontFamily': 'Arial',
            'fontSize': '12px'
        },
        style_header={
            'backgroundColor': '#f1f1f1',
            'fontWeight': 'bold'
        },
        style_data_conditional=[
            {
                'if': {'filter_query': '{niveau_recours} = "Prévention"'},
                'backgroundColor': '#e3f2fd'  
            },
            {
                'if': {'filter_query': '{niveau_recours} = "1er recours"'},
                'backgroundColor': '#e8f5e8'
            },
            {
                'if': {'filter_query': '{niveau_recours} = "2ème recours"'},
                'backgroundColor': '#fff3cd'
            },
            {
                'if': {'filter_query': '{niveau_recours} = "3ème recours"'},
                'backgroundColor': '#f8d7da'
            }
        ],
        sort_action="native",
        filter_action="native",
        page_action="native",
        page_current=0,
        page_size=15,
        export_format="csv"
    )
    
    
    vue_hierarchique = creer_vue_hierarchique_resume(df_filtre)
    
    
    stats_synthese = creer_statistiques_synthese(df_filtre)
    
    
    return html.Div([
        
        stats_synthese,
        
        
        html.Hr(style={"margin": "30px 0"}),
        
        
        html.Div([
            
            html.H5("Tableau Détaillé des Ressources", 
                   style={"marginBottom": "15px", "color": "#333"}),
            
            
            tableau,
            
            
            html.Div(style={"height": "30px"}),
            
            
            vue_hierarchique
        ])
    ])

def render_dashboard_parcours():
    """Rendu du dashboard des parcours"""
    if parcours_stats.empty:
        return html.Div("Aucune donnée sur les parcours disponible")
    
    fig_parcours = px.bar(
        parcours_stats,
        x='nom_parcours_type',
        y='nombre_patients',
        title="Nombre de patients par type de parcours"
    )
    
    
    if 'duree_moyenne' in parcours_stats.columns and parcours_stats['duree_moyenne'].notna().any():
        fig_duree = px.bar(
            parcours_stats[parcours_stats['duree_moyenne'].notna()],
            x='nom_parcours_type',
            y='duree_moyenne',
            title="Durée moyenne des parcours (en jours)"
        )
    else:
        fig_duree = px.bar(
            parcours_stats,
            x='nom_parcours_type',
            y='nombre_parcours',
            title="Nombre de parcours (durée non disponible)"
        )
    
    return html.Div([
        html.H4("Dashboard Parcours Patients"),
        html.Div([
            html.Div([
                html.H5("Statistiques générales"),
                html.P(f"Total parcours actifs : {parcours_stats['nombre_parcours'].sum()}"),
                html.P(f"Total patients suivis : {parcours_stats['nombre_patients'].sum()}"),
                html.P(f"Total consultations : {parcours_stats['total_consultations'].sum()}")
            ], style={"width": "100%", "marginBottom": "20px"})
        ]),
        
        html.Div([
            html.Div([dcc.Graph(figure=fig_parcours)], style={"width": "50%", "display": "inline-block"}),
            html.Div([dcc.Graph(figure=fig_duree)], style={"width": "50%", "display": "inline-block"})
        ])
    ])

def render_dashboard_pathologies():
    """Rendu du dashboard des pathologies"""
    if pathologies_overview.empty:
        return html.Div("Aucune donnée sur les pathologies disponible")
    
    fig_pathologies = px.bar(
        pathologies_overview,
        x='nomtheme',
        y='nombre_patients',
        color='niveau_theme',
        title="nombre de patients par pathologie",
        labels={'nombre_patients': 'Nombre de patients', 'nomtheme': 'pathologie'}
    )
    fig_pathologies.update_xaxes(tickangle=45)
    
    return html.Div([
        html.H4("Dashboard Pathologies"),
        html.Div([
            html.Div([
                html.H5("Pathologies principales"),
                *[html.P(f"• {row['nomtheme']} : {row['nombre_patients']} patients ({row['niveau_theme']})")
                  for _, row in pathologies_overview.head(5).iterrows()]
            ], style={"width": "48%", "display": "inline-block"}),
            
            html.Div([
                html.H5("Satisfaction par pathologie"),
                *[html.P(f"• {row['nomtheme']} : {row['satisfaction_moyenne']:.1f}/5")
                  for _, row in pathologies_overview[pathologies_overview['satisfaction_moyenne'].notna()].head(5).iterrows()]
            ], style={"width": "48%", "float": "right"})
        ]),
        
        dcc.Graph(figure=fig_pathologies)
    ])

def render_dashboard_satisfaction():
    """Rendu du dashboard de satisfaction"""
    if satisfaction_stats.empty:
        return html.Div("Aucune donnée de satisfaction disponible")
    

    top_satisfaction = satisfaction_stats.head(10)
    
    fig_satisfaction = px.bar(
        top_satisfaction,
        x='satisfaction_moyenne',
        y='nom_ressource',
        color='nom_niveau',
        orientation='h',
        title="Top 10 des ressources les mieux évaluées",
        labels={'satisfaction_moyenne': 'Satisfaction moyenne', 'nom_ressource': 'Ressource'},
        color_discrete_map={niveau: config["color"] for niveau, config in STRUCTURE_RECOURS.items()}
    )
    
    satisfaction_par_niveau = satisfaction_stats.groupby('nom_niveau')['satisfaction_moyenne'].mean().reset_index()
    
    fig_niveau = px.bar(
        satisfaction_par_niveau,
        x='nom_niveau',
        y='satisfaction_moyenne',
        title="Satisfaction moyenne par niveau de recours",
        color='nom_niveau',
        color_discrete_map={niveau: config["color"] for niveau, config in STRUCTURE_RECOURS.items()}
    )
    
    return html.Div([
        html.H4("Dashboard Satisfaction"),
        html.Div([
            html.H5("Statistiques globales"),
            html.P(f"Satisfaction moyenne générale : {satisfaction_stats['satisfaction_moyenne'].mean():.1f}/5"),
            html.P(f"nombre total d'évaluations : {satisfaction_stats['nombre_evaluations'].sum()}"),
            html.P(f"Coût moyen des consultations : {satisfaction_stats['cout_moyen'].mean():.2f} €")
        ], style={"marginBottom": "20px"}),
        
        html.Div([
            html.Div([dcc.Graph(figure=fig_satisfaction)], style={"width": "60%", "display": "inline-block"}),
            html.Div([dcc.Graph(figure=fig_niveau)], style={"width": "40%", "display": "inline-block"})
        ])
    ])

def creer_statistiques_synthese(df_filtre):
    """Crée les statistiques de synthèse"""
    if df_filtre.empty:
        return html.Div("Aucune donnée disponible")
    
    total = len(df_filtre)
    
    repartition = df_filtre['niveau_recours'].value_counts()
    
    note_moyenne = df_filtre['note_moyenne'].mean()
    ressources_avec_avis = len(df_filtre[df_filtre['nombre_avis'] > 0])
    
    return html.Div([
        html.Div([
            html.H4("Statistiques Générales"),
            html.P(f"Total ressources : {total}"),
            html.P(f"note moyenne : {note_moyenne:.1f}/5"),
            html.P(f"Ressources avec avis : {ressources_avec_avis}")
        ], style={"width": "30%", "display": "inline-block"}),
        
        html.Div([
            html.H4("Répartition par Niveau"),
            *[html.P(f"{niveau} : {count} ({count/total*100:.1f}%)", 
                     style={"color": STRUCTURE_RECOURS.get(niveau, {}).get("color", "#000")}) 
              for niveau, count in repartition.items()]
        ], style={"width": "40%", "display": "inline-block", "marginLeft": "5%"}),
        
        html.Div([
            html.H4("Top Types de Ressources"),
            *[html.P(f"{type_res} : {count}") 
              for type_res, count in df_filtre['typeressource'].value_counts().head(3).items()]
        ], style={"width": "25%", "float": "right"})
    ], style={"padding": "15px", "backgroundColor": "#f8f9fa", "borderRadius": "5px", "marginBottom": "20px"})


@dash.callback(
    [Output("contenu-visualisation", "children"),
     Output("controles-filtres", "style")],
    [Input("tabs-visualisation", "value"),
     Input("niveau-recours-dropdown", "value"),
     Input("type-praticien-dropdown", "value"),
     Input("type-ressource-dropdown", "value")]
)
def render_contenu_etendu(tab_actif, niveau_recours, type_praticien, type_ressource):
    if medecins_df.empty:
        return html.P("Aucune donnée disponible", style={"color": "red"}), {"display": "block"}
    
    show_filters = tab_actif in ['tab-carte', 'tab-tableau']
    filter_style = {"marginBottom": "20px"} if show_filters else {"display": "none"}
    
    if show_filters:
        df_filtre = medecins_df.copy()
        
        if niveau_recours != "all":
            df_filtre = df_filtre[df_filtre['niveau_recours'] == niveau_recours]
        
        if type_praticien != "all":
            df_filtre = df_filtre[df_filtre['type_praticien'] == type_praticien]
            
        if type_ressource != "all":
            df_filtre = df_filtre[df_filtre['typeressource'] == type_ressource]
        
        if df_filtre.empty:
            return html.P("Aucune donnée pour cette sélection", style={"color": "orange"}), filter_style
    
    if tab_actif == 'tab-carte':
        return render_carte(df_filtre), filter_style
    elif tab_actif == 'tab-tableau':
        return render_tableau(df_filtre), filter_style
    elif tab_actif == 'tab-parcours':
        return render_dashboard_parcours(), filter_style
    elif tab_actif == 'tab-pathologies':
        return render_dashboard_pathologies(), filter_style
    elif tab_actif == 'tab-satisfaction':
        return render_dashboard_satisfaction(), filter_style
    else:
        return html.P("Onglet non reconnu"), filter_style

print("=== INFORMATIONS SUR LES DONNÉES CHARGÉES ===")
print(f"Ressources médicales : {len(medecins_df)}")
print(f"Patients : {len(patients_df)}")  
print(f"Consultations : {len(consultations_df)}")
print(f"Stats parcours : {len(parcours_stats)}")
print(f"Stats satisfaction : {len(satisfaction_stats)}")
print(f"Pathologies : {len(pathologies_overview)}")

if not medecins_df.empty:
    print("\nRépartition des ressources par niveau :")
    for niveau, count in medecins_df['niveau_recours'].value_counts().items():
        print(f"  {niveau}: {count}")
    
    print("\nRépartition par type de ressource :")
    for type_res, count in medecins_df['typeressource'].value_counts().items():
        print(f"  {type_res}: {count}")

print("=== FIN DES INFORMATIONS ===")