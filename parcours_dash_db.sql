--
-- PostgreSQL database dump
--

-- Dumped from database version 17.5
-- Dumped by pg_dump version 17.5

-- Started on 2025-11-09 13:18:30

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- TOC entry 228 (class 1259 OID 34876)
-- Name: appartient; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.appartient (
    id_personne character varying(50) NOT NULL,
    id_groupe character varying(50) NOT NULL
);


--
-- TOC entry 230 (class 1259 OID 34906)
-- Name: appartient_a; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.appartient_a (
    id_categorie character varying(50) NOT NULL,
    id_theme character varying(50) NOT NULL
);


--
-- TOC entry 239 (class 1259 OID 35043)
-- Name: avis_ressource; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.avis_ressource (
    id_avis character varying(50) NOT NULL,
    id_ressource character varying(50),
    id_personne character varying(50),
    note smallint,
    commentaire text,
    date_avis date,
    CONSTRAINT avis_ressource_note_check CHECK (((note >= 1) AND (note <= 5)))
);


--
-- TOC entry 219 (class 1259 OID 34803)
-- Name: axe; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.axe (
    id_axe character varying(50) NOT NULL,
    nomaxe character varying(50),
    description_axe character varying(50)
);


--
-- TOC entry 220 (class 1259 OID 34808)
-- Name: categorie; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.categorie (
    id_categorie character varying(50) NOT NULL,
    nomcategorie character varying(50)
);


--
-- TOC entry 231 (class 1259 OID 34921)
-- Name: classe_dans; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.classe_dans (
    id_ressource character varying(50) NOT NULL,
    id_categorie character varying(50) NOT NULL
);


--
-- TOC entry 232 (class 1259 OID 34936)
-- Name: contient; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.contient (
    id_categorie character varying(50) NOT NULL,
    id_categorie_1 character varying(50) NOT NULL
);


--
-- TOC entry 242 (class 1259 OID 35071)
-- Name: diplome; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.diplome (
    id_diplome character varying(50) NOT NULL,
    nom_diplome character varying(100)
);


--
-- TOC entry 238 (class 1259 OID 35033)
-- Name: disponibilite; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.disponibilite (
    id_disponibilite character varying(50) NOT NULL,
    id_ressource character varying(50),
    jour_semaine character varying(20),
    heure_debut time without time zone,
    heure_fin time without time zone,
    type_creneau character varying(50)
);


--
-- TOC entry 229 (class 1259 OID 34891)
-- Name: est_associe_a; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.est_associe_a (
    id_parcours character varying(50) NOT NULL,
    id_theme character varying(50) NOT NULL
);


--
-- TOC entry 235 (class 1259 OID 34981)
-- Name: etre_malade; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.etre_malade (
    id_personne character varying(50) NOT NULL,
    id_theme character varying(50) NOT NULL,
    date_diagnostic date,
    gravite character varying(50)
);


--
-- TOC entry 241 (class 1259 OID 35066)
-- Name: formation; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.formation (
    id_formation character varying(50) NOT NULL,
    nom_formation character varying(100)
);


--
-- TOC entry 218 (class 1259 OID 34798)
-- Name: groupepersonne; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.groupepersonne (
    id_groupe character varying(50) NOT NULL,
    nomgroupe character varying(50),
    description_groupe character varying(50)
);


--
-- TOC entry 224 (class 1259 OID 34830)
-- Name: niveau_recours; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.niveau_recours (
    id_niveau_recours character varying(50) NOT NULL,
    nom_niveau character varying(50) NOT NULL,
    ordre_niveau smallint NOT NULL,
    description_niveau text
);


--
-- TOC entry 227 (class 1259 OID 34861)
-- Name: parcours; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.parcours (
    id_parcours character varying(50) NOT NULL,
    datedebut_parcours date NOT NULL,
    datefin_parcours date NOT NULL,
    id_parcours_type character varying(50),
    id_personne character varying(50) NOT NULL
);


--
-- TOC entry 222 (class 1259 OID 34818)
-- Name: parcours_type; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.parcours_type (
    id_parcours_type character varying(50) NOT NULL,
    nom_parcours_type character varying(50),
    description_parcours_type character varying(50)
);


--
-- TOC entry 217 (class 1259 OID 34793)
-- Name: personne; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.personne (
    id_personne character varying(50) NOT NULL,
    nom character varying(50),
    prenom character varying(50),
    datenaissance date NOT NULL,
    sex character varying(50),
    no_rue integer,
    code_postale character varying(50),
    ville character varying(50),
    csp character varying(50),
    latitude_personne numeric(15,2),
    longitude_personne numeric(15,2)
);


--
-- TOC entry 234 (class 1259 OID 34966)
-- Name: prevoit_ressource; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.prevoit_ressource (
    id_ressource character varying(50) NOT NULL,
    id_parcours_type character varying(50) NOT NULL,
    ordre smallint NOT NULL,
    frequence character varying(50),
    nombre_de_visite smallint NOT NULL
);


--
-- TOC entry 233 (class 1259 OID 34951)
-- Name: prevu_pour; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.prevu_pour (
    id_theme character varying(50) NOT NULL,
    id_parcours_type character varying(50) NOT NULL
);


--
-- TOC entry 226 (class 1259 OID 34849)
-- Name: ressource; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.ressource (
    id_ressource character varying(50) NOT NULL,
    nom_ressource character varying(100),
    description_ressource text,
    typeressource character varying(50),
    telephone character varying(20),
    email character varying(100),
    horaires_ouverture text,
    secteur character varying(10),
    conventionnement character varying(50),
    latitude_ressource numeric(15,2) NOT NULL,
    longitude_ressource numeric(15,2) NOT NULL,
    id_type character varying(50) NOT NULL
);


--
-- TOC entry 245 (class 1259 OID 35107)
-- Name: ressource_diplome; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.ressource_diplome (
    id_ressource character varying(50) NOT NULL,
    id_diplome character varying(50) NOT NULL,
    annee_obtention integer,
    etablissement character varying(100)
);


--
-- TOC entry 244 (class 1259 OID 35092)
-- Name: ressource_formation; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.ressource_formation (
    id_ressource character varying(50) NOT NULL,
    id_formation character varying(50) NOT NULL,
    date_formation date,
    organisme_formation character varying(100)
);


--
-- TOC entry 236 (class 1259 OID 34996)
-- Name: ressource_specialite; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.ressource_specialite (
    id_ressource character varying(50) NOT NULL,
    id_specialite character varying(50) NOT NULL
);


--
-- TOC entry 243 (class 1259 OID 35077)
-- Name: ressource_specificite; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.ressource_specificite (
    id_ressource character varying(50) NOT NULL,
    id_specificite character varying(50) NOT NULL
);


--
-- TOC entry 223 (class 1259 OID 34823)
-- Name: specialite; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.specialite (
    id_specialite character varying(50) NOT NULL,
    nom_specialite character varying(100),
    description_specialite text
);


--
-- TOC entry 240 (class 1259 OID 35061)
-- Name: specificite; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.specificite (
    id_specificite character varying(50) NOT NULL,
    nom_specificite character varying(100)
);


--
-- TOC entry 221 (class 1259 OID 34813)
-- Name: theme; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.theme (
    id_theme character varying(50) NOT NULL,
    nomtheme character varying(50),
    niveau_theme character varying(50),
    description_theme character varying(50)
);


--
-- TOC entry 225 (class 1259 OID 34837)
-- Name: type_praticien_structure; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.type_praticien_structure (
    id_type character varying(50) NOT NULL,
    nom_type character varying(50) NOT NULL,
    description_type text,
    id_niveau_recours character varying(50) NOT NULL
);


--
-- TOC entry 237 (class 1259 OID 35011)
-- Name: utilise_ressource; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.utilise_ressource (
    id_axe character varying(50) NOT NULL,
    id_parcours character varying(50) NOT NULL,
    id_ressource character varying(50) NOT NULL,
    date_consultation date NOT NULL,
    heure_consultation time without time zone,
    duree_consultation integer,
    cout_consultation numeric(10,2),
    type_consultation character varying(50),
    motif_consultation text,
    satisfaction_patient smallint
);


--
-- TOC entry 5102 (class 0 OID 34876)
-- Dependencies: 228
-- Data for Name: appartient; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.appartient (id_personne, id_groupe) FROM stdin;
P001	GP002
P002	GP002
P003	GP001
P004	GP001
P005	GP001
P006	GP002
P007	GP001
P008	GP003
P009	GP001
P010	GP003
P011	GP005
P012	GP006
P013	GP005
P013	GP007
P014	GP007
P015	GP006
P016	GP005
P016	GP007
P017	GP005
P018	GP005
P018	GP007
P019	GP007
P020	GP005
\.


--
-- TOC entry 5104 (class 0 OID 34906)
-- Dependencies: 230
-- Data for Name: appartient_a; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.appartient_a (id_categorie, id_theme) FROM stdin;
CAT001	TH001
CAT001	TH004
CAT002	TH002
CAT002	TH003
CAT002	TH005
CAT003	TH004
CAT006	TH006
CAT006	TH010
CAT007	TH008
CAT007	TH009
CAT007	TH007
CAT008	TH008
CAT008	TH007
CAT009	TH009
CAT010	TH011
\.


