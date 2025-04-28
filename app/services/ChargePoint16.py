"""
ChargePoint implementation for OCPP 1.6
"""
import logging
from datetime import datetime
import sys
from pathlib import Path
import httpx
import asyncio

from ocpp.routing import on
from ocpp.v16 import ChargePoint as cp
from ocpp.v16 import call, call_result
from ocpp.v16.datatypes import IdTagInfo
from ocpp.v16.enums import (
    Action,
    RegistrationStatus,
    AuthorizationStatus,
    ConfigurationStatus,
    TriggerMessageStatus,
    ClearCacheStatus,
    ResetStatus,
    UnlockStatus,
    AvailabilityStatus,
    RemoteStartStopStatus,
    ChargingProfileStatus,
    ReservationStatus,
    CancelReservationStatus,
    UpdateStatus,
    DataTransferStatus,
    CertificateSignedStatus,
    DeleteCertificateStatus,
    CertificateStatus,
    GetInstalledCertificateStatus,
    LogStatus,
    GenericStatus
)

def setup_logger(logger_name):
    """Set up a logger instance."""
    logger = logging.getLogger(logger_name)
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    return logger

# Set up logging
logger = setup_logger("ocpp_charge_point")

class ChargePoint16(cp):
    """
    ChargePoint implementation for OCPP 1.6
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.transaction_id = 0

    @on(Action.boot_notification)
    def on_boot_notification(self, **kwargs):
        """Handle BootNotification from Charge Point"""
        logger.info(f"Received BootNotification from {self.id}: {kwargs}")
        
        # Register charge point in the database
        asyncio.create_task(self._register_charger_in_db(kwargs))
        
        return call_result.BootNotification(
            current_time=datetime.now().isoformat(),
            interval=300, 
            status=RegistrationStatus.accepted
        )

    @on(Action.status_notification)
    def on_status_notification(self, **kwargs):
        """Handle StatusNotification from Charge Point"""
        logger.info(f"Received StatusNotification from {self.id}: {kwargs}")
        
        # Update connector status in the database
        asyncio.create_task(self._update_connector_status_in_db(kwargs))
        
        return call_result.StatusNotification()

    @on(Action.heartbeat)
    def on_heartbeat(self, **kwargs):
        """Handle Heartbeat from Charge Point"""
        logger.info(f"Received Heartbeat from {self.id}")
        
        # Update heartbeat in the database
        asyncio.create_task(self._update_heartbeat_in_db())
        
        return call_result.Heartbeat(current_time=datetime.now().isoformat())

    @on(Action.authorize)
    def on_authorize(self, **kwargs):
        """Handle Authorize from Charge Point"""
        id_tag = kwargs.get('id_tag')
        logger.info(f"Received Authorize from {self.id} with id_tag: {id_tag}")
        
        # In a real implementation, you'd validate the ID tag against the database
        # For now, we'll always accept
        
        return call_result.Authorize(
            id_tag_info=IdTagInfo(
                status=AuthorizationStatus.accepted
            )
        )

    @on(Action.start_transaction)
    def on_start_transaction(self, **kwargs):
        """Handle StartTransaction from Charge Point"""
        id_tag = kwargs.get('id_tag')
        connector_id = kwargs.get('connector_id')
        meter_start = kwargs.get('meter_start')
        
        logger.info(f"Received StartTransaction from {self.id} on connector {connector_id}")
        
        # Start charging session in the database
        self.transaction_id += 1  # In a real implementation, this should be fetched from the database
        transaction_id = self.transaction_id
        
        # Start session in the database
        asyncio.create_task(self._start_session_in_db(connector_id, id_tag, transaction_id))
        
        id_tag_info = IdTagInfo(status=AuthorizationStatus.accepted)
        return call_result.StartTransaction(
            transaction_id=transaction_id,
            id_tag_info=id_tag_info
        )

    @on(Action.stop_transaction)
    def on_stop_transaction(self, **kwargs):
        """Handle StopTransaction from Charge Point"""
        transaction_id = kwargs.get('transaction_id')
        id_tag = kwargs.get('id_tag')
        meter_stop = kwargs.get('meter_stop')
        timestamp = kwargs.get('timestamp')
        reason = kwargs.get('reason', 'Local')
        
        logger.info(f"Received StopTransaction from {self.id} for transaction {transaction_id}")
        
        # End session in the database
        asyncio.create_task(self._end_session_in_db(transaction_id, meter_stop, reason))
        
        return call_result.StopTransaction(
            id_tag_info=IdTagInfo(status=AuthorizationStatus.accepted)
        )

    @on(Action.meter_values)
    def on_meter_values(self, **kwargs):
        """Handle MeterValues from Charge Point"""
        connector_id = kwargs.get('connector_id')
        transaction_id = kwargs.get('transaction_id')
        meter_values = kwargs.get('meter_value', [])
        
        logger.info(f"Received MeterValues from {self.id} for connector {connector_id}")
        
        # Process meter values
        if transaction_id and meter_values:
            # Extract meter value (simplified)
            # In a real implementation, you'd parse the sampled_value structure properly
            try:
                if len(meter_values) > 0 and 'sampled_value' in meter_values[0]:
                    sampled_value = meter_values[0]['sampled_value'][0]
                    if 'value' in sampled_value:
                        value = float(sampled_value['value'])
                        # Update meter value in the database
                        asyncio.create_task(self._update_meter_value_in_db(
                            transaction_id, connector_id, int(value)
                        ))
            except Exception as e:
                logger.error(f"Error processing meter values: {e}")
        
        return call_result.MeterValues()

    async def _register_charger_in_db(self, boot_notification_data):
        """Register charger in the database via API call"""
        try:
            vendor = boot_notification_data.get('charge_point_vendor', 'Unknown')
            model = boot_notification_data.get('charge_point_model', 'Unknown')
            serial = boot_notification_data.get('charge_point_serial_number')
            firmware = boot_notification_data.get('firmware_version')
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "http://localhost:8000/db/ocpp/charger/register",
                    params={
                        "charger_id": self.id,
                        "vendor": vendor,
                        "model": model,
                        "serial_number": serial,
                        "firmware_version": firmware
                    }
                )
                
                if response.status_code != 200:
                    logger.warning(f"Failed to register charger: {response.text}")
                else:
                    logger.info(f"Charger {self.id} registered successfully in database")
        except Exception as e:
            logger.error(f"Error registering charger: {e}")

    async def _update_connector_status_in_db(self, status_data):
        """Update connector status in the database via API call"""
        try:
            connector_id = str(status_data.get('connector_id', '0'))
            status = status_data.get('status', 'Available')
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "http://localhost:8000/db/ocpp/connector/status",
                    params={
                        "charger_id": self.id,
                        "connector_id": connector_id,
                        "status": status
                    }
                )
                
                if response.status_code != 200:
                    logger.warning(f"Failed to update connector status: {response.text}")
                else:
                    logger.info(f"Connector {self.id}/{connector_id} status updated to {status}")
        except Exception as e:
            logger.error(f"Error updating connector status: {e}")

    async def _update_heartbeat_in_db(self):
        """Update heartbeat in the database via API call"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "http://localhost:8000/db/ocpp/charger/heartbeat",
                    params={"charger_id": self.id}
                )
                
                if response.status_code != 200:
                    logger.warning(f"Failed to update heartbeat: {response.text}")
                else:
                    logger.debug(f"Heartbeat for {self.id} updated in database")
        except Exception as e:
            logger.error(f"Error updating heartbeat: {e}")

    async def _start_session_in_db(self, connector_id, id_tag, transaction_id):
        """Start charging session in the database via API call"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "http://localhost:8000/db/ocpp/session/start",
                    params={
                        "charger_id": self.id,
                        "connector_id": connector_id,
                        "id_tag": id_tag,
                        "transaction_id": transaction_id
                    }
                )
                
                if response.status_code != 200:
                    logger.warning(f"Failed to start charging session: {response.text}")
                else:
                    logger.info(f"Started charging session for {self.id}/{connector_id}")
        except Exception as e:
            logger.error(f"Error starting charging session: {e}")

    async def _end_session_in_db(self, transaction_id, meter_stop, reason):
        """End charging session in the database via API call"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "http://localhost:8000/db/ocpp/session/end",
                    params={
                        "charger_id": self.id,
                        "connector_id": "1",  # Ideally should be fetched from active session
                        "transaction_id": transaction_id,
                        "meter_value": meter_stop,
                        "reason": reason
                    }
                )
                
                if response.status_code != 200:
                    logger.warning(f"Failed to end charging session: {response.text}")
                else:
                    logger.info(f"Ended charging session for transaction {transaction_id}")
        except Exception as e:
            logger.error(f"Error ending charging session: {e}")

    async def _update_meter_value_in_db(self, transaction_id, connector_id, meter_value):
        """Update meter value in the database via API call"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "http://localhost:8000/db/ocpp/meter-values",
                    params={
                        "charger_id": self.id,
                        "connector_id": connector_id,
                        "transaction_id": transaction_id,
                        "meter_value": meter_value
                    }
                )
                
                if response.status_code != 200:
                    logger.warning(f"Failed to update meter value: {response.text}")
                else:
                    logger.debug(f"Updated meter value for transaction {transaction_id} to {meter_value}")
        except Exception as e:
            logger.error(f"Error updating meter value: {e}")

    async def change_configuration_req(self, key, value):
        payload = call.ChangeConfiguration(key=key, value=value)
        return await self.call(payload)

    async def reset_req(self, type):
        payload = call.Reset(type=type)
        return await self.call(payload)

    async def unlock_connector_req(self, connector_id):
        payload = call.UnlockConnector(connector_id=connector_id)
        return await self.call(payload)

    async def get_configuration_req(self, key=None):
        payload = call.GetConfiguration(key=key)
        return await self.call(payload)

    async def change_availability_req(self, connector_id, type):
        payload = call.ChangeAvailability(connector_id=connector_id, type=type)
        return await self.call(payload)

    async def remote_start_transaction_req(self, id_tag, connector_id=None, charging_profile=None):
        payload = call.RemoteStartTransaction(
            id_tag=id_tag,
            connector_id=connector_id,
            charging_profile=charging_profile
        )
        return await self.call(payload)

    async def remote_stop_transaction_req(self, transaction_id):
        payload = call.RemoteStopTransaction(transaction_id=transaction_id)
        return await self.call(payload)

    async def set_charging_profile_req(self, connector_id, cs_charging_profiles):
        payload = call.SetChargingProfile(
            connector_id=connector_id,
            cs_charging_profiles=cs_charging_profiles
        )
        return await self.call(payload)

    async def reserve_now_req(self, connector_id, expiry_date, id_tag, reservation_id, parent_id_tag=None):
        payload = call.ReserveNow(
            connector_id=connector_id,
            expiry_date=expiry_date,
            id_tag=id_tag,
            reservation_id=reservation_id,
            parent_id_tag=parent_id_tag
        )
        return await self.call(payload)

    async def cancel_reservation_req(self, reservation_id):
        payload = call.CancelReservation(reservation_id=reservation_id)
        return await self.call(payload)