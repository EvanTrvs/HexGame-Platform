# Détection de Python
PYTHON_CMD = python3
ifeq ($(OS),Windows_NT)
    PYTHON_CMD = py
endif

PYTHON_VERSION_CHECK = $(shell $(PYTHON_CMD) --version)
ifeq ($(PYTHON_VERSION_CHECK),)
    $(error "Python non trouvé. Veuillez installer Python 3.x")
else
    PYTHON = $(PYTHON_CMD)
endif

# Variables d'environnement
VENV = .venv
VENV_BIN = $(VENV)/bin
ifeq ($(OS),Windows_NT)
    VENV_BIN = $(VENV)/Scripts
    PYTHON_VENV = $(VENV_BIN)/python.exe
    RM = rd /s /q
    FIND = for /d %%G in (__pycache__ *) do rd /s /q "%%G"
    DELETE = del /s /q
else
    PYTHON_VENV = $(VENV_BIN)/python
    RM = rm -rf
    FIND = find . -type d -name "__pycache__" -exec rm -r {} +
    DELETE = find . -type f -name "*.pyc" -delete
endif

.PHONY: install test lint format check clean venv run

# Cible par défaut
all: venv install lint format

# Créer l'environnement virtuel
venv:
	@echo "Création de l'environnement virtuel avec $(PYTHON)..."
	$(PYTHON) -m venv $(VENV)
	@echo "Environnement virtuel créé dans le dossier $(VENV)"
	@echo "Pour l'activer manuellement:"
ifeq ($(OS),Windows_NT)
	@echo "  $(VENV_BIN)/activate.bat"
else
	@echo "  source $(VENV_BIN)/activate"
endif

# Installation des dépendances dans l'environnement virtuel
install: venv
	@echo "Installation des dépendances..."
	$(PYTHON_VENV) -m pip install --upgrade pip
	$(PYTHON_VENV) -m pip install -r requirements.txt
	$(PYTHON_VENV) -m pip install flake8 pylint black pytest pytest-cov
	@echo "✅ Installation terminée."

# Supprimer l'environnement virtuel
clean-venv:
	@echo "Suppression de l'environnement virtuel..."
	$(RM) $(VENV)

# Lancer l'application
run: venv
	@echo "Lancement de l'application..."
	$(PYTHON_VENV) app.py

# Tester le code
test:
	$(PYTHON_VENV) -m pytest tests/ -v --html=report.html