--
-- TOC entry 5113 (class 0 OID 35043)
-- Dependencies: 239
-- Data for Name: avis_ressource; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.avis_ressource (id_avis, id_ressource, id_personne, note, commentaire, date_avis) FROM stdin;
AV001	R002	P001	4	Médecin attentif, bon suivi	2024-02-01
AV002	R011	P001	5	Excellente prise en charge oncologique	2024-03-01
AV003	R009	P003	5	Très compétent en diabétologie	2024-01-15
AV004	R010	P004	4	Bon conseil pour la gestion du diabète	2024-04-15
AV005	R016	P001	4	Bon accueil, personnel competent	2024-02-20
AV006	R013	P002	5	Gynécologue très professionnelle	2024-02-25
AV007	R005	P003	5	Infirmière très pédagogue	2024-03-10
AV008	R007	P005	4	Pharmacie bien équipée pour diabétiques	2024-04-01
AV009	R004	P006	4	Médecin disponible et à l'écoute	2024-03-15
AV010	R012	P002	5	Oncologue spécialiste du sein excellent	2024-04-10
AV011	R018	P006	5	Centre très bien organisé	2024-02-15
AV012	R014	P008	4	Radiologie efficace, délais corrects	2024-05-20
AV013	R001	P007	3	Médecin compétent mais parfois pressé	2023-06-15
AV014	R017	P009	4	Clinique moderne, bon suivi	2023-09-20
AV015	R008	P010	4	Pharmacie de quartier, bon conseil	2024-05-10
AV016	R019	P012	5	Centre très bien organisé, personnel accueillant	2024-07-20
AV017	R021	P011	5	Excellente approche préventive, médecin très pédagogue	2024-06-05
AV018	R023	P011	4	Conseils nutritionnels très pratiques et adaptés	2024-06-20
AV019	R025	P013	5	Éducatrice très compétente, méthode efficace	2024-06-05
AV020	R027	P012	4	Bon accompagnement psychologique, écoute attentive	2024-07-25
AV021	R029	P011	4	Laboratoire efficace, résultats rapides	2024-07-01
AV022	R032	P014	5	MSP très accessible, équipe pluridisciplinaire top	2024-08-25
AV023	R024	P014	4	Nutritionniste spécialisé, conseils adaptés sportifs	2024-08-15
AV024	R019	P015	4	Dépistage rapide et efficace, bien informée	2024-06-20
AV025	R022	P013	5	Médecin préventiviste excellent, bilan très complet	2024-05-20
AV026	R024	P016	4	Nutritionniste sportif, conseils adaptés vie active	2024-09-15
AV027	R028	P016	5	Psychologue très professionnel, méthodes efficaces	2024-09-25
AV028	R022	P017	5	Médecin préventiviste excellent, approche globale	2024-10-05
AV029	R025	P018	4	Éducatrice adaptée aux seniors, très patiente	2024-09-10
AV030	R032	P019	5	MSP parfaite pour étudiants, tarifs accessibles	2024-11-05
AV031	R030	P020	4	Laboratoire rapide et efficace pour dépistages	2024-09-30
AV032	R021	P018	4	Bon médecin prévention, à l'écoute des seniors	2024-08-20
AV033	R026	P011	5	Éducateur activité physique très motivant	2024-07-01
\.


--
-- TOC entry 5093 (class 0 OID 34803)
-- Dependencies: 219
-- Data for Name: axe; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.axe (id_axe, nomaxe, description_axe) FROM stdin;
AX001	Santé	Axe relatif à la santé générale
AX002	Soins	Axe relatif aux soins curatifs
AX003	Vie	Axe relatif à la qualité de vie
\.


--
-- TOC entry 5094 (class 0 OID 34808)
-- Dependencies: 220
-- Data for Name: categorie; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.categorie (id_categorie, nomcategorie) FROM stdin;
CAT001	Oncologie
CAT002	Endocrinologie
CAT003	Prévention
CAT004	Soins de support
CAT005	Urgences
CAT006	Dépistage organisé
CAT007	Éducation thérapeutique
CAT008	Nutrition préventive
CAT009	Activité physique adaptée
CAT010	Psychologie préventive
\.


--
-- TOC entry 5105 (class 0 OID 34921)
-- Dependencies: 231
-- Data for Name: classe_dans; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.classe_dans (id_ressource, id_categorie) FROM stdin;
R011	CAT001
R012	CAT001
R013	CAT001
R014	CAT001
R015	CAT001
R018	CAT001
R009	CAT002
R010	CAT002
R001	CAT003
R002	CAT003
R003	CAT003
R004	CAT003
R007	CAT003
R008	CAT003
R005	CAT004
R006	CAT004
R016	CAT005
R017	CAT005
R019	CAT003
R020	CAT003
R021	CAT003
R022	CAT003
R023	CAT003
R024	CAT003
R025	CAT003
R026	CAT003
R027	CAT003
R028	CAT003
R029	CAT003
R030	CAT003
R031	CAT003
R032	CAT003
R033	CAT003
R019	CAT006
R020	CAT006
R025	CAT007
R026	CAT007
R032	CAT007
R033	CAT007
R023	CAT008
R024	CAT008
R026	CAT009
R027	CAT010
R028	CAT010
\.


--
-- TOC entry 5106 (class 0 OID 34936)
-- Dependencies: 232
-- Data for Name: contient; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.contient (id_categorie, id_categorie_1) FROM stdin;
CAT001	CAT004
CAT002	CAT004
CAT003	CAT005
CAT001	CAT005
CAT002	CAT005
CAT003	CAT006
CAT003	CAT007
CAT003	CAT008
CAT003	CAT009
CAT003	CAT010
CAT007	CAT008
CAT007	CAT009
\.


--
-- TOC entry 5116 (class 0 OID 35071)
-- Dependencies: 242
-- Data for Name: diplome; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.diplome (id_diplome, nom_diplome) FROM stdin;
DIPL001	Doctorat en Médecine
DIPL002	DES Médecine générale
DIPL003	DES Endocrinologie
DIPL004	DES Oncologie médicale
DIPL005	DES Gynécologie-obstétrique
DIPL006	DES Radiologie et imagerie médicale
DIPL007	DES Chirurgie générale
DIPL008	Diplôme d'État d'Infirmier
DIPL009	Diplôme d'État de Sage-femme
DIPL010	Doctorat en Pharmacie
DIPL011	DESC Diabétologie-endocrinologie
DIPL012	DESC Chirurgie plastique
DIPL013	Capacité en médecine d'urgence
DIPL014	Master en Santé publique
DIPL015	Master en Épidémiologie
DIPL016	DU Échographie
DIPL017	DU Nutrition clinique
DIPL018	Certificat d'études supérieures en psychologie médicale
DIPL019	Master en Administration des entreprises (MBA)
DIPL020	Master en Management
DIPL021	Master en Communication
DIPL022	Licence en Langues étrangères appliquées
DIPL023	Master en Informatique
DIPL024	Licence en Économie-Gestion
DIPL025	Master en Droit
DIPL026	Licence en Psychologie
DIPL027	Master en Sciences de l'éducation
DIPL028	Licence en Sociologie
DIPL029	BTS Management des unités commerciales
DIPL030	DUT Gestion des entreprises et administrations
DIPL031	Licence professionnelle en Qualité
DIPL032	Certificat en Comptabilité et Gestion
DIPL033	Diplôme d'ingénieur informatique
DIPL034	Master en Sciences et Technologies
DIPL035	Licence en Arts
DIPL036	Diplôme d'études musicales
DIPL037	Certificat en Photographie
DIPL038	Brevet de secourisme
DIPL039	Licence STAPS
DIPL040	Master en Développement durable
\.


--
-- TOC entry 5112 (class 0 OID 35033)
-- Dependencies: 238
-- Data for Name: disponibilite; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.disponibilite (id_disponibilite, id_ressource, jour_semaine, heure_debut, heure_fin, type_creneau) FROM stdin;
D001	R001	Lundi	08:00:00	12:00:00	Consultation
D002	R001	Lundi	14:00:00	18:00:00	Consultation
D003	R001	Mardi	08:00:00	12:00:00	Consultation
D004	R001	Mercredi	08:00:00	12:00:00	Consultation
D005	R001	Jeudi	08:00:00	12:00:00	Consultation
D006	R001	Vendredi	08:00:00	12:00:00	Consultation
D007	R002	Lundi	09:00:00	17:00:00	Consultation
D008	R002	Mardi	09:00:00	17:00:00	Consultation
D009	R002	Mercredi	09:00:00	12:00:00	Consultation
D010	R002	Jeudi	09:00:00	17:00:00	Consultation
D011	R002	Vendredi	09:00:00	17:00:00	Consultation
D012	R009	Lundi	09:00:00	17:00:00	Consultation
D013	R009	Mardi	09:00:00	17:00:00	Consultation
D014	R009	Mercredi	09:00:00	17:00:00	Consultation
D015	R009	Jeudi	09:00:00	17:00:00	Consultation
D016	R009	Vendredi	09:00:00	17:00:00	Consultation
D017	R011	Lundi	09:00:00	17:00:00	Consultation
D018	R011	Mardi	09:00:00	17:00:00	Consultation
D019	R011	Mercredi	09:00:00	17:00:00	Consultation
D020	R011	Jeudi	09:00:00	17:00:00	Consultation
D021	R011	Vendredi	09:00:00	17:00:00	Consultation
D022	R005	Lundi	07:00:00	19:00:00	Soins à domicile
D023	R005	Mardi	07:00:00	19:00:00	Soins à domicile
D024	R005	Mercredi	07:00:00	19:00:00	Soins à domicile
D025	R005	Jeudi	07:00:00	19:00:00	Soins à domicile
D026	R005	Vendredi	07:00:00	19:00:00	Soins à domicile
D027	R016	Lundi	00:00:00	23:59:00	Urgence
D028	R016	Mardi	00:00:00	23:59:00	Urgence
D029	R016	Mercredi	00:00:00	23:59:00	Urgence
D030	R016	Jeudi	00:00:00	23:59:00	Urgence
D031	R016	Vendredi	00:00:00	23:59:00	Urgence
D032	R016	Samedi	00:00:00	23:59:00	Urgence
D033	R016	Dimanche	00:00:00	23:59:00	Urgence
D034	R019	Lundi	08:00:00	17:00:00	Dépistage
D035	R019	Mardi	08:00:00	17:00:00	Dépistage
D036	R019	Mercredi	08:00:00	17:00:00	Dépistage
D037	R019	Jeudi	08:00:00	17:00:00	Dépistage
D038	R019	Vendredi	08:00:00	17:00:00	Dépistage
D039	R021	Lundi	09:00:00	17:00:00	Consultation
D040	R021	Mardi	09:00:00	17:00:00	Consultation
D041	R021	Mercredi	09:00:00	17:00:00	Consultation
D042	R021	Jeudi	09:00:00	17:00:00	Consultation
D043	R021	Vendredi	09:00:00	17:00:00	Consultation
D044	R023	Lundi	09:00:00	18:00:00	Conseil nutrition
D045	R023	Mardi	09:00:00	18:00:00	Conseil nutrition
D046	R023	Mercredi	09:00:00	18:00:00	Conseil nutrition
D047	R023	Jeudi	09:00:00	18:00:00	Conseil nutrition
D048	R023	Vendredi	09:00:00	18:00:00	Conseil nutrition
D049	R025	Lundi	09:00:00	17:00:00	Éducation thérapeutique
D050	R025	Mardi	09:00:00	17:00:00	Éducation thérapeutique
D051	R025	Mercredi	09:00:00	17:00:00	Éducation thérapeutique
D052	R025	Jeudi	09:00:00	17:00:00	Éducation thérapeutique
D053	R025	Vendredi	09:00:00	17:00:00	Éducation thérapeutique
D054	R027	Lundi	09:00:00	18:00:00	Consultation psychologique
D055	R027	Mardi	09:00:00	18:00:00	Consultation psychologique
D056	R027	Mercredi	09:00:00	18:00:00	Consultation psychologique
D057	R027	Jeudi	09:00:00	18:00:00	Consultation psychologique
D058	R027	Vendredi	09:00:00	18:00:00	Consultation psychologique
D059	R029	Lundi	07:00:00	18:00:00	Prélèvements
D060	R029	Mardi	07:00:00	18:00:00	Prélèvements
D061	R029	Mercredi	07:00:00	18:00:00	Prélèvements
D062	R029	Jeudi	07:00:00	18:00:00	Prélèvements
D063	R029	Vendredi	07:00:00	18:00:00	Prélèvements
D064	R029	Samedi	08:00:00	12:00:00	Prélèvements
D065	R032	Lundi	08:00:00	19:00:00	Consultations multiples
D066	R032	Mardi	08:00:00	19:00:00	Consultations multiples
D067	R032	Mercredi	08:00:00	19:00:00	Consultations multiples
D068	R032	Jeudi	08:00:00	19:00:00	Consultations multiples
D069	R032	Vendredi	08:00:00	19:00:00	Consultations multiples
D070	R032	Samedi	09:00:00	12:00:00	Consultations multiples
\.


