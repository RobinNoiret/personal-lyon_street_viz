import sys
from utils import (
    TermColors,
    print_progress,
    print_section_title,
    get_user_preferences,
    load_geojson_data,
    filter_streets_data,
    create_map,
    add_streets_to_map,
    save_map,
    shape
)


print_section_title(0, "Lyon Street Viz")
user_prefs = get_user_preferences()


# 1- Récupération des données (rues de Lyon et limites de la ville)
print_section_title(1, "Récupération des données")
print_progress("Chargement des données des rues de Lyon...", color=TermColors.YELLOW)
streets_data = load_geojson_data('../data/raw-lyon_street_source.geojson')
print_progress("Chargement des limites de la ville...", color=TermColors.YELLOW)
lyon_bounds_data = load_geojson_data('../data/raw-lyon_limits.geojson')
print_progress("Extraction des limites de Lyon...", color=TermColors.YELLOW)
lyon_bounds = shape(lyon_bounds_data['features'][0]['geometry'])


# 2- Filtrage des données (uniquement la ville de Lyon)
print_section_title(2, "Filtrage des données")
print_progress("Filtrage des rues dans les limites de Lyon...", color=TermColors.YELLOW)
filtered_features = filter_streets_data(streets_data, lyon_bounds)


# 3- Visualisation des données
print_section_title(3, "Visualisation des données")
print_progress("Création de la carte...", color=TermColors.YELLOW)
m = create_map([45.764043, 4.835659], 13, user_prefs["map_theme"])
print_section_title(4, "Ajout des rues à la carte")
print_progress("Traitement des rues...", color=TermColors.YELLOW)
add_streets_to_map(m, filtered_features, user_prefs["color_theme"])


# 5- Finalisation
print_section_title(5, "Finalisation")
print_progress("Sauvegarde de la carte...", color=TermColors.YELLOW)
save_map(m, user_prefs["export_format"])
print(f"\n{TermColors.GREEN}✨ Traitement terminé avec succès! ✨{TermColors.END}")
