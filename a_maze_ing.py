"""Main entry point for the A-Maze-ing project."""

import sys
import os
from typing import Dict, Tuple, Any
from mazegen.generator import MazeGenerator


def parse_config(filename: str) -> Dict[str, Any]:
    """Parses the configuration file and returns a dictionary of settings."""
    config: Dict[str, Any] = {}

    if not os.path.exists(filename):
        raise FileNotFoundError(f"Configuration file '{filename}' not found.")

    with open(filename, 'r') as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            # Ignorar comentarios y líneas vacías
            if not line or line.startswith('#'):
                continue

            if '=' not in line:
                raise ValueError(f"Line {line_num}: Missing '=' in key-value pair.")

            key, value = line.split('=', 1)
            key = key.strip().upper()
            value = value.strip()

            # Parsear los tipos de datos
            if key in ('WIDTH', 'HEIGHT'):
                config[key] = int(value)
            elif key in ('ENTRY', 'EXIT'):
                coords = value.split(',')
                if len(coords) != 2:
                    raise ValueError(f"Line {line_num}: Invalid coordinates for {key}.")
                config[key] = (int(coords[0]), int(coords[1]))
            elif key == 'PERFECT':
                config[key] = value.lower() == 'true'
            elif key == 'SEED':
                config[key] = int(value)
            elif key == 'OUTPUT_FILE':
                config[key] = value
            else:
                # Guardar cualquier clave extra por si acaso
                config[key] = value

    # Validar claves obligatorias
    required_keys = {'WIDTH', 'HEIGHT', 'ENTRY', 'EXIT', 'OUTPUT_FILE', 'PERFECT'}
    missing = required_keys - config.keys()
    if missing:
        raise KeyError(f"Missing mandatory configuration keys: {', '.join(missing)}")

    return config


def main() -> None:
    """Main execution block."""
    if len(sys.argv) != 2:
        print("Usage: python3 a_maze_ing.py <config.txt>", file=sys.stderr)
        sys.exit(1)

    config_file = sys.argv[1]

    try:
        # Read and parse the configuration file
        config = parse_config(config_file)
        print("Configuration loaded successfully.")

        # Initialize the maze generator with the parsed configuration
        maze = MazeGenerator(
            width=config['WIDTH'],
            height=config['HEIGHT'],
            entry=config['ENTRY'],
            exit_coord=config['EXIT'],
            perfect=config['PERFECT'],
            seed=config.get('SEED')
        )

        # Generate the maze
        print("Carving the maze...")
        maze.generate()

        # Save the maze to the specified output file
        output_file = config['OUTPUT_FILE']
        maze.save_to_file(output_file)
        print(f"Maze successfully saved to {output_file}")

    except Exception as e:
        # Error handling: print the error message and exit with a non-zero status
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
