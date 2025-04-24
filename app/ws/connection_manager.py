from typing import Dict
from app.services.ChargePoint16 import ChargePoint16
import logging

logger = logging.getLogger("ocpp-server")

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, ChargePoint16] = {}

    async def connect(self, charge_point_id: str, charge_point: ChargePoint16):
        self.active_connections[charge_point_id] = charge_point
        logger.info(f"Charge point {charge_point_id} connected. Active: {len(self.active_connections)}")

    def disconnect(self, charge_point_id: str):
        if charge_point_id in self.active_connections:
            del self.active_connections[charge_point_id]
            logger.info(f"Charge point {charge_point_id} disconnected. Active: {len(self.active_connections)}")

    def get_charge_points(self):
        return self.active_connections

manager = ConnectionManager()
