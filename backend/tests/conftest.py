import os
import sys
import asyncio
import logging
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import sessionmaker as sync_sessionmaker
from sqlalchemy.pool import StaticPool
from sqlalchemy import create_engine
from sqlalchemy.orm import configure_mappers
from httpx import AsyncClient, ASGITransport
from fastapi.testclient import TestClient

# Configuration des logs
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Ajouter le répertoire parent au chemin de Python
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.models.database import Base, init_models
from app.main import app

# Configuration de la base de données de test
import os

TEST_DATABASE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "test_ai_dungeon.db"))
TEST_DATABASE_URL = f"sqlite+aiosqlite:///{TEST_DATABASE_PATH}"
SYNC_TEST_DATABASE_URL = f"sqlite:///{TEST_DATABASE_PATH}"

# Supprimer le fichier de base de données existant avant de créer un nouveau
try:
    os.remove(TEST_DATABASE_PATH)
except FileNotFoundError:
    pass

@pytest.fixture(scope="session")
def event_loop():
    """Créer une boucle d'événements pour les tests asynchrones"""
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    policy.set_event_loop(loop)
    try:
        yield loop
    finally:
        loop.close()

@pytest_asyncio.fixture(scope="session")
async def async_engine():
    """Créer un moteur SQLAlchemy asynchrone pour les tests"""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
        future=True,
        connect_args={
            "check_same_thread": False,
            "cached_statements": True,
            "timeout": 30  # Augmenter le délai de verrouillage
        },
        poolclass=StaticPool
    )
    
    # Initialiser les modèles
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    
    try:
        logger.info("Moteur asynchrone créé avec succès")
        yield engine
    except Exception as e:
        logger.error(f"Erreur lors de la création du moteur asynchrone : {e}")
        raise
    finally:
        await engine.dispose()
        # Supprimer le fichier de base de données après les tests
        try:
            os.remove(TEST_DATABASE_PATH)
        except FileNotFoundError:
            pass

@pytest_asyncio.fixture(scope="function")
async def async_session(async_engine):
    """Créer une session de base de données asynchrone pour chaque test"""
    async_session_factory = async_sessionmaker(
        async_engine,
        class_=AsyncSession,
        expire_on_commit=False
    )
    
    async with async_session_factory() as session:
        try:
            # Recréer les tables avant chaque test
            async with async_engine.begin() as conn:
                # Supprimir toutes les données de toutes les tables
                for table in reversed(Base.metadata.sorted_tables):
                    await conn.execute(table.delete())
                
                # Recréer les tables si nécessaire
                await conn.run_sync(Base.metadata.create_all)
            
            logger.info("Session asynchrone créée avec succès")
            yield session
        except Exception as e:
            logger.error(f"Erreur dans la session asynchrone : {e}")
            raise
        finally:
            await session.close()
            # Supprimer le fichier de base de données après le test
            import os
            try:
                os.remove("./test_ai_dungeon.db")
            except FileNotFoundError:
                pass

@pytest.fixture
def test_client():
    """Créer un client de test pour FastAPI"""
    return TestClient(app)

@pytest_asyncio.fixture
async def async_test_client():
    """Créer un client de test asynchrone pour FastAPI"""
    from httpx import AsyncClient
    
    # Créer un client asynchrone
    async_client = AsyncClient(
        base_url="http://test",
        app=app
    )
    
    try:
        logger.info("Client de test asynchrone créé avec succès")
        logger.info(f"Type de async_client : {type(async_client)}")
        logger.info(f"Méthodes disponibles : {dir(async_client)}")
        
        # Vérification explicite de la méthode aclose
        if not hasattr(async_client, 'aclose'):
            logger.error("ATTENTION : La méthode aclose() est manquante !")
        
        yield async_client
    except Exception as e:
        logger.error(f"Erreur lors de la création du client de test asynchrone : {e}")
        raise
    finally:
        try:
            logger.info("Tentative de fermeture du client asynchrone")
            if hasattr(async_client, 'aclose'):
                await async_client.aclose()
                logger.info("Client asynchrone fermé avec succès")
            else:
                logger.warning("Impossible de fermer le client : méthode aclose() non disponible")
        except Exception as close_error:
            logger.error(f"Erreur lors de la fermeture du client : {close_error}")

# Fixture pour mocker
@pytest.fixture
def mocker(request):
    """Fixture pour le mocking"""
    from unittest.mock import Mock
    return Mock()