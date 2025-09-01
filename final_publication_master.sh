#!/bin/bash

# Script Maître de Publication pour LlamaKeeper v0.1.0

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

# Étape 1: Vérification finale de préparation
run_readiness_check() {
    log_success "🔍 Début de la vérification finale de préparation"
    
    ./final_publication_readiness_check.sh
    
    if [ $? -ne 0 ]; then
        log_error "La vérification finale de préparation a échoué"
        exit 1
    fi
    
    log_success "✅ Vérification finale de préparation terminée avec succès"
}

# Étape 2: Préparation du package
prepare_package() {
    log_success "📦 Préparation du package de publication"
    
    # Mise à jour des métadonnées
    python3 -m pip install --upgrade build twine
    
    # Construction du package
    python3 -m build
    
    log_success "✅ Package préparé avec succès"
}

# Étape 3: Vérification pré-publication
pre_publish_checks() {
    log_success "🧪 Exécution des vérifications pré-publication"
    
    ./pre_publish_check.sh
    
    if [ $? -ne 0 ]; then
        log_error "Les vérifications pré-publication ont échoué"
        exit 1
    fi
    
    log_success "✅ Vérifications pré-publication terminées avec succès"
}

# Étape 4: Publication sur PyPI
publish_to_pypi() {
    log_success "🚀 Publication sur PyPI"
    
    # Utilisation de Twine pour la publication
    twine upload dist/*
    
    if [ $? -ne 0 ]; then
        log_error "La publication sur PyPI a échoué"
        exit 1
    fi
    
    log_success "✅ Publication sur PyPI terminée avec succès"
}

# Étape 5: Création et poussée des tags Git
create_git_release() {
    log_success "🏷️ Création de la release Git"
    
    # Récupération de la version
    VERSION=$(cat backend/VERSION)
    
    # Création du tag
    git tag -a "v$VERSION" -m "Release version $VERSION"
    git push origin "v$VERSION"
    
    log_success "✅ Release Git créée avec succès"
}

# Étape 6: Génération du rapport final de publication
generate_publication_report() {
    log_success "📄 Génération du rapport final de publication"
    
    # Création d'un rapport consolidé
    {
        echo "# Rapport Final de Publication - LlamaKeeper v0.1.0"
        echo "## Informations de Publication"
        echo "- Date de publication: $(date '+%Y-%m-%d %H:%M:%S')"
        echo "- Version: $(cat backend/VERSION)"
        echo "- Statut: Succès"
        echo ""
        echo "## Étapes de Publication"
        echo "1. Vérification finale de préparation: ✓"
        echo "2. Préparation du package: ✓"
        echo "3. Vérifications pré-publication: ✓"
        echo "4. Publication sur PyPI: ✓"
        echo "5. Création de la release Git: ✓"
    } > FINAL_PUBLICATION_CONSOLIDATED_REPORT.md
    
    log_success "✅ Rapport final généré avec succès"
}

# Fonction principale
main() {
    echo -e "${YELLOW}🚀 Début du processus de publication de LlamaKeeper v0.1.0 🚀${NC}"
    
    run_readiness_check
    prepare_package
    pre_publish_checks
    publish_to_pypi
    create_git_release
    generate_publication_report
    
    echo -e "${GREEN}✨ Publication terminée avec succès ! ✨${NC}"
}

# Exécution du script
main