--
-- TOC entry 5103 (class 0 OID 34891)
-- Dependencies: 229
-- Data for Name: est_associe_a; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.est_associe_a (id_parcours, id_theme) FROM stdin;
PC001	TH001
PC002	TH001
PC003	TH002
PC004	TH003
PC005	TH003
PC006	TH001
PC007	TH003
PC008	TH004
PC009	TH002
PC010	TH004
PC011	TH007
PC011	TH008
PC011	TH009
PC012	TH006
PC012	TH004
PC013	TH007
PC013	TH010
PC014	TH008
PC014	TH011
PC015	TH006
PC016	TH008
PC016	TH011
PC017	TH013
PC017	TH008
PC018	TH007
PC018	TH010
PC019	TH008
PC020	TH007
\.


--
-- TOC entry 5109 (class 0 OID 34981)
-- Dependencies: 235
-- Data for Name: etre_malade; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.etre_malade (id_personne, id_theme, date_diagnostic, gravite) FROM stdin;
P001	TH001	2024-02-10	Modérée
P002	TH001	2024-02-15	Sévère
P003	TH002	2023-06-15	Contrôlée
P004	TH003	2024-03-25	Légère
P005	TH003	2023-01-15	Modérée
P006	TH001	2024-01-25	Précoce
P007	TH003	2023-03-10	Modérée
P009	TH002	2023-08-20	Sévère
\.


--
-- TOC entry 5115 (class 0 OID 35066)
-- Dependencies: 241
-- Data for Name: formation; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.formation (id_formation, nom_formation) FROM stdin;
FORM001	DU Douleur et soins palliatifs
FORM002	Formation en éducation thérapeutique
FORM003	Capacité de médecine d'urgence
FORM004	Formation en échographie
FORM005	DU Oncologie médicale
FORM006	Formation en diabétologie
FORM007	Certificat en nutrition clinique
FORM008	Formation en psycho-oncologie
FORM009	DU Imagerie mammaire
FORM010	Formation en chirurgie reconstructrice
FORM011	Certification basque EUSKERA
FORM012	Formation en espagnol médical
FORM013	Anglais médical - Niveau B2
FORM014	Communication multilingue en santé
FORM015	Formation aux systèmes d'information hospitaliers
FORM016	Maîtrise des logiciels de radiologie
FORM017	Télémédecine et e-santé
FORM018	Sécurité informatique en santé
FORM019	Formation bureautique avancée
FORM020	Outils de gestion de projet
FORM021	Management d'équipes soignantes
FORM022	Communication patient-soignant
FORM023	Gestion de la qualité hospitalière
FORM024	Accueil et relation clientèle
FORM025	Formation de formateur
FORM026	Premiers secours - PSC1
FORM027	Développement durable en santé
FORM028	Musicothérapie
FORM029	Art-thérapie
FORM030	Médiation culturelle
FORM031	Comptabilité générale
FORM032	Droit de la santé
FORM033	Recherche documentaire médicale
FORM034	Statistiques médicales
FORM035	Photographie médicale
\.


--
-- TOC entry 5092 (class 0 OID 34798)
-- Dependencies: 218
-- Data for Name: groupepersonne; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.groupepersonne (id_groupe, nomgroupe, description_groupe) FROM stdin;
GP001	Patients diabétiques	Groupe de patients atteints de diabète
GP002	Patientes cancer du sein	Groupe de patientes atteintes de cancer du sein
GP003	Aidants familiaux	Groupe des aidants familiaux
GP004	Professionnels de santé	Groupe des professionnels de santé du territoire
GP005	Groupe prévention active	Personnes engagées dans la prévention
GP006	Dépistage organisé	Participants aux campagnes de dépistage
GP007	Éducation nutritionnelle	Participants aux ateliers nutrition
\.


--
-- TOC entry 5098 (class 0 OID 34830)
-- Dependencies: 224
-- Data for Name: niveau_recours; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.niveau_recours (id_niveau_recours, nom_niveau, ordre_niveau, description_niveau) FROM stdin;
NR001	1er recours	1	Accès aux praticiens généralistes, infirmières, pharmaciens
NR002	2ème recours	2	Accès aux médecins spécialistes
NR003	3ème recours	3	Accès aux structures de soin hospitalières
NR004	Prévention	0	Niveau préventif - actions de prévention primaire et secondaire, dépistages, éducation sanitaire
\.


--
-- TOC entry 5101 (class 0 OID 34861)
-- Dependencies: 227
-- Data for Name: parcours; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.parcours (id_parcours, datedebut_parcours, datefin_parcours, id_parcours_type, id_personne) FROM stdin;
PC001	2024-01-15	2024-12-15	PT001	P001
PC002	2024-02-01	2024-12-31	PT001	P002
PC003	2023-06-01	2024-06-01	PT002	P003
PC004	2024-03-15	2024-12-15	PT003	P004
PC005	2023-01-01	2024-01-01	PT003	P005
PC006	2024-01-10	2024-12-10	PT001	P006
PC007	2023-03-01	2024-03-01	PT003	P007
PC008	2024-05-01	2024-11-01	PT004	P008
PC009	2023-08-15	2024-08-15	PT002	P009
PC010	2024-04-01	2024-10-01	PT004	P010
PC011	2024-06-01	2025-06-01	PT005	P011
PC012	2024-07-01	2025-01-01	PT006	P012
PC013	2024-05-15	2025-05-15	PT007	P013
PC014	2024-08-01	2024-12-01	PT008	P014
PC015	2024-06-15	2024-12-15	PT006	P015
PC016	2024-09-01	2025-03-01	PT008	P016
PC017	2024-10-01	2025-10-01	PT005	P017
PC018	2024-08-15	2025-02-15	PT007	P018
PC019	2024-11-01	2025-05-01	PT008	P019
PC020	2024-09-15	2025-03-15	PT007	P020
\.


--
-- TOC entry 5096 (class 0 OID 34818)
-- Dependencies: 222
-- Data for Name: parcours_type; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.parcours_type (id_parcours_type, nom_parcours_type, description_parcours_type) FROM stdin;
PT001	Parcours Cancer du Sein	Parcours de soins pour le cancer du sein
PT002	Parcours Diabète Type 1	Parcours de soins pour diabète de type 1
PT003	Parcours Diabète Type 2	Parcours de soins pour diabète de type 2
PT004	Prévention et Dépistage	Parcours préventif et de dépistage
PT005	Parcours Prévention Globale	Parcours de prévention primaire et secondaire
PT006	Parcours Dépistage Cancer Sein	Parcours de dépistage organisé cancer du sein
PT007	Parcours Prévention Diabète	Parcours de prévention du diabète type 2
PT008	Parcours Éducation Santé	Parcours d'éducation thérapeutique et préventive
\.


