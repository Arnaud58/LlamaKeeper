import os
import sys
import logging

# Configurer la journalisation
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Journaliser les informations de débogage
logger.debug(f"Python Path: {sys.path}")
logger.debug(f"Current Working Directory: {os.getcwd()}")

from fastapi import Depends, FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.ext.asyncio import AsyncSession

# Journaliser les tentatives d'importation
try:
    from app.api import characters, stories
    logger.debug("Importation de characters et stories réussie")
except ImportError as e:
    logger.error(f"Erreur d'importation : {e}")
    raise

try:
    from app.core.websocket import handle_websocket_events
    logger.debug("Importation de handle_websocket_events réussie")
except ImportError as e:
    logger.error(f"Erreur d'importation : {e}")
    raise

try:
    from app.models.database import get_async_session, init_models
    logger.debug("Importation de get_async_session et init_models réussie")
except ImportError as e:
    logger.error(f"Erreur d'importation : {e}")
    raise

app = FastAPI(
    title="AI Dungeon Clone",
    description="A local AI-powered storytelling platform",
    version="0.1.0",
)

# CORS middleware to allow frontend interactions
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Include API routers
app.include_router(characters.router, prefix="/api/v1")
app.include_router(stories.router, prefix="/api/v1")

# Optional static files mounting
frontend_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")
if os.path.exists(os.path.join(frontend_dir, "static")):
    app.mount(
        "/static",
        StaticFiles(directory=os.path.join(frontend_dir, "static")),
        name="static",
    )


@app.on_event("startup")
async def startup_event():
    """Initialize database models on application startup"""
    await init_models()


# Health check endpoint
@app.get("/health")
async def health_check():
    """Simple health check endpoint"""
    return {"status": "healthy"}


# WebSocket endpoint for real-time story updates
@app.websocket("/ws/stories")
async def websocket_story_endpoint(
    websocket: WebSocket, session: AsyncSession = Depends(get_async_session)
):
    """
    WebSocket endpoint for real-time story interactions
    Allows subscribing to stories, receiving updates, and sending actions
    """
    await handle_websocket_events(websocket, session)
