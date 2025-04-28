from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime, Float, Text, ForeignKeyConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from ..database import Base
from datetime import datetime

class Company(Base):
    __tablename__ = "Companies"
    
    CompanyId = Column(String(5), primary_key=True, index=True)
    CompanyName = Column(String(30))
    CompanyEnabled = Column(Boolean, default=True)
    CompanyHomePhoto = Column(Text)
    CompanyBrandColour = Column(String(10))
    CompanyBrandLogo = Column(Text)
    CompanyBrandFavicon = Column(Text)
    CompanyCreated = Column(DateTime, default=datetime.now)
    CompanyUpdated = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relationships
    sites = relationship("Site", back_populates="company")
    drivers = relationship("Driver", back_populates="company")


class SitesGroup(Base):
    __tablename__ = "SitesGroup"
    
    SitesGroupId = Column(String(5), primary_key=True, index=True)
    SitesGroupName = Column(String(30))
    SitesGroupEnabled = Column(Boolean, default=True)
    SitesGroupCreated = Column(DateTime, default=datetime.now)
    SitesGroupUpdated = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relationships
    sites = relationship("Site", back_populates="sites_group")


class Site(Base):
    __tablename__ = "Sites"
    
    SiteCompanyID = Column(String(5), ForeignKey("Companies.CompanyId"), primary_key=True)
    SiteId = Column(String(5), primary_key=True)
    SiteEnabled = Column(Boolean, default=True)
    SiteName = Column(String(30))
    SiteGroupId = Column(String(5), ForeignKey("SitesGroup.SitesGroupId"))
    SiteAddress = Column(String(40))
    SiteCity = Column(String(30))
    SiteRegion = Column(String(30))
    SiteCountry = Column(String(30))
    SiteZipCode = Column(String(10))
    SiteGeoCoord = Column(String(255))
    SiteTaxRate = Column(Integer)
    SiteContactName = Column(String(50))
    SiteContactPh = Column(String(20))
    SiteContactEmail = Column(String(50))
    SiteCreated = Column(DateTime, default=datetime.now)
    SiteUpdated = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relationships
    company = relationship("Company", back_populates="sites")
    sites_group = relationship("SitesGroup", back_populates="sites")
    chargers = relationship("Charger", back_populates="site")


class Charger(Base):
    __tablename__ = "Chargers"
    
    ChargerCompanyId = Column(String(5), ForeignKey("Companies.CompanyId"), primary_key=True)
    ChargerSiteId = Column(String(5), primary_key=True)
    ChargerId = Column(String(10), primary_key=True)
    ChargerGeoCoord = Column(String(60))
    ChargerName = Column(String(30))
    ChargerGroupId = Column(String(5))
    ChargerBrand = Column(String(30))
    ChargerModel = Column(String(30))
    Charger_Type = Column(String(255))
    ChargerSerial = Column(String(30))
    ChargerMeter = Column(String(10))
    ChargerMeterSerial = Column(String(30))
    ChargerPincode = Column(String(10))
    ChargerWsURL = Column(String(255))
    Charger_Availability = Column(String(20))
    ChargerIsOnline = Column(Boolean, default=False)
    ChargerStatusNow = Column(String(255))
    ChargerEnabled = Column(Boolean, default=True)
    Charger_Access_Type = Column(String(15))
    ChargerConnectorId1 = Column(String(10))
    ChargerConnectorId2 = Column(String(10))
    ChargerActive24x7 = Column(Boolean, default=True)
    ChargerMonFrom = Column(DateTime)
    ChargerMonTo = Column(DateTime)
    ChargerTueFrom = Column(DateTime)
    ChargerTueTo = Column(DateTime)
    ChargerWedFrom = Column(DateTime)
    ChargerWedTo = Column(DateTime)
    ChargerThuFrom = Column(DateTime)
    ChargerThuTo = Column(DateTime)
    ChargerFriFrom = Column(DateTime)
    ChargerFriTo = Column(DateTime)
    ChargerSatFrom = Column(DateTime)
    ChargerSatTo = Column(DateTime)
    ChargerSunFrom = Column(DateTime)
    ChargerSunTo = Column(DateTime)
    ChargerLastConn = Column(DateTime)
    ChargerLastDisconn = Column(DateTime)
    ChargerLastHeartbeat = Column(DateTime)
    ChargerPhoto = Column(Text)
    ChargerFirmwareVersion = Column(String(10))
    ChargerPaymentId = Column(String(5))
    ChargerCreated = Column(DateTime, default=datetime.now)
    Charger_Updated = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Define foreign key relationship
    __table_args__ = (
        ForeignKeyConstraint([
            "ChargerCompanyId", "ChargerSiteId"
        ], [
            "Sites.SiteCompanyID", "Sites.SiteId"
        ]),
    )
    
    # Relationships
    site = relationship("Site", back_populates="chargers")
    connectors = relationship("Connector", back_populates="charger")
    charge_sessions = relationship("ChargeSession", back_populates="charger")


