import random
from typing import Dict, List, Optional, Tuple, Deque
from collections import deque


class Cell:
    """
    Representa una celda individual en el laberinto.

    Attributes:
        x: Coordenada x de la celda.
        y: Coordenada y de la celda.
        n: Pared norte abierta (True) o cerrada (False).
        s: Pared sur abierta (True) o cerrada (False).
        e: Pared este abierta (True) o cerrada (False).
        w: Pared oeste abierta (True) o cerrada (False).
        visited: Indica si la celda ha sido visitada durante la generación.
        is_42: Indica si la celda es parte del patrón '42'.
    """

    def __init__(self, x: int, y: int) -> None:
        """
        Inicializa una celda con todas las paredes cerradas.

        Args:
            x: Coordenada x de la celda.
            y: Coordenada y de la celda.
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
    Generador de laberintos usando backtracking recursivo.

    Esta clase implementa el algoritmo de backtracking recursivo para generar
    laberintos perfectos (con un único camino entre entrada y salida).

    Example:
        >>> gen = MazeGenerator(width=20, height=15, seed=42)
        >>> maze = gen.generate(entry=(1, 1), exit_=(20, 15))
        >>> path = gen.shortest_path(entry=(1, 1), exit_=(20, 15))
        >>> print(f"Camino de {len(path)} pasos: {path}")

    Attributes:
        width: Ancho del laberinto en celdas.
        height: Alto del laberinto en celdas.
        perfect: Si True, genera un laberinto perfecto.
        seed: Semilla para reproducibilidad (opcional).
        maze: Matriz de celdas del laberinto generado.
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
        Inicializa el generador de laberintos.

        Args:
            width: Ancho del laberinto en celdas.
            height: Alto del laberinto en celdas.
            perfect: Si True, genera un laberinto perfecto.
            seed: Semilla para reproducibilidad (opcional).
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
        Genera el laberinto usando backtracking recursivo.

        Args:
            entry: Coordenadas de entrada en base-1 (x, y).
            exit_: Coordenadas de salida en base-1 (x, y).

        Returns:
            Matriz de celdas del laberinto generado.
        """
        entry_0 = (entry[0] - 1, entry[1] - 1)

        maze = self._create_closed_maze()
        self._add_42_pattern(maze)
        start_x, start_y = self._find_start_cell(maze, entry_0)
        self._backtrack(start_x, start_y, maze)

        self.maze = maze
        return maze

    def shortest_path(self, entry: Tuple[int, int],
                      exit_: Tuple[int, int]) -> str:
        """
        Encuentra el camino más corto usando BFS.

        Args:
            entry: Coordenadas de entrada en base-1 (x, y).
            exit_: Coordenadas de salida en base-1 (x, y).

        Returns:
            String con las direcciones del camino (NSEW).

        Raises:
            ValueError: Si el laberinto no ha sido generado.
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
        Obtiene la estructura del laberinto generado.

        Returns:
            Matriz de celdas o None si no se ha generado.
        """
        return self.maze

    def to_hex_matrix(self) -> List[str]:
        """
        Convierte el laberinto a formato hexadecimal.

        Returns:
            Lista de strings hexadecimales, uno por fila.

        Raises:
            ValueError: Si el laberinto no ha sido generado.
        """
        if self.maze is None:
            raise ValueError("El laberinto no ha sido generado aún")

        return ["".join(self._cell_to_hex(cell) for cell in row)
                for row in self.maze]

    # Métodos privados (implementación interna)
    def _create_closed_maze(self) -> List[List[Cell]]:
        """Crea un laberinto con todas las paredes cerradas."""
        return [[Cell(x, y) for x in range(self.width)]
                for y in range(self.height)]

    def _close_all_walls(self, cell: Cell) -> None:
        """Cierra todas las paredes de una celda."""
        cell.n = cell.s = cell.e = cell.w = False

    def _add_42_pattern(self, maze: List[List[Cell]]) -> None:
        """Añade el patrón '42' al centro del laberinto."""
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
        """Verifica si una celda es un vecino válido."""
        return (0 <= x < self.width and 0 <= y < self.height and
                not maze[y][x].is_42)

    def _get_neighbors(self, x: int, y: int,
                       maze: List[List[Cell]]) -> List[Tuple[int, int, str]]:
        """Obtiene vecinos válidos de una celda."""
        potential = [
            (x, y - 1, "N"), (x, y + 1, "S"),
            (x - 1, y, "W"), (x + 1, y, "E"),
        ]
        return [(nx, ny, d) for nx, ny, d in potential
                if self._is_valid_neighbor(nx, ny, maze)]

    def _open_wall(self, current: Cell, nx: int, ny: int,
                   direction: str, maze: List[List[Cell]]) -> None:
        """Abre la pared entre dos celdas adyacentes."""
        neighbor = maze[ny][nx]
        wall_pairs = {
            "N": ("n", "s"), "S": ("s", "n"),
            "W": ("w", "e"), "E": ("e", "w")
        }
        cw, nw = wall_pairs[direction]
        setattr(current, cw, True)
        setattr(neighbor, nw, True)

    def _backtrack(self, x: int, y: int, maze: List[List[Cell]]) -> None:
        """Algoritmo de backtracking recursivo."""
        maze[y][x].visited = True
        neighbors = self._get_neighbors(x, y, maze)
        random.shuffle(neighbors)

        for nx, ny, direction in neighbors:
            if not maze[ny][nx].visited and not maze[ny][nx].is_42:
                self._open_wall(maze[y][x], nx, ny, direction, maze)
                self._backtrack(nx, ny, maze)

    def _find_start_cell(self, maze: List[List[Cell]],
                         entry: Tuple[int, int]) -> Tuple[int, int]:
        """Encuentra una celda de inicio válida."""
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
        """Procesa un vecino en BFS."""
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
        """Convierte una celda a representación hexadecimal."""
        value = 0
        if not cell.n:
            value |= 1
        if not cell.e:
            value |= 2
        if not cell.s:
            value |= 4
        if not cell.w:
            value |= 8
        return format(value, "X")
