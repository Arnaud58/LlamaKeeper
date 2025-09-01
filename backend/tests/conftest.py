import os
import sys
import asyncio
import logging
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.orm import configure_mappers

# Configuration des logs
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Ajouter le répertoire parent au chemin de Python pour permettre l'importation de app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.models.database import Base
from app.main import app
from fastapi.testclient import TestClient

# Test database configuration
TEST_DATABASE_URL = "sqlite+aiosqlite:///./test_ai_dungeon.db"

@pytest.fixture(scope="session")
def event_loop():
    """Create an event loop for async testing"""
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    policy.set_event_loop(loop)
    try:
        yield loop
    finally:
        loop.close()

@pytest_asyncio.fixture(scope="session")
async def async_engine():
    """Create async SQLAlchemy engine for testing"""
    try:
        # Configurer les mappeurs avant de créer l'engine
        configure_mappers()
        
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
        logger.info("Async engine created successfully")
        yield engine
    except Exception as e:
        logger.error(f"Error creating async engine: {e}")
        raise
    finally:
        await engine.dispose()

@pytest_asyncio.fixture(scope="session")
async def test_db(async_engine):
    """Create test database schema"""
    async with async_engine.begin() as conn:
        try:
            await conn.run_sync(Base.metadata.create_all)
            logger.info("Test database schema created successfully")
        except Exception as e:
            logger.error(f"Error creating test database schema: {e}")
            raise
    yield
    async with async_engine.begin() as conn:
        try:
            await conn.run_sync(Base.metadata.drop_all)
            logger.info("Test database schema dropped successfully")
        except Exception as e:
            logger.error(f"Error dropping test database schema: {e}")
            raise

@pytest_asyncio.fixture(scope="function")
async def async_session(async_engine, test_db):
    """Create an async database session for each test"""
    async_session_factory = async_sessionmaker(
        async_engine, 
        class_=AsyncSession, 
        expire_on_commit=False
    )
    
    async with async_session_factory() as session:
        try:
            logger.info("Async session created successfully")
            yield session
        except Exception as e:
            logger.error(f"Error in async session: {e}")
            raise
        finally:
            await session.close()

@pytest.fixture
def test_client():
    """Create a test client for FastAPI"""
    return TestClient(app)

@pytest_asyncio.fixture
async def async_test_client():
    """Create an async test client for FastAPI"""
    async with AsyncClient(base_url="http://testserver") as client:
        client.app = app
        try:
            logger.info("Async test client created successfully")
            yield client
        except Exception as e:
            logger.error(f"Error creating async test client: {e}")
            raise