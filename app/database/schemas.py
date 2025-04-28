from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

# Base schemas for request and response models

# Company schemas
class CompanyBase(BaseModel):
    CompanyName: str
    CompanyEnabled: bool = True
    CompanyHomePhoto: Optional[str] = None
    CompanyBrandColour: Optional[str] = None
    CompanyBrandLogo: Optional[str] = None
    CompanyBrandFavicon: Optional[str] = None

class CompanyCreate(CompanyBase):
    CompanyId: str

class CompanyUpdate(CompanyBase):
    CompanyName: Optional[str] = None
    CompanyEnabled: Optional[bool] = None

class CompanyResponse(CompanyBase):
    CompanyId: str
    CompanyCreated: datetime
    CompanyUpdated: Optional[datetime] = None

    class Config:
        orm_mode = True

# Site schemas
class SiteBase(BaseModel):
    SiteName: str
    SiteEnabled: bool = True
    SiteGroupId: Optional[str] = None
    SiteAddress: Optional[str] = None
    SiteCity: Optional[str] = None
    SiteRegion: Optional[str] = None
    SiteCountry: Optional[str] = None
    SiteZipCode: Optional[str] = None
    SiteGeoCoord: Optional[str] = None
    SiteTaxRate: Optional[int] = None
    SiteContactName: Optional[str] = None
    SiteContactPh: Optional[str] = None
    SiteContactEmail: Optional[str] = None

class SiteCreate(SiteBase):
    SiteCompanyID: str
    SiteId: str

class SiteUpdate(SiteBase):
    SiteName: Optional[str] = None
    SiteEnabled: Optional[bool] = None

class SiteResponse(SiteBase):
    SiteCompanyID: str
    SiteId: str
    SiteCreated: datetime
    SiteUpdated: Optional[datetime] = None

    class Config:
        orm_mode = True

# Charger schemas
class ChargerBase(BaseModel):
    ChargerName: str
    ChargerEnabled: bool = True
    ChargerBrand: Optional[str] = None
    ChargerModel: Optional[str] = None
    Charger_Type: Optional[str] = None
    ChargerSerial: Optional[str] = None
    ChargerGeoCoord: Optional[str] = None
    ChargerGroupId: Optional[str] = None
    ChargerMeter: Optional[str] = None
    ChargerMeterSerial: Optional[str] = None
    ChargerPincode: Optional[str] = None
    ChargerWsURL: Optional[str] = None
    Charger_Availability: Optional[str] = None
    ChargerIsOnline: bool = False
    ChargerStatusNow: Optional[str] = None
    Charger_Access_Type: Optional[str] = None
    ChargerConnectorId1: Optional[str] = None
    ChargerConnectorId2: Optional[str] = None
    ChargerActive24x7: bool = True
    ChargerPhoto: Optional[str] = None
    ChargerFirmwareVersion: Optional[str] = None
    ChargerPaymentId: Optional[str] = None

class ChargerCreate(ChargerBase):
    ChargerCompanyId: str
    ChargerSiteId: str
    ChargerId: str

class ChargerUpdate(ChargerBase):
    ChargerName: Optional[str] = None
    ChargerEnabled: Optional[bool] = None

class ChargerResponse(ChargerBase):
    ChargerCompanyId: str
    ChargerSiteId: str
    ChargerId: str
    ChargerCreated: datetime
    Charger_Updated: Optional[datetime] = None

    class Config:
        orm_mode = True

# Connector schemas
class ConnectorBase(BaseModel):
    ConnectorName: str
    ConnectorType: str
    ConnectorEnabled: bool = True
    ConnectorStatus: Optional[str] = None
    ConnectorRatedPowerKW: Optional[int] = None

class ConnectorCreate(ConnectorBase):
    ConnectorCompanyId: str
    ConnectorSiteId: str
    ConnectorChargerId: str
    ConnectorId: str

class ConnectorUpdate(ConnectorBase):
    ConnectorName: Optional[str] = None
    ConnectorType: Optional[str] = None
    ConnectorEnabled: Optional[bool] = None
    ConnectorStatus: Optional[str] = None
    ConnectorRatedPowerKW: Optional[int] = None

class ConnectorResponse(ConnectorBase):
    ConnectorCompanyId: str
    ConnectorSiteId: str
    ConnectorChargerId: str
    ConnectorId: str
    ConnectorCreated: datetime
    ConnectorUpdated: Optional[datetime] = None

    class Config:
        orm_mode = True

