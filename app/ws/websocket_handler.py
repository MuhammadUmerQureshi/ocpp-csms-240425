from fastapi import WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.orm import Session
from app.adapters.websocket_adapter import WebSocketAdapter
from app.services.ChargePoint16 import ChargePoint16
from app.ws.connection_manager import manager
from app.database.database import get_db
from app.database.repositories.repositories import ChargerRepository
import logging
import httpx
import asyncio

logger = logging.getLogger("ocpp-server")

async def websocket_endpoint(websocket: WebSocket, charge_point_id: str):
    requested_protocols = websocket.headers.get("sec-websocket-protocol", "")
    if "ocpp1.6" not in requested_protocols:
        logger.error(f"Client {charge_point_id} missing OCPP protocol.")
        return

    try:
        await websocket.accept(subprotocol="ocpp1.6")
        logger.info(f"Accepted OCPP 1.6 connection from {charge_point_id}")
        adapter = WebSocketAdapter(websocket)
        cp = ChargePoint16(charge_point_id, adapter)
        await manager.connect(charge_point_id, cp)
        
        # Update charger status in the database (async)
        asyncio.create_task(update_charger_connection_status(charge_point_id, True))
        
        await cp.start()

    except WebSocketDisconnect:
        logger.info(f"Charge point {charge_point_id} disconnected")
    except Exception as e:
        logger.error(f"Error with charge point {charge_point_id}: {e}", exc_info=True)
    finally:
        manager.disconnect(charge_point_id)
        # Update charger status in the database (async)
        asyncio.create_task(update_charger_connection_status(charge_point_id, False))

async def update_charger_connection_status(charge_point_id: str, connected: bool):
    """Update charger connection status in the database using the API endpoint"""
    try:
        status = "Available" if connected else "Unavailable"
        is_online = connected
        
        # Use httpx to call our own API endpoint
        async with httpx.AsyncClient() as client:
            response = await client.put(
                f"http://localhost:8000/db/companies/DEF01/sites/MAIN/chargers/{charge_point_id}/status",
                params={"status": status, "is_online": is_online}
            )
            
            if response.status_code != 200:
                logger.warning(f"Failed to update charger status: {response.text}")
    except Exception as e:
        logger.error(f"Error updating charger connection status: {e}", exc_info=True)