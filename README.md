# A-Maze-ing

<a id="top-es"></a>

*Este proyecto ha sido creado como parte del currículo de 42 por pmelo-cl y vhedo-ga.*

[English version](#top-en)

## Descripción

A-Maze-ing es un generador de laberintos aleatorios implementado en Python que utiliza el algoritmo de **Recursive Backtracking** para crear laberintos perfectos (con un único camino entre entrada y salida). El proyecto incluye:

- Generación de laberintos configurables mediante archivo de texto
- Visualización gráfica interactiva usando MiniLibX
- Búsqueda del camino más corto mediante BFS (Breadth-First Search)
- Exportación a formato hexadecimal
- Módulo reutilizable empaquetado como librería Python

El programa genera automáticamente un patrón '42' visible en el centro del laberinto como característica distintiva.

## Instrucciones

### Requisitos

- Python 3.10 o superior
- MiniLibX (para visualización gráfica)
- pip (gestor de paquetes de Python)

### Instalación

```bash
# Instalar dependencias
make venv
source venv/bin/activate
make install
```

### Ejecución

```bash
# Usando Makefile (recomendado)
make run CONFIG_FILE=config.txt

# O directamente con Python
python3 a_maze_ing.py config.txt
```

### Comandos del Makefile

```bash
make install      # Instalar dependencias
make run          # Ejecutar el programa
make debug        # Ejecutar en modo depuración
make clean        # Limpiar archivos temporales
make lint         # Verificar código con flake8 y mypy
make lint-strict  # Verificación estricta
make help         # Mostrar ayuda
```

## Formato del Archivo de Configuración

El archivo de configuración usa el formato `KEY=VALUE`. Ejemplo:

```
# config.txt
WIDTH=25
HEIGHT=20
ENTRY=1,8
EXIT=25,13
OUTPUT_FILE=maze_output.txt
PERFECT=True
SEED=42
```

### Claves Obligatorias

| Clave | Descripción | Ejemplo |
|-------|-------------|---------|
| `WIDTH` | Ancho del laberinto (número de celdas) | `WIDTH=25` |
| `HEIGHT` | Alto del laberinto | `HEIGHT=20` |
| `ENTRY` | Coordenadas de entrada (x,y) en base-1 | `ENTRY=1,8` |
| `EXIT` | Coordenadas de salida (x,y) en base-1 | `EXIT=25,13` |
| `OUTPUT_FILE` | Nombre del archivo de salida | `OUTPUT_FILE=maze.txt` |
| `PERFECT` | ¿Laberinto perfecto? (True/False) | `PERFECT=True` |

### Claves Opcionales

| Clave | Descripción | Ejemplo |
|-------|-------------|---------|
| `SEED` | Semilla para reproducibilidad | `SEED=42` |

### Controles Interactivos

Durante la visualización:

| Tecla | Acción |
|-------|--------|
| **Enter** | Mostrar/Ocultar el camino de solución |
| **C** | Cambiar color de las paredes (5 opciones) |
| **L** | Cambiar color del patrón '42' (6 opciones) |
| **↑ ↓ ← →** | Mover el punto de entrada por el laberinto |
| **1** | Generar un nuevo laberinto |
| **ESC** | Salir |

## Algoritmo de Generación

### Recursive Backtracking

El proyecto utiliza el algoritmo **Recursive Backtracking** (Retroceso Recursivo) para generar los laberintos.

#### ¿Cómo funciona?

1. **Inicialización**: Se crea una cuadrícula con todas las paredes cerradas
2. **Selección**: Se elige una celda aleatoria como punto de inicio
3. **Recursión**:
   - Marca la celda actual como visitada
   - Obtiene lista de vecinos no visitados
   - Si hay vecinos disponibles:
     - Elige uno al azar
     - Elimina la pared entre la celda actual y la elegida
     - Llama recursivamente sobre la celda elegida
   - Si no hay vecinos, retrocede (backtrack) a la celda anterior
4. **Patrón '42'**: Se añade en el centro con celdas completamente cerradas
5. **Finalización**: El proceso termina cuando todas las celdas visitables han sido procesadas

## Código Reutilizable

### Módulo `mazegen`

El código de generación está empaquetado como un módulo Python independiente que puede instalarse y reutilizarse en otros proyectos.

#### Instalación del Paquete

```bash
# Construir el paquete
python3 -m pip install -e .
```

#### Uso del Módulo

```python
from mazegen import MazeGenerator

# Crear generador
gen = MazeGenerator(width=20, height=15, seed=42)

# Generar laberinto
maze = gen.generate(entry=(1, 1), exit_=(20, 15))

# Obtener solución
path = gen.shortest_path(entry=(1, 1), exit_=(20, 15))
print(f"Camino: {path}, Pasos: {len(path)}")

# Acceder a la estructura
structure = gen.get_maze_structure()
cell = structure[5][10]  # Celda en fila 5, columna 10
print(f"Paredes: N={cell.n}, S={cell.s}, E={cell.e}, W={cell.w}")

# Exportar a hexadecimal
hex_matrix = gen.to_hex_matrix()
```

## Recursos

### Documentación Oficial

- [Python Documentation](https://docs.python.org/3/)
- [MiniLibX Guide](https://harm-smits.github.io/42docs/libs/minilibx)
- [Type Hints (PEP 484)](https://peps.python.org/pep-0484/)
- [Docstrings (PEP 257)](https://peps.python.org/pep-0257/)

### Algoritmos de Laberintos

- [Maze Generation Algorithms](https://en.wikipedia.org/wiki/Maze_generation_algorithm)
- [Recursive Backtracking](https://weblog.jamisbuck.org/2010/12/27/maze-generation-recursive-backtracking)
- [Breadth-First Search](https://en.wikipedia.org/wiki/Breadth-first_search)

### Artículos y Tutoriales

- [Think Labyrinth: Maze Algorithms](http://www.astrolog.org/labyrnth/algrithm.htm)
- [Buckblog: Maze Generation](https://weblog.jamisbuck.org/2011/2/7/maze-generation-algorithm-recap)

### Uso de IA en el Proyecto

La IA fue utilizada para:

1. **Revisión de código**: Sugerencias de mejoras y detección de bugs
2. **Generación de docstrings**: Plantillas iniciales de documentación (luego revisadas y adaptadas)
3. **Depuración**: Ayuda para entender errores complejos de tipos en mypy
4. **Optimización**: Sugerencias para mejorar eficiencia del BFS

## Formato del Archivo de Salida

El laberinto se guarda en formato hexadecimal:

```
913D15539153939553D515513
AAC38396EABAAAC3D453C57AA
...
1,8
25,13
WSSEENNEEEESW
```

- **Líneas 1-N**: Representación hexadecimal (un dígito por celda)
- **Línea N+1**: Vacía
- **Línea N+2**: Coordenadas de entrada (x,y)
- **Línea N+3**: Coordenadas de salida (x,y)
- **Línea N+4**: Camino de solución (N/S/E/W)

### Codificación Hexadecimal

Cada dígito codifica qué paredes están **cerradas**:

| Bit | Posición | Pared |
|-----|----------|-------|
| 0 (LSB) | 1 | Norte |
| 1 | 2 | Este |
| 2 | 4 | Sur |
| 3 | 8 | Oeste |

Ejemplo: `A` = 1010₂ = Paredes Este y Oeste cerradas.

---

---

# A-Maze-ing

<a id="top-en"></a>

*This project was created as part of the 42 curriculum by pmelo-cl and vhedo-ga.*

[Versión en español](#top-es)

## Description

A-Maze-ing is a random maze generator implemented in Python that uses the **Recursive Backtracking** algorithm to create perfect mazes (with a single path between entry and exit). The project includes:

- Configurable maze generation via text file
- Interactive graphical visualization using MiniLibX
- Shortest path search using BFS (Breadth-First Search)
- Export to hexadecimal format
- Reusable module packaged as a Python library

The program automatically generates a '42' pattern visible at the center of the maze as a distinctive feature.

## Instructions

### Requirements

- Python 3.10 or higher
- MiniLibX (for graphical visualization)
- pip (Python package manager)

### Installation

```bash
# Install dependencies
make venv
source venv/bin/activate
make install
```

### Running

```bash
# Using Makefile (recommended)
make run CONFIG_FILE=config.txt

# Or directly with Python
python3 a_maze_ing.py config.txt
```

### Makefile Commands

```bash
make install      # Install dependencies
make run          # Run the program
make debug        # Run in debug mode
make clean        # Clean temporary files
make lint         # Check code with flake8 and mypy
make lint-strict  # Strict verification
make help         # Show help
```

## Configuration File Format

The configuration file uses the `KEY=VALUE` format. Example:

```
# config.txt
WIDTH=25
HEIGHT=20
ENTRY=1,8
EXIT=25,13
OUTPUT_FILE=maze_output.txt
PERFECT=True
SEED=42
```

### Required Keys

| Key | Description | Example |
|-----|-------------|---------|
| `WIDTH` | Maze width (number of cells) | `WIDTH=25` |
| `HEIGHT` | Maze height | `HEIGHT=20` |
| `ENTRY` | Entry coordinates (x,y) in 1-based index | `ENTRY=1,8` |
| `EXIT` | Exit coordinates (x,y) in 1-based index | `EXIT=25,13` |
| `OUTPUT_FILE` | Output file name | `OUTPUT_FILE=maze.txt` |
| `PERFECT` | Perfect maze? (True/False) | `PERFECT=True` |

### Optional Keys

| Key | Description | Example |
|-----|-------------|---------|
| `SEED` | Seed for reproducibility | `SEED=42` |

### Interactive Controls

During visualization:

| Key | Action |
|-----|--------|
| **Enter** | Show/Hide the solution path |
| **C** | Cycle wall color (5 options) |
| **L** | Cycle '42' pattern color (6 options) |
| **↑ ↓ ← →** | Move the entry point across the maze |
| **1** | Generate a new maze |
| **ESC** | Quit |

## Generation Algorithm

### Recursive Backtracking

The project uses the **Recursive Backtracking** algorithm to generate mazes.

#### How does it work?

1. **Initialization**: A grid is created with all walls closed
2. **Selection**: A random cell is chosen as the starting point
3. **Recursion**:
   - Marks the current cell as visited
   - Gets a list of unvisited neighbors
   - If neighbors are available:
     - Picks one at random
     - Removes the wall between the current cell and the chosen one
     - Recursively calls itself on the chosen cell
   - If no neighbors remain, backtracks to the previous cell
4. **'42' Pattern**: Added at the center with fully closed cells
5. **Completion**: The process ends when all visitable cells have been processed

## Reusable Code

### `mazegen` Module

The generation code is packaged as a standalone Python module that can be installed and reused in other projects.

#### Package Installation

```bash
# Build the package
python3 -m pip install -e .
```

#### Module Usage

```python
from mazegen import MazeGenerator

# Create generator
gen = MazeGenerator(width=20, height=15, seed=42)

# Generate maze
maze = gen.generate(entry=(1, 1), exit_=(20, 15))

# Get solution
path = gen.shortest_path(entry=(1, 1), exit_=(20, 15))
print(f"Path: {path}, Steps: {len(path)}")

# Access structure
structure = gen.get_maze_structure()
cell = structure[5][10]  # Cell at row 5, column 10
print(f"Walls: N={cell.n}, S={cell.s}, E={cell.e}, W={cell.w}")

# Export to hexadecimal
hex_matrix = gen.to_hex_matrix()
```

## Resources

### Official Documentation

- [Python Documentation](https://docs.python.org/3/)
- [MiniLibX Guide](https://harm-smits.github.io/42docs/libs/minilibx)
- [Type Hints (PEP 484)](https://peps.python.org/pep-0484/)
- [Docstrings (PEP 257)](https://peps.python.org/pep-0257/)

### Maze Algorithms

- [Maze Generation Algorithms](https://en.wikipedia.org/wiki/Maze_generation_algorithm)
- [Recursive Backtracking](https://weblog.jamisbuck.org/2010/12/27/maze-generation-recursive-backtracking)
- [Breadth-First Search](https://en.wikipedia.org/wiki/Breadth-first_search)

### Articles and Tutorials

- [Think Labyrinth: Maze Algorithms](http://www.astrolog.org/labyrnth/algrithm.htm)
- [Buckblog: Maze Generation](https://weblog.jamisbuck.org/2011/2/7/maze-generation-algorithm-recap)

### AI Usage in the Project

AI was used for:

1. **Code review**: Improvement suggestions and bug detection
2. **Docstring generation**: Initial documentation templates (later reviewed and adapted)
3. **Debugging**: Help understanding complex mypy type errors
4. **Optimization**: Suggestions to improve BFS efficiency

## Output File Format

The maze is saved in hexadecimal format:

```
913D15539153939553D515513
AAC38396EABAAAC3D453C57AA
...
1,8
25,13
WSSEENNEEEESW
```

- **Lines 1-N**: Hexadecimal representation (one digit per cell)
- **Line N+1**: Empty
- **Line N+2**: Entry coordinates (x,y)
- **Line N+3**: Exit coordinates (x,y)
- **Line N+4**: Solution path (N/S/E/W)

### Hexadecimal Encoding

Each digit encodes which walls are **closed**:

| Bit | Position | Wall |
|-----|----------|------|
| 0 (LSB) | 1 | North |
| 1 | 2 | East |
| 2 | 4 | South |
| 3 | 8 | West |

Example: `A` = 1010₂ = East and West walls closed.