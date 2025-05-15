import sys
import time

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
