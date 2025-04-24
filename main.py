import logging
import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from typing import Dict

# Import the ChargePoint16 class we created earlier
from ChargePoint16 import ChargePoint16

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s"
)
logger = logging.getLogger("ocpp-server")

app = FastAPI(title="OCPP Central System Server")

# WebSocket adapter to make FastAPI's WebSocket compatible with ocpp library
class WebSocketAdapter:
    def __init__(self, websocket: WebSocket):
        self.websocket = websocket
        self.created_at = asyncio.get_event_loop().time()
        
    async def recv(self) -> str:
        """Receive message from websocket (compatibility with ocpp library)"""
        message = await self.websocket.receive_text()
        logger.debug(f"Received message: {message}")
        return message
        
    async def send(self, message: str) -> None:
        """Send message to websocket (compatibility with ocpp library)"""
        logger.debug(f"Sending message: {message}")
        await self.websocket.send_text(message)

# Store active connections
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, ChargePoint16] = {}
    
    async def connect(self, charge_point_id: str, charge_point: ChargePoint16):
        self.active_connections[charge_point_id] = charge_point
        logger.info(f"Charge point {charge_point_id} connected. Active connections: {len(self.active_connections)}")
    
    def disconnect(self, charge_point_id: str):
        if charge_point_id in self.active_connections:
            del self.active_connections[charge_point_id]
            logger.info(f"Charge point {charge_point_id} disconnected. Active connections: {len(self.active_connections)}")
    
    def get_charge_points(self):
        return self.active_connections

# Initialize connection manager
manager = ConnectionManager()

@app.on_event("startup")
async def startup_event():
    logger.info("OCPP Server starting up")

@app.get("/")
async def root():
    return {"status": "running", "message": "OCPP Server is running"}

@app.get("/charge_points")
async def get_charge_points():
    charge_points = manager.get_charge_points()
    return {"count": len(charge_points), "charge_points": list(charge_points.keys())}

@app.websocket("/ocpp/{charge_point_id}")
async def websocket_endpoint(websocket: WebSocket, charge_point_id: str):
    # Verify WebSocket subprotocol
    requested_protocols = websocket.headers.get("sec-websocket-protocol", "")
    if "ocpp1.6" not in requested_protocols:
        logger.error(f"Client {charge_point_id} hasn't requested OCPP subprotocol. Closing connection.")
        return
    
    try:
        await websocket.accept(subprotocol="ocpp1.6")
        logger.info(f"Accepted connection for {charge_point_id} with OCPP 1.6 subprotocol")
        
        # Create adapter for FastAPI's WebSocket
        adapter = WebSocketAdapter(websocket)
        
        # Create ChargePoint16 instance with our adapter
        cp = ChargePoint16(charge_point_id, adapter)
        
        # Register connection
        await manager.connect(charge_point_id, cp)
        
        # Start message handling for the charge point
        await cp.start()
        
    except WebSocketDisconnect:
        logger.info(f"Charge point {charge_point_id} disconnected")
    except Exception as e:
        logger.error(f"Error handling charge point {charge_point_id}: {e}", exc_info=True)
    finally:
        manager.disconnect(charge_point_id)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=9000)