import asyncio
import logging
from fastapi import WebSocket

logger = logging.getLogger("ocpp-server")

class WebSocketAdapter:
    def __init__(self, websocket: WebSocket):
        self.websocket = websocket
        self.created_at = asyncio.get_event_loop().time()

    async def recv(self) -> str:
        message = await self.websocket.receive_text()
        logger.info(f"Received: {message}")
        return message

    async def send(self, message: str) -> None:
        logger.info(f"Sending: {message}")
        await self.websocket.send_text(message)
