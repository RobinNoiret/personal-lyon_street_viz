import folium
import json
from shapely.geometry import shape
import datetime
import os
import time
import sys

# Import utility functions
from utils import (
    TermColors, 
    print_progress, 
    print_section_title, 
    get_prefix, 
    get_color
)

# 1- Récupération des données (rues de Lyon et limites de la ville)
print_section_title(1, "Récupération des données")
print_progress("Chargement des données des rues de Lyon...", color=TermColors.YELLOW)

with open('../data/raw-lyon_street_source.geojson', 'r', encoding='utf-8') as file:
    streets_data = json.load(file)

print_progress("Chargement des limites de la ville...", color=TermColors.YELLOW)
with open('../data/raw-lyon-limits.geojson', 'r', encoding='utf-8') as file:
    lyon_bounds_data = json.load(file)

print_progress("Extraction des limites de Lyon...", color=TermColors.YELLOW)
lyon_bounds = shape(lyon_bounds_data['features'][0]['geometry'])


# 2- Filtrage des données (uniquement la ville de Lyon)
print_section_title(2, "Filtrage des données")
print_progress("Filtrage des rues dans les limites de Lyon...", color=TermColors.YELLOW)

filtered_features = []
total_features = len(streets_data['features'])
for i, feature in enumerate(streets_data['features']):
    if i % 100 == 0 and i > 0:
        sys.stdout.write(f"\r   {i}/{total_features} rues analysées ({int(i/total_features*100)}%)...")
        sys.stdout.flush()
    feature_shape = shape(feature['geometry'])
    if feature_shape.within(lyon_bounds):
        filtered_features.append(feature)

print(f"\r   {total_features}/{total_features} rues analysées (100%) {TermColors.GREEN}✓{TermColors.END}")
print(f"   {len(filtered_features)} rues trouvées dans Lyon")


# 3- Visualisation des données
print_section_title(3, "Visualisation des données")
print_progress("Création de la carte...", color=TermColors.YELLOW)

m = folium.Map(location=[45.764043, 4.835659], zoom_start=13, tiles="CartoDB Positron")

print_section_title(4, "Ajout des rues à la carte")
print_progress("Traitement des rues...", color=TermColors.YELLOW)

total_filtered = len(filtered_features)
for i, feature in enumerate(filtered_features):
    if i % 100 == 0 and i > 0:
        sys.stdout.write(f"\r   {i}/{total_filtered} rues ajoutées ({int(i/total_filtered*100)}%)...")
        sys.stdout.flush()
    street_name = feature['properties'].get('name', '')
    prefix = get_prefix(street_name)
    folium.GeoJson(
        feature,
        style_function=lambda x, prefix=prefix: {
            'fillColor': get_color(prefix),
            'color': get_color(prefix),
            'weight': 1,
            'fillOpacity': 0.6,
        }
    ).add_to(m)

print(f"\r   {total_filtered}/{total_filtered} rues ajoutées (100%) {TermColors.GREEN}✓{TermColors.END}")

print_section_title(5, "Finalisation")
print_progress("Sauvegarde de la carte...", color=TermColors.YELLOW)

os.makedirs('../results', exist_ok=True)
now = datetime.datetime.now()
timestamp = now.strftime("%Y-%m-%d_%H-%M-%S")
result_filename = f'../results/{timestamp}-lyon.html'
m.save(result_filename)

print(f"\n{TermColors.GREEN}✨ Carte sauvegardée sous: {result_filename} ✨{TermColors.END}")
print(f"\n{TermColors.BOLD}{TermColors.GREEN}Traitement terminé avec succès!{TermColors.END}")
m
