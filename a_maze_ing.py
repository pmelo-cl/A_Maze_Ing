"""
Maze generator with interactive visualization.

This module implements a random maze generator using
the recursive backtracking algorithm, with graphical
visualization capabilities using MiniLibX.
"""

import os
import sys
import re
from typing import Callable, Dict, Any, List, Optional, Tuple, cast
from collections import deque

try:
    from mlx import Mlx
    MLX_AVAILABLE = True
except ImportError:
    MLX_AVAILABLE = False
    print("Advertencia: No se pudo importar mlx. \
        La visualización no estará disponible.")

try:
    from src.MazeGenerator import MazeGenerator
except ImportError:
    print("Advertencia: mazegen no instalado. Usando versión embebida.")

CELL_SIZE = 20
MIN_CELL_SIZE = 5
MAX_CELL_SIZE = 50

DEFAULT_WALL_COLOR = 0xFFFFFFFF
DEFAULT_BG_COLOR = 0xFF000000
DEFAULT_ENTRY_COLOR = 0xFF00FF00
DEFAULT_EXIT_COLOR = 0xFFFF0000
DEFAULT_PATH_COLOR = 0xFF0000FF
DEFAULT_CLOSED_CELL_COLOR = 0xAAFFFFFF
DEFAULT_PATTERN_42_COLOR = 0xFFFFFF00


ALT_WALL_COLORS = [
    0xFFFFFFFF,
    0xFFFF00FF,
    0xFF00FFFF,
    0xFFFFFF00,
    0xFFFF8800,
]

ALT_LOGO_COLORS = [
    0xAAFFFFFF,
    0xAAFF0000,
    0xAA00FF00,
    0xAA0000FF,
    0xAAFFFF00,
    0xAAFF00FF,
]

KEY_ESC = 65307
KEY_ENTER = 65293
KEY_1 = 49
KEY_C = 99
KEY_L = 108
KEY_UP = 65362
KEY_DOWN = 65364
KEY_LEFT = 65361
KEY_RIGHT = 65363
KEY_PLUS1 = 61
KEY_PLUS2 = 65451
KEY_MINUS1 = 45
KEY_MINUS2 = 65453
ON_DESTROY = 33

show_path_state = False
maze_state: Optional[Dict[str, Any]] = None
mlx_instance: Optional[Any] = None
current_wall_color_index = 0
current_logo_color_index = 0

if MLX_AVAILABLE:
    mlx_instance = Mlx()


class ConfigError(Exception):
    """Custom exception for configuration errors."""
    pass


