"""Maze generator module."""

import random
import sys
from collections import deque
from typing import List, Tuple, Optional, Set, Dict, Iterator

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

        # 15 means 1111 in binary (all 4 walls closed)
        self.grid: List[List[int]] = [
            [15 for _ in range(self.width)] for _ in range(self.height)
        ]

        self.reserved_cells: Set[Tuple[int, int]] = set()
        self._embed_42_pattern()

    def _embed_42_pattern(self) -> None:
        """Embeds the '42' pattern in the center of the maze if it fits."""
        MIN_WIDTH_FOR_42 = 9
        MIN_HEIGHT_FOR_42 = 7

        if self.width < MIN_WIDTH_FOR_42 or self.height < MIN_HEIGHT_FOR_42:
            print(
                "Error: Maze size is too small to fit the '42' pattern.",
                file=sys.stderr
            )
            return  # Skip embedding if the maze is too small

        cx = self.width // 2
        cy = self.height // 2

        four_coords = [
            (-3, -2),
            (-3, -1),
            (-3, 0), (-2, 0), (-1, 0),
                              (-1, 1),
                              (-1, 2)
        ]

        two_coords = [
            (1, -2), (2, -2), (3, -2),
                              (3, -1),
            (1, 0), (2, 0), (3, 0),
            (1, 1),
            (1, 2), (2, 2), (3, 2)
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

    def _remove_wall(
        self, cx: int, cy: int, nx: int, ny: int, direction: int
    ) -> None:
        """Helper function to remove a wall safely without breaking bounds."""
        if 0 <= nx < self.width and 0 <= ny < self.height:
            if (nx, ny) in self.reserved_cells:
                return
            if (cx, cy) in self.reserved_cells:
                return

            self.grid[cy][cx] &= ~direction
            self.grid[ny][nx] &= ~OPPOSITE[direction]

    def _is_3x3_open_at(self, tx: int, ty: int) -> bool:
        """Check if the 3x3 area starting at top-left has no internal walls."""
        if tx < 0 or ty < 0 or tx + 2 >= self.width or ty + 2 >= self.height:
            return False

        for y in range(ty, ty + 2):
            for x in range(tx, tx + 3):
                if (self.grid[y][x] & SOUTH) != 0:
                    return False

        for y in range(ty, ty + 3):
            for x in range(tx, tx + 2):
                if (self.grid[y][x] & EAST) != 0:
                    return False

        return True

    def _would_create_3x3(
        self, cx: int, cy: int, nx: int, ny: int, direction: int
    ) -> bool:
        """Simulates breaking a wall to check if it creates a 3x3 open area."""
        if not (0 <= nx < self.width and 0 <= ny < self.height):
            return True
        if (nx, ny) in self.reserved_cells or (cx, cy) in self.reserved_cells:
            return True

        self.grid[cy][cx] &= ~direction
        self.grid[ny][nx] &= ~OPPOSITE[direction]

        min_x = max(0, min(cx, nx) - 2)
        max_x = min(self.width - 3, max(cx, nx))
        min_y = max(0, min(cy, ny) - 2)
        max_y = min(self.height - 3, max(cy, ny))

        creates_3x3 = False
        for ty in range(min_y, max_y + 1):
            for tx in range(min_x, max_x + 1):
                if self._is_3x3_open_at(tx, ty):
                    creates_3x3 = True
                    break
            if creates_3x3:
                break

        self.grid[cy][cx] |= direction
        self.grid[ny][nx] |= OPPOSITE[direction]

        return creates_3x3

    def _remove_dead_ends(self) -> None:
        """Removes dead-ends to create a playable board (PERFECT=False)."""
        if self.perfect:
            return

        modified = True
        while modified:
            modified = False
            for y in range(self.height):
                for x in range(self.width):
                    if (x, y) in self.reserved_cells:
                        continue

                    # An open cell with exactly 3 walls is a dead-end
                    if bin(self.grid[y][x]).count('1') == 3:
                        dirs = [NORTH, SOUTH, EAST, WEST]
                        random.shuffle(dirs)
                        for d in dirs:
                            # Check if the wall in direction d is present
                            if (self.grid[y][x] & d) != 0:
                                nx, ny = x, y
                                if d == NORTH:
                                    ny -= 1
                                elif d == SOUTH:
                                    ny += 1
                                elif d == EAST:
                                    nx += 1
                                elif d == WEST:
                                    nx -= 1

                                # Check bounds and reserved cells
                                if not (0 <= nx < self.width and
                                        0 <= ny < self.height):
                                    continue
                                if (nx, ny) in self.reserved_cells:
                                    continue
                                if not self._would_create_3x3(x, y, nx, ny, d):
                                    self._remove_wall(x, y, nx, ny, d)
                                    modified = True
                                    break

    def _enforce_pacman_mode(self) -> None:
        """Ensures corners/center are open and creates Pac-Man loops."""
        if self.perfect:
            return

        critical_cells = [
            (0, 0, EAST, 1, 0),
            (self.width - 1, 0, WEST, self.width - 2, 0),
            (0, self.height - 1, NORTH, 0, self.height - 2),
            (
                self.width - 1, self.height - 1,
                WEST, self.width - 2, self.height - 1
            ),
            (
                self.width // 2, self.height // 2,
                NORTH, self.width // 2, (self.height // 2) - 1
            )
        ]

        for cx, cy, direction, nx, ny in critical_cells:
            self._remove_wall(cx, cy, nx, ny, direction)

        for y in range(1, self.height - 1):
            for x in range(1, self.width - 1):
                if random.random() < 0.15:
                    dirs = [
                        (NORTH, x, y - 1),
                        (SOUTH, x, y + 1),
                        (EAST, x + 1, y),
                        (WEST, x - 1, y)
                    ]
                    d, nx, ny = random.choice(dirs)

                    if not self._would_create_3x3(x, y, nx, ny, d):
                        self._remove_wall(x, y, nx, ny, d)

    def generate_animated(self) -> Iterator[None]:
        """Yields after each step to allow MLX to animate the process."""
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

            # Pause to allow MLX to render the current state of the maze
            yield

        # Apply the Pac-Man mode rules at the very end
        self._enforce_pacman_mode()
        self._remove_dead_ends()

        # Last yield to ensure the final state is rendered
        yield

    def generate(self) -> None:
        """Carves the maze instantly."""
        for _ in self.generate_animated():
            pass

    def solve(self) -> str:
        """Finds the shortest path from entry to exit using BFS."""
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
                if (cell_val & direction) == 0:
                    next_x, next_y = curr_x + dx, curr_y + dy
                    if (next_x, next_y) not in visited:
                        visited.add((next_x, next_y))
                        queue.append((next_x, next_y, path + letter))
        return ""

    def save_to_file(self, filename: str) -> None:
        """Saves the maze and its solution to a file matching the subject."""
        with open(filename, 'w') as f:
            for row in self.grid:
                row_hex = "".join([hex(cell)[2:].upper() for cell in row])
                f.write(row_hex + "\n")

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
