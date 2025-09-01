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
from httpx import AsyncClient
from fastapi.testclient import TestClient

# Configuration des logs
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Ajouter le répertoire parent au chemin de Python
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.models.database import Base, init_models
from app.main import app

# Configuration de la base de données de test
TEST_DATABASE_URL = "sqlite+aiosqlite:///./test_ai_dungeon.db"
SYNC_TEST_DATABASE_URL = "sqlite:///./test_ai_dungeon.db"

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
            "cached_statements": True
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
                await conn.run_sync(Base.metadata.drop_all)
                await conn.run_sync(Base.metadata.create_all)
            
            logger.info("Session asynchrone créée avec succès")
            yield session
        except Exception as e:
            logger.error(f"Erreur dans la session asynchrone : {e}")
            raise
        finally:
            await session.close()

@pytest.fixture
def test_client():
    """Créer un client de test pour FastAPI"""
    return TestClient(app)

@pytest_asyncio.fixture
async def async_test_client():
    """Créer un client de test asynchrone pour FastAPI"""
    async with AsyncClient(base_url="http://test", app=app) as client:
        try:
            logger.info("Client de test asynchrone créé avec succès")
            yield client
        except Exception as e:
            logger.error(f"Erreur lors de la création du client de test asynchrone : {e}")
            raise

# Fixture pour mocker
@pytest.fixture
def mocker(request):
    """Fixture pour le mocking"""
    from unittest.mock import Mock
    return Mock()