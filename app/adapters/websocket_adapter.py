import asyncio
import logging
from fastapi import WebSocket

logger = logging.getLogger("ocpp.adapter")

class WebSocketAdapter:
    def __init__(self, websocket):
        self.websocket = websocket
        self.created_at = asyncio.get_event_loop().time()
        
    async def recv(self) -> str:
        message = await self.websocket.receive_text()
        logger.info(f"⬅️  Received from Charge Point: {message}")
        return message
        
    async def send(self, message: str) -> None:
        logger.info(f"➡️  Sending to Charge Point: {message}")
        await self.websocket.send_text(message)