class Connector(Base):
    __tablename__ = "Connectors"
    
    ConnectorCompanyId = Column(String(5), primary_key=True)
    ConnectorSiteId = Column(String(5), primary_key=True)
    ConnectorChargerId = Column(String(10), primary_key=True)
    ConnectorId = Column(String(10), primary_key=True)
    ConnectorName = Column(String(20))
    ConnectorType = Column(String(255))
    ConnectorEnabled = Column(Boolean, default=True)
    ConnectorStatus = Column(String(50))
    ConnectorRatedPowerKW = Column(Integer)
    ConnectorCreated = Column(DateTime, default=datetime.now)
    ConnectorUpdated = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Define foreign key relationship
    __table_args__ = (
        ForeignKeyConstraint([
            "ConnectorCompanyId", "ConnectorSiteId", "ConnectorChargerId"
        ], [
            "Chargers.ChargerCompanyId", "Chargers.ChargerSiteId", "Chargers.ChargerId"
        ]),
    )
    
    # Relationships
    charger = relationship("Charger", back_populates="connectors")


class Driver(Base):
    __tablename__ = "Drivers"
    
    DriverCompanyId = Column(String(5), ForeignKey("Companies.CompanyId"), primary_key=True)
    DriverId = Column(String(10), primary_key=True)
    DriverEnabled = Column(Boolean, default=True)
    DriverFullName = Column(String(30))
    DriverEmail = Column(String(30))
    DriverPhone = Column(String(10))
    DriverGroupId = Column(String(5), ForeignKey("DriversGroup.DriversGroupId"))
    DriverNotifActions = Column(Boolean, default=False)
    DriverNotifPayments = Column(Boolean, default=False)
    DriverNotifSystem = Column(Boolean, default=False)
    DriverTariffId = Column(String(5), ForeignKey("Tariffs.TariffsId"))
    DriverCreated = Column(DateTime, default=datetime.now)
    DriverUpdated = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relationships
    company = relationship("Company", back_populates="drivers")
    drivers_group = relationship("DriversGroup", back_populates="drivers")
    tariff = relationship("Tariff", back_populates="drivers")
    rfid_cards = relationship("RFIDCard", back_populates="driver")


class DriversGroup(Base):
    __tablename__ = "DriversGroup"
    
    DriversGroupId = Column(String(5), primary_key=True, index=True)
    DriversGroupName = Column(String(30))
    DriversGroupEnabled = Column(Boolean, default=True)
    DriversGroupDiscountId = Column(String(5), ForeignKey("Discounts.DiscountId"))
    DriversGroupCreated = Column(DateTime, default=datetime.now)
    DriversGroupUpdated = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relationships
    drivers = relationship("Driver", back_populates="drivers_group")
    discount = relationship("Discount", back_populates="drivers_groups")


class Discount(Base):
    __tablename__ = "Discounts"
    
    DiscountId = Column(String(5), primary_key=True, index=True)
    DiscountName = Column(String(20))
    DiscountEnabled = Column(Boolean, default=True)
    DiscountPercent = Column(Integer)
    DiscountFixedFee = Column(Float)
    DiscountStartDate = Column(DateTime)
    DiscountEndDate = Column(DateTime)
    DiscountCreated = Column(DateTime, default=datetime.now)
    DiscountUpdated = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relationships
    drivers_groups = relationship("DriversGroup", back_populates="discount")
    charge_sessions = relationship("ChargeSession", back_populates="discount")


class Tariff(Base):
    __tablename__ = "Tariffs"
    
    TariffsId = Column(String(5), primary_key=True, index=True)
    TariffsEnabled = Column(Boolean, default=True)
    TariffsName = Column(String(30))
    TariffsType = Column(String(255))
    TariffsFixedStartFee = Column(Float)
    TariffsPerKW = Column(Float)
    TariffsPerMinute = Column(Float)
    TariffsIdleChargingFee = Column(Float)
    TariffsIdleApplyAfter = Column(DateTime)
    TariffsTaxRateDaytime = Column(Integer)
    TariffsTaxRateNighttime = Column(Integer)
    TariffsCreated = Column(DateTime, default=datetime.now)
    TariffsUpdated = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relationships
    drivers = relationship("Driver", back_populates="tariff")
    charge_sessions = relationship("ChargeSession", back_populates="tariff")


class RFIDCard(Base):
    __tablename__ = "RFIDCards"
    
    RFIDCardCompanyId = Column(String(5), primary_key=True)
    RFIDCardDriverId = Column(String(10), primary_key=True)
    RFIDCardId = Column(String(20), primary_key=True)
    RFIDCardEnabled = Column(Boolean, default=True)
    RFIDCardNameOn = Column(String(30))
    RFIDCardNumberOn = Column(String(20))
    RFIDCardExpiration = Column(DateTime)
    RFIDCardCreated = Column(DateTime, default=datetime.now)
    RFIDCardUpdated = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Define foreign key relationship
    __table_args__ = (
        ForeignKeyConstraint([
            "RFIDCardCompanyId", "RFIDCardDriverId"
        ], [
            "Drivers.DriverCompanyId", "Drivers.DriverId"
        ]),
    )
    
    # Relationships
    driver = relationship("Driver", back_populates="rfid_cards")
    charge_sessions = relationship("ChargeSession", back_populates="rfid_card")


