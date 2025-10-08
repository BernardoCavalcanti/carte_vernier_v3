
# 🗺️ Carte interactive – Vernier (v3)

Ce projet présente une carte interactive de la commune de Vernier, montrant :
- Les **Maisons de Quartier (MQ)**, **Centres de Rencontres / Maisons de Jeunesse (CR/MJ)**, **Ludothèques**, et **Travailleurs Sociaux Hors Murs (TSHM)** avec des **icônes distinctes**
- La **répartition des enfants par tranche d’âge** (5-8, 9-12, 13-15, 16-18, 19-25) dans chaque sous-secteur, via des étiquettes visibles à la demande

## 🧩 Données utilisées
- `Coordonées_écoles_mqs_addresses.xlsx` – coordonnées et type de chaque structure
- `enfants_par_tranche_soussecteur.xlsx` – nombre d’enfants par tranche d’âge et sous-secteur
- `final_subsector_data.xlsx` – coordonnées des sous-secteurs

## ⚙️ Fichiers clés
- `generate_map.py` – script Python pour générer la carte
- `index.html` – carte interactive exportée et publiée via GitHub Pages

## 🌐 Voir la carte
📍 [Carte en ligne](https://bernardocavalcanti.github.io/carte_vernier_v3/)

## 🧪 Instructions
Pour regénérer la carte localement :
```bash
python generate_map.py
```

## 🔄 Publication
La carte est hébergée automatiquement via GitHub Pages (branche `main`, dossier racine).

---
**Auteur** : Bernardo Cavalcanti  
**Dernière mise à jour** : Octobre 2025
