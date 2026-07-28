*This project has been created as part of the 42 curriculum by luisesti and malopez-.*

# A-Maze-ing: Procedural Maze Generator

## Description
The A-Maze-ing project is a comprehensive procedural maze generator and visualizer written in Python 3.10+. Its primary goal is to apply graph theory and randomness to generate coherent, fully connected mazes, while managing constraints such as embedding a predefined "42" solid pattern and calculating the shortest path between entry and exit points.

This project explores algorithm optimization, memory management (avoiding recursion limits), bitwise operations for data storage, and the creation of a reusable, pip-installable Python package.

---

## Instructions

### Prerequisites
* Python 3.10 or higher.
* `pip` and standard build tools.
* MiniLibX dependencies (for the graphical frontend).

### Installation and Execution
We have provided a `Makefile` to automate the workflow.

1. **Install dependencies and linters:**
   ```bash
   make install
   ```

2. **Run the program:**
   Execute the main program passing the configuration file as an argument:
   ```bash
   make run
   # Or manually: python3 a_maze_ing.py config.txt
   ```

3. **Visualizer Controls (MiniLibX):**
   * `ESC` - Close the application.
   * `1` - Generate a new random maze (using current config).
   * `2` - Show/Hide the shortest path solution (BFS).
   * `4` - **[Bonus]** Start the real-time generation animation.

4. **Clean cache and temporary files:**
   ```bash
   make clean
   ```

5. **Run strict linting (flake8 & mypy):**
   ```bash
   make lint
   # Or 'make lint-strict' depending on Makefile setup
   ```

---

## Configuration File Format
The program requires a plain text configuration file (`config.txt`) passed as an argument. Lines starting with `#` are ignored. Each setting must follow the `KEY=VALUE` format.

* **WIDTH**: Maze width in cells (integer).
* **HEIGHT**: Maze height in cells (integer).
* **ENTRY**: Entry coordinates in `x,y` format.
* **EXIT**: Exit coordinates in `x,y` format.
* **OUTPUT_FILE**: Name of the text file where the hexadecimal output will be saved.
* **PERFECT**: Boolean (`True` or `False`). If True, generates a maze with a single unique path between any two cells.
* **SEED**: (Optional) Integer to initialize the random number generator for reproducible mazes.

**Example:**
```text
WIDTH=20
HEIGHT=15
ENTRY=0,0
EXIT=19,14
OUTPUT_FILE=maze.txt
PERFECT=True
SEED=42
```

---

## Technical Choices: The Algorithm

### The Chosen Algorithm
We implemented the **Iterative Recursive Backtracker** (Depth-First Search) to carve the maze, paired with a **Breadth-First Search (BFS)** algorithm to calculate the shortest path.

