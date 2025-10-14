import json
import pandas as pd
import random
import folium
from folium.features import DivIcon
from folium import Element

# === FICHIERS D'ENTRÉE ===
F_XLS_CENTRES = "Coordonées_écoles_mqs_addresses.xlsx"   # onglets: "centres", "écoles"
F_XLS_TRANCHES = "enfants_par_tranche_soussecteur.xlsx"  # Sous-secteur, Tranche âge, Nombre enfants
F_XLS_CENTROIDS = "final_subsector_data.xlsx"             # Sous-secteur, Latitude, Longitude
F_GEOJSON_SS = "soussecteurs_4300.geojson"                # propriétés: NOM, NUMERO

# === CHARGEMENT DES DONNÉES ===
centres_df = pd.read_excel(F_XLS_CENTRES, sheet_name="centres")
ecoles_df  = pd.read_excel(F_XLS_CENTRES, sheet_name="écoles")
enfants_df = pd.read_excel(F_XLS_TRANCHES)
coords_df  = pd.read_excel(F_XLS_CENTROIDS)

# Fusion tranches + coordonnées
df = pd.merge(enfants_df, coords_df, on="Sous-secteur", how="left")

# Correction des suffixes de colonnes
lat_col = [c for c in df.columns if "Latitude" in c][0]
lon_col = [c for c in df.columns if "Longitude" in c][0]

# === CHARGER LES SOUS-SECTEURS GEOJSON ===
with open(F_GEOJSON_SS, encoding="utf-8") as f:
    geojson_data = json.load(f)

def norm(s): return str(s).strip().lower()
features_by_nom = {norm(feat["properties"]["NOM"]): feat for feat in geojson_data["features"]}

# === CRÉATION DE LA CARTE ===
m = folium.Map(location=[46.213, 6.084], zoom_start=13, tiles="cartodbpositron")

# === COUCHES POUR LES STRUCTURES ===
fg_mq = folium.FeatureGroup(name="Maisons de Quartier", show=True)
fg_crmj = folium.FeatureGroup(name="CR / MJ", show=True)
fg_ludo = folium.FeatureGroup(name="Ludothèques", show=True)
fg_tshm = folium.FeatureGroup(name="TSHM", show=True)
fg_ecoles = folium.FeatureGroup(name="Écoles", show=True)

# Fonction pour déterminer l’icône selon le type
def icon_for_type(t):
    t = str(t).strip().upper()
    if t == "MQ":
        return folium.Icon(color="green", icon="home", prefix="fa")
    elif t in ("CR/MJ", "CRMJ", "CR-MJ"):
        return folium.Icon(color="purple", icon="users", prefix="fa")
    elif t in ("LUDOTHÈQUE", "LUDOTHEQUE", "LUDO"):
        return folium.Icon(color="orange", icon="puzzle-piece", prefix="fa")
    elif t == "TSHM":
        return folium.Icon(color="red", icon="street-view", prefix="fa")
    return folium.Icon(color="gray")

# === AJOUT DES CENTRES ===
for _, row in centres_df.iterrows():
    nom = row["Nom"]
    lat = float(row["Latitude"])
    lon = float(row["Longitude"])
    type_ = str(row["Type"]).strip().upper()

    icn = icon_for_type(type_)
    if type_ == "MQ":
        fg = fg_mq
    elif type_ in ("CR/MJ", "CRMJ", "CR-MJ"):
        fg = fg_crmj
    elif type_ in ("LUDOTHÈQUE", "LUDOTHEQUE", "LUDO"):
        fg = fg_ludo
    elif type_ == "TSHM":
        fg = fg_tshm
    else:
        continue

    folium.Marker(location=[lat, lon], tooltip=nom, popup=nom, icon=icn).add_to(fg)

# === AJOUT DES ÉCOLES ===
for _, r in ecoles_df.iterrows():
    nom = r["Nom"]
    # petit décalage aléatoire pour éviter la superposition
    lat = float(r["Latitude"]) + random.uniform(0.0005, 0.0012)
    lon = float(r["Longitude"]) + random.uniform(-0.0012, 0.0012)
    folium.Marker(
        location=[lat, lon],
        tooltip=nom,
        icon=folium.Icon(color="blue", icon="graduation-cap", prefix="fa")
    ).add_to(fg_ecoles)

# Ajouter toutes les couches principales
for fg in [fg_mq, fg_crmj, fg_ludo, fg_tshm, fg_ecoles]:
    fg.add_to(m)

# === COUCHES SOUS-SECTEURS (étiquettes + polygones liés) ===
ordre_tranches = ["5-8", "9-12", "13-15", "16-18", "19-25"]
grouped = df.groupby("Sous-secteur")

for secteur, group in grouped:
    group = group.copy()
    group["Tranche âge"] = pd.Categorical(group["Tranche âge"], categories=ordre_tranches, ordered=True)
    group = group.sort_values("Tranche âge")

    lat = group[lat_col].iloc[0]
    lon = group[lon_col].iloc[0]

    texte = f"<b>{secteur}</b><br>"
    for _, row in group.iterrows():
        texte += f"{row['Tranche âge']} : {int(row['Nombre enfants'])}<br>"

    fg = folium.FeatureGroup(name=secteur, show=False)

    # Étiquette
    folium.Marker(
        location=[lat, lon],
        icon=DivIcon(
            icon_size=(120, 40),
            icon_anchor=(0, 0),
            html=f"""
                <div style='
                    background-color: white;
                    border: 1px solid #999;
                    border-radius: 6px;
                    padding: 4px 6px;
                    font-size: 10px;
                    line-height: 1.2;
                    box-shadow: 1px 1px 3px rgba(0,0,0,0.25);
                '>{texte}</div>
            """
        )
    ).add_to(fg)

    # Polygone (coloré + lié à la même case)
    feat = features_by_nom.get(norm(secteur))
    if feat:
        folium.GeoJson(
            data=feat,
            style_function=lambda x: {
                "fillColor": "#3B82F6",   # bleu clair
                "color": "#1E40AF",       # contour
                "weight": 2,
                "fillOpacity": 0.45
            },
            highlight_function=lambda x: {
                "weight": 3,
                "color": "#0F766E",
                "fillOpacity": 0.6
            },
            tooltip=secteur
        ).add_to(fg)

    fg.add_to(m)

# === CONTRÔLE DES COUCHES ===
folium.LayerControl(collapsed=True).add_to(m)

# === EXPORT ===
m.save("index.html")
print("✅ Carte générée : index.html")
