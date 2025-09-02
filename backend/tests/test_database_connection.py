import asyncio
import logging
import sys
import os

# Ajouter le répertoire parent au chemin pour l'import des modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.models.database import async_engine, Base, get_async_session
from app.models.database import Character, Story, Action, Memory
from app.core.config import settings

# Configuration du logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

async def test_database_connection():
    """
    Test complet de la connexion à la base de données et des opérations de base
    """
    logger.info("🔍 Début du test de connexion à la base de données")
    
    try:
        # Supprimer toutes les tables existantes avant de les recréer
        logger.info("🗑️ Suppression des tables existantes")
        async with async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
        
        # Création des tables
        logger.info("📋 Création des tables")
        async with async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("✅ Tables créées avec succès")
        
        # Test de création d'un personnage sans updated_at
        logger.info("👤 Test de création d'un personnage")
        test_character = Character(
            name="Test Character",
            description="Un personnage de test",
            personality={"trait": "courageux"}
        )
        
        # Utilisation de la session asynchrone
        async for session in get_async_session():
            try:
                session.add(test_character)
                await session.commit()
                logger.info("✅ Personnage créé avec succès")
                
                # Récupération du personnage
                retrieved_character = await session.get(Character, test_character.id)
                
                if retrieved_character:
                    logger.info(f"🔎 Personnage récupéré : {retrieved_character.name}")
                    assert retrieved_character.name == "Test Character", "Nom du personnage incorrect"
                else:
                    logger.error("❌ Impossible de récupérer le personnage")
                
            except Exception as e:
                logger.error(f"❌ Erreur lors de l'opération sur le personnage : {e}")
                await session.rollback()
                raise
    
    except Exception as e:
        logger.error(f"❌ Erreur globale : {e}")
        raise
    
    logger.info("🎉 Test de connexion à la base de données terminé avec succès")

def run_async_test():
    """Exécute le test asynchrone"""
    asyncio.run(test_database_connection())

if __name__ == "__main__":
    run_async_test()