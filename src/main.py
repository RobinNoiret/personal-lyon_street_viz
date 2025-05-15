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
    get_color,
)

# Fonction pour obtenir les préférences de l'utilisateur
def get_user_preferences():
    preferences = {}
    
    print_section_title("Configuration", "Options de visualisation")
    
    # Option pour le thème de la carte
    print(f"{TermColors.YELLOW}Choisissez le thème de la carte :{TermColors.END}")
    print("  1. Mode clair (CartoDB Positron)")
    print("  2. Mode sombre (CartoDB Dark Matter)")
    
    while True:
        try:
            choice = input(f"{TermColors.BOLD}Votre choix [1/2] (défaut: 1): {TermColors.END}")
            if choice == "":
                choice = "1"  # Valeur par défaut
            choice = int(choice)
            if choice in [1, 2]:
                break
            else:
                print(f"{TermColors.RED}Choix invalide. Veuillez entrer 1 ou 2.{TermColors.END}")
        except ValueError:
            print(f"{TermColors.RED}Veuillez entrer un nombre.{TermColors.END}")
    
    # Stocker à la fois le thème de carte et la palette de couleurs
    preferences["map_theme"] = "CartoDB Positron" if choice == 1 else "CartoDB dark_matter"
    preferences["color_theme"] = "light" if choice == 1 else "dark"
    
    # Option pour l'export (possibilité d'extension future)
    print(f"\n{TermColors.YELLOW}Formats d'export :{TermColors.END}")
    print("  1. HTML uniquement")
    print("  2. HTML + PNG (nécessite des dépendances supplémentaires)")
    
    while True:
        try:
            choice = input(f"{TermColors.BOLD}Votre choix [1/2] (défaut: 1): {TermColors.END}")
            if choice == "":
                choice = "1"  # Valeur par défaut
            choice = int(choice)
            if choice in [1, 2]:
                break
            else:
                print(f"{TermColors.RED}Choix invalide. Veuillez entrer 1 ou 2.{TermColors.END}")
        except ValueError:
            print(f"{TermColors.RED}Veuillez entrer un nombre.{TermColors.END}")
    
    preferences["export_format"] = choice
    
    print(f"\n{TermColors.GREEN}Configuration enregistrée !{TermColors.END}\n")
    return preferences

# Début du programme
print_section_title(0, "Lyon Street Viz")

# Récupérer les préférences utilisateur
user_prefs = get_user_preferences()

# 1- Récupération des données (rues de Lyon et limites de la ville)
print_section_title(1, "Récupération des données")
print_progress("Chargement des données des rues de Lyon...", color=TermColors.YELLOW)

with open('../data/raw-lyon_street_source.geojson', 'r', encoding='utf-8') as file:
    streets_data = json.load(file)

print_progress("Chargement des limites de la ville...", color=TermColors.YELLOW)
with open('../data/raw-lyon_limits.geojson', 'r', encoding='utf-8') as file:
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
    
    # Ignorer les trottoirs séparés
    if feature['properties'].get('highway') == 'footway' and feature['properties'].get('footway') == 'sidewalk':
        continue
    
    # Ignorer les passages piétons
    if feature['properties'].get('highway') == 'footway' and feature['properties'].get('footway') == 'crossing':
        continue
    
    # Ignorer également les autres types de passages piétons
    if feature['properties'].get('highway') == 'crossing':
        continue
    
    feature_shape = shape(feature['geometry'])
    if feature_shape.within(lyon_bounds):
        filtered_features.append(feature)

print(f"\r   {total_features}/{total_features} rues analysées (100%) {TermColors.GREEN}✓{TermColors.END}")
print(f"   {len(filtered_features)} rues trouvées dans Lyon")


# 3- Visualisation des données
print_section_title(3, "Visualisation des données")
print_progress("Création de la carte...", color=TermColors.YELLOW)

# Utiliser le thème choisi par l'utilisateur
m = folium.Map(location=[45.764043, 4.835659], zoom_start=13, tiles=user_prefs["map_theme"])

print_section_title(4, "Ajout des rues à la carte")
print_progress("Traitement des rues...", color=TermColors.YELLOW)

total_filtered = len(filtered_features)
for i, feature in enumerate(filtered_features):
    if i % 100 == 0 and i > 0:
        sys.stdout.write(f"\r   {i}/{total_filtered} rues ajoutées ({int(i/total_filtered*100)}%)...")
        sys.stdout.flush()
    street_name = feature['properties'].get('name', '')
    prefix = get_prefix(street_name)
    

    weight_map = {
        'Boulevard': 1.5,
        'Avenue': 1.5,
        'Cours': 1.5,
        'Quai': 1.5,
        'Rue': 1.2,
        'Place': 1.2,
        'Allée': 1,
        'Montée': 1,
        'Impasse': 0.9,
        'Passage': 0.9,
        'Autre': 0.5 
    }
    
    weight = weight_map.get(prefix, 1)
    
    folium.GeoJson(
        feature,
        style_function=lambda x, prefix=prefix, weight=weight: {
            'fillColor': get_color(prefix, theme=user_prefs["color_theme"]),
            'color': get_color(prefix, theme=user_prefs["color_theme"]),
            'weight': weight,
            'fillOpacity': 0.5,  # Légèrement réduit pour plus de clarté
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

print(f"   Carte HTML sauvegardée: {result_filename}")

# Export PNG si demandé
if user_prefs["export_format"] == 2:
    print(f"\n{TermColors.RED}❌ Feature en cours de développement !{TermColors.END}")

print(f"\n{TermColors.GREEN}✨ Traitement terminé avec succès! ✨{TermColors.END}")
