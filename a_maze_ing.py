# a_maze_ing.py
"""
Generador de laberintos con visualización interactiva.

Este módulo implementa un generador de laberintos aleatorios usando
el algoritmo de backtracking recursivo, con capacidad de visualización
gráfica usando MiniLibX.
"""

# ============================================
# IMPORTS
# ============================================
import sys
import re
from typing import Dict, Any, List, Optional, Tuple

try:
    from mlx import Mlx
    MLX_AVAILABLE = True
except ImportError:
    MLX_AVAILABLE = False
    print("Advertencia: No se pudo importar mlx. La visualización no estará disponible.")

try:
    from mazegen.MazeGenerator import MazeGenerator
except ImportError:
    print("Advertencia: mazegen no instalado. Usando versión embebida.")

# ============================================
# CONSTANTES GLOBALES
# ============================================
CELL_SIZE = 20

# Colores por defecto
DEFAULT_WALL_COLOR = 0xFFFFFFFF
DEFAULT_BG_COLOR = 0xFF000000
DEFAULT_ENTRY_COLOR = 0xFFFF0000  # Rojo
DEFAULT_EXIT_COLOR = 0xFF00FF00   # Verde
DEFAULT_PATH_COLOR = 0xFF0000FF   # Azul
DEFAULT_CLOSED_CELL_COLOR = 0xAAFFFFFF
DEFAULT_PATTERN_42_COLOR = 0xFFFFFF00  # Amarillo

# Colores alternativos
ALT_WALL_COLORS = [
    0xFFFFFFFF,  # Blanco
    0xFFFF00FF,  # Magenta
    0xFF00FFFF,  # Cian
    0xFFFFFF00,  # Amarillo
    0xFFFF8800,  # Naranja
]

# Teclas
KEY_ESC = 65307
KEY_ENTER = 65293
KEY_1 = 49
KEY_C = 99  # Para cambiar colores

# ============================================
# VARIABLES GLOBALES DE ESTADO
# ============================================
show_path_state = False
maze_state: Optional[Dict[str, Any]] = None
mlx_instance: Optional[Any] = None
current_wall_color_index = 0

if MLX_AVAILABLE:
    mlx_instance = Mlx()


# ============================================
# EXCEPCIONES PERSONALIZADAS
# ============================================
class ConfigError(Exception):
    """Excepción personalizada para errores de configuración."""

    pass

# ============================================
# UTILIDADES DE ARCHIVO
# ============================================
def read_file_lines(filepath: str) -> List[str]:
    """
    Lee un archivo y devuelve sus líneas sin espacios en blanco.

    Args:
        filepath: Ruta al archivo.

    Returns:
        Lista de líneas sin espacios en blanco.

    Raises:
        FileNotFoundError: Si el archivo no existe.
        IOError: Si hay error de lectura.
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
    Escribe contenido en un archivo.

    Args:
        filepath: Ruta al archivo.
        content: Contenido a escribir.

    Raises:
        IOError: Si hay error de escritura.
    """
    try:
        with open(filepath, 'w', encoding='utf-8') as file:
            file.write(content)
    except IOError as e:
        raise IOError(f"Error al escribir el archivo: {e}")


# ============================================
# PARSER DE CONFIGURACIÓN
# ============================================
def parse_coordinate(coord_str: str) -> Tuple[int, int]:
    """
    Parsea una cadena de coordenadas 'x,y' a una tupla (x, y).

    Args:
        coord_str: Cadena con formato "x,y".

    Returns:
        Tupla con las coordenadas (x, y).

    Raises:
        ValueError: Si el formato es inválido.
    """
    parts = coord_str.split(',')
    if len(parts) != 2:
        raise ValueError(f"Formato de coordenadas inválido: {coord_str}")
    return (int(parts[0]), int(parts[1]))


def parse_boolean(bool_str: str) -> bool:
    """
    Parsea una cadena a booleano.

    Args:
        bool_str: Cadena con "true" o "false" (case-insensitive).

    Returns:
        Valor booleano correspondiente.
    """
    return bool_str.lower() == "true"


