"""
OCPP 1.6 ChargePoint Simulator

This script simulates a charging station communicating over OCPP 1.6 protocol.
It connects to an OCPP Central System and simulates a typical charging session.
"""
import asyncio
import logging
import sys
import uuid
from datetime import datetime
import websockets
import json
import argparse

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("cp.simulator")

class ChargePointSimulator:
    """
    Simulates a charge point (charging station) that communicates 
    with a Central System using OCPP 1.6 over WebSocket
    """
    def __init__(self, cp_id, csms_url, connector_count=1):
        self.cp_id = cp_id
        self.csms_url = csms_url
        self.connector_count = connector_count
        self.websocket = None
        self.connection_closed = False
        self.transaction_id = None
        self.message_queue = asyncio.Queue()
        
        # For tracking message responses
        self.waiting_for_response = {}

    async def connect(self):
        """Establish WebSocket connection to the CSMS"""
        try:
            connection_url = f"{self.csms_url}/{self.cp_id}"
            logger.info(f"Connecting to {connection_url}")
            
            # Connect with the ocpp1.6 subprotocol
            self.websocket = await websockets.connect(
                connection_url,
                subprotocols=["ocpp1.6"],
                ping_interval=30,
                ping_timeout=10
            )
            
            logger.info(f"Connected to {connection_url}")
            return True
        except Exception as e:
            logger.error(f"Connection failed: {e}")
            return False

    async def start(self):
        """Start the charge point simulation"""
        if not await self.connect():
            return
        
        # Start message handling tasks
        send_task = asyncio.create_task(self.send_messages())
        receive_task = asyncio.create_task(self.receive_messages())
        
        # Start the simulation flow
        simulation_task = asyncio.create_task(self.run_simulation())
        
        # Wait for all tasks to complete
        await asyncio.gather(
            send_task, 
            receive_task, 
            simulation_task,
            return_exceptions=True
        )

    async def run_simulation(self):
        """Run a complete charging simulation sequence"""
        try:
            # 1. Boot notification
            await self.send_boot_notification()
            await asyncio.sleep(2)
            
            # 2. Status notification - changing to available
            for connector_id in range(1, self.connector_count + 1):
                await self.send_status_notification(connector_id, "Available")
            await asyncio.sleep(2)
            
            # 3. Heartbeat
            await self.send_heartbeat()
            await asyncio.sleep(5)
            
            # 4. Authorize a user
            await self.send_authorize("RFID1234567890")
            await asyncio.sleep(2)
            
            # 5. Start transaction
            connector_id = 1
            await self.send_status_notification(connector_id, "Preparing")
            await asyncio.sleep(1)
            await self.start_transaction(connector_id, "RFID1234567890")
            await asyncio.sleep(2)
            
            # 6. Set status to charging
            await self.send_status_notification(connector_id, "Charging")
            
            # 7. Send meter values periodically
            for i in range(3):
                meter_value = 10000 + (i * 100)  # Simulated energy consumption
                await self.send_meter_values(connector_id, meter_value)
                await asyncio.sleep(5)
            
            # 8. Stop transaction
            meter_stop = 10300  # Final meter reading
            await self.stop_transaction("RFID1234567890", meter_stop)
            await asyncio.sleep(2)
            
            # 9. Set status back to available
            await self.send_status_notification(connector_id, "Finishing")
            await asyncio.sleep(1)
            await self.send_status_notification(connector_id, "Available")
            
            # 10. Continue with heartbeats
            for _ in range(3):
                await asyncio.sleep(10)
                await self.send_heartbeat()
                
            logger.info("Simulation completed successfully")
                
        except Exception as e:
            logger.error(f"Simulation error: {e}")

    async def send_messages(self):
        """Send messages from queue to CSMS"""
        try:
            while not self.connection_closed:
                # Check connection state in a compatible way with different websockets versions
                try:
                    if hasattr(self.websocket, "closed") and self.websocket.closed:
                        logger.info("WebSocket closed, stopping send_messages task")
                        break
                    elif hasattr(self.websocket, "is_closing") and self.websocket.is_closing():
                        logger.info("WebSocket is closing, stopping send_messages task")
                        break
                except Exception:
                    # If we can't check the state, just continue
                    pass
                
                message = await self.message_queue.get()
                message_id = message[1]
                await self.websocket.send(json.dumps(message))
                logger.info(f"Sent message: {message}")
                self.message_queue.task_done()
                
        except websockets.exceptions.ConnectionClosed:
            logger.info("WebSocket connection closed")
            self.connection_closed = True
        except Exception as e:
            logger.error(f"Error in send_messages: {e}")
            self.connection_closed = True

    async def receive_messages(self):
        """Receive and process messages from CSMS"""
        try:
            while not self.connection_closed:
                # Check connection state in a compatible way with different websockets versions
                try:
                    if hasattr(self.websocket, "closed") and self.websocket.closed:
                        logger.info("WebSocket closed, stopping receive_messages task")
                        break
                    elif hasattr(self.websocket, "is_closing") and self.websocket.is_closing():
                        logger.info("WebSocket is closing, stopping receive_messages task")
                        break
                except Exception:
                    # If we can't check the state, just continue
                    pass
                    
                message = await self.websocket.recv()
                logger.info(f"Received message: {message}")
                await self.handle_message(message)
                
        except websockets.exceptions.ConnectionClosed:
            logger.info("WebSocket connection closed")
            self.connection_closed = True
        except Exception as e:
            logger.error(f"Error in receive_messages: {e}")
            self.connection_closed = True

    async def handle_message(self, message):
        """Process incoming messages from CSMS"""
        try:
            parsed_message = json.loads(message)
            message_type_id = parsed_message[0]
            
            if message_type_id == 3:  # CALLRESULT
                unique_id = parsed_message[1]
                payload = parsed_message[2]
                
                # Handle specific response actions
                if unique_id in self.waiting_for_response:
                    action = self.waiting_for_response[unique_id]
                    await self.handle_response(action, payload)
                    del self.waiting_for_response[unique_id]
                    
            elif message_type_id == 2:  # CALL (from CSMS to CP)
                unique_id = parsed_message[1]
                action = parsed_message[2]
                payload = parsed_message[3]
                
                await self.handle_call(unique_id, action, payload)
                
            elif message_type_id == 4:  # CALLERROR
                logger.error(f"Received CALLERROR: {parsed_message}")
                
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON message: {message}")
        except Exception as e:
            logger.error(f"Error handling message: {e}")

    async def handle_response(self, action, payload):
        """Handle responses to our requests"""
        if action == "BootNotification":
            if payload.get("status") == "Accepted":
                logger.info(f"Boot notification accepted, interval: {payload.get('interval')}")
                
        elif action == "StartTransaction":
            if "transactionId" in payload:
                self.transaction_id = payload["transactionId"]
                logger.info(f"Transaction started with ID: {self.transaction_id}")
                
        elif action == "StopTransaction":
            logger.info("Transaction stopped successfully")

    async def handle_call(self, unique_id, action, payload):
        """Handle incoming requests from CSMS"""
        response_payload = {}
        
        if action == "Reset":
            logger.info(f"Received Reset command: {payload}")
            response_payload = {"status": "Accepted"}
            
        elif action == "RemoteStartTransaction":
            logger.info(f"Received RemoteStartTransaction: {payload}")
            # Here you could automatically start a transaction
            response_payload = {"status": "Accepted"}
            
        elif action == "RemoteStopTransaction":
            logger.info(f"Received RemoteStopTransaction: {payload}")
            # Here you could stop the active transaction
            response_payload = {"status": "Accepted"}
            
        elif action == "UnlockConnector":
            logger.info(f"Received UnlockConnector: {payload}")
            response_payload = {"status": "Unlocked"}
            
        elif action == "GetConfiguration":
            logger.info(f"Received GetConfiguration: {payload}")
            response_payload = {
                "configurationKey": [
                    {"key": "HeartbeatInterval", "readonly": False, "value": "60"}
                ],
                "unknownKey": []
            }
            
        elif action == "ChangeConfiguration":
            logger.info(f"Received ChangeConfiguration: {payload}")
            response_payload = {"status": "Accepted"}
            
        elif action == "TriggerMessage":
            logger.info(f"Received TriggerMessage: {payload}")
            response_payload = {"status": "Accepted"}
            
        else:
            logger.warning(f"Unhandled action {action}: {payload}")
            response_payload = {"status": "NotImplemented"}
        
        # Send response
        response = [3, unique_id, response_payload]
        await self.websocket.send(json.dumps(response))
        logger.info(f"Sent response to {action}: {response}")

    async def send_boot_notification(self):
        """Send a BootNotification request"""
        message_id = str(uuid.uuid4())
        self.waiting_for_response[message_id] = "BootNotification"
        
        message = [
            2,  # Message Type ID for Call
            message_id,
            "BootNotification",
            {
                "chargePointVendor": "TestVendor",
                "chargePointModel": "TestModel",
                "chargePointSerialNumber": f"{self.cp_id}-SN001",
                "chargeBoxSerialNumber": f"{self.cp_id}-CB001",
                "firmwareVersion": "1.0.0",
                "iccid": "",
                "imsi": "",
                "meterType": "Test Meter",
                "meterSerialNumber": f"{self.cp_id}-M001"
            }
        ]
        
        await self.message_queue.put(message)

    async def send_heartbeat(self):
        """Send a Heartbeat request"""
        message_id = str(uuid.uuid4())
        self.waiting_for_response[message_id] = "Heartbeat"
        
        message = [
            2,  # Message Type ID for Call
            message_id,
            "Heartbeat",
            {}
        ]
        
        await self.message_queue.put(message)

    async def send_status_notification(self, connector_id, status):
        """Send a StatusNotification request"""
        message_id = str(uuid.uuid4())
        self.waiting_for_response[message_id] = "StatusNotification"
        
        message = [
            2,  # Message Type ID for Call
            message_id,
            "StatusNotification",
            {
                "connectorId": connector_id,
                "errorCode": "NoError",
                "status": status,
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "info": f"Connector {connector_id} status change to {status}",
                "vendorId": "TestVendor",
                "vendorErrorCode": ""
            }
        ]
        
        await self.message_queue.put(message)

    async def send_authorize(self, id_tag):
        """Send an Authorize request"""
        message_id = str(uuid.uuid4())
        self.waiting_for_response[message_id] = "Authorize"
        
        message = [
            2,  # Message Type ID for Call
            message_id,
            "Authorize",
            {
                "idTag": id_tag
            }
        ]
        
        await self.message_queue.put(message)

    async def start_transaction(self, connector_id, id_tag):
        """Start a charging transaction"""
        message_id = str(uuid.uuid4())
        self.waiting_for_response[message_id] = "StartTransaction"
        
        message = [
            2,  # Message Type ID for Call
            message_id,
            "StartTransaction",
            {
                "connectorId": connector_id,
                "idTag": id_tag,
                "meterStart": 10000,  # Initial meter reading in Wh
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }
        ]
        
        await self.message_queue.put(message)

    async def send_meter_values(self, connector_id, meter_value):
        """Send meter values during a transaction"""
        message_id = str(uuid.uuid4())
        self.waiting_for_response[message_id] = "MeterValues"
        
        message = [
            2,  # Message Type ID for Call
            message_id,
            "MeterValues",
            {
                "connectorId": connector_id,
                "transactionId": self.transaction_id,
                "meterValue": [
                    {
                        "timestamp": datetime.utcnow().isoformat() + "Z",
                        "sampledValue": [
                            {
                                "value": str(meter_value),
                                "context": "Sample.Periodic",
                                "format": "Raw",
                                "measurand": "Energy.Active.Import.Register",
                                "unit": "Wh"
                            },
                            {
                                "value": "20",
                                "context": "Sample.Periodic",
                                "format": "Raw",
                                "measurand": "Current.Import",
                                "unit": "A"
                            },
                            {
                                "value": "230",
                                "context": "Sample.Periodic",
                                "format": "Raw",
                                "measurand": "Voltage",
                                "unit": "V"
                            }
                        ]
                    }
                ]
            }
        ]
        
        await self.message_queue.put(message)

    async def stop_transaction(self, id_tag, meter_stop):
        """Stop a charging transaction"""
        message_id = str(uuid.uuid4())
        self.waiting_for_response[message_id] = "StopTransaction"
        
        message = [
            2,  # Message Type ID for Call
            message_id,
            "StopTransaction",
            {
                "transactionId": self.transaction_id,
                "idTag": id_tag,
                "meterStop": meter_stop,
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "reason": "Local"
            }
        ]
        
        await self.message_queue.put(message)

async def main():
    parser = argparse.ArgumentParser(description='OCPP 1.6 Charge Point Simulator')
    parser.add_argument('--id', type=str, default='CP001', help='Charge Point ID')
    parser.add_argument('--url', type=str, default='ws://localhost:9000/ocpp', help='CSMS WebSocket URL')
    parser.add_argument('--connectors', type=int, default=1, help='Number of connectors')
    
    args = parser.parse_args()
    
    cp = ChargePointSimulator(args.id, args.url, args.connectors)
    await cp.start()
    
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Simulator stopped by user")