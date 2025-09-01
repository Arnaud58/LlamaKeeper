#!/bin/bash

# Script de Processus de Publication Global pour LlamaKeeper v0.1.0

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

# Étape 2: Exécution du script maître de publication
run_publication_master() {
    log_success "🚀 Début du script maître de publication"
    
    ./final_publication_master.sh
    
    if [ $? -ne 0 ]; then
        log_error "Le script maître de publication a échoué"
        exit 1
    fi
    
    log_success "✅ Script maître de publication terminé avec succès"
}

# Étape 3: Génération du rapport final consolidé
generate_final_report() {
    log_success "📄 Génération du rapport final de publication"
    
    {
        echo "# Rapport Final Consolidé - LlamaKeeper v0.1.0"
        echo "## Informations Générales"
        echo "- Date de publication: $(date '+%Y-%m-%d %H:%M:%S')"
        echo "- Version: $(cat backend/VERSION)"
        echo "- Statut: Succès"
        echo ""
        echo "## Étapes de Publication"
        echo "1. Vérification finale de préparation: ✓"
        echo "2. Publication via script maître: ✓"
        echo ""
        echo "## Détails Supplémentaires"
        echo "- Tous les scripts de publication ont été exécutés avec succès"
        echo "- Vérifications de qualité passées"
        echo "- Package prêt pour distribution"
    } > FINAL_PUBLICATION_CONSOLIDATED_REPORT.md
    
    log_success "✅ Rapport final consolidé généré avec succès"
}

# Fonction principale
main() {
    echo -e "${YELLOW}🚀 Début du processus global de publication de LlamaKeeper v0.1.0 🚀${NC}"
    
    run_readiness_check
    run_publication_master
    generate_final_report
    
    echo -e "${GREEN}✨ Processus de publication global terminé avec succès ! ✨${NC}"
}

# Exécution du script
main