--
-- TOC entry 5091 (class 0 OID 34793)
-- Dependencies: 217
-- Data for Name: personne; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.personne (id_personne, nom, prenom, datenaissance, sex, no_rue, code_postale, ville, csp, latitude_personne, longitude_personne) FROM stdin;
P001	Dubois	Marie	1965-03-15	F	25	64100	Bayonne	Employée	43.49	-1.48
P002	Garcia	Carmen	1958-07-22	F	12	64100	Bayonne	Retraitée	43.48	-1.48
P003	Martin	Pierre	1972-11-08	M	8	64100	Bayonne	Cadre	43.49	-1.47
P004	Etcheverry	Maite	1980-05-30	F	45	64100	Bayonne	Enseignante	43.49	-1.48
P005	Lopez	Jean	1955-12-12	M	33	64100	Bayonne	Retraité	43.48	-1.47
P006	Iraola	Amaia	1975-09-18	F	18	64100	Bayonne	Infirmière	43.49	-1.47
P007	Perez	Miguel	1968-04-25	M	52	64100	Bayonne	Ouvrier	43.48	-1.48
P008	Dufour	Sylvie	1962-11-30	F	7	64100	Bayonne	Commerçante	43.49	-1.48
P009	Mendiboure	Patxi	1985-02-14	M	23	64100	Bayonne	Technicien	43.48	-1.48
P010	Robert	Claire	1970-06-08	F	41	64100	Bayonne	Secrétaire	43.49	-1.47
P011	Larralde	Nerea	1978-08-15	F	14	64100	Bayonne	Professeur	43.49	-1.47
P012	Dupouy	Henri	1965-01-20	M	36	64100	Bayonne	Cadre	43.49	-1.48
P013	Etchebarne	Maider	1985-12-03	F	21	64100	Bayonne	Ingénieure	43.48	-1.48
P014	Sallaberry	Peio	1970-03-28	M	9	64100	Bayonne	Artisan	43.48	-1.48
P015	Mousques	Fabienne	1955-09-12	F	48	64100	Bayonne	Retraitée	43.49	-1.47
P016	Ospital	Xabier	1982-06-10	M	15	64100	Bayonne	Développeur	43.48	-1.47
P017	Barbé	Sandrine	1973-02-18	F	28	64100	Bayonne	Infirmière	43.49	-1.48
P018	Harispe	Michel	1960-10-05	M	33	64100	Bayonne	Retraité	43.48	-1.48
P019	Lascaux	Julie	1990-04-22	F	19	64100	Bayonne	Étudiante	43.49	-1.47
P020	Errecart	Manex	1977-12-30	M	42	64100	Bayonne	Commercial	43.49	-1.48
\.


--
-- TOC entry 5108 (class 0 OID 34966)
-- Dependencies: 234
-- Data for Name: prevoit_ressource; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.prevoit_ressource (id_ressource, id_parcours_type, ordre, frequence, nombre_de_visite) FROM stdin;
R002	PT001	1	Une fois	1
R013	PT001	2	Une fois	1
R014	PT001	3	Une fois	1
R011	PT001	4	Mensuelle	6
R016	PT001	5	Selon besoin	2
R005	PT001	6	Hebdomadaire	12
R001	PT002	1	Une fois	1
R009	PT002	2	Trimestrielle	4
R005	PT002	3	Mensuelle	3
R007	PT002	4	Mensuelle	12
R003	PT003	1	Une fois	1
R010	PT003	2	Semestrielle	2
R005	PT003	3	Une fois	1
R008	PT003	4	Trimestrielle	4
R004	PT004	1	Annuelle	1
R013	PT004	2	Bisannuelle	1
R014	PT004	3	Bisannuelle	1
R021	PT005	1	Annuelle	1
R023	PT005	2	Semestrielle	2
R026	PT005	3	Trimestrielle	4
R029	PT005	4	Annuelle	1
R019	PT006	1	Bisannuelle	1
R021	PT006	2	Annuelle	1
R027	PT006	3	Selon besoin	2
R022	PT007	1	Semestrielle	2
R023	PT007	2	Trimestrielle	4
R025	PT007	3	Mensuelle	6
R030	PT007	4	Trimestrielle	4
R025	PT008	1	Mensuelle	6
R024	PT008	2	Mensuelle	3
R027	PT008	3	Mensuelle	4
R032	PT008	4	Hebdomadaire	12
\.


--
-- TOC entry 5107 (class 0 OID 34951)
-- Dependencies: 233
-- Data for Name: prevu_pour; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.prevu_pour (id_theme, id_parcours_type) FROM stdin;
TH001	PT001
TH004	PT001
TH002	PT002
TH003	PT003
TH005	PT002
TH005	PT003
TH004	PT004
TH001	PT004
TH007	PT005
TH008	PT005
TH009	PT005
TH013	PT005
TH006	PT006
TH004	PT006
TH007	PT007
TH010	PT007
TH008	PT007
TH009	PT007
TH008	PT008
TH011	PT008
TH009	PT008
\.


--
-- TOC entry 5100 (class 0 OID 34849)
-- Dependencies: 226
-- Data for Name: ressource; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.ressource (id_ressource, nom_ressource, description_ressource, typeressource, telephone, email, horaires_ouverture, secteur, conventionnement, latitude_ressource, longitude_ressource, id_type) FROM stdin;
R001	Dr Puyoo Jean	Médecin généraliste expérimenté	Praticien	05.59.25.48.72	dr.puyoo@email.com	Lu-Ve: 8h-18h	Secteur 1	Conventionné	43.48	-1.49	TP001
R002	Dr Labatut Marie	Médecin généraliste, suivi diabète	Praticien	05.59.46.12.35	dr.labatut@email.com	Lu-Ve: 9h-17h	Secteur 1	Conventionné	43.49	-1.49	TP001
R003	Dr Durand Pierre	Médecin généraliste centre-ville	Praticien	05.59.59.23.45	dr.durand@email.com	Lu-Sa: 8h30-19h	Secteur 1	Conventionné	43.49	-1.47	TP001
R004	Dr Etxeberria Maite	Médecin généraliste bilingue	Praticien	05.59.63.18.92	dr.etxeberria@email.com	Lu-Ve: 8h-18h	Secteur 1	Conventionné	43.48	-1.49	TP001
R005	Mme Etcheverry Sophie	Infirmière à domicile, spécialisée diabète	Praticien	06.12.34.56.78	setcheverry@infirmier.com	Lu-Ve: 7h-19h		Conventionné	43.49	-1.48	TP002
R006	M. Darrigrand Paul	Infirmier cabinet libéral	Praticien	06.23.45.67.89	pdarrigrand@infirmier.com	Lu-Sa: 8h-20h		Conventionné	43.49	-1.47	TP002
R007	Pharmacie de la Nive	Pharmacie centre-ville, conseil diabète	Praticien	05.59.59.12.34	pharmacie.nive@email.com	Lu-Sa: 8h30-19h30		Conventionné	43.49	-1.47	TP003
R008	Pharmacie Sainte-Croix	Pharmacie de quartier, matériel diabète	Praticien	05.59.63.45.67	pharmacie.stecroix@email.com	Lu-Sa: 9h-19h		Conventionné	43.48	-1.49	TP003
R009	Dr Aguirre Carmen	Endocrinologue diabétologue	Praticien	05.59.42.18.73	dr.aguirre@endocrino.com	Lu-Ve: 9h-17h	Secteur 2	Conventionné DP	43.49	-1.47	TP005
R010	Dr Martinez Luis	Diabétologue, nouvelles technologies	Praticien	05.59.55.27.84	dr.martinez@diabeto.com	Lu-Je: 8h30-18h	Secteur 1	Conventionné	43.48	-1.48	TP010
R011	Dr Berasategui Ana	Oncologue médical	Praticien	05.59.46.37.92	dr.berasategui@onco.com	Lu-Ve: 9h-17h	Secteur 2	Conventionné DP	43.49	-1.47	TP006
R012	Dr Larrea Michel	Oncologue, spécialiste sein	Praticien	05.59.51.43.28	dr.larrea@onco.com	Ma-Sa: 8h-16h	Secteur 2	Conventionné DP	43.49	-1.48	TP006
R013	Dr Irigoyen Elena	Gynécologue obstétricien	Praticien	05.59.39.17.54	dr.irigoyen@gyneco.com	Lu-Ve: 9h-18h	Secteur 2	Conventionné DP	43.48	-1.48	TP007
R014	Cabinet Radiologie Bayonne	Imagerie mammaire et générale	Praticien	05.59.64.82.39	contact@radio-bayonne.com	Lu-Ve: 8h-18h	Secteur 2	Conventionné DP	43.49	-1.47	TP008
R015	Dr Pereira João	Chirurgien général et sein	Praticien	05.59.48.73.91	dr.pereira@chirurgie.com	Lu-Ve: 8h-17h	Secteur 2	Conventionné DP	43.49	-1.47	TP009
R016	Centre Hospitalier de la Côte Basque	Hôpital public de Bayonne	Structure	05.59.44.35.35	contact@ch-cotebasque.fr	24h/24 7j/7		Service public	43.47	-1.47	TP011
R017	Clinique Belharra	Clinique privée pluridisciplinaire	Structure	05.59.44.44.44	accueil@belharra.com	24h/24 7j/7		Conventionné	43.48	-1.48	TP012
R018	Centre de Cancérologie du Pays Basque	Centre spécialisé oncologie	Structure	05.59.52.73.84	contact@cancer-paysbasque.fr	Lu-Ve: 8h-18h		Conventionné	43.48	-1.47	TP013
R019	Centre de Dépistage ADECA 64	Centre de dépistage cancer sein, côlon	Structure	05.59.44.10.10	bayonne@adeca64.fr	Lu-Ve: 8h-17h		Service public	43.49	-1.47	TP015
R020	Unité Mobile de Dépistage	Mammographe mobile pour zones isolées	Structure	05.59.44.10.15	mobile@adeca64.fr	Selon planning		Service public	43.48	-1.48	TP015
R021	Dr Harriague Sophie	Médecin de prévention et santé publique	Praticien	05.59.46.23.18	dr.harriague@prevention.com	Lu-Ve: 9h-17h	Secteur 1	Conventionné	43.49	-1.48	TP016
R022	Dr Etchegoyen Marc	Médecin préventiviste, bilans santé	Praticien	05.59.52.41.29	dr.etchegoyen@prevention.com	Ma-Sa: 8h30-16h30	Secteur 1	Conventionné	43.49	-1.47	TP016
R023	Mme Cazaubon Élise	Diététicienne-nutritionniste prévention	Praticien	05.59.25.63.47	e.cazaubon@nutrition.com	Lu-Ve: 9h-18h		Conventionné	43.48	-1.48	TP017
R024	M. Olharan Mikel	Nutritionniste sport et prévention	Praticien	05.59.59.18.73	m.olharan@nutrition.com	Lu-Sa: 8h-19h		Conventionné	43.49	-1.47	TP017
R025	Mme Bergé Annie	Éducatrice thérapeutique diabète	Praticien	05.59.63.92.14	a.berge@education-sante.fr	Lu-Ve: 9h-17h		Conventionné	43.49	-1.47	TP018
R026	M. Idiart Jon	Éducateur santé activité physique	Praticien	05.59.48.25.86	j.idiart@education-sante.fr	Lu-Ve: 8h-18h		Conventionné	43.48	-1.48	TP018
R027	Mme Lassalle Catherine	Psychologue prévention, gestion stress	Praticien	05.59.39.74.52	c.lassalle@psy-prevention.fr	Lu-Ve: 9h-18h	Secteur 2	Conventionné DP	43.49	-1.47	TP019
R028	M. Duhalde Paul	Psychologue comportements de santé	Praticien	05.59.55.17.83	p.duhalde@psy-prevention.fr	Ma-Sa: 9h-17h	Secteur 2	Conventionné DP	43.48	-1.48	TP019
R029	Laboratoire Biobasque	Analyses biologiques préventives	Structure	05.59.44.67.89	accueil@biobasque.fr	Lu-Ve: 7h-18h, Sa: 8h-12h		Conventionné	43.49	-1.47	TP020
R030	Laboratoire Côte Basque Analyses	Bilans préventifs spécialisés	Structure	05.59.52.83.94	contact@labo-cotebasque.fr	Lu-Ve: 7h30-18h30, Sa: 8h-13h		Conventionné	43.49	-1.47	TP020
R031	Centre de Vaccination Municipal	Vaccinations adultes et voyages	Structure	05.59.46.60.00	vaccination@bayonne.fr	Lu-Ve: 9h-16h		Service public	43.49	-1.47	TP021
R032	Maison de Santé Pluridisciplinaire Nive	MSP prévention et éducation santé	Structure	05.59.25.74.85	contact@msp-nive.fr	Lu-Ve: 8h-19h, Sa: 9h-12h		Conventionné	43.49	-1.48	TP022
R033	Maison de Santé Saint-Esprit	MSP quartier, actions préventives	Structure	05.59.63.85.96	accueil@msp-stesprit.fr	Lu-Ve: 8h30-18h30		Conventionné	43.48	-1.48	TP022
\.


