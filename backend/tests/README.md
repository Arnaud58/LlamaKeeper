# Tests pour LlamaKeeper Backend

## Configuration des Tests

### Dépendances
Les tests utilisent les bibliothèques suivantes :
- `pytest`: Framework de tests principal
- `pytest-asyncio`: Support des tests asynchrones
- `pytest-cov`: Génération de rapports de couverture de code
- `httpx`: Client HTTP asynchrone pour les tests d'API

### Exécution des Tests

#### Exécution Complète
Pour exécuter tous les tests avec rapport de couverture :
```bash
./run_tests.sh
```

#### Options de Pytest
- `-v`: Mode verbeux
- `--cov=app`: Mesure de la couverture de code pour le package `app`
- `--cov-report=html`: Génère un rapport de couverture HTML
- `--cov-report=term-missing`: Affiche les lignes de code non couvertes dans le terminal

## Structure des Tests

### Types de Tests
1. `test_characters.py`: Tests pour les endpoints de personnages
2. `test_stories.py`: Tests pour les endpoints d'histoires
3. `test_error_handling.py`: Tests de gestion des erreurs
4. `test_abstract_base_classes.py`: Tests des classes de base

### Conventions
- Utilisation de `@pytest.mark.asyncio` pour les tests asynchrones
- Utilisation de `async_session` comme fixture pour les sessions de base de données
- Validation des schémas de réponse
- Tests couvrant les cas de succès et d'erreur

## Configuration de la Base de Données de Test
- Utilisation d'une base de données SQLite in-memory
- Création et suppression automatique des tables pour chaque session de test

## Bonnes Pratiques
- Chaque test doit être indépendant
- Utiliser des données de test uniques
- Couvrir les chemins heureux et les cas d'erreur
- Maintenir une couverture de code élevée

## Contribution
1. Ajouter de nouveaux tests pour les nouvelles fonctionnalités
2. Mettre à jour les tests existants lors de modifications
3. Vérifier que la couverture de code reste élevée