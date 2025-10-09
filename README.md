# 🗺️ Carte Vernier – Version 3.1

Ce projet affiche une carte interactive de la Commune de **Vernier (GE)** avec :

- ✅ les **Maisons de Quartier (MQ)**, **CR/MJ**, **Ludothèques**, **TSHM** et **Écoles**
- ✅ des **étiquettes dynamiques** indiquant le nombre d’enfants par **tranche d’âge**
- ✅ les **polygones des sous-secteurs** de Vernier (codes `4300***`)
- ✅ un **fond gris clair** pour une meilleure lisibilité
- ✅ possibilité d’activer/désactiver chaque couche depuis le panneau latéral

### 🔧 Données sources
- `Coordonées_écoles_mqs_addresses.xlsx` – coordonnées des structures
- `enfants_par_tranche_soussecteur.xlsx` – enfants par tranche d’âge et sous-secteur
- `final_subsector_data.xlsx` – coordonnées des sous-secteurs
- `soussecteurs_4300.geojson` – polygones des sous-secteurs de Vernier (extraits de GEO_GIREC.kmz)

### 🗂️ Processus d’acquisition et de conversion des données géographiques (SITG)

Les contours des sous-secteurs de la commune de Vernier proviennent du **Système d’Information du Territoire à Genève (SITG)**.

#### Étapes principales

1. **Téléchargement depuis SITG**
   - Jeu de données : `GEO_GIREC` – *Découpage géographique communal et sous-sectoriel (GIREC)*
   - Source : [https://www.sitg.ch/](https://www.sitg.ch/)
   - Format téléchargé : `GEO_GIREC.kmz`

2. **Extraction du KML**
   - Le fichier `.kmz` a été décompressé à l’aide du module Python `zipfile` pour obtenir `doc.kml`.

3. **Analyse du contenu**
   - Le fichier `doc.kml` contient 475 entités `<Placemark>`, chacune décrivant un sous-secteur.
   - Les attributs (dont `NUMERO`, `NOM`, etc.) sont inclus dans la balise `<description>` sous forme de tableau HTML.

4. **Filtrage des sous-secteurs de Vernier**
   - Les sous-secteurs de Vernier ont un **code `NUMERO` commençant par `4300`**.
   - Le script Python lit les balises `<Placemark>`, extrait les valeurs de `NUMERO` et `NOM`, puis sélectionne uniquement celles correspondant à Vernier.

5. **Extraction des géométries**
   - Le code recherche les balises `<Polygon>` (y compris dans `<MultiGeometry>`), convertit les coordonnées en paires `(longitude, latitude)` et crée un objet GeoJSON.

6. **Génération du fichier GeoJSON**
   - Les entités sélectionnées sont regroupées dans un fichier unique :
     ```
     soussecteurs_4300.geojson
     ```
   - Ce fichier contient 25 polygones correspondant aux sous-secteurs de la commune de Vernier.

#### 📜 Outils utilisés
- **Python 3**
- **BeautifulSoup (bs4)** pour le parsing XML/HTML
- **json** pour la création du GeoJSON
- **folium** pour la visualisation et la validation des polygones


### 📦 Génération de la carte
```bash
python generate_map.py