--
-- TOC entry 5119 (class 0 OID 35107)
-- Dependencies: 245
-- Data for Name: ressource_diplome; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.ressource_diplome (id_ressource, id_diplome, annee_obtention, etablissement) FROM stdin;
R001	DIPL001	1995	Université de Bordeaux
R001	DIPL002	1999	Université de Bordeaux
R001	DIPL022	1993	Université de Pau
R002	DIPL001	2001	Université de Toulouse
R002	DIPL002	2005	Université de Toulouse
R002	DIPL017	2010	CHU Toulouse
R003	DIPL001	1998	Université de Bordeaux
R003	DIPL002	2002	Université de Bordeaux
R003	DIPL013	2005	Université de Bordeaux
R003	DIPL019	1996	IAE Bordeaux
R004	DIPL001	2003	Université du Pays Basque - Espagne
R004	DIPL002	2007	Université de Bordeaux
R004	DIPL022	2001	Université du Pays Basque
R005	DIPL008	2008	IFSI Bayonne
R005	DIPL018	2015	Université de Bordeaux
R005	DIPL026	2006	Université de Pau
R006	DIPL008	2005	IFSI Pau
R006	DIPL030	2003	IUT Bayonne
R006	DIPL038	2004	Croix-Rouge Française
R009	DIPL001	1992	Université de Salamanque - Espagne
R009	DIPL003	1996	CHU Bordeaux
R009	DIPL015	2000	ISPED Bordeaux
R009	DIPL022	1990	Université de Salamanque
R010	DIPL001	2000	Université de Saragosse - Espagne
R010	DIPL011	2004	CHU Toulouse
R010	DIPL023	1998	Université de Saragosse
R011	DIPL001	1997	Université de Navarre - Espagne
R011	DIPL004	2001	CHU Bordeaux
R011	DIPL014	2005	EHESP Rennes
R012	DIPL001	1994	Université de Bordeaux
R012	DIPL004	1998	CHU Bordeaux
R012	DIPL012	2003	CHU Paris
R013	DIPL001	1999	Université du Pays Basque - Espagne
R013	DIPL005	2003	CHU Bordeaux
R013	DIPL026	1997	Université du Pays Basque
R014	DIPL001	1989	Université de Bordeaux
R014	DIPL006	1993	CHU Bordeaux
R014	DIPL031	2010	Université de Bordeaux
R015	DIPL001	1985	Université de Lisbonne - Portugal
R015	DIPL007	1989	CHU Bordeaux
R015	DIPL012	1995	CHU Paris
\.


--
-- TOC entry 5118 (class 0 OID 35092)
-- Dependencies: 244
-- Data for Name: ressource_formation; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.ressource_formation (id_ressource, id_formation, date_formation, organisme_formation) FROM stdin;
R001	FORM011	2018-06-15	Institut Culturel Basque
R001	FORM025	2020-09-10	CHU Bordeaux
R002	FORM002	2019-03-20	AFDET
R002	FORM006	2021-11-15	SFD - Société Francophone du Diabète
R003	FORM003	2017-05-12	CFMU
R003	FORM021	2022-01-18	EHESP Rennes
R004	FORM011	2016-08-22	Institut Culturel Basque
R004	FORM012	2019-10-05	Centre Hispanique Bayonne
R005	FORM002	2020-04-12	AFDET
R005	FORM001	2021-09-30	SFAP
R009	FORM008	2019-06-18	AFSOS
R009	FORM033	2022-03-25	Université de Bordeaux
R010	FORM017	2021-11-08	ASIP Santé
R010	FORM006	2018-09-14	SFD
R011	FORM005	2020-02-28	SFO - Société Française d'Oncologie
R011	FORM008	2021-05-20	AFSOS
R012	FORM009	2019-10-15	SIFEM
R012	FORM021	2022-07-12	Institut Curie
R013	FORM022	2020-11-30	CNGOF
R014	FORM016	2021-08-25	SFR - Société Française de Radiologie
\.


--
-- TOC entry 5110 (class 0 OID 34996)
-- Dependencies: 236
-- Data for Name: ressource_specialite; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.ressource_specialite (id_ressource, id_specialite) FROM stdin;
R001	SP001
R002	SP001
R003	SP001
R004	SP001
R009	SP002
R010	SP008
R011	SP003
R012	SP003
R013	SP004
R014	SP005
R015	SP006
R019	SP011
R020	SP011
R021	SP009
R022	SP009
R023	SP010
R024	SP010
R025	SP012
R026	SP012
R027	SP013
R028	SP013
R029	SP014
R030	SP014
R031	SP015
R032	SP009
R032	SP010
R032	SP012
R033	SP009
R033	SP012
\.


--
-- TOC entry 5117 (class 0 OID 35077)
-- Dependencies: 243
-- Data for Name: ressource_specificite; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.ressource_specificite (id_ressource, id_specificite) FROM stdin;
R001	SPEC004
R001	SPEC011
R001	SPEC020
R002	SPEC004
R002	SPEC003
R002	SPEC007
R003	SPEC005
R003	SPEC019
R003	SPEC017
R004	SPEC011
R004	SPEC012
R004	SPEC016
R005	SPEC003
R005	SPEC010
R005	SPEC011
R006	SPEC005
R006	SPEC015
R006	SPEC020
R009	SPEC009
R009	SPEC021
R009	SPEC012
R010	SPEC017
R010	SPEC003
R010	SPEC012
R011	SPEC008
R011	SPEC002
R011	SPEC013
R012	SPEC006
R012	SPEC001
R012	SPEC021
R013	SPEC013
R013	SPEC011
R013	SPEC003
R014	SPEC007
R014	SPEC017
R014	SPEC018
\.


--
-- TOC entry 5097 (class 0 OID 34823)
-- Dependencies: 223
-- Data for Name: specialite; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.specialite (id_specialite, nom_specialite, description_specialite) FROM stdin;
SP001	Médecine générale	Médecine de première ligne
SP002	Endocrinologie	Spécialité des glandes endocrines et hormones
SP003	Oncologie médicale	Traitement médical des cancers
SP004	Gynécologie	Spécialité de l'appareil génital féminin
SP005	Radiologie	Imagerie médicale et radiologie interventionnelle
SP006	Chirurgie générale	Chirurgie viscérale et générale
SP007	Chirurgie plastique	Chirurgie reconstructrice et esthétique
SP008	Diabétologie	Spécialité du diabète et de ses complications
SP009	Médecine préventive	Prévention primaire et secondaire
SP010	Nutrition préventive	Conseil nutritionnel et diététique préventive
SP011	Dépistage organisé	Coordination des programmes de dépistage
SP012	Éducation thérapeutique	Formation et accompagnement des patients
SP013	Psychologie préventive	Accompagnement psychologique préventif
SP014	Biologie préventive	Analyses biologiques de prévention
SP015	Vaccination	Prévention par vaccination
\.


--
-- TOC entry 5114 (class 0 OID 35061)
-- Dependencies: 240
-- Data for Name: specificite; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.specificite (id_specificite, nom_specificite) FROM stdin;
SPEC001	Prise en charge de la douleur
SPEC002	Médecine palliative
SPEC003	Éducation thérapeutique du patient
SPEC004	Suivi des pathologies chroniques
SPEC005	Urgences vitales
SPEC006	Chirurgie mammaire
SPEC007	Imagerie interventionnelle
SPEC008	Oncologie digestive
SPEC009	Diabétologie pédiatrique
SPEC010	Soins palliatifs à domicile
SPEC011	Langue basque
SPEC012	Langue espagnole
SPEC013	Accompagnement psychologique
SPEC014	Nutrition sportive
SPEC015	Gestion administrative
SPEC016	Communication interculturelle
SPEC017	Informatique médicale
SPEC018	Qualité et accréditation
SPEC019	Management d'équipe
SPEC020	Formation et pédagogie
SPEC021	Recherche clinique
SPEC022	Économie de la santé
SPEC023	Relations publiques
SPEC024	Développement durable
SPEC025	Arts thérapeutiques
\.


