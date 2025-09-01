#!/bin/bash

# Script de vérification pré-publication pour LlamaKeeper

# Couleurs pour les messages
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Fonction de log
log_success() {
    echo -e "${GREEN}[✓ SUCCÈS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[⚠️ AVERTISSEMENT]${NC} $1"
}

log_error() {
    echo -e "${RED}[✗ ERREUR]${NC} $1"
}

# Vérification des prérequis
check_prerequisites() {
    log_success "Début des vérifications pré-publication"
    
    # Vérifier Python
    python_version=$(python3 --version)
    if [[ $python_version == *"3.10"* || $python_version == *"3.11"* ]]; then
        log_success "Version Python compatible : $python_version"
    else
        log_error "Version Python incompatible. Requis : 3.10+"
        exit 1
    fi
    
    # Vérifier Ollama
    if command -v ollama &> /dev/null; then
        log_success "Ollama installé"
    else
        log_error "Ollama n'est pas installé"
        exit 1
    fi
}

# Vérification des tests
run_tests() {
    log_success "Exécution des tests"
    
    # Exécuter les tests avec couverture
    pytest backend/tests/ --cov=backend/app
    test_result=$?
    
    if [ $test_result -eq 0 ]; then
        log_success "Tous les tests passent"
    else
        log_error "Échec des tests"
        exit 1
    fi
}

# Vérification de la qualité du code
check_code_quality() {
    log_success "Vérification de la qualité du code"
    
    # Formatage
    black --check backend/app
    black_result=$?
    
    # Typage statique
    mypy backend/app
    mypy_result=$?
    
    # Vérification des imports
    isort --check backend/app
    isort_result=$?
    
    if [ $black_result -eq 0 ] && [ $mypy_result -eq 0 ] && [ $isort_result -eq 0 ]; then
        log_success "Qualité du code vérifiée"
    else
        log_error "Problèmes de qualité de code détectés"
        exit 1
    fi
}

# Vérification de la documentation
check_documentation() {
    log_success "Vérification de la documentation"
    
    # Liste des fichiers de documentation critiques
    docs=("README.md" "CONTRIBUTING.md" "SECURITY.md" "CHANGELOG.md")
    
    for doc in "${docs[@]}"; do
        if [ -f "$doc" ]; then
            log_success "Document $doc présent"
        else
            log_error "Document $doc manquant"
            exit 1
        fi
    done
}

# Vérification de la configuration de publication
check_publish_config() {
    log_success "Vérification de la configuration de publication"
    
    # Vérifier le fichier de version
    if [ -f "backend/VERSION" ]; then
        version=$(cat backend/VERSION)
        log_success "Version détectée : $version"
    else
        log_error "Fichier de version manquant"
        exit 1
    fi
    
    # Vérifier setup.py
    if [ -f "setup.py" ]; then
        log_success "Configuration de publication présente"
    else
        log_error "Configuration de publication manquante"
        exit 1
    fi
}

# Fonction principale
main() {
    check_prerequisites
    run_tests
    check_code_quality
    check_documentation
    check_publish_config
    
    log_success "🚀 Tous les contrôles pré-publication sont passés !"
    log_success "Prêt pour la publication de la version $(cat backend/VERSION)"
}

# Exécuter le script principal
main