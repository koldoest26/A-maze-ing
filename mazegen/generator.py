"""Maze generator module."""

import random
import sys
from collections import deque
from typing import List, Tuple, Optional, Set, Dict

# Bit constants for walls
NORTH: int = 1  # 2^0
EAST: int = 2   # 2^1
SOUTH: int = 4  # 2^2
WEST: int = 8   # 2^3

OPPOSITE: Dict[int, int] = {
    NORTH: SOUTH,
    SOUTH: NORTH,
    EAST: WEST,
    WEST: EAST
}

# Template for the "42" shape. Relative coordinates.
PATTERN_42: List[Tuple[int, int]] = [
    (0, 0), (2, 0),
    (0, 1), (2, 1),
    (0, 2), (1, 2), (2, 2),
    (2, 3),
    (2, 4),
    (4, 0), (5, 0), (6, 0),
    (6, 1),
    (4, 2), (5, 2), (6, 2),
    (4, 3),
    (4, 4), (5, 4), (6, 4)
]


class MazeGenerator:
    """Generates a maze using the iterative Recursive Backtracker algorithm."""

    def __init__(
        self,
        width: int,
        height: int,
        entry: Tuple[int, int],
        exit_coord: Tuple[int, int],
        perfect: bool = True,
        seed: Optional[int] = None
    ) -> None:
        """Initializes the MazeGenerator with the given parameters."""
        self.width: int = width
        self.height: int = height
        self.entry: Tuple[int, int] = entry
        self.exit_coord: Tuple[int, int] = exit_coord
        self.perfect: bool = perfect
        self.seed: Optional[int] = seed

        if self.seed is not None:
            random.seed(self.seed)

        self.grid: List[List[int]] = [
            [15 for _ in range(self.width)] for _ in range(self.height)
        ]

        self.reserved_cells: Set[Tuple[int, int]] = set()
        self._embed_42_pattern()

    def _embed_42_pattern(self) -> None:
        """Embeds the '42' pattern in the center of the maze."""
        cx = self.width // 2
        cy = self.height // 2

        # Exact coordinates for the "42" pattern, relative to the center
        four_coords = [
            (-3, -2),                      # #
            (-3, -1),                      # #
            (-3,  0), (-2,  0), (-1,  0),  # # # #
                                (-1,  1),  # . . #
                                (-1,  2)   # . . #
        ]

        two_coords = [
            ( 1, -2), ( 2, -2), ( 3, -2),  # # # #
                                ( 3, -1),  # . . #
            ( 1,  0), ( 2,  0), ( 3,  0),  # # # #
            ( 1,  1),                      # # . .
            ( 1,  2), ( 2,  2), ( 3,  2)   # # # #
        ]

        for dx, dy in four_coords + two_coords:
            x, y = cx + dx, cy + dy
            if 0 <= x < self.width and 0 <= y < self.height:
                self.reserved_cells.add((x, y))

    def _get_unvisited_neighbors(
        self, x: int, y: int, visited: Set[Tuple[int, int]]
    ) -> List[Tuple[int, int, int]]:
        """Returns a list of valid, unvisited neighbors."""
        neighbors = []
        if y > 0 and (x, y - 1) not in visited:
            neighbors.append((x, y - 1, NORTH))
        if y < self.height - 1 and (x, y + 1) not in visited:
            neighbors.append((x, y + 1, SOUTH))
        if x < self.width - 1 and (x + 1, y) not in visited:
            neighbors.append((x + 1, y, EAST))
        if x > 0 and (x - 1, y) not in visited:
            neighbors.append((x - 1, y, WEST))

        return neighbors

    def generate(self) -> None:
        """Carves the maze using the iterative Recursive Backtracker."""
        stack: List[Tuple[int, int]] = [self.entry]
        visited: Set[Tuple[int, int]] = set([self.entry])
        visited.update(self.reserved_cells)

        while stack:
            current_x, current_y = stack[-1]
            neighbors = self._get_unvisited_neighbors(
                current_x, current_y, visited
            )

            if neighbors:
                next_x, next_y, direction = random.choice(neighbors)

                self.grid[current_y][current_x] &= ~direction
                self.grid[next_y][next_x] &= ~OPPOSITE[direction]

                visited.add((next_x, next_y))
                stack.append((next_x, next_y))
            else:
                stack.pop()

    def solve(self) -> str:
        """Finds the shortest path from entry to exit using BFS."""
        # Queue stores: (x, y, path_string)
        queue: deque[Tuple[int, int, str]] = deque([(
            self.entry[0], self.entry[1], ""
        )])
        visited: Set[Tuple[int, int]] = set([self.entry])

        dir_moves = {
            NORTH: (0, -1, 'N'),
            SOUTH: (0, 1, 'S'),
            EAST: (1, 0, 'E'),
            WEST: (-1, 0, 'W')
        }

        while queue:
            curr_x, curr_y, path = queue.popleft()

            if (curr_x, curr_y) == self.exit_coord:
                return path

            cell_val = self.grid[curr_y][curr_x]

            for direction, (dx, dy, letter) in dir_moves.items():
                # If the wall is open (bit is 0), we can move there
                if (cell_val & direction) == 0:
                    next_x, next_y = curr_x + dx, curr_y + dy
                    if (next_x, next_y) not in visited:
                        visited.add((next_x, next_y))
                        queue.append((next_x, next_y, path + letter))

        return ""

    def save_to_file(self, filename: str) -> None:
        """Saves the maze and its solution to a file matching the subject."""
        with open(filename, 'w') as f:
            # Write grid
            for row in self.grid:
                row_hex = "".join([hex(cell)[2:].upper() for cell in row])
                f.write(row_hex + "\n")

            # Write required footer
            f.write("\n")
            f.write(f"{self.entry[0]},{self.entry[1]}\n")
            f.write(f"{self.exit_coord[0]},{self.exit_coord[1]}\n")

            solution = self.solve()
            f.write(f"{solution}\n")

    def print_ascii_debug(self) -> None:
        """Prints a basic ASCII representation of the grid for debugging."""
        for row in self.grid:
            row_hex = [hex(cell)[2:].upper() for cell in row]
            print(" ".join(row_hex))
