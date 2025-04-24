from fastapi import WebSocket, WebSocketDisconnect
from app.adapters.websocket_adapter import WebSocketAdapter
from app.services.ChargePoint16 import ChargePoint16
from app.ws.connection_manager import manager
import logging

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
        await cp.start()

    except WebSocketDisconnect:
        logger.info(f"Charge point {charge_point_id} disconnected")
    except Exception as e:
        logger.error(f"Error with charge point {charge_point_id}: {e}", exc_info=True)
    finally:
        manager.disconnect(charge_point_id)