--
-- TOC entry 5095 (class 0 OID 34813)
-- Dependencies: 221
-- Data for Name: theme; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.theme (id_theme, nomtheme, niveau_theme, description_theme) FROM stdin;
TH001	Cancer du sein	Critique	Pathologie oncologique 
TH002	Diabète de type 1	Chronique	Pathologie endocrinienne
TH003	Diabète de type 2	Chronique	Pathologie métabolique courante
TH004	Prévention cancer du sein	Préventif	Dépistage et prévention du cancer du sein
TH005	Complications diabétiques	Critique	Complications liées au diabète non contrôlé
TH006	Dépistage mammographique	Préventif	Dépistage organisé du cancer du sein
TH007	Prévention diabète	Préventif	Prévention primaire du diabète type 2
TH008	Éducation nutritionnelle	Préventif	Éducation alimentaire préventive
TH009	Activité physique adaptée	Préventif	Promotion de l'activité physique
TH010	Dépistage précoce diabète	Préventif	Détection précoce des troubles glycémiques
TH011	Soutien psychologique préventif	Préventif	Accompagnement psychologique en prévention
TH012	Vaccination adulte	Préventif	Programme vaccinal adulte
TH013	Bilan de santé préventif	Préventif	Check-up préventif global
\.


--
-- TOC entry 5099 (class 0 OID 34837)
-- Dependencies: 225
-- Data for Name: type_praticien_structure; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.type_praticien_structure (id_type, nom_type, description_type, id_niveau_recours) FROM stdin;
TP001	Médecin généraliste	Médecine générale de proximité	NR001
TP002	Infirmier(ère)	Soins infirmiers à domicile et en cabinet	NR001
TP003	Pharmacien	Conseil pharmaceutique et suivi médicamenteux	NR001
TP004	Sage-femme	Suivi gynécologique et obstétrical	NR001
TP005	Endocrinologue	Spécialiste des pathologies endocriniennes (diabète)	NR002
TP006	Oncologue	Spécialiste en cancérologie	NR002
TP007	Gynécologue	Spécialiste en gynécologie	NR002
TP008	Radiologue	Spécialiste en imagerie médicale	NR002
TP009	Chirurgien	Spécialiste en chirurgie	NR002
TP010	Diabétologue	Spécialiste du diabète	NR002
TP011	Hôpital public	Structure hospitalière publique	NR003
TP012	Clinique privée	Structure de soins privée	NR003
TP013	Centre de cancérologie	Centre spécialisé en oncologie	NR003
TP014	Centre de dialyse	Centre spécialisé pour les soins de dialyse	NR003
TP015	Centre de dépistage	Structure dédiée au dépistage organisé	NR004
TP016	Médecin de prévention	Médecin spécialisé en médecine préventive	NR004
TP017	Nutritionniste	Professionnel de la nutrition préventive	NR004
TP018	Éducateur en santé	Professionnel de l'éducation thérapeutique	NR004
TP019	Psychologue de prévention	Psychologue spécialisé en prévention	NR004
TP020	Laboratoire d'analyses	Structure pour analyses préventives	NR004
TP021	Centre de vaccination	Structure pour vaccinations	NR004
TP022	Maison de santé	Structure pluridisciplinaire préventive	NR004
\.


--
-- TOC entry 5111 (class 0 OID 35011)
-- Dependencies: 237
-- Data for Name: utilise_ressource; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.utilise_ressource (id_axe, id_parcours, id_ressource, date_consultation, heure_consultation, duree_consultation, cout_consultation, type_consultation, motif_consultation, satisfaction_patient) FROM stdin;
AX002	PC001	R002	2024-01-15	09:00:00	30	25.00	Consultation	Suspicion nodule sein	4
AX002	PC001	R013	2024-01-22	14:30:00	45	120.00	Consultation spécialisée	Examen gynécologique	5
AX002	PC001	R014	2024-01-25	10:15:00	20	80.00	Imagerie	Mammographie + échographie	4
AX002	PC001	R011	2024-02-05	15:00:00	60	150.00	Consultation spécialisée	Consultation oncologique	5
AX002	PC001	R016	2024-02-15	08:00:00	180	0.00	Hospitalisation	Biopsie mammaire	4
AX001	PC003	R003	2023-06-01	16:00:00	20	25.00	Consultation	Bilan diabète	4
AX002	PC003	R009	2023-06-15	09:30:00	45	135.00	Consultation spécialisée	Consultation endocrinologique	5
AX002	PC003	R005	2023-07-01	18:00:00	15	15.00	Soins	Formation auto-surveillance	5
AX003	PC003	R007	2023-07-01	19:00:00	10	0.00	Conseil	Conseil matériel diabète	4
AX001	PC004	R004	2024-03-15	08:30:00	25	25.00	Consultation	Diagnostic diabète type 2	4
AX002	PC004	R010	2024-03-25	10:00:00	60	125.00	Consultation spécialisée	Bilan diabétologique complet	5
AX002	PC004	R005	2024-04-01	17:30:00	20	18.00	Soins	Education thérapeutique	5
AX001	PC002	R004	2024-02-01	10:00:00	20	25.00	Consultation	Palpation nodule sein	4
AX002	PC002	R013	2024-02-08	15:00:00	40	120.00	Consultation spécialisée	Examen approfondi	5
AX002	PC002	R014	2024-02-12	09:30:00	25	95.00	Imagerie	IRM mammaire	4
AX002	PC002	R012	2024-02-20	14:00:00	75	180.00	Consultation spécialisée	Annonce diagnostic	5
AX002	PC002	R018	2024-03-01	08:30:00	120	0.00	Consultation	Plan de traitement	5
AX002	PC002	R015	2024-03-15	10:00:00	90	200.00	Consultation spécialisée	Consultation pré-opératoire	4
AX001	PC005	R001	2023-01-01	09:00:00	30	25.00	Consultation	Bilan annuel	4
AX002	PC005	R009	2023-01-20	11:00:00	60	135.00	Consultation spécialisée	Bilan diabétologique	5
AX002	PC005	R005	2023-02-01	16:00:00	30	25.00	Soins	Education diététique	4
AX003	PC005	R007	2023-02-15	17:00:00	10	0.00	Conseil	Adaptation traitement	4
AX001	PC005	R001	2023-04-01	08:30:00	20	25.00	Suivi	Contrôle glycémie	4
AX001	PC005	R001	2023-07-01	09:15:00	25	25.00	Suivi	Ajustement traitement	3
AX002	PC005	R009	2023-10-15	14:30:00	45	135.00	Suivi spécialisé	Bilan semestriel	5
AX001	PC003	R003	2023-09-01	10:30:00	20	25.00	Suivi	Contrôle diabète T1	4
AX002	PC003	R010	2023-09-15	15:00:00	50	125.00	Suivi spécialisé	Ajustement insuline	5
AX003	PC003	R005	2023-10-01	18:30:00	25	20.00	Soins	Contrôle technique injection	5
AX001	PC004	R004	2024-06-15	11:00:00	20	25.00	Suivi	Contrôle diabète T2	4
AX002	PC004	R010	2024-07-01	09:30:00	40	125.00	Suivi spécialisé	Bilan trimestriel	4
AX001	PC001	R007	2024-05-15	16:00:00	5	0.00	Conseil	Conseil nutrition cancer	4
AX003	PC001	R005	2024-06-01	17:00:00	45	35.00	Soins	Soins post-chimiothérapie	5
AX001	PC002	R008	2024-06-15	18:00:00	10	0.00	Conseil	Suivi traitement hormonal	4
AX001	PC011	R021	2024-06-01	09:00:00	45	130.00	Bilan préventif	Check-up prévention globale	5
AX001	PC011	R023	2024-06-15	14:30:00	60	75.00	Consultation	Conseil nutritionnel préventif	4
AX001	PC011	R026	2024-06-20	16:00:00	30	45.00	Éducation	Programme activité physique	5
AX001	PC011	R029	2024-06-25	08:00:00	15	45.00	Analyses	Bilan biologique préventif	4
AX001	PC012	R021	2024-07-01	10:00:00	30	130.00	Consultation	Information dépistage	4
AX001	PC012	R019	2024-07-15	09:30:00	20	0.00	Dépistage	Mammographie de dépistage	5
AX003	PC012	R027	2024-07-20	15:00:00	45	90.00	Soutien	Accompagnement psychologique	4
AX001	PC013	R022	2024-05-15	11:00:00	40	130.00	Évaluation	Évaluation risque diabète	5
AX001	PC013	R023	2024-05-25	16:30:00	60	75.00	Conseil	Plan alimentaire préventif	5
AX001	PC013	R025	2024-06-01	09:00:00	45	50.00	Éducation	Éducation prévention diabète	4
AX001	PC013	R030	2024-06-10	08:30:00	10	35.00	Analyses	Test de tolérance glucose	4
AX003	PC014	R025	2024-08-01	14:00:00	60	50.00	Éducation	Atelier éducation santé	5
AX001	PC014	R024	2024-08-10	10:30:00	45	75.00	Conseil	Nutrition et mode de vie	4
AX003	PC014	R027	2024-08-15	16:00:00	50	90.00	Soutien	Gestion stress et santé	5
AX001	PC014	R032	2024-08-20	09:00:00	30	0.00	Atelier	Atelier groupe MSP	4
AX001	PC015	R019	2024-06-15	10:00:00	15	0.00	Dépistage	Mammographie dépistage	4
AX003	PC015	R032	2024-06-20	14:30:00	20	0.00	Information	Information santé femmes	4
AX001	PC011	R023	2024-09-15	15:00:00	45	75.00	Suivi	Suivi plan nutritionnel	5
AX001	PC011	R026	2024-09-20	17:00:00	30	45.00	Suivi	Évaluation activité physique	4
AX001	PC011	R029	2024-12-01	08:30:00	15	45.00	Contrôle	Bilan biologique 6 mois	4
AX001	PC012	R019	2026-07-15	10:00:00	20	0.00	Dépistage	Mammographie contrôle +2 ans	5
AX001	PC013	R022	2024-11-15	14:00:00	30	130.00	Suivi	Contrôle 6 mois prévention	5
AX001	PC013	R025	2024-09-01	10:00:00	45	50.00	Renforcement	Séance renforcement éducation	4
AX001	PC013	R030	2024-12-10	08:00:00	10	35.00	Contrôle	Contrôle glycémie 6 mois	4
AX003	PC014	R025	2024-09-01	15:30:00	60	50.00	Suivi	Atelier suivi éducation	5
AX001	PC014	R032	2024-09-10	10:00:00	45	0.00	Atelier	Atelier cuisine santé MSP	5
AX003	PC014	R027	2024-10-15	16:30:00	45	90.00	Suivi	Bilan gestion stress	4
AX001	PC015	R021	2024-12-15	11:00:00	30	130.00	Bilan	Bilan prévention annuel	4
AX001	PC013	R031	2024-10-01	14:00:00	15	0.00	Vaccination	Vaccination grippe	4
AX001	PC011	R031	2024-10-15	15:00:00	15	0.00	Vaccination	Rappel vaccins	4
AX003	PC016	R025	2024-09-01	10:00:00	60	50.00	Première consultation	Évaluation besoins éducation santé	5
AX001	PC016	R024	2024-09-10	16:30:00	45	75.00	Consultation	Nutrition et vie active	4
AX003	PC016	R028	2024-09-20	14:00:00	50	90.00	Consultation	Gestion stress professionnel	5
AX001	PC017	R022	2024-10-01	09:30:00	45	130.00	Bilan	Check-up prévention professionnels santé	5
AX001	PC017	R023	2024-10-15	15:00:00	60	75.00	Consultation	Nutrition équilibrée travail posté	4
AX001	PC017	R029	2024-10-20	08:00:00	15	50.00	Analyses	Bilan biologique complet	4
AX001	PC018	R021	2024-08-15	11:00:00	40	130.00	Évaluation	Évaluation risque diabète senior	4
AX001	PC018	R023	2024-08-25	10:30:00	60	75.00	Conseil	Adaptation alimentaire âge	5
AX001	PC018	R025	2024-09-05	14:30:00	45	50.00	Éducation	Éducation prévention senior	4
AX003	PC019	R032	2024-11-01	16:00:00	30	0.00	Atelier	Atelier étudiants MSP	5
AX001	PC019	R024	2024-11-10	17:30:00	45	75.00	Conseil	Nutrition étudiant budget serré	4
AX003	PC019	R027	2024-11-15	18:00:00	45	90.00	Soutien	Gestion stress études	5
AX001	PC020	R022	2024-09-15	08:30:00	35	130.00	Dépistage	Dépistage précoce diabète	4
AX001	PC020	R030	2024-09-25	07:30:00	10	40.00	Analyses	Test tolérance glucose	4
AX001	PC020	R025	2024-10-05	15:00:00	50	50.00	Éducation	Prévention diabète actifs	5
AX001	PC017	R031	2024-11-15	09:00:00	20	0.00	Vaccination	Vaccin grippe professionnel santé	5
AX001	PC018	R031	2024-11-01	10:30:00	15	0.00	Vaccination	Rappel vaccins senior	4
AX001	PC020	R033	2024-10-20	14:00:00	30	0.00	Atelier	Atelier prévention diabète	4
AX003	PC016	R033	2024-10-01	16:30:00	45	0.00	Groupe	Groupe parole santé au travail	5
\.