def validate_coordinates(entry: Tuple[int, int], exit_: Tuple[int, int]) -> None:
    """
    Valida que las coordenadas sean correctas.

    Args:
        entry: Coordenadas de entrada.
        exit_: Coordenadas de salida.

    Raises:
        ConfigError: Si las coordenadas son inválidas.
    """
    if not isinstance(entry, tuple) or len(entry) != 2:
        raise ConfigError("ENTRY debe ser una tupla de dos enteros (x, y)")
    if not isinstance(exit_, tuple) or len(exit_) != 2:
        raise ConfigError("EXIT debe ser una tupla de dos enteros (x, y)")
    if entry == exit_:
        raise ConfigError("ENTRY y EXIT deben ser diferentes")


def parse_config(config_path: str) -> Dict[str, Any]:
    """
    Parsea el archivo de configuración y devuelve un diccionario con los valores.

    Args:
        config_path: Ruta al archivo de configuración.

    Returns:
        Diccionario con las claves y valores parseados.

    Raises:
        ConfigError: Si hay algún error en el formato, valores faltantes o inválidos.
        FileNotFoundError: Si el archivo no existe.
    """
    # Claves obligatorias y sus tipos (conversor)
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
        # Ignorar comentarios
        if line.startswith('#'):
            continue

        # Separar clave y valor (solo primer '=')
        if '=' not in line:
            raise ConfigError(
                f"Línea {line_num}: Formato inválido, se esperaba 'KEY=VALUE'"
            )

        key, value = line.split('=', 1)
        config[key.strip()] = value.strip()

    # Validar claves obligatorias
    missing_keys = [key for key in REQUIRED_KEYS if key not in config]
    if missing_keys:
        raise ConfigError(
            f"Claves obligatorias faltantes: {missing_keys}"
        )

    # Convertir valores a los tipos esperados
    for key, converter in REQUIRED_KEYS.items():
        try:
            config[key] = converter(config[key])
        except (ValueError, TypeError) as e:
            raise ConfigError(
                f"Error al convertir '{key}': {config[key]} - {e}"
            )

    # Validaciones adicionales
    validate_coordinates(config["ENTRY"], config["EXIT"])

    if config["WIDTH"] <= 0 or config["HEIGHT"] <= 0:
        raise ConfigError("WIDTH y HEIGHT deben ser mayores a 0")

    return config

