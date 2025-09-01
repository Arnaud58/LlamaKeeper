#!/bin/bash

# Script de vérification finale pour la publication de LlamaKeeper

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
    exit 1
}

# Vérification des fichiers critiques
check_critical_files() {
    log_success "Vérification des fichiers critiques"
    
    critical_files=(
        "README.md"
        "CHANGELOG.md"
        "CONTRIBUTING.md"
        "SECURITY.md"
        "LICENSE"
        "backend/VERSION"
        "setup.py"
    )
    
    for file in "${critical_files[@]}"; do
        if [ ! -f "$file" ]; then
            log_error "Fichier manquant : $file"
            exit 1
        else
            log_success "Fichier présent : $file"
        fi
    done
}

# Vérification des scripts
check_scripts() {
    log_success "Vérification des scripts"
    
    scripts=(
        "setup_dev_env.sh"
        "start.sh"
        "publish.sh"
        "pre_publish_check.sh"
        "release.sh"
        "finalize_release.sh"
    )
    
    for script in "${scripts[@]}"; do
        if [ ! -x "$script" ]; then
            log_error "Script non exécutable : $script"
            exit 1
        else
            log_success "Script exécutable : $script"
        fi
    done
}

# Vérification de la configuration GitHub
check_github_config() {
    log_success "Vérification de la configuration GitHub"
    
    github_files=(
        ".github/workflows/python-publish.yml"
        ".github/pull_request_template.md"
    )
    
    for file in "${github_files[@]}"; do
        if [ ! -f "$file" ]; then
            log_error "Fichier GitHub manquant : $file"
            exit 1
        else
            log_success "Fichier GitHub présent : $file"
        fi
    done
}

# Vérification des tests
run_final_tests() {
    log_success "Exécution des tests finaux"
    
    # Exécuter les tests avec couverture
    cd backend
    pytest tests/ --cov=app
    test_result=$?
    
    if [ $test_result -ne 0 ]; then
        log_error "Les tests ont échoué"
        exit 1
    fi
    
    # Vérification de la couverture de code
    coverage_report=$(pytest tests/ --cov=app --cov-report=term-missing)
    
    if [[ $coverage_report == *"TOTAL    0%"* ]]; then
        log_error "Aucune couverture de code"
        exit 1
    fi
    
    log_success "Tous les tests passent"
}

# Vérification de la version
check_version() {
    log_success "Vérification de la version"
    
    VERSION=$(cat backend/VERSION)
    
    if [[ ! "$VERSION" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
        log_error "Format de version invalide : $VERSION"
        exit 1
    fi
    
    log_success "Version valide : $VERSION"
}

# Fonction principale
main() {
    log_success "🚀 Début de la vérification finale de publication"
    
    check_critical_files
    check_scripts
    check_github_config
    run_final_tests
    check_version
    
    log_success "🎉 Toutes les vérifications sont passées !"
    log_success "Prêt pour la publication de la version $(cat backend/VERSION)"
}

# Exécuter le script principal
main