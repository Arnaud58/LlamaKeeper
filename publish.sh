#!/bin/bash

# Script de publication pour LlamaKeeper Backend

# Couleurs pour les messages
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Fonction de log
log() {
    echo -e "${GREEN}[PUBLICATION]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[AVERTISSEMENT]${NC} $1"
}

error() {
    echo -e "${RED}[ERREUR]${NC} $1"
    exit 1
}

# Vérifier les prérequis
check_prerequisites() {
    log "Vérification des prérequis..."
    
    # Vérifier Git
    if ! command -v git &> /dev/null; then
        error "Git n'est pas installé"
    fi
    
    # Vérifier Python
    if ! command -v python3 &> /dev/null; then
        error "Python 3 n'est pas installé"
    fi
    
    # Vérifier pip
    if ! command -v pip &> /dev/null; then
        error "pip n'est pas installé"
    fi
    
    # Vérifier twine pour publication PyPI
    if ! command -v twine &> /dev/null; then
        warn "twine n'est pas installé. Installation en cours..."
        pip install twine
    fi
}

# Exécuter les tests
run_tests() {
    log "Exécution des tests..."
    pytest backend/tests/
    if [ $? -ne 0 ]; then
        error "Les tests ont échoué. Publication annulée."
    fi
}

# Vérifier le statut Git
check_git_status() {
    log "Vérification du statut Git..."
    if [[ -n $(git status -s) ]]; then
        warn "Il y a des modifications non commitées."
        git status
        read -p "Voulez-vous continuer ? (o/N) " continue_publish
        if [[ "$continue_publish" != "o" ]]; then
            error "Publication annulée par l'utilisateur"
        fi
    fi
}

# Créer un tag Git
create_git_tag() {
    VERSION=$(cat backend/VERSION)
    log "Création du tag Git v${VERSION}..."
    git add backend/VERSION backend/CHANGELOG.md
    git commit -m "Préparer la release v${VERSION}"
    git tag -a "v${VERSION}" -m "Release v${VERSION}"
}

# Publier sur PyPI
publish_to_pypi() {
    log "Publication sur PyPI..."
    python3 setup.py sdist bdist_wheel
    twine upload dist/*
}

# Pousser les tags sur GitHub
push_to_github() {
    log "Poussage des tags sur GitHub..."
    git push origin main
    git push origin --tags
}

# Fonction principale
main() {
    check_prerequisites
    run_tests
    check_git_status
    create_git_tag
    publish_to_pypi
    push_to_github
    
    log "Publication terminée avec succès !"
}

# Exécuter le script principal
main