class ChargeSession(Base):
    __tablename__ = "ChargeSessions"
    
    ChargeSessionId = Column(Integer, primary_key=True, autoincrement=True)
    ChargerSessionCompanyId = Column(String(5))
    ChargerSessionSiteId = Column(String(5))
    ChargerSessionChargerId = Column(String(10))
    ChargerSessionConnectorId = Column(String(10))
    ChargerSessionDriverId = Column(String(10))
    ChargerSessionRFIDCard = Column(String(20))
    ChargerSessionStart = Column(DateTime)
    ChargerSessionEnd = Column(DateTime)
    ChargerSessionDuration = Column(Integer)  # Store duration in seconds
    ChargerSessionReason = Column(String(20))
    ChargerSessionStatus = Column(String(255))
    ChargerSessionEnergyKWH = Column(Integer)
    ChargerSessionPricingPlanId = Column(String(5), ForeignKey("Tariffs.TariffsId"))
    ChargerSessionCost = Column(Float)
    ChargerSessionDiscountId = Column(String(5), ForeignKey("Discounts.DiscountId"))
    ChargerSessionPaymentId = Column(String(5))
    ChargerSessionPaymentAmount = Column(Float)
    ChargerSessionPaymentStatus = Column(String(255))
    ChargerSessionCreated = Column(DateTime, default=datetime.now)
    
    # Define foreign key relationships
    __table_args__ = (
        ForeignKeyConstraint([
            "ChargerSessionCompanyId", "ChargerSessionSiteId", "ChargerSessionChargerId"
        ], [
            "Chargers.ChargerCompanyId", "Chargers.ChargerSiteId", "Chargers.ChargerId"
        ]),
        ForeignKeyConstraint([
            "ChargerSessionCompanyId", "ChargerSessionSiteId", "ChargerSessionChargerId", "ChargerSessionConnectorId"
        ], [
            "Connectors.ConnectorCompanyId", "Connectors.ConnectorSiteId", "Connectors.ConnectorChargerId", "Connectors.ConnectorId"
        ]),
        ForeignKeyConstraint([
            "ChargerSessionCompanyId", "ChargerSessionDriverId"
        ], [
            "Drivers.DriverCompanyId", "Drivers.DriverId"
        ]),
        ForeignKeyConstraint([
            "ChargerSessionCompanyId", "ChargerSessionDriverId", "ChargerSessionRFIDCard"
        ], [
            "RFIDCards.RFIDCardCompanyId", "RFIDCards.RFIDCardDriverId", "RFIDCards.RFIDCardId"
        ]),
    )
    
    # Relationships
    charger = relationship("Charger", back_populates="charge_sessions")
    connector = relationship("Connector")
    driver = relationship("Driver")
    rfid_card = relationship("RFIDCard", back_populates="charge_sessions")
    tariff = relationship("Tariff", back_populates="charge_sessions")
    discount = relationship("Discount", back_populates="charge_sessions")
    events_data = relationship("EventsData", back_populates="charge_session", uselist=False)


class EventsData(Base):
    __tablename__ = "EventsData"
    
    EventsDataSessionId = Column(Integer, ForeignKey("ChargeSessions.ChargeSessionId"), primary_key=True)
    EventsDataCompanyId = Column(String(5))
    EventsDataSiteId = Column(String(5))
    EventsDataChargerId = Column(String(10))
    EventsDataConnectorId = Column(String(10))
    EventsDataDateTime = Column(DateTime)
    EventsDataType = Column(String(10))
    EventsDataTriggerReason = Column(String(50))
    EventsDataOrigin = Column(String(10))
    EventsDataData = Column(String(255))
    EventsDataTemperature = Column(Integer)
    EventsDataCurrent = Column(Integer)
    EventsDataVoltage = Column(Integer)
    EventsDataMeterValue = Column(String(255))
    
    # Relationships
    charge_session = relationship("ChargeSession", back_populates="events_data")


class PaymentMethod(Base):
    __tablename__ = "PaymentMethods"
    
    PaymentMethodId = Column(String(5), primary_key=True, index=True)
    PaymentMethodName = Column(String(20))
    PaymentMethodEnabled = Column(Boolean, default=True)
    PaymentMethodCreated = Column(DateTime, default=datetime.now)
    PaymentMethodUpdated = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relationships
    payment_transactions = relationship("PaymentTransaction", back_populates="payment_method")


class PaymentTransaction(Base):
    __tablename__ = "PaymentTransactions"
    
    PaymentTransactionId = Column(String(30), primary_key=True, index=True)
    PaymentTransactionMethodUsed = Column(String(6), ForeignKey("PaymentMethods.PaymentMethodId"))
    PaymentTransactionDriverId = Column(String(10))
    PaymentTransactionDateTime = Column(DateTime)
    PaymentTransactionAmount = Column(Float)
    PaymentTransactionStatus = Column(String(10))
    PaymentTransactionCompanyId = Column(String(5))
    PaymentTransactionSiteId = Column(String(5))
    PaymentTransactionChargerId = Column(String(10))
    
    # Relationships
    payment_method = relationship("PaymentMethod", back_populates="payment_transactions")