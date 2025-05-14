import json
from shapely.geometry import shape
import sys

from utils import TermColors, print_section_title

def analyze_street_prefixes(features):
    """
    Analyse les préfixes des noms de rues et retourne un dictionnaire de comptage
    
    Args:
        features: Liste des features contenant les propriétés des rues
        
    Returns:
        dict: Dictionnaire avec les préfixes et leur nombre d'occurrences
    """
    prefixes = {}
    no_name = 0
    
    print(f"{TermColors.BLUE}Analyse des préfixes de noms de rues...{TermColors.END}")
    
    for feature in features:
        street_name = feature['properties'].get('name', '')
        
        if not street_name:
            no_name += 1
            continue

        first_word = street_name.split()[0] if street_name.split() else ''
        
        if first_word:
            prefixes[first_word] = prefixes.get(first_word, 0) + 1
    
    sorted_prefixes = sorted(prefixes.items(), key=lambda x: x[1], reverse=True)
    
    print(f"\n{TermColors.BOLD}Résultats de l'analyse des préfixes:{TermColors.END}")
    print(f"{TermColors.YELLOW}{'Préfixe':<20} | {'Occurrences':<10} | {'Pourcentage':<10}{TermColors.END}")
    print("-" * 45)
    
    total = sum(prefixes.values())

    for prefix, count in sorted_prefixes[:20]:
        percentage = (count / total) * 100
        print(f"{prefix:<20} | {count:<10} | {percentage:.2f}%")
    
    if no_name > 0:
        print(f"\n{TermColors.YELLOW}Rues sans nom: {no_name}{TermColors.END}")
    
    # Générer le code pour la fonction get_prefix dans utils.py
    print(f"\n{TermColors.BOLD}Code suggéré pour la fonction get_prefix dans utils.py:{TermColors.END}")

    print("    prefixes = [")
    for prefix, count in sorted_prefixes[:10]:
        if count > 5:
            print(f"        '{prefix}',")
    print("    ]")
    
    # Générer le code pour la fonction get_color dans utils.py
    print(f"\n{TermColors.BOLD}Code suggéré pour la fonction get_color dans utils.py:{TermColors.END}")
    
    print("    color_map = {")
    colors = [
        '#E6E6FA',  # Lavender
        '#FFD700',  # Gold
        '#98FB98',  # Pale Green
        '#FFA07A',  # Light Salmon
        '#ADD8E6',  # Light Blue
        '#FFCCCB',  # Light Red
        '#FFD1DC',  # Light Pink
        '#C1FFC1',  # Light Green
        '#87CEFA',  # Light Sky Blue
        '#FFDEAD',  # Navajo White
    ]
    
    for i, (prefix, count) in enumerate(sorted_prefixes[:10]):
        if count > 5:
            color = colors[i % len(colors)]
            print(f"        '{prefix}': '{color}',  # {prefix}")
    
    print("        'Autre': '#F0E68C'      # Khaki")
    print("    }")
    print("    return color_map.get(prefix, '#D3D3D3')")
    
    return dict(sorted_prefixes)

def main():
    print_section_title("1", "Chargement des données pour analyse")
    
    try:
        with open('../data/raw-lyon_street_source.geojson', 'r', encoding='utf-8') as file:
            streets_data = json.load(file)
            
        with open('../data/raw-lyon-limits.geojson', 'r', encoding='utf-8') as file:
            lyon_bounds_data = json.load(file)
    except FileNotFoundError as e:
        print(f"{TermColors.RED}Erreur: Fichier non trouvé - {e}{TermColors.END}")
        return
    except json.JSONDecodeError:
        print(f"{TermColors.RED}Erreur: Format JSON invalide{TermColors.END}")
        return
    
    lyon_bounds = shape(lyon_bounds_data['features'][0]['geometry'])
    
    print_section_title("2", "Filtrage des rues dans Lyon")
    filtered_features = []
    total_features = len(streets_data['features'])
    print(f"Total des features à analyser: {total_features}")
    
    for i, feature in enumerate(streets_data['features']):
        if i % 1000 == 0:
            sys.stdout.write(f"\r   {i}/{total_features} rues analysées ({int(i/total_features*100)}%)...")
            sys.stdout.flush()
        feature_shape = shape(feature['geometry'])
        if feature_shape.within(lyon_bounds):
            filtered_features.append(feature)
    
    print(f"\r   {total_features}/{total_features} rues analysées (100%) {TermColors.GREEN}✓{TermColors.END}")
    print(f"   {len(filtered_features)} rues trouvées dans Lyon")

    print_section_title("3", "Analyse des préfixes de rues")
    analyze_street_prefixes(filtered_features)
    
    print(f"\n{TermColors.BOLD}{TermColors.GREEN}Analyse terminée avec succès!{TermColors.END}")
    print(f"{TermColors.YELLOW}Utilisez les suggestions ci-dessus pour mettre à jour les fonctions get_prefix et get_color dans utils.py{TermColors.END}")

if __name__ == "__main__":
    main()