# ============================================
# ARCHIVO DE SALIDA
# ============================================
def write_output_file(filename: str, maze: MazeGenerator,
                     entry: Tuple[int, int], exit_: Tuple[int, int],
                     path: str) -> None:
    """
    Escribe el laberinto en el archivo de salida en formato especificado.

    Args:
        filename: Nombre del archivo de salida.
        maze: Generador de laberinto con el maze generado.
        entry: Coordenadas de entrada.
        exit_: Coordenadas de salida.
        path: Camino de solución como string de direcciones.
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


# ============================================
# PARSER DE ARCHIVO DE LABERINTO
# ============================================
def parse_maze_coordinate(line: str,
                         default: Tuple[int, int]) -> Tuple[int, int]:
    """
    Parsea una línea de coordenadas del archivo de laberinto.

    Args:
        line: Línea con formato "x,y".
        default: Coordenadas por defecto si el parsing falla.

    Returns:
        Tupla con las coordenadas parseadas o las por defecto.
    """
    try:
        parts = line.replace(' ', '').split(',')
        return (int(parts[0]), int(parts[1]))
    except (ValueError, IndexError):
        print(f"Advertencia: Formato inválido: {line}. Usando {default}")
        return default


def normalize_hex_line(line: str, width: int) -> str:
    """
    Normaliza una línea hexadecimal al ancho especificado.

    Args:
        line: Línea hexadecimal a normalizar.
        width: Ancho deseado.

    Returns:
        Línea normalizada.
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
    Parsea un archivo de laberinto y devuelve sus componentes.

    Args:
        file_path: Ruta al archivo de laberinto.

    Returns:
        Tupla con (hex_lines, width, height, entry, exit, path).

    Raises:
        ValueError: Si el archivo está vacío o no tiene líneas hexadecimales.
    """
    lines = read_file_lines(file_path)

    if not lines:
        raise ValueError("El archivo está vacío")

    hex_lines = []
    entry_line = None
    exit_line = None
    path_line = None

    # Clasificar líneas
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
        raise ValueError("No se encontraron líneas hexadecimales en el archivo")

    # Dimensiones
    width = len(hex_lines[0])
    height = len(hex_lines)

    # Normalizar líneas hexadecimales
    hex_lines = [normalize_hex_line(line, width) for line in hex_lines]

    # Parsear coordenadas
    entry = (parse_maze_coordinate(entry_line, (1, 1))
             if entry_line else (1, 1))
    exit_coords = (parse_maze_coordinate(exit_line, (width, height))
                   if exit_line else (width, height))

    # Extraer camino
    path = (''.join(c.upper() for c in path_line if c.upper() in 'NSEW')
            if path_line else "")

    return hex_lines, width, height, entry, exit_coords, path


# ============================================
# VISUALIZACIÓN
# ============================================
def get_current_wall_color() -> int:
    """
    Obtiene el color actual de las paredes.

    Returns:
        Color hexadecimal de las paredes.
    """
    global current_wall_color_index
    return ALT_WALL_COLORS[current_wall_color_index % len(ALT_WALL_COLORS)]


def cycle_wall_color() -> None:
    """Cambia al siguiente color de pared disponible."""
    global current_wall_color_index
    current_wall_color_index = (current_wall_color_index + 1) % len(ALT_WALL_COLORS)
    print(f"Color de pared cambiado (#{current_wall_color_index + 1}/{len(ALT_WALL_COLORS)})")


def is_cell_in_path(x: int, y: int, entry_coords: Tuple[int, int],
                   path: str, maze_width: int, maze_height: int) -> bool:
    """
    Verifica si una celda está en el camino de solución.

    Args:
        x: Coordenada x de la celda (base-0).
        y: Coordenada y de la celda (base-0).
        entry_coords: Coordenadas de entrada (base-1).
        path: String con el camino de solución.
        maze_width: Ancho del laberinto.
        maze_height: Alto del laberinto.

    Returns:
        True si la celda está en el camino.
    """
    # Convertir a base-0
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
    Determina el color de fondo de una celda.

    Args:
        j: Coordenada x de la celda.
        i: Coordenada y de la celda.
        is_entry: Si es la celda de entrada.
        is_exit: Si es la celda de salida.
        show_path: Si se debe mostrar el camino.
        entry_coords: Coordenadas de entrada.
        path: String con el camino de solución.
        width: Ancho del laberinto.
        height: Alto del laberinto.
        is_42: Si la celda es parte del patrón '42'.

    Returns:
        Color hexadecimal para el fondo de la celda.
    """
    if is_entry:
        return DEFAULT_ENTRY_COLOR
    elif is_exit:
        return DEFAULT_EXIT_COLOR
    elif is_42:
        return DEFAULT_PATTERN_42_COLOR
    elif show_path and is_cell_in_path(j, i, entry_coords, path, width, height):
        return DEFAULT_PATH_COLOR
    else:
        return DEFAULT_BG_COLOR


def draw_cell_background(mlx_ptr: Any, win_ptr: Any, x_start: int,
                        y_start: int, x_end: int, y_end: int,
                        color: int) -> None:
    """
    Dibuja el fondo de una celda.

    Args:
        mlx_ptr: Puntero a MLX.
        win_ptr: Puntero a la ventana.
        x_start: Coordenada x inicial.
        y_start: Coordenada y inicial.
        x_end: Coordenada x final.
        y_end: Coordenada y final.
        color: Color del fondo.
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
    Dibuja una pared de la celda.

    Args:
        mlx_ptr: Puntero a MLX.
        win_ptr: Puntero a la ventana.
        x_start: Coordenada x inicial.
        y_start: Coordenada y inicial.
        x_end: Coordenada x final.
        y_end: Coordenada y final.
        wall_type: Tipo de pared ('N', 'S', 'E', 'W').
        wall_color: Color de la pared.
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
    Dibuja las paredes de una celda basándose en su valor hexadecimal.

    Args:
        mlx_ptr: Puntero a MLX.
        win_ptr: Puntero a la ventana.
        x_start: Coordenada x inicial.
        y_start: Coordenada y inicial.
        x_end: Coordenada x final.
        y_end: Coordenada y final.
        hex_value: Valor hexadecimal de la celda.
        wall_color: Color de las paredes.
    """
    wall_bits = [
        ('W', 0b1000),
        ('S', 0b0100),
        ('E', 0b0010),
        ('N', 0b0001)
    ]

    for wall_type, bit_mask in wall_bits:
        if hex_value & bit_mask:
            draw_wall(mlx_ptr, win_ptr, x_start, y_start, x_end, y_end,
                     wall_type, wall_color)


