import pandas as pd
import json
import folium
from folium.features import DivIcon
from folium.plugins import MarkerCluster
import random

# === FICHIERS SOURCES ===
centres_path = "Coordonées_écoles_mqs_addresses.xlsx"
geojson_path = "soussecteurs_4300.geojson"
assoc_path = "centres_soussecteurs.xlsx"
ages_path = "enfants_par_tranche_soussecteur.xlsx"

# === CHARGER LES DONNÉES ===
centres_df = pd.read_excel(centres_path, sheet_name="centres")
ecoles_df = pd.read_excel(centres_path, sheet_name="écoles")
geo = json.load(open(geojson_path, encoding="utf-8"))
assoc_df = pd.read_excel(assoc_path, sheet_name="Association")
ages_df = pd.read_excel(ages_path)

# === CRÉER LA CARTE ===
m = folium.Map(location=[46.213, 6.084], zoom_start=13, tiles="cartodb positron")

# === COUCHES INDÉPENDANTES ===

## ÉCOLES – décalage aléatoire pour éviter chevauchement
fg_ecoles = folium.FeatureGroup(name="Écoles", show=True)
for _, r in ecoles_df.iterrows():
    lat = r["Latitude"] + random.uniform(0.0001, 0.002)
    lon = r["Longitude"] + random.uniform(-0.001, 0.001)
    folium.Marker(
        location=[lat, lon],
        tooltip=r["Nom"],
        icon=folium.Icon(color="blue", icon="graduation-cap", prefix="fa")
    ).add_to(fg_ecoles)
fg_ecoles.add_to(m)

## LUDOTHÈQUES
fg_ludo = folium.FeatureGroup(name="Ludothèques", show=True)
ludos_df = centres_df[centres_df["Nom"].str.contains("Ludo", case=False, na=False)]
for _, r in ludos_df.iterrows():
    folium.Marker(
        location=[r["Latitude"], r["Longitude"]],
        tooltip=r["Nom"],
        icon=folium.Icon(color="orange", icon="puzzle-piece", prefix="fa")
    ).add_to(fg_ludo)
fg_ludo.add_to(m)

## TSHM – filtrage élargi
fg_tshm = folium.FeatureGroup(name="TSHM", show=True)
tshm_df = centres_df[centres_df["Nom"].str.contains("TSHM|Travailleurs", case=False, na=False)]
for _, r in tshm_df.iterrows():
    folium.Marker(
        location=[r["Latitude"], r["Longitude"]],
        tooltip=r["Nom"],
        icon=folium.Icon(color="red", icon="users", prefix="fa")
    ).add_to(fg_tshm)
fg_tshm.add_to(m)

# === PALETTE DE COULEURS UNIQUE PAR STRUCTURE ===
palette = [
    "#1E90FF", "#32CD32", "#FFD700", "#FF69B4", "#FF4500",
    "#9ACD32", "#20B2AA", "#9370DB", "#FF8C00", "#00CED1", "#DC143C"
]
structures = assoc_df["Nom structure"].unique()
color_map = {name: palette[i % len(palette)] for i, name in enumerate(structures)}

# === COUCHES MQ / CR / MJ ET LEURS SOUS-SECTEURS ===
assoc_df["Sous-secteur"] = assoc_df["Sous-secteur"].str.strip()
ages_df["Sous-secteur"] = ages_df["Sous-secteur"].str.strip()

for structure, group in assoc_df.groupby("Nom structure"):
    fg = folium.FeatureGroup(name=structure, show=False)
    couleur = color_map[structure]

    # === Ajouter le marker du centre ===
    centre_row = centres_df[centres_df["Nom"].str.strip() == structure.strip()]
    if not centre_row.empty:
        lat = float(centre_row["Latitude"].iloc[0])
        lon = float(centre_row["Longitude"].iloc[0])
        folium.Marker(
            location=[lat, lon],
            tooltip=structure,
            icon=folium.Icon(color="gray", icon_color=couleur, icon="home", prefix="fa")
        ).add_to(fg)

    # === Ajouter les polygones et fiches ===
    for ss in group["Sous-secteur"]:
        feature = next(
            (f for f in geo["features"]
             if f["properties"]["NOM"].strip().lower() == ss.strip().lower()),
            None
        )
        if feature:
            folium.GeoJson(
                data=feature,
                style_function=lambda x, col=couleur: {
                    "fillColor": col,
                    "color": col,
                    "weight": 1.2,
                    "fillOpacity": 0.35
                },
                tooltip=ss
            ).add_to(fg)

            # === Fiche de tranches d’âge ===
            sub_ages = ages_df[ages_df["Sous-secteur"].str.lower() == ss.lower()]
            if not sub_ages.empty:
                texte = f"<b>{ss}</b><br>"
                for _, row in sub_ages.iterrows():
                    texte += f"{row['Tranche âge']}: {int(row['Nombre enfants'])}<br>"

                coords_data = feature["geometry"]["coordinates"]
                if feature["geometry"]["type"] == "MultiPolygon":
                    coords = coords_data[0][0]
                else:
                    coords = coords_data[0]

                if isinstance(coords[0], (list, tuple)) and len(coords[0]) == 2:
                    lon_avg = sum(p[0] for p in coords) / len(coords)
                    lat_avg = sum(p[1] for p in coords) / len(coords)
                else:
                    lon_avg, lat_avg = 0, 0

                folium.Marker(
                    location=[lat_avg, lon_avg],
                    icon=DivIcon(
                        icon_size=(120, 40),
                        icon_anchor=(0, 0),
                        html=f"""
                            <div style='
                                background-color: white;
                                border: 1px solid #999;
                                border-radius: 6px;
                                padding: 4px;
                                font-size: 10px;
                                line-height: 1.2;
                                box-shadow: 1px 1px 3px rgba(0,0,0,0.25);
                                color: #111;
                            '>{texte}</div>
                        """
                    )
                ).add_to(fg)

    fg.add_to(m)

# === MENU ET SAUVEGARDE ===
folium.LayerControl(collapsed=True).add_to(m)
m.save("index.html")

print("✅ Carte générée : index.html")
