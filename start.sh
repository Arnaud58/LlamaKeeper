#!/bin/bash

# Script de démarrage pour LlamaKeeper

# Définir les variables par défaut
ENV_MODE=${1:-development}
PYTHON_VERSION="3.10"
VENV_NAME="keeper"

# Fonctions utilitaires
log() {
    echo "[LlamaKeeper Startup] $1"
}

error() {
    echo "[ERROR] $1" >&2
    exit 1
}

# Vérifier les prérequis
check_prerequisites() {
    command -v python3 >/dev/null 2>&1 || error "Python 3 est requis"
    command -v conda >/dev/null 2>&1 || error "Conda est requis"
}

# Configurer l'environnement virtuel
setup_environment() {
    log "Configuration de l'environnement virtuel"
    
    # Créer ou activer l'environnement conda
    if ! conda env list | grep -q "$VENV_NAME"; then
        log "Création de l'environnement conda"
        conda create -n "$VENV_NAME" python="$PYTHON_VERSION" -y
    fi

    # Activer l'environnement
    source ~/miniconda3/etc/profile.d/conda.sh
    conda activate "$VENV_NAME"
}

# Installer les dépendances
install_dependencies() {
    log "Installation des dépendances"
    pip install -r backend/requirements.txt
}

# Configurer la base de données
setup_database() {
    log "Configuration de la base de données"
    cd backend
    
    # Exécuter les migrations
    alembic upgrade head
}

# Démarrer le serveur
start_server() {
    log "Démarrage du serveur LlamaKeeper en mode $ENV_MODE"
    
    case "$ENV_MODE" in
        development)
            uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
            ;;
        production)
            gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app
            ;;
        *)
            error "Mode non supporté. Utilisez 'development' ou 'production'"
            ;;
    esac
}

# Fonction principale
main() {
    check_prerequisites
    setup_environment
    install_dependencies
    setup_database
    start_server
}

# Exécuter le script
main