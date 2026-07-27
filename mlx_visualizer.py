"""Visualizer module using MiniLibX and Image Buffers."""

import os
from typing import Any
from mazegen.generator import MazeGenerator

try:
    from mlx.mlx import Mlx
    MLX_READY = True
except ImportError as e:
    print(f"Warning: MLX wrapper not found ({e}). Headless mode.")
    MLX_READY = False


class MazeVisualizer:
    """Handles the graphical representation of the maze using MLX."""

    def __init__(self, maze: MazeGenerator, config: dict[str, Any]) -> None:
        """Initializes the visualizer with the maze data."""
        self.maze = maze
        self.config = config

        self.cell_size = 20
        self.show_path = False
        self.colors = [0xFFFFFF, 0xFF0000, 0x00FF00, 0x00FFFF]
        self.color_idx = 0
        self.needs_redraw = True

        self.w_width = self.maze.width * self.cell_size
        self.w_height = self.maze.height * self.cell_size

        self.animating = False
        self.gen_iterator = None
        self.steps_per_frame = 10  # Speed

        if MLX_READY:
            # Dinamically import Mlx to avoid issues in headless environments
            _Mlx: Any = Mlx
            self.mlx = _Mlx()
            self.mlx_ptr = self.mlx.mlx_init()

            # Window height includes +130 pixels for the menu area
            self.win_ptr = self.mlx.mlx_new_window(
                self.mlx_ptr, self.w_width, self.w_height + 130,
                "A-Maze-Ing 42"
            )

            # Create image buffer
            self.img_ptr = self.mlx.mlx_new_image(
                self.mlx_ptr, self.w_width, self.w_height
            )
            # Extract memory array
            img_data_tuple = self.mlx.mlx_get_data_addr(self.img_ptr)
            self.img_data = img_data_tuple[0]
            self.bpp = img_data_tuple[1]
            self.size_line = img_data_tuple[2]
            self.bytes_per_pixel = self.bpp // 8

    def put_pixel(self, x: int, y: int, color: int) -> None:
        """Puts a pixel directly into the image memory buffer instantly."""
        if 0 <= x < self.w_width and 0 <= y < self.w_height:
            idx = (y * self.size_line) + (x * self.bytes_per_pixel)
            try:
                self.img_data[idx] = color & 0xFF
                self.img_data[idx + 1] = (color >> 8) & 0xFF
                self.img_data[idx + 2] = (color >> 16) & 0xFF
                if self.bytes_per_pixel == 4:
                    self.img_data[idx + 3] = 255  # FORCE OPAQUE
            except IndexError:
                pass

    def draw_line(
        self, x1: int, y1: int, x2: int, y2: int, color: int
    ) -> None:
        """Draws a line using Bresenham's algorithm."""
        if not MLX_READY:
            return

        dx = abs(x2 - x1)
        dy = -abs(y2 - y1)
        sx = 1 if x1 < x2 else -1
        sy = 1 if y1 < y2 else -1
        err = dx + dy

        while True:
            self.put_pixel(x1, y1, color)
            if x1 == x2 and y1 == y2:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x1 += sx
            if e2 <= dx:
                err += dx
                y1 += sy

    def draw_square(self, x: int, y: int, size: int, color: int) -> None:
        """Draws a filled square."""
        if not MLX_READY:
            return
        for i in range(size):
            for j in range(size):
                self.put_pixel(x + i, y + j, color)

    def draw_thick_line(
        self, x1: int, y1: int, x2: int, y2: int, color: int, thickness: int
    ) -> None:
        """Draws a line with a custom thickness."""
        for i in range(-thickness // 2, thickness // 2):
            self.draw_line(x1 + i, y1 + i, x2 + i, y2 + i, color)

    def draw_rect(self, x: int, y: int, w: int, h: int, color: int) -> None:
        """Draws a solid rectangle."""
        for i in range(x, x + w):
            for j in range(y, y + h):
                self.put_pixel(i, j, color)

    def render(self) -> None:
        """Renders the maze and the UI menu using the clean layer order."""
        if not MLX_READY:
            return

        # Clear background
        if self.bytes_per_pixel == 4:
            self.img_data[:] = bytes(
                [0, 0, 0, 255] * (self.w_width * self.w_height)
            )
        else:
            self.img_data[:] = bytes(len(self.img_data))

        cs = self.cell_size
        wall_col = self.colors[self.color_idx]

        # Draw reserved cells (The "42" pattern)
        for (rx, ry) in self.maze.reserved_cells:
            self.draw_square(rx * cs, ry * cs, cs, 0x555555)

        # Draw maze walls
        for y in range(self.maze.height):
            for x in range(self.maze.width):
                val = self.maze.grid[y][x]
                px, py = x * cs, y * cs
                if val & 1:
                    self.draw_line(px, py, px + cs, py, wall_col)
                if val & 2:
                    self.draw_line(px + cs, py, px + cs, py + cs, wall_col)
                if val & 4:
                    self.draw_line(px, py + cs, px + cs, py + cs, wall_col)
                if val & 8:
                    self.draw_line(px, py, px, py + cs, wall_col)

        # Draw outer border
        mw = self.w_width - 1
        mh = self.w_height - 1
        for i in range(2):
            self.draw_line(i, i, mw - i, i, wall_col)
            self.draw_line(i, mh - i, mw - i, mh - i, wall_col)
            self.draw_line(i, i, i, mh - i, wall_col)
            self.draw_line(mw - i, i, mw - i, mh - i, wall_col)

        # UI Elements
        self._draw_entry_exit()
        if self.show_path:
            self.draw_path()

        # Render menu dynamically (Text at the bottom)
        menu_items = [
            "=== A-Maze-ing ===",
            "1. Re-generate a new maze",
            "2. Show/Hide path from entry to exit",
            "3. Rotate maze colors",
            "4. Animate maze generation",
            "ESC: Quit"
        ]

        start_y = self.w_height + 20
        for i, text in enumerate(menu_items):
            self.mlx.mlx_string_put(
                self.mlx_ptr, self.win_ptr, 10,
                start_y + (i * 20), 0xFFFFFF, text
            )

        # 7. Push to window
        self.mlx.mlx_put_image_to_window(
            self.mlx_ptr, self.win_ptr, self.img_ptr, 0, 0
        )
        self.mlx.mlx_sync(self.mlx_ptr, 2, self.win_ptr)

    def _draw_entry_exit(self) -> None:
        """Helper to draw the entry (green) and exit (red) squares."""
        cs = self.cell_size
        en_x = self.maze.entry[0] * cs
        en_y = self.maze.entry[1] * cs
        ex_x = self.maze.exit_coord[0] * cs
        ex_y = self.maze.exit_coord[1] * cs

        self.draw_square(en_x + 2, en_y + 2, cs - 4, 0x00FF00)
        self.draw_square(ex_x + 2, ex_y + 2, cs - 4, 0xFF0000)

    def draw_path(self) -> None:
        """Draws the solution path as a continuous series of rectangles."""
        path = self.maze.solve()
        cx, cy = self.maze.entry
        cs = self.cell_size
        off = cs // 2
        thickness = 10

        self.draw_square(
            cx * cs + off - (thickness // 2),
            cy * cs + off - (thickness // 2),
            thickness, 0x0000FF
        )

        for step in path:
            nx, ny = cx, cy
            if step == 'N':
                ny -= 1
            elif step == 'S':
                ny += 1
            elif step == 'E':
                nx += 1
            elif step == 'W':
                nx -= 1

            curr_x, curr_y = cx * cs + off, cy * cs + off
            next_x, next_y = nx * cs + off, ny * cs + off

            self.draw_rect(
                min(curr_x, next_x) - (thickness // 2),
                min(curr_y, next_y) - (thickness // 2),
                abs(next_x - curr_x) + thickness,
                abs(next_y - curr_y) + thickness,
                0x0000FF
            )
            cx, cy = nx, ny

    def loop_hook(self, param: Any) -> None:
        """Continuously running hook to draw when needed."""
        if self.animating and self.gen_iterator is not None:
            try:
                # Continue the maze generation for a few steps per frame
                for _ in range(self.steps_per_frame):
                    next(self.gen_iterator)
                self.needs_redraw = True
            except StopIteration:
                # Generation finished
                self.animating = False
                self.gen_iterator = None
                self.needs_redraw = True
                print("Animation complete!")

        if self.needs_redraw:
            self.render()
            self.needs_redraw = False

    def key_press(self, keycode: int, param: Any) -> None:
        """Handles keyboard events (ESC, 1, 2, 3)."""
        if keycode in (65307, 53):  # ESC
            self.mlx.mlx_loop_exit(self.mlx_ptr)
            os._exit(0)
        elif keycode in (49, 18, 49 + 65360):   # '1' or Num1
            w = self.maze.width
            h = self.maze.height
            self.maze.grid = [[15 for _ in range(w)] for _ in range(h)]
            self.maze.reserved_cells.clear()
            self.maze._embed_42_pattern()
            self.maze.generate()
            self.needs_redraw = True
        elif keycode in (50, 19, 50 + 65360):   # '2' or Num2
            self.show_path = not self.show_path
            self.needs_redraw = True
        elif keycode in (51, 20, 51 + 65360):   # '3' or Num3
            self.color_idx = (self.color_idx + 1) % len(self.colors)
            self.needs_redraw = True
        # '4' to animate maze generation'
        elif keycode in (52, 21):
            print("Animating maze generation...")
            # Reset the maze grid to all walls (15)
            self.maze.grid = [
                [15 for _ in range(self.maze.width)]
                for _ in range(self.maze.height)
            ]
            # 42 pattern is reserved, so we clear it and re-embed it
            self.maze.reserved_cells.clear()
            self.maze._embed_42_pattern()

            # Start the animated generation
            self.animating = True
            self.gen_iterator = self.maze.generate_animated()
            self.show_path = False

    def run(self) -> None:
        """Starts the MLX loop."""
        if not MLX_READY:
            return

        self.mlx.mlx_key_hook(self.win_ptr, self.key_press, None)
        self.mlx.mlx_loop_hook(self.mlx_ptr, self.loop_hook, None)
        self.mlx.mlx_loop(self.mlx_ptr)