def draw_closed_cell_fill(mlx_ptr: Any, win_ptr: Any, x_start: int,
                         y_start: int, x_end: int, y_end: int) -> None:
    """
    Dibuja el relleno de una celda completamente cerrada (patrón '42').

    Args:
        mlx_ptr: Puntero a MLX.
        win_ptr: Puntero a la ventana.
        x_start: Coordenada x inicial.
        y_start: Coordenada y inicial.
        x_end: Coordenada x final.
        y_end: Coordenada y final.
    """
    if mlx_instance is None:
        return

    for x in range(x_start + 1, x_end - 1):
        for y in range(y_start + 1, y_end - 1):
            mlx_instance.mlx_pixel_put(mlx_ptr, win_ptr, x, y,
                                      DEFAULT_CLOSED_CELL_COLOR)


def draw_maze(maze_state: Dict[str, Any]) -> None:
    """
    Dibuja el laberinto en la ventana existente.

    Args:
        maze_state: Diccionario con el estado del laberinto.
    """
    global show_path_state

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

    mlx_instance.mlx_clear_window(mlx_ptr, win_ptr)

    # Dibujar el laberinto
    for i in range(height):
        line = hex_lines[i]

        for j in range(width):
            x_start = j * CELL_SIZE
            y_start = i * CELL_SIZE
            x_end = x_start + CELL_SIZE
            y_end = y_start + CELL_SIZE

            is_entry = (j + 1 == entry_coords[0] and i + 1 == entry_coords[1])
            is_exit = (j + 1 == exit_coords[0] and i + 1 == exit_coords[1])

            # Obtener valor hexadecimal
            hex_char = line[j].upper()
            if hex_char not in '0123456789ABCDEF':
                continue

            hex_value = int(hex_char, 16)
            is_42_cell = (hex_value == 0b1111)

            # Color de fondo
            bg_color = get_cell_background_color(
                j, i, is_entry, is_exit, show_path_state,
                entry_coords, path, width, height, is_42_cell
            )

            # Dibujar fondo
            draw_cell_background(mlx_ptr, win_ptr, x_start, y_start,
                               x_end, y_end, bg_color)

            # Dibujar paredes
            draw_cell_walls(mlx_ptr, win_ptr, x_start, y_start, x_end,
                          y_end, hex_value, wall_color)

            # Celdas completamente cerradas (patrón '42')
            if is_42_cell:
                draw_closed_cell_fill(mlx_ptr, win_ptr, x_start, y_start,
                                    x_end, y_end)


def create_window(width: int, height: int) -> Optional[Tuple[Any, Any]]:
    """
    Crea una ventana MLX.

    Args:
        width: Ancho del laberinto en celdas.
        height: Alto del laberinto en celdas.

    Returns:
        Tupla (mlx_ptr, win_ptr) o None si hay error.
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
    Imprime información sobre el laberinto cargado.

    Args:
        maze_data: Diccionario con datos del laberinto.
    """
    print(f"\nLaberinto cargado: {maze_data['width']}x{maze_data['height']}")
    print(f"Entrada: {maze_data['entry_coords']}")
    print(f"Salida: {maze_data['exit_coords']}")
    print(f"Longitud del camino: {len(maze_data['path'])} pasos")
    print("\nControles:")
    print("  Enter: Mostrar/ocultar camino")
    print("  C: Cambiar color de paredes")
    print("  1: Generar nuevo laberinto")
    print("  ESC: Salir")


