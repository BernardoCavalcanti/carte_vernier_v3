import pandas as pd
import folium
from folium.features import DivIcon

# === Charger les fichiers ===
ecoles_df = pd.read_excel("Coordonées_écoles_mqs_addresses.xlsx", sheet_name="écoles")
mqs_df = pd.read_excel("Coordonées_écoles_mqs_addresses.xlsx", sheet_name="centres")
enfants_df = pd.read_excel("enfants_par_tranche_soussecteur.xlsx")
coord_df = pd.read_excel("final_subsector_data.xlsx")

# === Fusion coordonnées + tranches d’âge ===
df = enfants_df.merge(coord_df, on="Sous-secteur", how="left")

# Debug : voir les colonnes et quelques lignes
print("Colonnes dans df :", df.columns.tolist())
print(df.head(10))

# === Créer la carte ===
m = folium.Map(location=[46.213, 6.084], zoom_start=13, tiles="cartodbpositron")

# === Icônes pour les types ===
icones = {
    "MQ": folium.Icon(color="green", icon="home", prefix="fa"),
    "CR/MJ": folium.Icon(color="purple", icon="users", prefix="fa"),
    "Ludothèque": folium.Icon(color="orange", icon="puzzle-piece", prefix="fa"),
    "TSHM": folium.Icon(color="red", icon="street-view", prefix="fa")
}

# === FeatureGroups ===
fg_mq = folium.FeatureGroup(name="Maisons de Quartier", show=True)
fg_crmj = folium.FeatureGroup(name="CR / MJ", show=True)
fg_ludo = folium.FeatureGroup(name="Ludothèques", show=True)
fg_tshm = folium.FeatureGroup(name="TSHM", show=True)

# === Ajouter les MQs par type ===
for _, row in mqs_df.iterrows():
    nom = row["Nom"]
    lat = row["Latitude"]
    lon = row["Longitude"]
    type_ = row["Type"]
    icon = icones.get(type_, folium.Icon(color="gray"))

    if type_ == "MQ":
        fg = fg_mq
    elif type_ == "CR/MJ":
        fg = fg_crmj
    elif type_ == "Ludothèque":
        fg = fg_ludo
    elif type_ == "TSHM":
        fg = fg_tshm
    else:
        continue

    folium.Marker(
        location=[lat, lon],
        tooltip=nom,
        popup=nom,
        icon=icon
    ).add_to(fg)

# === Ajouter les écoles (bleu, décalé) ===
fg_ecoles = folium.FeatureGroup(name="Écoles", show=True)
for _, row in ecoles_df.iterrows():
    nom = row["Nom"]
    lat = row["Latitude"] + 0.0007
    lon = row["Longitude"]
    folium.Marker(
        location=[lat, lon],
        tooltip=nom,
        icon=folium.Icon(color="blue", icon="graduation-cap", prefix="fa")
    ).add_to(fg_ecoles)

# === Étiquettes par sous-secteur avec tranches d’âge triées ===
ordre_tranches = ["5-8", "9-12", "13-15", "16-18", "19-25"]
df["Tranche Âge"] = pd.Categorical(df["Tranche âge"], categories=ordre_tranches, ordered=True)
grouped = df.groupby("Sous-secteur")

for secteur, group in grouped:
    group = group.sort_values("Tranche Âge")
    lat = group["Latitude_y"].iloc[0]
    lon = group["Longitude_y"].iloc[0]
    texte = f"<b>{secteur}</b><br>"
    for _, row in group.iterrows():
        texte += f"{row['Tranche âge']} : {int(row['Nombre enfants'])}<br>"

    fg = folium.FeatureGroup(name=secteur, show=False)
    folium.Marker(
        location=[lat, lon],
        icon=DivIcon(
            icon_size=(120, 40),
            icon_anchor=(0, 0),
            html=f"""
                <div style='
                    background-color: white;
                    border: 1px solid gray;
                    border-radius: 6px;
                    padding: 4px;
                    font-size: 10px;
                    line-height: 1.2;
                    box-shadow: 1px 1px 3px rgba(0,0,0,0.3);
                '>
                    {texte}
                </div>
            """
        )
    ).add_to(fg)
    fg.add_to(m)

# Ajouter tous les groupes à la carte
fg_mq.add_to(m)
fg_crmj.add_to(m)
fg_ludo.add_to(m)
fg_tshm.add_to(m)
fg_ecoles.add_to(m)
folium.LayerControl(collapsed=False).add_to(m)

# Sauvegarder
m.save("index.html")