#!/bin/bash

# Script de workflow global pour la publication de LlamaKeeper

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
    log_success "Vérification des prérequis de publication"
    
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

# Workflow de publication complet
publish_workflow() {
    log_success "🚀 Début du workflow de publication LlamaKeeper"
    
    # Étape 1: Vérification pré-publication
    log_success "Étape 1: Vérification pré-publication"
    ./pre_publish_check.sh
    
    # Étape 2: Vérification de la publication
    log_success "Étape 2: Vérification de la publication"
    ./publish_checklist.sh
    
    # Étape 3: Préparation finale
    log_success "Étape 3: Préparation finale"
    ./final_publication_preparation.sh
    
    # Étape 4: Vérification finale de préparation
    log_success "Étape 4: Vérification finale de préparation"
    ./final_publication_readiness.sh
    
    # Étape 5: Publication finale
    log_success "Étape 5: Publication finale"
    ./final_publication_launch.sh
    
    log_success "🎉 Workflow de publication terminé avec succès !"
}

# Fonction principale
main() {
    check_prerequisites
    publish_workflow
    
    log_success "📦 Publication de LlamaKeeper v$(cat backend/VERSION) terminée !"
}

# Exécuter le script principal
main