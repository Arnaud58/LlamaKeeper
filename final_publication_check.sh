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

# Exécuter les vérifications complètes
run_comprehensive_checks() {
    log_success "Exécution des vérifications complètes"
    
    # Vérification pré-publication
    ./pre_publish_check.sh
    pre_publish_result=$?
    
    # Vérification de la publication
    ./publish_checklist.sh
    publish_checklist_result=$?
    
    # Vérification finale
    ./final_publish_prep.sh
    final_prep_result=$?
    
    if [ $pre_publish_result -ne 0 ] || 
       [ $publish_checklist_result -ne 0 ] || 
       [ $final_prep_result -ne 0 ]; then
        log_error "Les vérifications complètes ont échoué"
        exit 1
    fi
}

# Préparation des métadonnées de publication
prepare_publication_metadata() {
    log_success "Préparation des métadonnées de publication"
    
    VERSION=$(cat backend/VERSION)
    
    # Créer un fichier de métadonnées de publication
    cat > PUBLICATION_METADATA.md << EOL
# Métadonnées de Publication LlamaKeeper

## Informations de Version
- **Version**: ${VERSION}
- **Date de Publication**: $(date +"%Y-%m-%d")
- **Statut**: Prêt pour la publication

## Vérifications Effectuées
- [x] Tests unitaires
- [x] Couverture de code
- [x] Vérification de la qualité du code
- [x] Validation des dépendances
- [x] Préparation de la documentation

## Notes de Release
Voir le CHANGELOG.md pour les détails complets des modifications.

## Prochaines Étapes
- Collecte des retours de la communauté
- Préparation des futures améliorations
EOL

    log_success "Métadonnées de publication créées"
}

# Préparation finale du dépôt
final_repository_prep() {
    log_success "Préparation finale du dépôt"
    
    VERSION=$(cat backend/VERSION)
    
    # Ajouter tous les fichiers
    git add .
    
    # Créer un commit de publication
    git commit -m "Préparation finale pour la publication v${VERSION}"
    
    # Créer un tag
    git tag -a "v${VERSION}" -m "Release v${VERSION}"
    
    log_success "Dépôt préparé pour la publication"
}

# Fonction principale
main() {
    log_success "🚀 Début de la préparation finale de publication"
    
    check_prerequisites
    run_comprehensive_checks
    prepare_publication_metadata
    final_repository_prep
    
    log_success "🎉 Préparation finale terminée avec succès !"
    log_success "Prêt pour la publication de la version $(cat backend/VERSION)"
}

# Exécuter le script principal
main