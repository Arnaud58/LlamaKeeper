#!/bin/bash

# Script de configuration de l'environnement de développement pour LlamaKeeper

# Vérifier Python
if ! command -v python3 &> /dev/null
then
    echo "Python 3 n'est pas installé. Veuillez l'installer."
    exit 1
fi

# Créer un environnement virtuel
python3 -m venv venv
source venv/bin/activate

# Mettre à jour pip
pip install --upgrade pip

# Installer les dépendances
pip install -r requirements.txt

# Installer les outils de développement
pip install black isort mypy pytest pytest-cov

# Configurer les hooks git (optionnel)
if [ -d .git ]; then
    echo "Configuration des hooks git pour le formatage et les tests"
    cat > .git/hooks/pre-commit << EOL
#!/bin/sh
# Formatage du code
black app
isort app

# Vérification du typage
mypy app

# Tests
pytest
EOL
    chmod +x .git/hooks/pre-commit
fi

# Initialiser la base de données
if [ -f run_migrations.py ]; then
    python run_migrations.py
fi

# Vérifier la configuration
echo "Vérification de la configuration..."
black --check app
isort --check app
mypy app

# Message de succès
echo "Environnement de développement configuré avec succès !"
echo "Activez l'environnement avec 'source venv/bin/activate'"
echo "Démarrez le serveur avec 'uvicorn app.main:app --reload'"