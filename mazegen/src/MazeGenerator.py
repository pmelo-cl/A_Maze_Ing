import random
from typing import Dict, List, Optional, Tuple, Deque
from collections import deque


class Cell:
    """
    Represents an individual cell in the maze.

    Attributes:
        x: X coordinate of the cell.
        y: Y coordinate of the cell.
        n: North wall open (True) or closed (False).
        s: South wall open (True) or closed (False).
        e: East wall open (True) or closed (False).
        w: West wall open (True) or closed (False).
        visited: Whether the cell has been visited during generation.
        is_42: Whether the cell is part of the '42' pattern.
    """

    def __init__(self, x: int, y: int) -> None:
        """
        Initializes a cell with all walls closed.

        Args:
            x: X coordinate of the cell.
            y: Y coordinate of the cell.
        """
        self.n = False
        self.s = False
        self.e = False
        self.w = False
        self.visited = False
        self.x = x
        self.y = y
        self.is_42 = False


class MazeGenerator:
    """
    Maze generator using iterative backtracking.

    This class implements the backtracking algorithm to generate
    perfect mazes (with a single path between entry and exit).
    An iterative version is used to avoid recursion errors on large
    mazes (FIX 7).

    Example:
        >>> gen = MazeGenerator(width=20, height=15, seed=42)
        >>> maze = gen.generate(entry=(1, 1), exit_=(20, 15))
        >>> path = gen.shortest_path(entry=(1, 1), exit_=(20, 15))
        >>> print(f"Camino de {len(path)} pasos: {path}")

    Attributes:
        width: Width of the maze in cells.
        height: Height of the maze in cells.
        perfect: If True, generates a perfect maze.
        seed: Seed for reproducibility (optional).
        maze: Matrix of cells of the generated maze.
    """

    PATTERN_42 = [
        [1, 0, 1, 0, 1, 1, 1],
        [1, 0, 1, 0, 0, 0, 1],
        [1, 1, 1, 0, 1, 1, 1],
        [0, 0, 1, 0, 1, 0, 0],
        [0, 0, 1, 0, 1, 1, 1],
    ]
    PATTERN_HEIGHT = 5
    PATTERN_WIDTH = 7

    def __init__(self, width: int, height: int, perfect: bool = True,
                 seed: Optional[int] = None) -> None:
        """
        Initializes the maze generator.

        Args:
            width: Width of the maze in cells.
            height: Height of the maze in cells.
            perfect: If True, generates a perfect maze.
            seed: Seed for reproducibility (optional).
        """
        self.width = width
        self.height = height
        self.perfect = perfect
        self.seed = seed
        self.maze: Optional[List[List[Cell]]] = None

        if self.seed is not None:
            random.seed(self.seed)

    def generate(self, entry: Tuple[int, int],
                 exit_: Tuple[int, int]) -> List[List[Cell]]:
        """
        Generates the maze using iterative backtracking.

        Args:
            entry: Entry coordinates in 1-based index (x, y).
            exit_: Exit coordinates in 1-based index (x, y).

        Returns:
            Matrix of cells of the generated maze.
        """
        entry_0 = (entry[0] - 1, entry[1] - 1)

        maze = self._create_closed_maze()
        self._add_42_pattern(maze)
        start_x, start_y = self._find_start_cell(maze, entry_0)
        # FIX 7: Use iterative version to avoid RecursionError on large mazes
        self._backtrack_iterative(start_x, start_y, maze)

        self.maze = maze
        return maze

    def shortest_path(self, entry: Tuple[int, int],
                      exit_: Tuple[int, int]) -> str:
        """
        Finds the shortest path using BFS.

        Args:
            entry: Entry coordinates in 1-based index (x, y).
            exit_: Exit coordinates in 1-based index (x, y).

        Returns:
            String with path directions (NSEW).

        Raises:
            ValueError: If the maze has not been generated yet.
        """
        if self.maze is None:
            raise ValueError("El laberinto no ha sido generado aún")

        ex, ey = entry[0] - 1, entry[1] - 1
        fx, fy = exit_[0] - 1, exit_[1] - 1

        if not (0 <= ex < self.width and 0 <= ey < self.height):
            raise ValueError(f"Coordenadas de entrada fuera de rango: {entry}")
        if not (0 <= fx < self.width and 0 <= fy < self.height):
            raise ValueError(f"Coordenadas de salida fuera de rango: {exit_}")

        visited = [[False] * self.width for _ in range(self.height)]
        prev: Dict[Tuple[int, int], Tuple[Tuple[int, int], str]] = {}
        queue: Deque[Tuple[int, int]] = deque([(ey, ex)])
        visited[ey][ex] = True

        while queue:
            y, x = queue.popleft()
            if y == fy and x == fx:
                break

            neighbors = [
                (y - 1, x, "n", "s", "N"),
                (y + 1, x, "s", "n", "S"),
                (y, x + 1, "e", "w", "E"),
                (y, x - 1, "w", "e", "W"),
            ]

            for ny, nx, cw, nw, direction in neighbors:
                if 0 <= ny < self.height and 0 <= nx < self.width:
                    self._process_neighbor(y, x, ny, nx, cw, nw,
                                           direction, visited, prev, queue)

        if not visited[fy][fx]:
            return ""

        path = []
        current = (fy, fx)
        while current != (ey, ex):
            previous, direction = prev[current]
            path.append(direction)
            current = previous

        path.reverse()
        return "".join(path)

    def get_maze_structure(self) -> Optional[List[List[Cell]]]:
        """
        Gets the structure of the generated maze.

        Returns:
            Cell matrix or None if not yet generated.
        """
        return self.maze

    def to_hex_matrix(self) -> List[str]:
        """
        Converts the maze to hexadecimal format.

        Returns:
            List of hexadecimal strings, one per row.

        Raises:
            ValueError: If the maze has not been generated yet.
        """
        if self.maze is None:
            raise ValueError("El laberinto no ha sido generado aún")

        return ["".join(self._cell_to_hex(cell) for cell in row)
                for row in self.maze]

    def _create_closed_maze(self) -> List[List[Cell]]:
        """Creates a maze with all walls closed."""
        return [[Cell(x, y) for x in range(self.width)]
                for y in range(self.height)]

    def _close_all_walls(self, cell: Cell) -> None:
        """Closes all walls of a cell."""
        cell.n = cell.s = cell.e = cell.w = False

    def _add_42_pattern(self, maze: List[List[Cell]]) -> None:
        """Adds the '42' pattern to the center of the maze."""
        if (self.height < self.PATTERN_HEIGHT or
                self.width < self.PATTERN_WIDTH):
            return

        start_y = (self.height - self.PATTERN_HEIGHT) // 2
        start_x = (self.width - self.PATTERN_WIDTH) // 2

        for py in range(self.PATTERN_HEIGHT):
            for px in range(self.PATTERN_WIDTH):
                if self.PATTERN_42[py][px] == 1:
                    y, x = start_y + py, start_x + px
                    if 0 <= y < self.height and 0 <= x < self.width:
                        maze[y][x].is_42 = True
                        self._close_all_walls(maze[y][x])

    def _is_valid_neighbor(self, x: int, y: int,
                           maze: List[List[Cell]]) -> bool:
        """Checks if a cell is a valid neighbor."""
        return (0 <= x < self.width and 0 <= y < self.height and
                not maze[y][x].is_42)

    def _get_neighbors(self, x: int, y: int,
                       maze: List[List[Cell]]) -> List[Tuple[int, int, str]]:
        """Gets valid neighbors of a cell."""
        potential = [
            (x, y - 1, "N"), (x, y + 1, "S"),
            (x - 1, y, "W"), (x + 1, y, "E"),
        ]
        return [(nx, ny, d) for nx, ny, d in potential
                if self._is_valid_neighbor(nx, ny, maze)]

    def _open_wall(self, current: Cell, nx: int, ny: int,
                   direction: str, maze: List[List[Cell]]) -> None:
        """Opens the wall between two adjacent cells."""
        neighbor = maze[ny][nx]
        wall_pairs = {
            "N": ("n", "s"), "S": ("s", "n"),
            "W": ("w", "e"), "E": ("e", "w")
        }
        cw, nw = wall_pairs[direction]
        setattr(current, cw, True)
        setattr(neighbor, nw, True)

    def _backtrack_iterative(self, start_x: int, start_y: int,
                             maze: List[List[Cell]]) -> None:
        """
        Iterative backtracking algorithm using an explicit stack.

        FIX 7: Replaces the recursive version to avoid RecursionError
        on large mazes where Python's call stack is exhausted.
        """
        stack: List[Tuple[int, int]] = [(start_x, start_y)]
        maze[start_y][start_x].visited = True

        while stack:
            x, y = stack[-1]
            neighbors = self._get_neighbors(x, y, maze)
            unvisited = [(nx, ny, d) for nx, ny, d in neighbors
                         if not maze[ny][nx].visited and
                         not maze[ny][nx].is_42]

            if unvisited:
                random.shuffle(unvisited)
                nx, ny, direction = unvisited[0]
                self._open_wall(maze[y][x], nx, ny, direction, maze)
                maze[ny][nx].visited = True
                stack.append((nx, ny))
            else:
                stack.pop()

    def _find_start_cell(self, maze: List[List[Cell]],
                         entry: Tuple[int, int]) -> Tuple[int, int]:
        """Finds a valid starting cell."""
        ex, ey = entry
        if not maze[ey][ex].is_42:
            return ex, ey

        for radius in range(1, max(self.width, self.height)):
            for dx in range(-radius, radius + 1):
                for dy in range(-radius, radius + 1):
                    nx, ny = ex + dx, ey + dy
                    if (self._is_valid_neighbor(nx, ny, maze) and
                            not maze[ny][nx].is_42):
                        return nx, ny

        raise ValueError("No se encontró celda de inicio válida")

    def _process_neighbor(self, y: int, x: int, ny: int, nx: int,
                          cw: str, nw: str, direction: str,
                          visited: List[List[bool]],
                          prev: Dict[Tuple[int, int],
                                     Tuple[Tuple[int, int], str]],
                          queue: Deque[Tuple[int, int]]) -> None:
        """Processes a neighbor during BFS."""
        if self.maze is None:
            return

        current_cell = self.maze[y][x]
        neighbor = self.maze[ny][nx]

        if (getattr(current_cell, cw) and getattr(neighbor, nw) and
                not neighbor.is_42 and not visited[ny][nx]):
            visited[ny][nx] = True
            prev[(ny, nx)] = ((y, x), direction)
            queue.append((ny, nx))

    def _cell_to_hex(self, cell: Cell) -> str:
        """
        Converts a cell to its hexadecimal representation.

        Bits: active bit = CLOSED wall (no passage).
        N=0x1, E=0x2, S=0x4, W=0x8
        A cell with all walls closed equals 0xF.
        """
        value = 0
        if not cell.n:
            value |= 0x1
        if not cell.e:
            value |= 0x2
        if not cell.s:
            value |= 0x4
        if not cell.w:
            value |= 0x8
        return format(value, "X")