--
-- TOC entry 4881 (class 2606 OID 34910)
-- Name: appartient_a appartient_a_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.appartient_a
    ADD CONSTRAINT appartient_a_pkey PRIMARY KEY (id_categorie, id_theme);


--
-- TOC entry 4877 (class 2606 OID 34880)
-- Name: appartient appartient_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.appartient
    ADD CONSTRAINT appartient_pkey PRIMARY KEY (id_personne, id_groupe);


--
-- TOC entry 4899 (class 2606 OID 35050)
-- Name: avis_ressource avis_ressource_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.avis_ressource
    ADD CONSTRAINT avis_ressource_pkey PRIMARY KEY (id_avis);


--
-- TOC entry 4859 (class 2606 OID 34807)
-- Name: axe axe_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.axe
    ADD CONSTRAINT axe_pkey PRIMARY KEY (id_axe);


--
-- TOC entry 4861 (class 2606 OID 34812)
-- Name: categorie categorie_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.categorie
    ADD CONSTRAINT categorie_pkey PRIMARY KEY (id_categorie);


--
-- TOC entry 4883 (class 2606 OID 34925)
-- Name: classe_dans classe_dans_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.classe_dans
    ADD CONSTRAINT classe_dans_pkey PRIMARY KEY (id_ressource, id_categorie);


--
-- TOC entry 4885 (class 2606 OID 34940)
-- Name: contient contient_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.contient
    ADD CONSTRAINT contient_pkey PRIMARY KEY (id_categorie, id_categorie_1);


--
-- TOC entry 4905 (class 2606 OID 35075)
-- Name: diplome diplome_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.diplome
    ADD CONSTRAINT diplome_pkey PRIMARY KEY (id_diplome);


--
-- TOC entry 4897 (class 2606 OID 35037)
-- Name: disponibilite disponibilite_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.disponibilite
    ADD CONSTRAINT disponibilite_pkey PRIMARY KEY (id_disponibilite);


--
-- TOC entry 4879 (class 2606 OID 34895)
-- Name: est_associe_a est_associe_a_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.est_associe_a
    ADD CONSTRAINT est_associe_a_pkey PRIMARY KEY (id_parcours, id_theme);


--
-- TOC entry 4891 (class 2606 OID 34985)
-- Name: etre_malade etre_malade_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.etre_malade
    ADD CONSTRAINT etre_malade_pkey PRIMARY KEY (id_personne, id_theme);


--
-- TOC entry 4903 (class 2606 OID 35070)
-- Name: formation formation_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.formation
    ADD CONSTRAINT formation_pkey PRIMARY KEY (id_formation);


--
-- TOC entry 4857 (class 2606 OID 34802)
-- Name: groupepersonne groupepersonne_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.groupepersonne
    ADD CONSTRAINT groupepersonne_pkey PRIMARY KEY (id_groupe);


--
-- TOC entry 4869 (class 2606 OID 34836)
-- Name: niveau_recours niveau_recours_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.niveau_recours
    ADD CONSTRAINT niveau_recours_pkey PRIMARY KEY (id_niveau_recours);


--
-- TOC entry 4875 (class 2606 OID 34865)
-- Name: parcours parcours_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.parcours
    ADD CONSTRAINT parcours_pkey PRIMARY KEY (id_parcours);


--
-- TOC entry 4865 (class 2606 OID 34822)
-- Name: parcours_type parcours_type_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.parcours_type
    ADD CONSTRAINT parcours_type_pkey PRIMARY KEY (id_parcours_type);


--
-- TOC entry 4855 (class 2606 OID 34797)
-- Name: personne personne_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.personne
    ADD CONSTRAINT personne_pkey PRIMARY KEY (id_personne);


--
-- TOC entry 4889 (class 2606 OID 34970)
-- Name: prevoit_ressource prevoit_ressource_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.prevoit_ressource
    ADD CONSTRAINT prevoit_ressource_pkey PRIMARY KEY (id_ressource, id_parcours_type);


--
-- TOC entry 4887 (class 2606 OID 34955)
-- Name: prevu_pour prevu_pour_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.prevu_pour
    ADD CONSTRAINT prevu_pour_pkey PRIMARY KEY (id_theme, id_parcours_type);


--
-- TOC entry 4911 (class 2606 OID 35111)
-- Name: ressource_diplome ressource_diplome_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.ressource_diplome
    ADD CONSTRAINT ressource_diplome_pkey PRIMARY KEY (id_ressource, id_diplome);


--
-- TOC entry 4909 (class 2606 OID 35096)
-- Name: ressource_formation ressource_formation_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.ressource_formation
    ADD CONSTRAINT ressource_formation_pkey PRIMARY KEY (id_ressource, id_formation);


--
-- TOC entry 4873 (class 2606 OID 34855)
-- Name: ressource ressource_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.ressource
    ADD CONSTRAINT ressource_pkey PRIMARY KEY (id_ressource);


--
-- TOC entry 4893 (class 2606 OID 35000)
-- Name: ressource_specialite ressource_specialite_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.ressource_specialite
    ADD CONSTRAINT ressource_specialite_pkey PRIMARY KEY (id_ressource, id_specialite);


--
-- TOC entry 4907 (class 2606 OID 35081)
-- Name: ressource_specificite ressource_specificite_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.ressource_specificite
    ADD CONSTRAINT ressource_specificite_pkey PRIMARY KEY (id_ressource, id_specificite);


--
-- TOC entry 4867 (class 2606 OID 34829)
-- Name: specialite specialite_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.specialite
    ADD CONSTRAINT specialite_pkey PRIMARY KEY (id_specialite);


--
-- TOC entry 4901 (class 2606 OID 35065)
-- Name: specificite specificite_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.specificite
    ADD CONSTRAINT specificite_pkey PRIMARY KEY (id_specificite);


--
-- TOC entry 4863 (class 2606 OID 34817)
-- Name: theme theme_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.theme
    ADD CONSTRAINT theme_pkey PRIMARY KEY (id_theme);


--
-- TOC entry 4871 (class 2606 OID 34843)
-- Name: type_praticien_structure type_praticien_structure_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.type_praticien_structure
    ADD CONSTRAINT type_praticien_structure_pkey PRIMARY KEY (id_type);


--
-- TOC entry 4895 (class 2606 OID 35017)
-- Name: utilise_ressource utilise_ressource_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.utilise_ressource
    ADD CONSTRAINT utilise_ressource_pkey PRIMARY KEY (id_axe, id_parcours, id_ressource, date_consultation);


--
-- TOC entry 4920 (class 2606 OID 34911)
-- Name: appartient_a appartient_a_id_categorie_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.appartient_a
    ADD CONSTRAINT appartient_a_id_categorie_fkey FOREIGN KEY (id_categorie) REFERENCES public.categorie(id_categorie);


