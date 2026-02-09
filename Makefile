PYTHON = python3
MAIN_SCRIPT = a_maze_ing.py
CONFIG_FILE = config.txt
PACKAGE_DIR = mazegen
PACKAGE_NAME = mazegen
MINILIBX_DIR = mlx_CLXV
MINILIBX_PYTHON_DIR = mlx_CLXV/python


help:
	@echo "A-Maze-ing - Makefile$"
	@echo ""
	@echo "Comandos disponibles:"
	@echo "  make venv         - Crear un entorno virtual"
	@echo "  make install      - Instalar dependencias del proyecto"
	@echo "  make install-mlx-python - Instalar minilibx para Python"
	@echo "  make run          - Ejecutar el script principal"
	@echo "  make debug        - Ejecutar en modo depuración"
	@echo "  make clean        - Eliminar archivos temporales"
	@echo "  make lint         - Ejecutar flake8 y mypy"
	@echo "  make lint-strict  - Ejecutar flake8 y mypy con --strict"
	@echo "  make help         - Mostrar esta ayuda"

venv:
	@echo "creando entorno virtual..."
	@$(PYTHON) -m venv venv

install:
	@echo "Instalando dependencias..."
	@$(PYTHON) -m pip install --upgrade pip
	@$(PYTHON) -m pip install flake8 mypy build
	@echo "Dependencias instaladas"
	@if [ -f "$(PACKAGE_DIR)/pyproject.toml" ]; then \
		cd $(PACKAGE_DIR) && $(PYTHON) -m pip install -e .; \
	elif [ -f "pyproject.toml" ]; then \
		$(PYTHON) -m pip install -e .; \
	else \
		echo "Error: No se encontró pyproject.toml"; \
		exit 1; \
	fi
	@echo "Paquete mazegen instalado en modo editable"
	@if [ -d "$(MINILIBX_DIR)" ]; then \
		echo "Compilando minilibx..."; \
		cd $(MINILIBX_DIR) && make; \
	else \
		echo "Advertencia: No se encontró el directorio $(MINILIBX_DIR). Asegúrate de que esté presente para la visualización."; \
	fi

install-mlx-python:
	@echo "Instalando minilibx para Python..."
	@if [ -d "$(MINILIBX_PYTHON_DIR)" ]; then \
		cd $(MINILIBX_PYTHON_DIR) && $(PYTHON) -m pip install .; \
	else \
		echo "Advertencia: No se encontró el directorio $(MINILIBX_PYTHON_DIR). Asegúrate de que esté presente para la visualización."; \
	fi

run:
	@echo "Ejecutando $(MAIN_SCRIPT)..."
	@if [ ! -f $(CONFIG_FILE) ]; then \
		echo "Advertencia: $(CONFIG_FILE) no encontrado"; \
		echo "Uso: make run CONFIG_FILE=tu_config.txt"; \
	else \
		$(PYTHON) $(MAIN_SCRIPT) $(CONFIG_FILE); \
	fi

debug:
	@echo "Ejecutando en modo depuración..."
	@if [ ! -f $(CONFIG_FILE) ]; then \
		echo "Advertencia: $(CONFIG_FILE) no encontrado"; \
		echo "Uso: make debug CONFIG_FILE=tu_config.txt"; \
	else \
		$(PYTHON) -m pdb $(MAIN_SCRIPT) $(CONFIG_FILE); \
	fi

clean:
	@echo "Limpiando archivos temporales..."
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@find . -type f -name "*.pyo" -delete 2>/dev/null || true
	@find . -type f -name "*.pyd" -delete 2>/dev/null || true
	@find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name "dist" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name "build" -exec rm -rf {} + 2>/dev/null || true
	@cd $(MINILIBX_DIR) && make clean 2>/dev/null || true
	@rm -rf venv 2>/dev/null || true
	@echo "Archivos temporales eliminados"

lint:
	@echo "Ejecutando flake8..."
	@$(PYTHON) -m flake8 . --exclude venv,build,*.egg-info,mlx_CLXV || echo "flake8 encontró problemas"
	@echo ""
	@echo "Ejecutando mypy..."
	@$(PYTHON) -m mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs --exclude venv,build,*.egg-info,mlx_CLXV || echo "mypy encontró problemas"
	@echo "Lint completado"

lint-strict:
	@echo "Ejecutando flake8..."
	@$(PYTHON) -m flake8 . --exclude venv,build,*.egg-info,mlx_CLXV || echo "flake8 encontró problemas"
	@echo ""
	@echo "Ejecutando mypy --strict..."
	@$(PYTHON) -m mypy . --strict || echo "mypy strict encontró problemas"
	@echo "Lint strict completado"

.PHONY: venv install install-mlx-python run debug clean lint lint-strict help