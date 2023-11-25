def print_with_color(text, color='white', return_as_string=False):
    colors = {
        'white': '\033[0m',
        'red': '\033[91m',
        'green': '\033[92m',
        'yellow': '\033[93m',
        'blue': '\033[94m',
        'purple': '\033[95m',
        'cyan': '\033[96m',
        'inverse': '\033[7m'
    }
    if not return_as_string:
        print(f"{colors[color]}{text}{colors['white']}")
    else:
        return f"{colors[color]}{text}{colors['white']}"