import folium
import json
from shapely.geometry import shape
import datetime
import os
import time
import sys

def print_progress(message, seconds=0.5):
    """Affiche un message avec une animation de progression"""
    animation = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
    sys.stdout.write(f"\r{message} ")
    for i in range(10):
        sys.stdout.write(f"{animation[i % len(animation)]}")
        sys.stdout.flush()
        time.sleep(seconds/10)
    sys.stdout.write("\r" + message + " ✓\n")

# 1- Récupération des données (rues de Lyon et limites de la ville)
print_progress("1- Chargement des données des rues de Lyon...")
with open('../data/raw-lyon_street_source.geojson', 'r', encoding='utf-8') as file:
    streets_data = json.load(file)

print_progress("   Chargement des limites de la ville...")
with open('../data/raw-lyon-limits.geojson', 'r', encoding='utf-8') as file:
    lyon_bounds_data = json.load(file)

print_progress("   Extraction des limites de Lyon...")
lyon_bounds = shape(lyon_bounds_data['features'][0]['geometry'])

# 2- Filtrage des données (uniquement la ville de Lyon)
print_progress("2- Filtrage des rues dans les limites de Lyon...")
filtered_features = []
total_features = len(streets_data['features'])
for i, feature in enumerate(streets_data['features']):
    if i % 100 == 0 and i > 0:
        sys.stdout.write(f"\r   {i}/{total_features} rues analysées ({int(i/total_features*100)}%)...")
        sys.stdout.flush()
    feature_shape = shape(feature['geometry'])
    if feature_shape.within(lyon_bounds):
        filtered_features.append(feature)
print(f"\r   {total_features}/{total_features} rues analysées (100%) ✓")
print(f"   {len(filtered_features)} rues trouvées dans Lyon")

#3- Visualisation des données
print_progress("3- Création de la carte...")
m = folium.Map(location=[45.764043, 4.835659], zoom_start=13, tiles='CartoDB Positron')


def get_prefix(street_name):
    prefixes = ['Allée', 'Route', 'Chemin', 'Rue', 'Avenue', 'Boulevard', 'Place', 'Impasse']

    for prefix in prefixes:
        if street_name.startswith(prefix):
            return prefix
    return 'Autre'

def get_color(prefix):
    color_map = {
        'Allée': '#FFD1DC',  # Pastel Pink
        'Route': '#C1FFC1',  # Pastel Green
        'Chemin': '#FFCCCB',  # Pastel Red
        'Rue': '#E6E6FA',    # Pastel Purple
        'Avenue': '#FFD700',  # Pastel Gold
        'Boulevard': '#98FB98',  # Pastel Green
        'Place': '#FFA07A',   # Pastel Orange
        'Impasse': '#ADD8E6',  # Pastel Blue
        'Autoroute/Périphérique': '#D3D3D3',  # Pastel Gray
        'Autre': '#F0E68C'     # Pastel Yellow
    }
    return color_map.get(prefix, '#D3D3D3')

print_progress("4- Ajout des rues à la carte...")
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
print(f"\r   {total_filtered}/{total_filtered} rues ajoutées (100%) ✓")

print_progress("5- Sauvegarde de la carte...")
os.makedirs('../results', exist_ok=True)
now = datetime.datetime.now()
timestamp = now.strftime("%Y-%m-%d_%H-%M-%S")
result_filename = f'../results/{timestamp}-lyon.html'
m.save(result_filename)

print(f"\n✨ Carte sauvegardée sous: {result_filename} ✨")
print("\nTraitement terminé avec succès!")
m
