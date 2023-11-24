def print_with_color(text, color='white'):
    colors = {
        'white': '\033[0m',
        'red': '\033[91m',
        'green': '\033[92m',
        'yellow': '\033[93m',
        'blue': '\033[94m',
        'purple': '\033[95m',
        'cyan': '\033[96m'
    }
    print(f"{colors[color]}{text}{colors['white']}")