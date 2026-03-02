# mazegen

<a id="top-es"></a>

*Módulo Python independiente extraído del proyecto A-Maze-ing, creado como parte del currículo de 42 por pmelo-cl y vhedo-ga.*

[English version](#top-en)

## Descripción

`mazegen` es el módulo de generación de laberintos de A-Maze-ing, empaquetado como librería Python independiente para que pueda instalarse y reutilizarse en otros proyectos.

## Instalación del Paquete

```bash
# Construir el paquete
python3 -m pip install -e .
```

## Uso del Módulo

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

---

---

# mazegen

<a id="top-en"></a>

*Standalone Python module extracted from the A-Maze-ing project, created as part of the 42 curriculum by pmelo-cl and vhedo-ga.*

[Versión en español](#top-es)

## Description

`mazegen` is the maze generation module from A-Maze-ing, packaged as a standalone Python library so it can be installed and reused in other projects.

## Package Installation

```bash
# Build the package
python3 -m pip install -e .
```

## Module Usage

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