def read_file_lines(filepath: str) -> List[str]:
    """
    Reads a file and returns its lines stripped of whitespace.

    Args:
        filepath: Path to the file.

    Returns:
        List of lines stripped of whitespace.

    Raises:
        FileNotFoundError: If the file does not exist.
        IOError: If a read error occurs.
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as file:
            return [line.strip() for line in file.readlines() if line.strip()]
    except FileNotFoundError:
        raise FileNotFoundError(f"Archivo no encontrado: {filepath}")
    except IOError as e:
        raise IOError(f"Error de lectura del archivo: {e}")


def write_file(filepath: str, content: str) -> None:
    """
    Writes content to a file.

    Args:
        filepath: Path to the file.
        content: Content to write.

    Raises:
        IOError: If a write error occurs.
    """
    try:
        with open(filepath, 'w', encoding='utf-8') as file:
            file.write(content)
    except IOError as e:
        raise IOError(f"Error al escribir el archivo: {e}")


def parse_coordinate(coord_str: str) -> Tuple[int, int]:
    """
    Parses a coordinate string 'x,y' into a tuple (x, y).

    Args:
        coord_str: String in the format "x,y".

    Returns:
        Tuple with the coordinates (x, y).

    Raises:
        ValueError: If the format is invalid.
    """
    parts = coord_str.split(',')
    if len(parts) != 2:
        raise ValueError(f"Formato de coordenadas inválido: {coord_str}")
    return (int(parts[0]), int(parts[1]))


def parse_boolean(bool_str: str) -> bool:
    """
    Parses a string into a boolean value.

    Args:
        bool_str: String containing "true" or "false" (case-insensitive).

    Returns:
        Corresponding boolean value.
    """
    return bool_str.lower() == "true"


def validate_coordinates(entry: Tuple[int, int], exit_: Tuple[int, int]
                         ) -> None:
    """
    Validates that the coordinates are correct.

    Args:
        entry: Entry coordinates.
        exit_: Exit coordinates.

    Raises:
        ConfigError: If the coordinates are invalid.
    """
    if not isinstance(entry, tuple) or len(entry) != 2:
        raise ConfigError("ENTRY debe ser una tupla de dos enteros (x, y)")
    if not isinstance(exit_, tuple) or len(exit_) != 2:
        raise ConfigError("EXIT debe ser una tupla de dos enteros (x, y)")
    if entry == exit_:
        raise ConfigError("ENTRY y EXIT deben ser diferentes")


def parse_config(config_path: str) -> Dict[str, Any]:
    """
    Parses the configuration file and returns a dictionary with the values.

    Args:
        config_path: Path to the configuration file.

    Returns:
        Dictionary with the parsed keys and values.

    Raises:
        ConfigError: If there is any error in the format,
        missing or invalid values.
        FileNotFoundError: If the file does not exist.
    """
    REQUIRED_KEYS = {
        "WIDTH": int,
        "HEIGHT": int,
        "ENTRY": parse_coordinate,
        "EXIT": parse_coordinate,
        "OUTPUT_FILE": str,
        "PERFECT": parse_boolean
    }

    config: Dict[str, Any] = {}
    lines = read_file_lines(config_path)

    for line_num, line in enumerate(lines, start=1):
        if line.startswith('#'):
            continue

        if '=' not in line:
            raise ConfigError(
                f"Línea {line_num}: Formato inválido, se esperaba 'KEY=VALUE'"
            )

        key, value = line.split('=', 1)
        config[key.strip()] = value.strip()

    missing_keys = [key for key in REQUIRED_KEYS if key not in config]
    if missing_keys:
        raise ConfigError(
            f"Claves obligatorias faltantes: {missing_keys}"
        )

    for key, converter in REQUIRED_KEYS.items():
        try:
            if key not in config:
                raise ConfigError(f"Clave requerida '{key}' no "
                                  f"encontrada en configuración")

            value = config[key]
            if value is None:
                raise ConfigError(f"El valor para '{key}' no puede ser None")

            converter_func = cast(Callable[[Any], Any], converter)
            config[key] = converter_func(value)

        except KeyError:
            raise ConfigError(f"Clave '{key}' no encontrada en configuración")
        except (ValueError, TypeError) as e:
            raise ConfigError(
                f"Error al convertir '{key}': {config.get(key, 'N/A')} - {e}"
            )

    validate_coordinates(config["ENTRY"], config["EXIT"])

    if config["WIDTH"] <= 0 or config["HEIGHT"] <= 0:
        raise ConfigError("WIDTH y HEIGHT deben ser mayores a 0")

    return config


def write_output_file(filename: str, maze: MazeGenerator,
                      entry: Tuple[int, int], exit_: Tuple[int, int],
                      path: str) -> None:
    """
    Writes the maze to the output file in the specified format.

    Args:
        filename: Name of the output file.
        maze: Maze generator with the generated maze.
        entry: Entry coordinates.
        exit_: Exit coordinates.
        path: Solution path as a string of directions.
    """
    hex_matrix = maze.to_hex_matrix()

    content_parts = [
        "\n".join(hex_matrix),
        "",
        f"{entry[0]},{entry[1]}",
        f"{exit_[0]},{exit_[1]}",
        path,
        ""
    ]

    write_file(filename, "\n".join(content_parts))
    print(f"Laberinto guardado en: {filename}")


def parse_maze_coordinate(line: str,
                          default: Tuple[int, int]) -> Tuple[int, int]:
    """
    Parses a coordinate line from the maze file.

    Args:
        line: Line in the format "x,y".
        default: Default coordinates if parsing fails.

    Returns:
        Tuple with the parsed coordinates or the defaults.
    """
    try:
        parts = line.replace(' ', '').split(',')
        return (int(parts[0]), int(parts[1]))
    except (ValueError, IndexError):
        print(f"Advertencia: Formato inválido: {line}. Usando {default}")
        return default


def normalize_hex_line(line: str, width: int) -> str:
    """
    Normalizes a hexadecimal line to the specified width.

    Args:
        line: Hexadecimal line to normalize.
        width: Desired width.

    Returns:
        Normalized line.
    """
    if len(line) < width:
        return line.ljust(width, '0')
    elif len(line) > width:
        return line[:width]
    return line


def parse_maze_file(file_path: str) -> Tuple[List[str], int, int,
                                             Tuple[int, int], Tuple[int, int],
                                             str]:
    """
    Parses a maze file and returns its components.

    Args:
        file_path: Path to the maze file.

    Returns:
        Tuple with (hex_lines, width, height, entry, exit, path).

    Raises:
        ValueError: If the file is empty or has no hexadecimal lines.
    """
    lines = read_file_lines(file_path)

    if not lines:
        raise ValueError("El archivo está vacío")

    hex_lines = []
    entry_line = None
    exit_line = None
    path_line = None

    for line in lines:
        if re.fullmatch(r'[0-9A-Fa-f]+', line):
            hex_lines.append(line)
        elif ',' in line and entry_line is None:
            entry_line = line
        elif ',' in line and exit_line is None:
            exit_line = line
        elif any(c in line.upper() for c in 'NSEW'):
            path_line = line

    if not hex_lines:
        raise ValueError("No se encontraron líneas "
                         "hexadecimales en el archivo")

    width = len(hex_lines[0])
    height = len(hex_lines)

    hex_lines = [normalize_hex_line(line, width) for line in hex_lines]

    entry = (parse_maze_coordinate(entry_line, (1, 1))
             if entry_line else (1, 1))
    exit_coords = (parse_maze_coordinate(exit_line, (width, height))
                   if exit_line else (width, height))

    path = (''.join(c.upper() for c in path_line if c.upper() in 'NSEW')
            if path_line else "")

    return hex_lines, width, height, entry, exit_coords, path


def get_current_wall_color() -> int:
    """
    Gets the current wall color.

    Returns:
        Hexadecimal wall color.
    """
    return ALT_WALL_COLORS[current_wall_color_index % len(ALT_WALL_COLORS)]


def get_current_logo_color() -> int:
    """
    Gets the current 42 logo color.

    Returns:
        Hexadecimal color for closed cell fill.
    """
    return ALT_LOGO_COLORS[current_logo_color_index % len(ALT_LOGO_COLORS)]


def cycle_wall_color() -> None:
    """Cycles to the next available wall color."""
    global current_wall_color_index
    current_wall_color_index = (
        (current_wall_color_index + 1) % len(ALT_WALL_COLORS)
    )
    color_num = current_wall_color_index + 1
    total_colors = len(ALT_WALL_COLORS)
    print(f"Color de pared cambiado (#{color_num}/{total_colors})")


def cycle_logo_color() -> None:
    """Cycles to the next available logo color."""
    global current_logo_color_index
    current_logo_color_index = (
        (current_logo_color_index + 1) % len(ALT_LOGO_COLORS)
    )
    color_num = current_logo_color_index + 1
    total_colors = len(ALT_LOGO_COLORS)
    print(f"Color del logo cambiado (#{color_num}/{total_colors})")


def is_cell_in_path(x: int, y: int, entry_coords: Tuple[int, int],
                    path: str, maze_width: int, maze_height: int) -> bool:
    """
    Checks whether a cell is part of the solution path.

    Args:
        x: X coordinate of the cell (0-based).
        y: Y coordinate of the cell (0-based).
        entry_coords: Entry coordinates (1-based).
        path: String with the solution path.
        maze_width: Width of the maze.
        maze_height: Height of the maze.

    Returns:
        True if the cell is on the path.
    """
    entry_x, entry_y = entry_coords[0] - 1, entry_coords[1] - 1

    if (x, y) == (entry_x, entry_y):
        return True

    current_x, current_y = entry_x, entry_y

    direction_map = {
        'N': (0, -1),
        'S': (0, 1),
        'E': (1, 0),
        'W': (-1, 0)
    }

    for direction in path:
        dx, dy = direction_map.get(direction, (0, 0))
        current_x += dx
        current_y += dy

        if not (0 <= current_x < maze_width and 0 <= current_y < maze_height):
            continue

        if (current_x, current_y) == (x, y):
            return True

    return False


def get_cell_background_color(j: int, i: int, is_entry: bool, is_exit: bool,
                              show_path: bool, entry_coords: Tuple[int, int],
                              path: str, width: int, height: int,
                              is_42: bool) -> int:
    """
    Determines the background color of a cell.

    Args:
        j: X coordinate of the cell.
        i: Y coordinate of the cell.
        is_entry: Whether this is the entry cell.
        is_exit: Whether this is the exit cell.
        show_path: Whether the solution path should be displayed.
        entry_coords: Entry coordinates.
        path: String with the solution path.
        width: Width of the maze.
        height: Height of the maze.
        is_42: Whether the cell is part of the '42' pattern.

    Returns:
        Hexadecimal color for the cell background.
    """
    if is_entry:
        return DEFAULT_ENTRY_COLOR
    elif is_exit:
        return DEFAULT_EXIT_COLOR
    elif is_42:
        return DEFAULT_PATTERN_42_COLOR
    elif show_path and is_cell_in_path(j, i, entry_coords,
                                       path, width, height):
        return DEFAULT_PATH_COLOR
    else:
        return DEFAULT_BG_COLOR


def draw_cell_background(mlx_ptr: Any, win_ptr: Any, x_start: int,
                         y_start: int, x_end: int, y_end: int,
                         color: int) -> None:
    """
    Draws the background of a cell.

    Args:
        mlx_ptr: Pointer to MLX.
        win_ptr: Pointer to the window.
        x_start: Starting x coordinate.
        y_start: Starting y coordinate.
        x_end: Ending x coordinate.
        y_end: Ending y coordinate.
        color: Background color.
    """
    if mlx_instance is None:
        return

    for x in range(x_start, x_end):
        for y in range(y_start, y_end):
            mlx_instance.mlx_pixel_put(mlx_ptr, win_ptr, x, y, color)


def draw_wall(mlx_ptr: Any, win_ptr: Any, x_start: int, y_start: int,
              x_end: int, y_end: int, wall_type: str,
              wall_color: int) -> None:
    """
    Draws a wall of a cell.

    Args:
        mlx_ptr: Pointer to MLX.
        win_ptr: Pointer to the window.
        x_start: Starting x coordinate.
        y_start: Starting y coordinate.
        x_end: Ending x coordinate.
        y_end: Ending y coordinate.
        wall_type: Wall type ('N', 'S', 'E', 'W').
        wall_color: Wall color.
    """
    if mlx_instance is None:
        return

    wall_positions = {
        'W': lambda: [(x_start, y) for y in range(y_start, y_end)],
        'S': lambda: [(x, y_end - 1) for x in range(x_start, x_end)],
        'E': lambda: [(x_end - 1, y) for y in range(y_start, y_end)],
        'N': lambda: [(x, y_start) for x in range(x_start, x_end)]
    }

    if wall_type in wall_positions:
        for x, y in wall_positions[wall_type]():
            mlx_instance.mlx_pixel_put(mlx_ptr, win_ptr, x, y, wall_color)


def draw_cell_walls(mlx_ptr: Any, win_ptr: Any, x_start: int, y_start: int,
                    x_end: int, y_end: int, hex_value: int,
                    wall_color: int) -> None:
    """
    Draws the walls of a cell based on its hexadecimal value.

    An active bit indicates a CLOSED wall (no passage), consistent
    with _cell_to_hex.
    Bits: N=0x1, E=0x2, S=0x4, W=0x8

    Args:
        mlx_ptr: Pointer to MLX.
        win_ptr: Pointer to the window.
        x_start: Starting x coordinate.
        y_start: Starting y coordinate.
        x_end: Ending x coordinate.
        y_end: Ending y coordinate.
        hex_value: Hexadecimal value of the cell.
        wall_color: Wall color.
    """
    wall_bits = [
        ('N', 0b0001),
        ('E', 0b0010),
        ('S', 0b0100),
        ('W', 0b1000),
    ]

    for wall_type, bit_mask in wall_bits:
        if hex_value & bit_mask:
            draw_wall(mlx_ptr, win_ptr, x_start, y_start, x_end, y_end,
                      wall_type, wall_color)


def draw_closed_cell_fill(mlx_ptr: Any, win_ptr: Any, x_start: int,
                          y_start: int, x_end: int, y_end: int) -> None:
    """
    Draws the fill of a fully closed cell (part of the '42' pattern).

    Args:
        mlx_ptr: Pointer to MLX.
        win_ptr: Pointer to the window.
        x_start: Starting x coordinate.
        y_start: Starting y coordinate.
        x_end: Ending x coordinate.
        y_end: Ending y coordinate.
    """
    if mlx_instance is None:
        return

    color = get_current_logo_color()
    for x in range(x_start + 1, x_end - 1):
        for y in range(y_start + 1, y_end - 1):
            mlx_instance.mlx_pixel_put(mlx_ptr, win_ptr, x, y, color)


def draw_maze(maze_state: Dict[str, Any]) -> None:
    """
    Draws the maze in the existing window.

    Args:
        maze_state: Dictionary with the maze state.
    """
    if not MLX_AVAILABLE or mlx_instance is None:
        print("MLX no está disponible, no se puede visualizar.")
        return

    mlx_ptr = maze_state['mlx_ptr']
    win_ptr = maze_state['win_ptr']
    hex_lines = maze_state['hex_lines']
    width = maze_state['width']
    height = maze_state['height']
    entry_coords = maze_state['entry_coords']
    exit_coords = maze_state['exit_coords']
    path = maze_state['path']

    wall_color = get_current_wall_color()

    for i in range(height):
        line = hex_lines[i]

        for j in range(width):
            x_start = j * CELL_SIZE
            y_start = i * CELL_SIZE
            x_end = x_start + CELL_SIZE
            y_end = y_start + CELL_SIZE

            is_entry = (j + 1 == entry_coords[0] and i + 1 == entry_coords[1])
            is_exit = (j + 1 == exit_coords[0] and i + 1 == exit_coords[1])

            hex_char = line[j].upper()
            if hex_char not in '0123456789ABCDEF':
                continue

            hex_value = int(hex_char, 16)
            is_42_cell = (hex_value == 0b1111)

            bg_color = get_cell_background_color(
                j, i, is_entry, is_exit, show_path_state,
                entry_coords, path, width, height, is_42_cell
            )

            draw_cell_background(mlx_ptr, win_ptr, x_start, y_start,
                                 x_end, y_end, bg_color)

            draw_cell_walls(mlx_ptr, win_ptr, x_start, y_start, x_end,
                            y_end, hex_value, wall_color)

            if is_42_cell:
                draw_closed_cell_fill(mlx_ptr, win_ptr, x_start, y_start,
                                      x_end, y_end)


def create_window(width: int, height: int) -> Optional[Tuple[Any, Any]]:
    """
    Creates an MLX window.

    Args:
        width: Maze width in cells.
        height: Maze height in cells.

    Returns:
        Tuple (mlx_ptr, win_ptr) or None if an error occurs.
    """
    if not MLX_AVAILABLE or mlx_instance is None:
        return None

    screen_width = width * CELL_SIZE
    screen_height = height * CELL_SIZE

    try:
        mlx_ptr = mlx_instance.mlx_init()
        win_ptr = mlx_instance.mlx_new_window(
            mlx_ptr, screen_width, screen_height, "A-Maze-ing Visualizer"
        )
        return mlx_ptr, win_ptr
    except Exception as e:
        print(f"Error inicializando mlx: {e}")
        return None


def print_maze_info(maze_data: Dict[str, Any]) -> None:
    """
    Prints information about the loaded maze.

    Args:
        maze_data: Dictionary with maze data.
    """
    print(f"\nLaberinto cargado: {maze_data['width']}x{maze_data['height']}")
    print(f"Entrada: {maze_data['entry_coords']}")
    print(f"Salida: {maze_data['exit_coords']}")
    print(f"Longitud del camino: {len(maze_data['path'])} pasos")
    print("\nControles:")
    print("  Enter   : Mostrar/ocultar camino")
    print("  C       : Cambiar color de paredes")
    print("  L       : Cambiar color del logo 42")
    print("  Flechas : Mover la entrada")
    print("  1       : Generar nuevo laberinto")
    print("  ESC     : Salir")


def _find_path_from_hex(hex_lines: List[str], entry: Tuple[int, int],
                        exit_coords: Tuple[int, int]) -> str:
    """
    Finds the shortest path using BFS directly on hex_lines.

    Args:
        hex_lines: Hexadecimal lines of the maze.
        entry: Entry coordinates (1-based).
        exit_coords: Exit coordinates (1-based).

    Returns:
        String with path directions (NSEW) or "" if no path exists.
    """
    height = len(hex_lines)
    width = len(hex_lines[0]) if hex_lines else 0

    ex, ey = entry[0] - 1, entry[1] - 1
    fx, fy = exit_coords[0] - 1, exit_coords[1] - 1

    if not (0 <= ex < width and 0 <= ey < height):
        return ""
    if not (0 <= fx < width and 0 <= fy < height):
        return ""

    moves = [
        (-1,  0, 0x1, 0x4, 'N'),
        (1,  0, 0x4, 0x1, 'S'),
        (0,  1, 0x2, 0x8, 'E'),
        (0, -1, 0x8, 0x2, 'W'),
    ]

    visited = [[False] * width for _ in range(height)]
    prev: Dict[Tuple[int, int], Tuple[Tuple[int, int], str]] = {}
    queue: deque = deque([(ey, ex)])
    visited[ey][ex] = True

    while queue:
        y, x = queue.popleft()
        if y == fy and x == fx:
            break

        hex_char = hex_lines[y][x].upper()
        if hex_char not in '0123456789ABCDEF':
            continue
        cell_val = int(hex_char, 16)

        for dy, dx, bit_cur, bit_nbr, direction in moves:
            ny, nx = y + dy, x + dx
            if not (0 <= ny < height and 0 <= nx < width):
                continue
            if cell_val & bit_cur:
                continue
            nbr_char = hex_lines[ny][nx].upper()
            if nbr_char not in '0123456789ABCDEF':
                continue
            nbr_val = int(nbr_char, 16)
            if nbr_val & bit_nbr:
                continue
            if visited[ny][nx]:
                continue
            visited[ny][nx] = True
            prev[(ny, nx)] = ((y, x), direction)
            queue.append((ny, nx))

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


def move_entry(dx: int, dy: int) -> None:
    """
    Moves the entry point and recalculates the path.

    Args:
        dx: Displacement in x (-1, 0, 1).
        dy: Displacement in y (-1, 0, 1).
    """

    if not maze_state:
        return

    old_x, old_y = maze_state['entry_coords']
    new_x = old_x + dx
    new_y = old_y + dy

    if 1 <= new_x <= maze_state['width'] and 1 <= new_y \
       <= maze_state['height']:
        maze_state['entry_coords'] = (new_x, new_y)

        new_path = _find_path_from_hex(
            maze_state['hex_lines'],
            maze_state['entry_coords'],
            maze_state['exit_coords']
        )
        maze_state['path'] = new_path
        print(f"Entrada movida a {maze_state['entry_coords']} – "
              f"Camino: {len(new_path)} pasos")
        if mlx_instance is None:
            return
        mlx_instance.mlx_clear_window(maze_state['mlx_ptr'],
                                      maze_state['win_ptr'])
        draw_maze(maze_state)


def visualize_maze(maze_data: Dict[str, Any]) -> None:
    """
    Initializes the window and displays the maze.

    Args:
        maze_data: Dictionary with maze data.
    """
    global maze_state

    if not MLX_AVAILABLE:
        print("MLX no está disponible, no se puede visualizar.")
        return

    if (maze_state and
            maze_state.get('mlx_ptr') is not None and
            maze_state.get('win_ptr') is not None):
        mlx_ptr = maze_state['mlx_ptr']
        win_ptr = maze_state['win_ptr']
    else:
        window_result = create_window(maze_data['width'], maze_data['height'])
        if window_result is None:
            print("No se pudo crear la ventana. Saliendo.")
            sys.exit(1)
        mlx_ptr, win_ptr = window_result

    maze_state = {
        'mlx_ptr': mlx_ptr,
        'win_ptr': win_ptr,
        'hex_lines': maze_data['hex_lines'],
        'width': maze_data['width'],
        'height': maze_data['height'],
        'entry_coords': maze_data['entry_coords'],
        'exit_coords': maze_data['exit_coords'],
        'path': maze_data['path']
    }

    draw_maze(maze_state)

    print_maze_info(maze_data)

    if mlx_instance is None or win_ptr is None:
        print("Error: MLX no inicializado correctamente")
        return

    mlx_instance.mlx_key_hook(win_ptr, handle_key_event, maze_state)
    mlx_instance.mlx_hook(win_ptr, ON_DESTROY, 0, cleanup_window, None)

    try:
        mlx_instance.mlx_loop(mlx_ptr)
    except KeyboardInterrupt:
        print("\nVisualización interrumpida por el usuario.")
        cleanup_window(None)
    except Exception as e:
        print(f"Error en el loop de mlx: {e}")


def cleanup_window(params: Any = None) -> int:
    """
    Cleans up and destroys the MLX window.

    Args:
        params: Parameter required by mlx_hook (can be None).

    Returns:
        Always 0.
    """

    if not maze_state:
        return 0

    mlx_ptr = maze_state.get('mlx_ptr')
    win_ptr = maze_state.get('win_ptr')

    if mlx_instance and mlx_ptr and win_ptr:
        try:
            mlx_instance.mlx_destroy_window(mlx_ptr, win_ptr)
        except Exception as e:
            print(f"Error al limpiar ventana: {e}")

    os._exit(0)
    return 0


def handle_key_event(keynum: int, mystuff: Any) -> None:
    """
    Handles keyboard events.

    Args:
        keynum: Key code of the pressed key.
        mystuff: Additional data (unused).
    """
    global show_path_state

    if not maze_state:
        return

    mlx_ptr = maze_state['mlx_ptr']
    win_ptr = maze_state['win_ptr']

    if keynum == KEY_ESC:
        try:
            if mlx_instance and mlx_ptr and win_ptr:
                mlx_instance.mlx_destroy_window(mlx_ptr, win_ptr)
        except Exception as e:
            print(f"Error al cerrar ventana: {e}")
        os._exit(0)
    elif keynum == KEY_ENTER:
        show_path_state = not show_path_state
        print(f"Mostrar camino: {show_path_state}")
        if maze_state:
            if mlx_instance is None:
                return
            mlx_instance.mlx_clear_window(mlx_ptr, win_ptr)
            draw_maze(maze_state)
    elif keynum == KEY_C:
        cycle_wall_color()
        if maze_state:
            if mlx_instance is None:
                return
            mlx_instance.mlx_clear_window(mlx_ptr, win_ptr)
            draw_maze(maze_state)
    elif keynum == KEY_L:
        cycle_logo_color()
        if maze_state:
            if mlx_instance is None:
                return
            mlx_instance.mlx_clear_window(mlx_ptr, win_ptr)
            draw_maze(maze_state)
    elif keynum == KEY_1:
        if mlx_instance is None:
            return
        mlx_instance.mlx_clear_window(mlx_ptr, win_ptr)
        generate_maze()
        see_maze()
    elif keynum == KEY_UP:
        move_entry(0, -1)
    elif keynum == KEY_DOWN:
        move_entry(0, 1)
    elif keynum == KEY_LEFT:
        move_entry(-1, 0)
    elif keynum == KEY_RIGHT:
        move_entry(1, 0)


def generate_maze() -> None:
    """Generates a new maze based on the configuration."""
    try:
        config = parse_config(sys.argv[1])
        print("✓ Configuración parseada correctamente")

        print("Generando laberinto...")
        generator = MazeGenerator(
            width=config["WIDTH"],
            height=config["HEIGHT"],
            perfect=config["PERFECT"],
            seed=config.get("SEED")
        )

        generator.generate(config["ENTRY"], config["EXIT"])
        print(f"✓ Laberinto generado: {config['WIDTH']}x{config['HEIGHT']}")

        print("Buscando camino más corto...")
        path = generator.shortest_path(entry=config["ENTRY"],
                                       exit_=config["EXIT"])

        if path:
            print(f"Camino encontrado: {len(path)} pasos")
        else:
            print("No se encontró camino")

        write_output_file(
            config["OUTPUT_FILE"],
            generator,
            config["ENTRY"],
            config["EXIT"],
            path
        )
    except (ConfigError, FileNotFoundError, ValueError) as e:
        print(f"Error durante la generación: {e}")
        raise


def see_maze() -> None:
    """Loads and visualizes a maze from the output file."""
    try:
        config = parse_config(sys.argv[1])

        if not config or not config.get("OUTPUT_FILE"):
            raise ConfigError("Archivo de salida no especificado")

        hex_lines, width, height, entry_coords, exit_coords, path = \
            parse_maze_file(config["OUTPUT_FILE"])

        maze_data = {
            'hex_lines': hex_lines,
            'width': width,
            'height': height,
            'entry_coords': entry_coords,
            'exit_coords': exit_coords,
            'path': path
        }

        visualize_maze(maze_data)
    except Exception as e:
        print(f"Error al visualizar el laberinto: {e}")
        sys.exit(1)


def main() -> None:
    """Main function of the program."""
    if len(sys.argv) != 2:
        print("Uso: python3 a_maze_ing.py <archivo_configuracion>")
        sys.exit(1)

    try:
        generate_maze()
        see_maze()
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except ConfigError as e:
        print(f"Error de configuración: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error inesperado: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
