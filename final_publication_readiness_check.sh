#!/bin/bash

# Script de Vérification Finale de Préparation pour LlamaKeeper

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

# Vérification des prérequis
check_prerequisites() {
    log_success "Vérification des prérequis finaux"
    
    # Vérifier Git
    if ! command -v git &> /dev/null; then
        log_error "Git n'est pas installé"
    fi
    
    # Vérifier Python
    if ! command -v python3 &> /dev/null; then
        log_error "Python 3 n'est pas installé"
    fi
    
    # Vérifier Twine
    if ! command -v twine &> /dev/null; then
        log_warning "Twine n'est pas installé. Installation en cours..."
        pip install twine
    fi
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
        "PUBLICATION_GUIDE.md"
        "PUBLICATION_METADATA.md"
        "FINAL_PUBLICATION_REPORT.md"
        "FINAL_PUBLICATION_CONSOLIDATED_REPORT.md"
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
        "final_publication_check.sh"
        "release_and_publish.sh"
        "final_publication_preparation.sh"
        "final_publication_process.sh"
        "final_publication_master.sh"
    )
    
    for script in "${scripts[@]}"; do
        if [ ! -f "$script" ]; then
            log_error "Script manquant : $script"
            exit 1
        else
            # Vérifier les permissions d'exécution
            if [ ! -x "$script" ]; then
                log_warning "Script non exécutable : $script. Ajout des permissions..."
                chmod +x "$script"
            fi
            log_success "Script vérifié : $script"
        fi
    done
}

# Vérification des tests
run_tests() {
    log_success "Exécution des tests"
    
    cd backend || exit 1
    
    # Exécuter pytest avec coverage
    python3 -m pytest tests/ --cov=app --cov-report=xml
    
    # Vérifier la couverture des tests
    coverage_percentage=$(python3 -c "import xml.etree.ElementTree as ET; tree = ET.parse('coverage.xml'); print(f'{float(tree.find('.//coverage').get('line-rate')) * 100:.2f}')")
    
    if (( $(echo "$coverage_percentage < 80" | bc -l) )); then
        log_warning "Couverture des tests inférieure à 80% : $coverage_percentage%"
    else
        log_success "Couverture des tests : $coverage_percentage%"
    fi
    
    cd ..
}

# Vérification de la documentation
check_documentation() {
    log_success "Vérification de la documentation"
    
    # Vérifier la présence de documentation technique
    doc_files=(
        "README.md"
        "DEPLOYMENT.md"
        "CONTRIBUTING.md"
        "PUBLICATION_GUIDE.md"
    )
    
    for doc in "${doc_files[@]}"; do
        if [ ! -f "$doc" ]; then
            log_error "Documentation manquante : $doc"
            exit 1
        else
            log_success "Documentation présente : $doc"
        fi
    done
}

# Vérification de la configuration Git
check_git_configuration() {
    log_success "Vérification de la configuration Git"
    
    # Vérifier que tous les fichiers sont commitables
    if [[ -n $(git status -s) ]]; then
        log_warning "Il y a des modifications non commitées"
        git status
    else
        log_success "Tous les fichiers sont à jour"
    fi
    
    # Vérifier la présence de tags de release
    if ! git tag | grep -q "v0.1.0"; then
        log_warning "Tag de release v0.1.0 manquant"
    else
        log_success "Tag de release v0.1.0 présent"
    fi
}

# Fonction principale
main() {
    echo -e "${YELLOW}🚀 Début de la vérification finale de préparation pour LlamaKeeper 🚀${NC}"
    
    check_prerequisites
    check_critical_files
    check_scripts
    run_tests
    check_documentation
    check_git_configuration
    
    echo -e "${GREEN}✨ Préparation finale terminée avec succès ! ✨${NC}"
}

# Exécution du script
main