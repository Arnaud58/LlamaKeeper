# Guide de Dépannage des Migrations SQLAlchemy et Alembic

## Contexte

Ce document décrit les problèmes courants de migration de base de données et les stratégies de résolution pour le projet LlamaKeeper.

## Problèmes Courants et Solutions

### 1. Erreur "Table Already Exists"

#### Symptômes
- Message d'erreur : `sqlite3.OperationalError: table X already exists`
- Impossible d'appliquer de nouvelles migrations

#### Solutions

1. **Réinitialisation Complète**
   ```bash
   # Marquer la dernière migration comme appliquée
   alembic stamp head
   
   # Générer une nouvelle migration
   alembic revision --autogenerate -m "Reset migrations"
   
   # Appliquer la migration
   alembic upgrade head
   ```

2. **Vérification des Tables Existantes**
   ```bash
   # Lister les tables dans la base de données SQLite
   sqlite3 keeper.db ".tables"
   ```

### 2. Configuration de Base de Données Incohérente

#### Problèmes Potentiels
- Différentes URL de base de données dans différents fichiers
- Configurations asynchrones et synchrones incompatibles

#### Bonnes Pratiques
- Utiliser une configuration centralisée (`config.py`)
- Convertir systématiquement les URL asynchrones
- Ajouter des logs détaillés

### 3. Migrations Incomplètes ou Bloquées

#### Diagnostic
- Vérifier l'historique des migrations
  ```bash
  alembic history
  ```

- Afficher la version courante
  ```bash
  alembic current
  ```

### 4. Stratégie de Gestion des Migrations

1. **Configuration Centralisée**
   - Utiliser `settings.SQLALCHEMY_DATABASE_URI`
   - Convertir dynamiquement les URL de base de données

2. **Logs Détaillés**
   - Configurer des logs de débogage dans `migrations/env.py`
   - Tracer chaque étape de migration

3. **Tests Automatisés**
   - Créer des scripts de test pour valider les migrations
   - Vérifier la création et l'intégrité des tables

## Exemple de Script de Test de Migration

```python
# tests/test_database_connection.py
async def test_database_connection():
    # Supprimer les tables existantes
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    # Recréer les tables
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Tester la création d'un modèle
    test_character = Character(name="Test", description="Test Description")
    
    async with AsyncSessionLocal() as session:
        session.add(test_character)
        await session.commit()
```

## Conseils Supplémentaires

- Toujours utiliser `alembic revision --autogenerate`
- Ne jamais modifier manuellement les fichiers de migration
- Garder les migrations dans le contrôle de version
- Tester les migrations dans un environnement de développement avant la production

## Dépannage Avancé

1. Problèmes de chemin : Vérifier les chemins absolus et relatifs
2. Versions de bibliothèques : Maintenir des versions compatibles
3. Configurations d'environnement : Utiliser des fichiers `.env`

## Conclusion

Une gestion rigoureuse des migrations nécessite de la vigilance, des tests systématiques et une configuration cohérente.