--
-- TOC entry 4921 (class 2606 OID 34916)
-- Name: appartient_a appartient_a_id_theme_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.appartient_a
    ADD CONSTRAINT appartient_a_id_theme_fkey FOREIGN KEY (id_theme) REFERENCES public.theme(id_theme);


--
-- TOC entry 4916 (class 2606 OID 34886)
-- Name: appartient appartient_id_groupe_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.appartient
    ADD CONSTRAINT appartient_id_groupe_fkey FOREIGN KEY (id_groupe) REFERENCES public.groupepersonne(id_groupe);


--
-- TOC entry 4917 (class 2606 OID 34881)
-- Name: appartient appartient_id_personne_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.appartient
    ADD CONSTRAINT appartient_id_personne_fkey FOREIGN KEY (id_personne) REFERENCES public.personne(id_personne);


--
-- TOC entry 4938 (class 2606 OID 35056)
-- Name: avis_ressource avis_ressource_id_personne_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.avis_ressource
    ADD CONSTRAINT avis_ressource_id_personne_fkey FOREIGN KEY (id_personne) REFERENCES public.personne(id_personne);


--
-- TOC entry 4939 (class 2606 OID 35051)
-- Name: avis_ressource avis_ressource_id_ressource_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.avis_ressource
    ADD CONSTRAINT avis_ressource_id_ressource_fkey FOREIGN KEY (id_ressource) REFERENCES public.ressource(id_ressource);


--
-- TOC entry 4922 (class 2606 OID 34931)
-- Name: classe_dans classe_dans_id_categorie_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.classe_dans
    ADD CONSTRAINT classe_dans_id_categorie_fkey FOREIGN KEY (id_categorie) REFERENCES public.categorie(id_categorie);


--
-- TOC entry 4923 (class 2606 OID 34926)
-- Name: classe_dans classe_dans_id_ressource_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.classe_dans
    ADD CONSTRAINT classe_dans_id_ressource_fkey FOREIGN KEY (id_ressource) REFERENCES public.ressource(id_ressource);


--
-- TOC entry 4924 (class 2606 OID 34946)
-- Name: contient contient_id_categorie_1_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.contient
    ADD CONSTRAINT contient_id_categorie_1_fkey FOREIGN KEY (id_categorie_1) REFERENCES public.categorie(id_categorie);


--
-- TOC entry 4925 (class 2606 OID 34941)
-- Name: contient contient_id_categorie_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.contient
    ADD CONSTRAINT contient_id_categorie_fkey FOREIGN KEY (id_categorie) REFERENCES public.categorie(id_categorie);


--
-- TOC entry 4937 (class 2606 OID 35038)
-- Name: disponibilite disponibilite_id_ressource_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.disponibilite
    ADD CONSTRAINT disponibilite_id_ressource_fkey FOREIGN KEY (id_ressource) REFERENCES public.ressource(id_ressource);


--
-- TOC entry 4918 (class 2606 OID 34896)
-- Name: est_associe_a est_associe_a_id_parcours_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.est_associe_a
    ADD CONSTRAINT est_associe_a_id_parcours_fkey FOREIGN KEY (id_parcours) REFERENCES public.parcours(id_parcours);


--
-- TOC entry 4919 (class 2606 OID 34901)
-- Name: est_associe_a est_associe_a_id_theme_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.est_associe_a
    ADD CONSTRAINT est_associe_a_id_theme_fkey FOREIGN KEY (id_theme) REFERENCES public.theme(id_theme);


--
-- TOC entry 4930 (class 2606 OID 34986)
-- Name: etre_malade etre_malade_id_personne_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.etre_malade
    ADD CONSTRAINT etre_malade_id_personne_fkey FOREIGN KEY (id_personne) REFERENCES public.personne(id_personne);


--
-- TOC entry 4931 (class 2606 OID 34991)
-- Name: etre_malade etre_malade_id_theme_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.etre_malade
    ADD CONSTRAINT etre_malade_id_theme_fkey FOREIGN KEY (id_theme) REFERENCES public.theme(id_theme);


--
-- TOC entry 4914 (class 2606 OID 34866)
-- Name: parcours parcours_id_parcours_type_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.parcours
    ADD CONSTRAINT parcours_id_parcours_type_fkey FOREIGN KEY (id_parcours_type) REFERENCES public.parcours_type(id_parcours_type);


--
-- TOC entry 4915 (class 2606 OID 34871)
-- Name: parcours parcours_id_personne_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.parcours
    ADD CONSTRAINT parcours_id_personne_fkey FOREIGN KEY (id_personne) REFERENCES public.personne(id_personne);


--
-- TOC entry 4928 (class 2606 OID 34976)
-- Name: prevoit_ressource prevoit_ressource_id_parcours_type_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.prevoit_ressource
    ADD CONSTRAINT prevoit_ressource_id_parcours_type_fkey FOREIGN KEY (id_parcours_type) REFERENCES public.parcours_type(id_parcours_type);


--
-- TOC entry 4929 (class 2606 OID 34971)
-- Name: prevoit_ressource prevoit_ressource_id_ressource_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.prevoit_ressource
    ADD CONSTRAINT prevoit_ressource_id_ressource_fkey FOREIGN KEY (id_ressource) REFERENCES public.ressource(id_ressource);


--
-- TOC entry 4926 (class 2606 OID 34961)
-- Name: prevu_pour prevu_pour_id_parcours_type_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.prevu_pour
    ADD CONSTRAINT prevu_pour_id_parcours_type_fkey FOREIGN KEY (id_parcours_type) REFERENCES public.parcours_type(id_parcours_type);


--
-- TOC entry 4927 (class 2606 OID 34956)
-- Name: prevu_pour prevu_pour_id_theme_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.prevu_pour
    ADD CONSTRAINT prevu_pour_id_theme_fkey FOREIGN KEY (id_theme) REFERENCES public.theme(id_theme);


--
-- TOC entry 4944 (class 2606 OID 35117)
-- Name: ressource_diplome ressource_diplome_id_diplome_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.ressource_diplome
    ADD CONSTRAINT ressource_diplome_id_diplome_fkey FOREIGN KEY (id_diplome) REFERENCES public.diplome(id_diplome);


--
-- TOC entry 4945 (class 2606 OID 35112)
-- Name: ressource_diplome ressource_diplome_id_ressource_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.ressource_diplome
    ADD CONSTRAINT ressource_diplome_id_ressource_fkey FOREIGN KEY (id_ressource) REFERENCES public.ressource(id_ressource);


--
-- TOC entry 4942 (class 2606 OID 35102)
-- Name: ressource_formation ressource_formation_id_formation_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.ressource_formation
    ADD CONSTRAINT ressource_formation_id_formation_fkey FOREIGN KEY (id_formation) REFERENCES public.formation(id_formation);


--
-- TOC entry 4943 (class 2606 OID 35097)
-- Name: ressource_formation ressource_formation_id_ressource_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.ressource_formation
    ADD CONSTRAINT ressource_formation_id_ressource_fkey FOREIGN KEY (id_ressource) REFERENCES public.ressource(id_ressource);


--
-- TOC entry 4913 (class 2606 OID 34856)
-- Name: ressource ressource_id_type_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.ressource
    ADD CONSTRAINT ressource_id_type_fkey FOREIGN KEY (id_type) REFERENCES public.type_praticien_structure(id_type);


--
-- TOC entry 4932 (class 2606 OID 35001)
-- Name: ressource_specialite ressource_specialite_id_ressource_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.ressource_specialite
    ADD CONSTRAINT ressource_specialite_id_ressource_fkey FOREIGN KEY (id_ressource) REFERENCES public.ressource(id_ressource);


--
-- TOC entry 4933 (class 2606 OID 35006)
-- Name: ressource_specialite ressource_specialite_id_specialite_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.ressource_specialite
    ADD CONSTRAINT ressource_specialite_id_specialite_fkey FOREIGN KEY (id_specialite) REFERENCES public.specialite(id_specialite);


--
-- TOC entry 4940 (class 2606 OID 35082)
-- Name: ressource_specificite ressource_specificite_id_ressource_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.ressource_specificite
    ADD CONSTRAINT ressource_specificite_id_ressource_fkey FOREIGN KEY (id_ressource) REFERENCES public.ressource(id_ressource);


--
-- TOC entry 4941 (class 2606 OID 35087)
-- Name: ressource_specificite ressource_specificite_id_specificite_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.ressource_specificite
    ADD CONSTRAINT ressource_specificite_id_specificite_fkey FOREIGN KEY (id_specificite) REFERENCES public.specificite(id_specificite);


--
-- TOC entry 4912 (class 2606 OID 34844)
-- Name: type_praticien_structure type_praticien_structure_id_niveau_recours_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.type_praticien_structure
    ADD CONSTRAINT type_praticien_structure_id_niveau_recours_fkey FOREIGN KEY (id_niveau_recours) REFERENCES public.niveau_recours(id_niveau_recours);


--
-- TOC entry 4934 (class 2606 OID 35018)
-- Name: utilise_ressource utilise_ressource_id_axe_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.utilise_ressource
    ADD CONSTRAINT utilise_ressource_id_axe_fkey FOREIGN KEY (id_axe) REFERENCES public.axe(id_axe);


--
-- TOC entry 4935 (class 2606 OID 35023)
-- Name: utilise_ressource utilise_ressource_id_parcours_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.utilise_ressource
    ADD CONSTRAINT utilise_ressource_id_parcours_fkey FOREIGN KEY (id_parcours) REFERENCES public.parcours(id_parcours);


--
-- TOC entry 4936 (class 2606 OID 35028)
-- Name: utilise_ressource utilise_ressource_id_ressource_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.utilise_ressource
    ADD CONSTRAINT utilise_ressource_id_ressource_fkey FOREIGN KEY (id_ressource) REFERENCES public.ressource(id_ressource);


-- Completed on 2025-11-09 13:18:31

--
-- PostgreSQL database dump complete
--