### Why this algorithm?
1. **Guarantees a Perfect Maze:** By definition, the backtracker visits every cell exactly once without breaking walls into already visited cells. This naturally creates a spanning tree (a maze with exactly one solution and no loops), fulfilling the `PERFECT=True` requirement effortlessly.
2. **Memory Efficiency:** Instead of using classic recursion (which would hit Python's `RecursionError` limit on large grids), we used a `while` loop and an explicit list-based stack. This makes the generator highly scalable.
3. **Obstacle Handling:** The Backtracker makes it incredibly easy to embed the required "42" pattern. We simply pre-calculated the pattern's coordinates and added them to the "visited" set before starting the generation. The algorithm naturally routes around these cells, leaving the solid shape intact.
4. **Aesthetic:** It produces mazes with long, winding corridors ("high river factor"), which look complex and are visually engaging when rendered.

---

## Advanced Features & Bonuses

Beyond the mandatory requirements, we implemented the following advanced features:

1. **Playable "Pac-Man" Mode (`PERFECT=False`):** 
   When a non-perfect maze is requested, the generator post-processes the perfect tree by intelligently removing dead-ends without creating large open areas (preventing 3x3 open zones). This creates a "braided" maze with multiple independent routes (loops) while explicitly ensuring the corners and the center remain accessible, scoring a maximum "Bonus-grade" rating in the official `maze_analyzer.py` tool.
   
2. **Real-Time Generation Animation:** 
   Instead of generating the maze instantly, we decoupled the mathematical generation from the visual rendering using Python Generators (`yield`). This allows the MiniLibX interface to visually animate the algorithm carving out the paths step-by-step in real-time, without blocking the main execution thread or hitting recursion limits.

3. **Strict I/O Security Validation (Defensive Programming):** 
   To prevent arbitrary file overwriting (e.g., maliciously setting `OUTPUT_FILE=main.py`) or path traversal attacks (e.g., attempting to write outside the execution directory), the configuration parser implements strict defensive checks. It enforces `.txt` extensions and local directory paths exclusively, safely aborting execution with a clear error if malicious inputs are detected.

---

## Reusable Code (The `mazegen` Module)

The core logic of the maze generator has been strictly decoupled from the main execution script and packaged into a standalone module called `mazegen`.

### How to reuse it
The package is built as a `.whl` and `.tar.gz` file located in the repository. It can be installed in any Python environment using pip:

```bash
pip install mazegen-1.0.0-py3-none-any.whl
```

### How to build the package from source
During the evaluation, you will be asked to rebuild this package. From the root of the repository, ensure you have the build tools installed and run the build command:

```bash
# Install the build tool
pip install build

# Build the package from the source files
python3 -m build

# Build the package from Makefile
make build
```

### Usage Example in a New Project

```python
from mazegen.generator import MazeGenerator

# Instantiate the generator
maze = MazeGenerator(width=20, height=15, entry=(0,0), exit_coord=(19,14))

# Carve the paths
maze.generate()

# Access the generated grid (2D list of integers)
grid_data = maze.grid

# Get the shortest path string (e.g., "NNEESSSW")
solution = maze.solve()
```

---

## Team and Project Management

### Roles
To ensure efficiency and avoid merge conflicts, we divided the project into two distinct architectural layers:
* **luisesti (Backend & Logic):** Responsible for the mathematical generation of the maze, the backtracker algorithm, bitwise data formatting, BFS pathfinding, configuration parsing, and building the pip-installable module.
* **malopez- (Frontend & UI):** Responsible for integrating the MiniLibX library, translating the backend's data into visual pixels, handling keyboard hooks, managing application state (regenerate, toggle path, color changes), and memory leak prevention.

### Anticipated Planning vs. Evolution
* *Initial Plan:* We aimed to work on the algorithm together and then split the visual aspects.
* *Evolution:* We quickly realized that the frontend required the backend's data structure to be stable. We adapted our plan so the backend was completed first using ASCII rendering for debugging, allowing the frontend development to proceed unblocked using a stable API.

### What Worked Well & Areas for Improvement
* **Worked Well:** Decoupling the logic from the visualizer. By standardizing the hexadecimal grid format early on, the frontend could be tested with hardcoded text files before the generator was fully finished.
* **Improvement:** Navigating the strict formatting limits of `flake8` while keeping complex algorithmic logic readable was challenging and required several refactoring sessions. Additionally, integrating the official `maze_analyzer.py` earlier in our pipeline would have helped us detect edge-cases with the "42" pattern enclosure sooner.

### Tools Used
* **Version Control:** Git & GitHub.
* **Linters:** `flake8` for style checking and `mypy` for strict static type checking.
* **Build Tools:** `setuptools` and `build` for the Python package creation.
* **Libraries:** `MiniLibX` (Campus standard graphical interface).

---

## Resources & AI Usage

### References
* [Maze Generation Algorithms - Wikipedia](https://en.wikipedia.org/wiki/Maze_generation_algorithm)
* [Jamis Buck's Maze Algorithm Book & Blog](http://weblog.jamisbuck.org/2011/2/7/maze-generation-algorithm-recap)
* [Python `typing` documentation](https://docs.python.org/3/library/typing.html)

### AI Usage Declaration
Artificial Intelligence (LLMs) was used during this project as a conceptual sounding board and formatting assistant, specifically for:
* Discussing the tradeoffs between Prim's, Kruskal's, and the Recursive Backtracker algorithms.
* Generating boilerplate code for the `pyproject.toml` file to package the reusable module.
* Reviewing `flake8` errors to format line lengths and docstrings properly.
* Structuring and formatting this README.md file to ensure it clearly meets all curriculum requirements.
All generated concepts and texts were thoroughly reviewed, manually tested, and deeply understood before integration into the final codebase.