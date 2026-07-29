"""Main entry point for the A-Maze-ing project."""

import sys
import os
from typing import Dict, Any
from mazegen.generator import MazeGenerator


def parse_config(filename: str) -> Dict[str, Any]:
    """Parses the configuration file and returns a dictionary of settings."""
    config: Dict[str, Any] = {}

    if not os.path.exists(filename):
        raise FileNotFoundError(f"Config file '{filename}' not found.")

    with open(filename, 'r') as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            # Ignore comments and empty lines
            if not line or line.startswith('#'):
                continue

            if '=' not in line:
                raise ValueError(
                    f"Line {line_num}: Missing '=' in key-value pair."
                )

            key, value = line.split('=', 1)
            key = key.strip().upper()
            value = value.strip()

            # Parse data types
            if key in ('WIDTH', 'HEIGHT'):
                config[key] = int(value)
            elif key in ('ENTRY', 'EXIT'):
                coords = value.split(',')
                if len(coords) != 2:
                    raise ValueError(
                        f"Line {line_num}: Invalid coords for {key}."
                    )
                config[key] = (int(coords[0]), int(coords[1]))
            elif key == 'PERFECT':
                # Validate boolean value
                val_lower = value.lower()
                if val_lower not in ('true', 'false'):
                    raise ValueError(
                        f"Line {line_num}: PERFECT must be 'true' or 'false'."
                    )
                config[key] = val_lower == 'true'
            elif key == 'SEED':
                config[key] = int(value)
            elif key == 'OUTPUT_FILE':
                config[key] = value
            else:
                # Store any extra keys just in case
                config[key] = value

    # Validate mandatory keys
    required_keys = {
        'WIDTH', 'HEIGHT', 'ENTRY', 'EXIT', 'OUTPUT_FILE', 'PERFECT'
    }
    missing = required_keys - config.keys()
    if missing:
        raise KeyError(
            f"Missing mandatory configuration keys: {', '.join(missing)}"
        )

    # Impossible to generate a maze smaller than 3x3
    if config['WIDTH'] < 3 or config['HEIGHT'] < 3:
        raise ValueError("Maze dimensions must be at least 3x3")

    # Validate that the entry and exit points are within bounds
    entry_x, entry_y = config['ENTRY']
    exit_x, exit_y = config['EXIT']

    if not (0 <= entry_x < config['WIDTH'] and
            0 <= entry_y < config['HEIGHT']):
        raise ValueError(
            f"ENTRY coordinates {config['ENTRY']} are out of bounds."
        )

    if not (0 <= exit_x < config['WIDTH'] and
            0 <= exit_y < config['HEIGHT']):
        raise ValueError(
            f"EXIT coordinates {config['EXIT']} are out of bounds."
        )

    # Check that ENTRY and EXIT are not the same
    if config['ENTRY'] == config['EXIT']:
        raise ValueError("ENTRY and EXIT coordinates must be different.")

    # Validate OUTPUT_FILE to prevent malicious overwrites (e.g. main.py)
    output_file = config['OUTPUT_FILE']
    if not output_file.endswith('.txt'):
        raise ValueError("OUTPUT_FILE must have a .txt extension.")

    if '/' in output_file or '\\' in output_file or '..' in output_file:
        raise ValueError(
            "OUTPUT_FILE must be in the current directory, not a path."
        )

    return config


def main() -> None:
    """Main execution block."""
    if len(sys.argv) != 2:
        print("Usage: python3 a_maze_ing.py <config.txt>", file=sys.stderr)
        sys.exit(1)

    config_file = sys.argv[1]

    try:
        # Read configuration
        config = parse_config(config_file)
        print("Configuration loaded successfully.")

        # Initialize generator
        maze = MazeGenerator(
            width=config['WIDTH'],
            height=config['HEIGHT'],
            entry=config['ENTRY'],
            exit_coord=config['EXIT'],
            perfect=config['PERFECT'],
            seed=config.get('SEED')
        )

        # Generate and solve
        print("Carving the maze...")
        maze.generate()

        # Save output file
        output_file = config['OUTPUT_FILE']
        maze.save_to_file(output_file)
        print(f"Maze successfully saved to {output_file}")

        # Start the graphical interface
        from mlx_visualizer import MazeVisualizer
        print("Starting MLX visualizer...")
        print("Controls: 1:Regen | 2:Path | 3:Color | 4:Animate | ESC:Quit")

        gui = MazeVisualizer(maze, config)
        gui.run()

    except Exception as e:
        # Graceful error handling (no abrupt crash)
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
