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