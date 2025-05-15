import sys
import time
import folium
import json
from shapely.geometry import shape
import os
import datetime

class TermColors:
    """ANSI color codes for terminal text formatting"""
    HEADER = '\033[95m'    # Pink
    BLUE = '\033[94m'      # Blue
    GREEN = '\033[92m'     # Green
    YELLOW = '\033[93m'    # Yellow
    RED = '\033[91m'       # Red
    BOLD = '\033[1m'       # Bold
    UNDERLINE = '\033[4m'  # Underline
    END = '\033[0m'        # Reset formatting

def print_progress(message, seconds=0.5, color=None):
    """
    Display a progress message with animation and optional color
    
    Args:
        message (str): Message to display
        seconds (float): Duration of the animation
        color: Terminal color code
    """
    animation = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
    formatted_message = f"{color}{message}{TermColors.END}" if color else message
    sys.stdout.write(f"\r{formatted_message} ")

    for i in range(10):
        sys.stdout.write(f"{animation[i % len(animation)]}")
        sys.stdout.flush()
        time.sleep(seconds/10)
        sys.stdout.write("\b \b")
        sys.stdout.flush()

    sys.stdout.write(f"{TermColors.GREEN}✓{TermColors.END}\n")
    sys.stdout.flush()

def print_section_title(number, title):
    """
    Display a formatted section title with borders
    
    Args:
        number (int or str): Section number
        title (str): Section title text
    """
    print(f"\n{TermColors.BOLD}{TermColors.BLUE}{'='*50}{TermColors.END}")
    print(f"{TermColors.BOLD}{TermColors.BLUE}{number}- {title}{TermColors.END}")
    print(f"{TermColors.BOLD}{TermColors.BLUE}{'='*50}{TermColors.END}")

def get_prefix(street_name):
    """
    Extract street type prefix from street name
    
    Args:
        street_name (str): Full street name
        
    Returns:
        str: Street type prefix or 'Autre' if no match
    """
    prefixes = [
        'Rue',
        'Place',
        'Avenue',
        'Quai',
        'Allée',
        'Boulevard',
        'Impasse',
        'Cours',
        'Montée',
        'Passage',
    ]

    for prefix in prefixes:
        if street_name.startswith(prefix):
            return prefix
    return 'Autre'

def get_color(prefix, theme="light"):
    """
    Get color code for street type visualization
    
    Args:
        prefix (str): Street type prefix
        theme (str): 'light' or 'dark' color theme
        
    Returns:
        str: Hex color code
    """
    # Color for the light version of the map
    light_color_map = {
        'Rue': '#6929c4',
        'Place': '#1192e8',
        'Avenue': '#005d5d',
        'Quai': '#fa4d56',
        'Allée': '#198038',
        'Boulevard': '#002d9c',
        'Impasse': '#ee538b',
        'Cours': '#b28600',
        'Montée': '#8a3800',
        'Passage': '#009d9a',
        'Autre': '#4d4d4d'
    }

    # Color for the dark version of the map
    dark_color_map = {
        'Rue': '#8a3ffc',
        'Place': '#33b1ff',
        'Avenue': '#007d79',
        'Quai': '#fa4d56',
        'Allée': '#6fdc8c',
        'Boulevard': '#4589ff',
        'Impasse': '#d12771',
        'Cours': '#d2a106',
        'Montée': '#ba4e00',
        'Passage': '#bae6ff',
        'Autre': '#fff1f1'
    }
    
    color_map = dark_color_map if theme == "dark" else light_color_map
    return color_map.get(prefix, '#D3D3D3')

def get_user_preferences():
    """
    Interactive prompt to get user preferences for visualization
    
    Returns:
        dict: User preferences
    """
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

def load_geojson_data(filepath):
    """
    Load GeoJSON data from a file
    
    Args:
        filepath (str): Path to the GeoJSON file
        
    Returns:
        dict: Parsed GeoJSON data
    """
    with open(filepath, 'r', encoding='utf-8') as file:
        return json.load(file)

def filter_streets_data(streets_data, bounds):
    """
    Filter streets data based on boundaries and other criteria
    
    Args:
        streets_data (dict): GeoJSON streets data
        bounds (shapely.geometry): City boundary geometry
        
    Returns:
        list: Filtered street features
    """
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
        if feature_shape.within(bounds):
            filtered_features.append(feature)
    
    print(f"\r   {total_features}/{total_features} rues analysées (100%) {TermColors.GREEN}✓{TermColors.END}")
    print(f"   {len(filtered_features)} rues trouvées dans Lyon")
    
    return filtered_features

def create_map(center_coords, zoom_level, map_theme):
    """
    Create a Folium map with specified parameters
    
    Args:
        center_coords (list): [latitude, longitude] center coordinates
        zoom_level (int): Initial zoom level
        map_theme (str): Map tile theme
        
    Returns:
        folium.Map: Initialized map object
    """
    return folium.Map(location=center_coords, zoom_start=zoom_level, tiles=map_theme)

def get_street_weight(prefix):
    """
    Get the line weight based on street type prefix
    
    Args:
        prefix (str): Street type prefix
        
    Returns:
        float: Line weight value
    """
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
    
    return weight_map.get(prefix, 1)

def add_streets_to_map(m, features, color_theme):
    """
    Add street features to the map
    
    Args:
        m (folium.Map): Map object
        features (list): List of GeoJSON features
        color_theme (str): Color theme (light/dark)
    """
    total_filtered = len(features)
    for i, feature in enumerate(features):
        if i % 100 == 0 and i > 0:
            sys.stdout.write(f"\r   {i}/{total_filtered} rues ajoutées ({int(i/total_filtered*100)}%)...")
            sys.stdout.flush()
        
        street_name = feature['properties'].get('name', '')
        prefix = get_prefix(street_name)
        weight = get_street_weight(prefix)
        
        folium.GeoJson(
            feature,
            style_function=lambda x, prefix=prefix, weight=weight: {
                'fillColor': get_color(prefix, theme=color_theme),
                'color': get_color(prefix, theme=color_theme),
                'weight': weight,
                'fillOpacity': 0.5,
            }
        ).add_to(m)
    
    print(f"\r   {total_filtered}/{total_filtered} rues ajoutées (100%) {TermColors.GREEN}✓{TermColors.END}")

def save_map(m, export_format=1):
    """
    Save map to file(s)
    
    Args:
        m (folium.Map): Map object
        export_format (int): Export format (1=HTML only, 2=HTML+PNG)
        
    Returns:
        str: Path to the saved HTML file
    """
    os.makedirs('../results', exist_ok=True)
    now = datetime.datetime.now()
    timestamp = now.strftime("%Y-%m-%d_%H-%M-%S")
    result_filename = f'../results/{timestamp}-lyon.html'
    m.save(result_filename)
    
    print(f"   Carte HTML sauvegardée: {result_filename}")
    
    # Export PNG si demandé
    if export_format == 2:
        print(f"\n{TermColors.RED}❌ Feature en cours de développement !{TermColors.END}")
    
    return result_filename
