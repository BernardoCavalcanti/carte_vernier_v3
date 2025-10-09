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

### 📦 Génération de la carte
```bash
python generate_map.py
