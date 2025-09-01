import os
import sys
import logging
import traceback

# Configure logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[
                        logging.FileHandler('migration_debug.log'),
                        logging.StreamHandler()
                    ])

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine
from app.models.database import Base
from app.core.config import settings

def validate_database_configuration():
    """Validate database configuration before migrations"""
    logging.info("Validating database configuration")
    
    # Check DATABASE_URL
    if not settings.DATABASE_URL:
        logging.error("DATABASE_URL is not set")
        raise ValueError("DATABASE_URL must be configured")
    
    # Check if it's a SQLite database
    if not settings.DATABASE_URL.startswith(('sqlite:', 'sqlite+aiosqlite:')):
        logging.warning(f"Unexpected database type: {settings.DATABASE_URL}")
    
    # Validate path for file-based SQLite databases
    if settings.DATABASE_URL.startswith('sqlite:///./'):
        db_relative_path = settings.DATABASE_URL.split('///./')[1]
        db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), db_relative_path))
        
        logging.debug(f"Database relative path: {db_relative_path}")
        logging.debug(f"Database absolute path: {db_path}")
        
        # Check if directory exists or can be created
        try:
            os.makedirs(os.path.dirname(db_path), exist_ok=True)
        except Exception as e:
            logging.error(f"Cannot create database directory: {e}")
            raise

def run_migrations():
    """Run Alembic migrations with detailed logging and validation"""
    try:
        logging.info("Starting migration process")
        logging.debug(f"Current working directory: {os.getcwd()}")
        logging.debug(f"Python path: {sys.path}")
        logging.debug(f"Original DATABASE_URL: {settings.DATABASE_URL}")

        # Validate database configuration first
        validate_database_configuration()

        # Construct the absolute path to alembic.ini
        alembic_ini_path = os.path.join(os.path.dirname(__file__), 'alembic.ini')
        logging.debug(f"Alembic config path: {alembic_ini_path}")
    
        # Create Alembic configuration
        alembic_cfg = Config(alembic_ini_path)
    
        # Construct absolute path for the database
        if settings.DATABASE_URL.startswith('sqlite:///./'):
            db_relative_path = settings.DATABASE_URL.split('///./')[1]
            db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), db_relative_path))
            db_url = f'sqlite:///{db_path}'
        else:
            db_url = settings.DATABASE_URL
    
        # Ensure we're using a synchronous SQLite engine
        db_url = db_url.replace('+aiosqlite', '')
        logging.info(f"Final database URL: {db_url}")
    
        # Create the database tables using a synchronous SQLite engine
        logging.info(f"Creating database engine")
        engine = create_engine(db_url)
        
        logging.info("Creating database tables")
        Base.metadata.create_all(engine)
    
        # Set the database URL in the Alembic configuration
        alembic_cfg.set_main_option('sqlalchemy.url', db_url)
    
        # Upgrade to the latest version
        logging.info("Running Alembic migrations")
        command.upgrade(alembic_cfg, "head")
        
        logging.info("Migration process completed successfully")

    except Exception as e:
        logging.error(f"Migration failed: {e}")
        logging.error(traceback.format_exc())
        raise

if __name__ == "__main__":
    run_migrations()