def visualize_maze(maze_data: Dict[str, Any]) -> None:
    """
    Inicializa la ventana y muestra el laberinto.

    Args:
        maze_data: Diccionario con datos del laberinto.
    """
    global show_path_state, maze_state

    if not MLX_AVAILABLE:
        print("MLX no está disponible, no se puede visualizar.")
        return

    # Crear o reutilizar ventana
    if maze_state and maze_state.get('mlx_ptr') and maze_state.get('win_ptr'):
        mlx_ptr = maze_state['mlx_ptr']
        win_ptr = maze_state['win_ptr']
    else:
        window_result = create_window(maze_data['width'], maze_data['height'])
        if window_result is None:
            print("No se pudo crear la ventana. Saliendo.")
            sys.exit(1)
        mlx_ptr, win_ptr = window_result

    # Actualizar estado global
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

    # Dibujar laberinto
    draw_maze(maze_state)

    # Mostrar información
    print_maze_info(maze_data)

    # Configurar hooks
    mlx_instance.mlx_key_hook(win_ptr, handle_key_event, maze_state)

    # Loop principal
    try:
        mlx_instance.mlx_loop(mlx_ptr)
    except KeyboardInterrupt:
        print("\nVisualización interrumpida por el usuario.")
        cleanup_window()
    except Exception as e:
        print(f"Error en el loop de mlx: {e}")


# ============================================
# MANEJADORES DE EVENTOS
# ============================================
def cleanup_window() -> None:
    """Limpia y destruye la ventana MLX."""
    global maze_state

    if (MLX_AVAILABLE and maze_state and maze_state.get('mlx_ptr') and
            maze_state.get('win_ptr')):
        mlx_instance.mlx_destroy_window(maze_state['mlx_ptr'],
                                       maze_state['win_ptr'])
        maze_state['mlx_ptr'] = None
        maze_state['win_ptr'] = None
        print("Ventana limpiada y destruida.")


def handle_key_event(keynum: int, mystuff: Any) -> None:
    """
    Maneja eventos de teclado.

    Args:
        keynum: Código de la tecla presionada.
        mystuff: Datos adicionales (no usado).
    """
    global show_path_state, maze_state

    if keynum == KEY_ESC:
        cleanup_window()
        sys.exit(0)
    elif keynum == KEY_ENTER:
        # Alternar visualización del camino
        cleanup_window()
        show_path_state = not show_path_state
        print(f"Mostrar camino: {show_path_state}")
        if maze_state:
            see_maze()
    elif keynum == KEY_C:
        # Cambiar color de paredes
        cycle_wall_color()
        if maze_state:
            cleanup_window()
            see_maze()
    elif keynum == KEY_1:
        # Generar nuevo laberinto
        cleanup_window()
        if maze_state:
            maze_state['mlx_ptr'] = None
            maze_state['win_ptr'] = None
        generate_maze()
        see_maze()


# ============================================
# FUNCIONES PRINCIPALES
# ============================================
def generate_maze() -> None:
    """Genera un nuevo laberinto basado en la configuración."""
    try:
        config = parse_config(sys.argv[1])
        print("✓ Configuración parseada correctamente")

        # Crear y generar laberinto
        print("Generando laberinto...")
        generator = MazeGenerator(
            width=config["WIDTH"],
            height=config["HEIGHT"],
            perfect=config["PERFECT"],
            seed=config.get("SEED")
        )

        generator.generate(config["ENTRY"], config["EXIT"])
        print(f"✓ Laberinto generado: {config['WIDTH']}x{config['HEIGHT']}")

        # Encontrar camino más corto
        print("Buscando camino más corto...")
        path = generator.shortest_path(entry=config["ENTRY"],
                                       exit_=config["EXIT"])

        if path:
            print(f"✓ Camino encontrado: {len(path)} pasos")
        else:
            print("⚠ No se encontró camino")

        # Escribir archivo de salida
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
    """Carga y visualiza un laberinto desde el archivo de salida."""
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
        import traceback
        traceback.print_exc()
        sys.exit(1)


def main() -> None:
    """Función principal del programa."""
    if len(sys.argv) != 2:
        print("Uso: python3 a_maze_ing.py <archivo_configuracion>")
        sys.exit(1)

    try:
        generate_maze()
        see_maze()
    except FileNotFoundError as e:
        print(f"✗ Error: {e}", file=sys.stderr)
        sys.exit(1)
    except ConfigError as e:
        print(f"✗ Error de configuración: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"✗ Error inesperado: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


# ============================================
# PUNTO DE ENTRADA
# ============================================
if __name__ == "__main__":
    main()