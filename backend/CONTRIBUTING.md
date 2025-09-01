# Guide de Contribution pour LlamaKeeper Backend

## Configuration de l'Environnement de Développement

### Prérequis
- Python 3.10+
- Conda ou venv recommandé
- Git

### Installation
1. Clonez le dépôt
```bash
git clone https://github.com/votre-utilisateur/LlamaKeeper.git
cd LlamaKeeper/backend
```

2. Créez un environnement virtuel
```bash
python -m venv venv
source venv/bin/activate  # Sur Unix
# ou
venv\Scripts\activate  # Sur Windows
```

3. Installez les dépendances
```bash
pip install -r requirements.txt
```

## Tests

### Exécution des Tests
```bash
# Tous les tests avec couverture de code
./run_tests.sh

# Tests spécifiques
pytest tests/test_characters.py
pytest tests/test_stories.py
```

### Écriture de Tests

#### Principes Généraux
- Chaque nouvelle fonctionnalité doit être accompagnée de tests
- Couvrez les cas de succès et d'erreur
- Utilisez des données de test uniques et significatives

#### Structure des Tests
- Utilisez `@pytest.mark.asyncio` pour les tests asynchrones
- Nommez vos fonctions de test de manière descriptive
- Utilisez des assertions précises

#### Exemple de Test
```python
@pytest.mark.asyncio
async def test_create_character(async_session: AsyncSession):
    """Test creating a new character"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        character_data = {
            "name": "Test Character",
            "description": "A test character"
        }
        
        response = await client.post("/api/v1/characters/", json=character_data)
        
        assert response.status_code == 200
        character = CharacterResponse(**response.json())
        assert character.name == "Test Character"
```

### Couverture de Code
- Visez une couverture de code d'au moins 80%
- Utilisez `--cov-report=html` pour générer un rapport détaillé

## Bonnes Pratiques de Développement

### Style de Code
- Suivez PEP 8
- Utilisez `black` pour le formatage
- Utilisez `mypy` pour le typage statique

### Gestion des Dépendances
- Mettez à jour `requirements.txt` lors de l'ajout de nouvelles dépendances
- Préférez des versions spécifiques des packages

### Gestion des Erreurs
- Utilisez des exceptions personnalisées
- Loggez les erreurs de manière informative
- Fournissez des messages d'erreur clairs

## Processus de Contribution

1. Créez une branche pour votre fonctionnalité
```bash
git checkout -b feature/ma-nouvelle-fonctionnalite
```

2. Développez et testez
- Écrivez du code
- Ajoutez des tests
- Vérifiez la couverture de code

3. Commit et Push
```bash
git add .
git commit -m "Description claire du changement"
git push origin feature/ma-nouvelle-fonctionnalite
```

4. Créez une Pull Request
- Décrivez les changements
- Liez les issues associées
- Attendez la revue de code

## Ressources Supplémentaires
- [Documentation FastAPI](https://fastapi.tiangolo.com/)
- [SQLAlchemy Async Documentation](https://docs.sqlalchemy.org/en/14/orm/extensions/asyncio.html)
- [Pytest Documentation](https://docs.pytest.org/)

## Contact
Pour toute question, ouvrez une issue sur GitHub ou contactez l'équipe de développement.