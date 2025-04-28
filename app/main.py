from fastapi import FastAPI
from app.api.routes import router as api_router
from app.api.db_routes import router as db_router
from app.ws.websocket_handler import websocket_endpoint
from contextlib import asynccontextmanager
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("ocpp-server")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize database 
    from app.database.database import Base, engine
    logger.info("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    
    logger.info("OCPP Server starting up")
    yield
    logger.info("OCPP Server shutting down")

app = FastAPI(title="OCPP Central System Server", lifespan=lifespan)

# Include routers
app.include_router(api_router)
app.include_router(db_router)

# Add WebSocket endpoint
app.add_api_websocket_route("/ocpp/{charge_point_id}", websocket_endpoint)