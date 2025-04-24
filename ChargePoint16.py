"""
ChargePoint implementation for OCPP 1.6
"""
import logging
from datetime import datetime
import sys
from pathlib import Path

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

    @on(Action.boot_notification)
    def on_boot_notification(self, **kwargs):
        logging.debug("Received a BootNotification")
        return call_result.BootNotification(
            current_time=datetime.now().isoformat(),
            interval=300, 
            status=RegistrationStatus.accepted
        )

    @on(Action.status_notification)
    def on_status_notification(self, **kwargs):
        return call_result.StatusNotification()

    @on(Action.heartbeat)
    def on_heartbeat(self, **kwargs):
        return call_result.Heartbeat(current_time=datetime.now().isoformat())

    @on(Action.authorize)
    def on_authorize(self, **kwargs):
        return call_result.Authorize(
            id_tag_info=IdTagInfo(
                status=AuthorizationStatus.accepted
            )
        )

    @on(Action.start_transaction)
    def on_start_transaction(self, **kwargs):
        id_tag_info = IdTagInfo(status=AuthorizationStatus.accepted)
        return call_result.StartTransaction(
            transaction_id=1,
            id_tag_info=id_tag_info
        )

    @on(Action.stop_transaction)
    def on_stop_transaction(self, **kwargs):
        return call_result.StopTransaction(
            id_tag_info=IdTagInfo(status=AuthorizationStatus.accepted)
        )

    @on(Action.meter_values)
    def on_meter_values(self, **kwargs):
        return call_result.MeterValues()

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

