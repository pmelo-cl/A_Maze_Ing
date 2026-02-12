# A-Maze-Ing

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

- **Enter**: Mostrar/Ocultar el camino de solución
- **C**: Cambiar color de las paredes
- **1**: Generar un nuevo laberinto
- **ESC**: Salir

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
#### Regeneración del paquete
```bash
cd mazegen
python3 -m buid
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
