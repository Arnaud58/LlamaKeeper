# Changelog

## [0.1.0] - 2025-08-29 (Date de la première version stable)

### Ajouts
- Architecture de base du projet LlamaKeeper
- API RESTful asynchrone avec FastAPI
- Gestion des personnages et des histoires
- Système de base de données SQLAlchemy asynchrone
- Support initial des modèles IA via Ollama
- Système de tests complet
  - Tests unitaires pour les personnages et les histoires
  - Gestion des erreurs
  - Couverture de code

### Fonctionnalités
- Création, lecture, mise à jour et suppression de personnages
- Création, lecture, mise à jour et suppression d'histoires
- Validation des données avec Pydantic
- Gestion des erreurs personnalisée
- Configuration de développement et de déploiement
- Documentation complète

### Améliorations
- Configuration de mypy pour le typage statique
- Formatage du code avec black et isort
- Scripts de configuration de l'environnement
- Guide de contribution détaillé

### Dépendances Principales
- FastAPI
- SQLAlchemy (Async)
- Pydantic
- Ollama
- Pytest

### Problèmes Connus
- Aucun problème majeur identifié à ce stade

### Notes de Version
- Version initiale du projet
- Implémentation des fonctionnalités de base
- Architecture modulaire et extensible
- Prêt pour les premiers tests et retours utilisateurs

## Prochaines Étapes
- Amélioration de l'intégration IA
- Développement de fonctionnalités avancées de génération d'histoires
- Optimisation des performances
- Ajout de plus de tests de couverture