# Driver schemas
class DriverBase(BaseModel):
    DriverFullName: str
    DriverEnabled: bool = True
    DriverEmail: Optional[str] = None
    DriverPhone: Optional[str] = None
    DriverGroupId: Optional[str] = None
    DriverNotifActions: bool = False
    DriverNotifPayments: bool = False
    DriverNotifSystem: bool = False
    DriverTariffId: Optional[str] = None

class DriverCreate(DriverBase):
    DriverCompanyId: str
    DriverId: str

class DriverUpdate(DriverBase):
    DriverFullName: Optional[str] = None
    DriverEnabled: Optional[bool] = None

class DriverResponse(DriverBase):
    DriverCompanyId: str
    DriverId: str
    DriverCreated: datetime
    DriverUpdated: Optional[datetime] = None

    class Config:
        orm_mode = True

# RFIDCard schemas
class RFIDCardBase(BaseModel):
    RFIDCardEnabled: bool = True
    RFIDCardNameOn: Optional[str] = None
    RFIDCardNumberOn: Optional[str] = None
    RFIDCardExpiration: Optional[datetime] = None

class RFIDCardCreate(RFIDCardBase):
    RFIDCardCompanyId: str
    RFIDCardDriverId: str
    RFIDCardId: str

class RFIDCardUpdate(RFIDCardBase):
    RFIDCardEnabled: Optional[bool] = None

class RFIDCardResponse(RFIDCardBase):
    RFIDCardCompanyId: str
    RFIDCardDriverId: str
    RFIDCardId: str
    RFIDCardCreated: datetime
    RFIDCardUpdated: Optional[datetime] = None

    class Config:
        orm_mode = True

# ChargeSession schemas
class ChargeSessionBase(BaseModel):
    ChargerSessionCompanyId: str
    ChargerSessionSiteId: str
    ChargerSessionChargerId: str
    ChargerSessionConnectorId: str
    ChargerSessionDriverId: Optional[str] = None
    ChargerSessionRFIDCard: Optional[str] = None
    ChargerSessionStart: datetime
    ChargerSessionEnd: Optional[datetime] = None
    ChargerSessionReason: Optional[str] = None
    ChargerSessionStatus: str
    ChargerSessionEnergyKWH: Optional[int] = None
    ChargerSessionPricingPlanId: Optional[str] = None
    ChargerSessionCost: Optional[float] = None
    ChargerSessionDiscountId: Optional[str] = None
    ChargerSessionPaymentId: Optional[str] = None
    ChargerSessionPaymentAmount: Optional[float] = None
    ChargerSessionPaymentStatus: Optional[str] = None

class ChargeSessionCreate(ChargeSessionBase):
    pass

class ChargeSessionUpdate(BaseModel):
    ChargerSessionEnd: Optional[datetime] = None
    ChargerSessionReason: Optional[str] = None
    ChargerSessionStatus: Optional[str] = None
    ChargerSessionEnergyKWH: Optional[int] = None
    ChargerSessionCost: Optional[float] = None
    ChargerSessionPaymentId: Optional[str] = None
    ChargerSessionPaymentAmount: Optional[float] = None
    ChargerSessionPaymentStatus: Optional[str] = None

class ChargeSessionResponse(ChargeSessionBase):
    ChargeSessionId: int
    ChargerSessionDuration: Optional[int] = None
    ChargerSessionCreated: datetime

    class Config:
        orm_mode = True

# EventsData schemas
class EventsDataBase(BaseModel):
    EventsDataCompanyId: str
    EventsDataSiteId: str
    EventsDataChargerId: str
    EventsDataConnectorId: str
    EventsDataDateTime: datetime
    EventsDataType: str
    EventsDataTriggerReason: Optional[str] = None
    EventsDataOrigin: Optional[str] = None
    EventsDataData: Optional[str] = None
    EventsDataTemperature: Optional[int] = None
    EventsDataCurrent: Optional[int] = None
    EventsDataVoltage: Optional[int] = None
    EventsDataMeterValue: Optional[str] = None

class EventsDataCreate(EventsDataBase):
    EventsDataSessionId: int

class EventsDataResponse(EventsDataBase):
    EventsDataSessionId: int

    class Config:
        orm_mode = True