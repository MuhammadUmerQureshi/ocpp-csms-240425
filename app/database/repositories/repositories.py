from sqlalchemy.orm import Session
from ..models.models import (
    Company, SitesGroup, Site, Charger, Connector, 
    Driver, DriversGroup, Discount, Tariff, RFIDCard,
    ChargeSession, EventsData, PaymentMethod, PaymentTransaction
)
from typing import List, Optional, Dict, Any
from datetime import datetime

# Company Repository
class CompanyRepository:
    @staticmethod
    def get_companies(db: Session, skip: int = 0, limit: int = 100):
        return db.query(Company).offset(skip).limit(limit).all()
    
    @staticmethod
    def get_company(db: Session, company_id: str):
        return db.query(Company).filter(Company.CompanyId == company_id).first()
    
    @staticmethod
    def create_company(db: Session, company_data: Dict[str, Any]):
        company = Company(**company_data)
        db.add(company)
        db.commit()
        db.refresh(company)
        return company
    
    @staticmethod
    def update_company(db: Session, company_id: str, company_data: Dict[str, Any]):
        company = db.query(Company).filter(Company.CompanyId == company_id).first()
        if company:
            for key, value in company_data.items():
                setattr(company, key, value)
            company.CompanyUpdated = datetime.now()
            db.commit()
            db.refresh(company)
        return company
    
    @staticmethod
    def delete_company(db: Session, company_id: str):
        company = db.query(Company).filter(Company.CompanyId == company_id).first()
        if company:
            db.delete(company)
            db.commit()
            return True
        return False

# Site Repository
class SiteRepository:
    @staticmethod
    def get_sites(db: Session, company_id: Optional[str] = None, skip: int = 0, limit: int = 100):
        query = db.query(Site)
        if company_id:
            query = query.filter(Site.SiteCompanyID == company_id)
        return query.offset(skip).limit(limit).all()
    
    @staticmethod
    def get_site(db: Session, company_id: str, site_id: str):
        return db.query(Site).filter(
            Site.SiteCompanyID == company_id,
            Site.SiteId == site_id
        ).first()
    
    @staticmethod
    def create_site(db: Session, site_data: Dict[str, Any]):
        site = Site(**site_data)
        db.add(site)
        db.commit()
        db.refresh(site)
        return site
    
    @staticmethod
    def update_site(db: Session, company_id: str, site_id: str, site_data: Dict[str, Any]):
        site = db.query(Site).filter(
            Site.SiteCompanyID == company_id,
            Site.SiteId == site_id
        ).first()
        if site:
            for key, value in site_data.items():
                setattr(site, key, value)
            site.SiteUpdated = datetime.now()
            db.commit()
            db.refresh(site)
        return site
    
    @staticmethod
    def delete_site(db: Session, company_id: str, site_id: str):
        site = db.query(Site).filter(
            Site.SiteCompanyID == company_id,
            Site.SiteId == site_id
        ).first()
        if site:
            db.delete(site)
            db.commit()
            return True
        return False

# Charger Repository
class ChargerRepository:
    @staticmethod
    def get_chargers(
        db: Session, 
        company_id: Optional[str] = None, 
        site_id: Optional[str] = None,
        skip: int = 0, 
        limit: int = 100
    ):
        query = db.query(Charger)
        if company_id:
            query = query.filter(Charger.ChargerCompanyId == company_id)
        if site_id:
            query = query.filter(Charger.ChargerSiteId == site_id)
        return query.offset(skip).limit(limit).all()
    
    @staticmethod
    def get_charger(db: Session, company_id: str, site_id: str, charger_id: str):
        return db.query(Charger).filter(
            Charger.ChargerCompanyId == company_id,
            Charger.ChargerSiteId == site_id,
            Charger.ChargerId == charger_id
        ).first()
    
    @staticmethod
    def create_charger(db: Session, charger_data: Dict[str, Any]):
        charger = Charger(**charger_data)
        db.add(charger)
        db.commit()
        db.refresh(charger)
        return charger
    
    @staticmethod
    def update_charger(db: Session, company_id: str, site_id: str, charger_id: str, charger_data: Dict[str, Any]):
        charger = db.query(Charger).filter(
            Charger.ChargerCompanyId == company_id,
            Charger.ChargerSiteId == site_id,
            Charger.ChargerId == charger_id
        ).first()
        if charger:
            for key, value in charger_data.items():
                setattr(charger, key, value)
            charger.Charger_Updated = datetime.now()
            db.commit()
            db.refresh(charger)
        return charger
    
    @staticmethod
    def delete_charger(db: Session, company_id: str, site_id: str, charger_id: str):
        charger = db.query(Charger).filter(
            Charger.ChargerCompanyId == company_id,
            Charger.ChargerSiteId == site_id,
            Charger.ChargerId == charger_id
        ).first()
        if charger:
            db.delete(charger)
            db.commit()
            return True
        return False
    
    @staticmethod
    def update_charger_status(
        db: Session, 
        company_id: str, 
        site_id: str, 
        charger_id: str,
        status: str,
        is_online: bool = None
    ):
        charger = db.query(Charger).filter(
            Charger.ChargerCompanyId == company_id,
            Charger.ChargerSiteId == site_id,
            Charger.ChargerId == charger_id
        ).first()
        
        if charger:
            charger.ChargerStatusNow = status
            if is_online is not None:
                charger.ChargerIsOnline = is_online
                if is_online:
                    charger.ChargerLastConn = datetime.now()
                else:
                    charger.ChargerLastDisconn = datetime.now()
            
            charger.ChargerLastHeartbeat = datetime.now()
            charger.Charger_Updated = datetime.now()
            db.commit()
            db.refresh(charger)
        
        return charger

# ChargeSession Repository
class ChargeSessionRepository:
    @staticmethod
    def get_sessions(
        db: Session,
        company_id: Optional[str] = None,
        site_id: Optional[str] = None,
        charger_id: Optional[str] = None,
        driver_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        skip: int = 0,
        limit: int = 100
    ):
        query = db.query(ChargeSession)
        
        if company_id:
            query = query.filter(ChargeSession.ChargerSessionCompanyId == company_id)
        if site_id:
            query = query.filter(ChargeSession.ChargerSessionSiteId == site_id)
        if charger_id:
            query = query.filter(ChargeSession.ChargerSessionChargerId == charger_id)
        if driver_id:
            query = query.filter(ChargeSession.ChargerSessionDriverId == driver_id)
        if start_date:
            query = query.filter(ChargeSession.ChargerSessionStart >= start_date)
        if end_date:
            query = query.filter(ChargeSession.ChargerSessionStart <= end_date)
            
        return query.order_by(ChargeSession.ChargerSessionStart.desc()).offset(skip).limit(limit).all()
    
    @staticmethod
    def get_session(db: Session, session_id: int):
        return db.query(ChargeSession).filter(ChargeSession.ChargeSessionId == session_id).first()
    
    @staticmethod
    def create_session(db: Session, session_data: Dict[str, Any]):
        session = ChargeSession(**session_data)
        db.add(session)
        db.commit()
        db.refresh(session)
        return session
    
    @staticmethod
    def update_session(db: Session, session_id: int, session_data: Dict[str, Any]):
        session = db.query(ChargeSession).filter(ChargeSession.ChargeSessionId == session_id).first()
        if session:
            for key, value in session_data.items():
                setattr(session, key, value)
            db.commit()
            db.refresh(session)
        return session
    
    @staticmethod
    def end_session(
        db: Session, 
        session_id: int, 
        end_time: datetime,
        energy_kwh: int,
        reason: str = "Completed",
        cost: Optional[float] = None
    ):
        session = db.query(ChargeSession).filter(ChargeSession.ChargeSessionId == session_id).first()
        if session and not session.ChargerSessionEnd:
            session.ChargerSessionEnd = end_time
            session.ChargerSessionEnergyKWH = energy_kwh
            session.ChargerSessionReason = reason
            
            if cost is not None:
                session.ChargerSessionCost = cost
            
            # Calculate duration in seconds
            if session.ChargerSessionStart:
                delta = end_time - session.ChargerSessionStart
                session.ChargerSessionDuration = delta.total_seconds()
            
            session.ChargerSessionStatus = "Completed"
            db.commit()
            db.refresh(session)
        
        return session

# Driver Repository
class DriverRepository:
    @staticmethod
    def get_drivers(
        db: Session, 
        company_id: Optional[str] = None,
        group_id: Optional[str] = None,
        skip: int = 0, 
        limit: int = 100
    ):
        query = db.query(Driver)
        if company_id:
            query = query.filter(Driver.DriverCompanyId == company_id)
        if group_id:
            query = query.filter(Driver.DriverGroupId == group_id)
        return query.offset(skip).limit(limit).all()
    
    @staticmethod
    def get_driver(db: Session, company_id: str, driver_id: str):
        return db.query(Driver).filter(
            Driver.DriverCompanyId == company_id,
            Driver.DriverId == driver_id
        ).first()
    
    @staticmethod
    def create_driver(db: Session, driver_data: Dict[str, Any]):
        driver = Driver(**driver_data)
        db.add(driver)
        db.commit()
        db.refresh(driver)
        return driver
    
    # Continuing the DriverRepository class
    @staticmethod
    def update_driver(db: Session, company_id: str, driver_id: str, driver_data: Dict[str, Any]):
        driver = db.query(Driver).filter(
            Driver.DriverCompanyId == company_id,
            Driver.DriverId == driver_id
        ).first()
        if driver:
            for key, value in driver_data.items():
                setattr(driver, key, value)
            driver.DriverUpdated = datetime.now()
            db.commit()
            db.refresh(driver)
        return driver
    
    @staticmethod
    def delete_driver(db: Session, company_id: str, driver_id: str):
        driver = db.query(Driver).filter(
            Driver.DriverCompanyId == company_id,
            Driver.DriverId == driver_id
        ).first()
        if driver:
            db.delete(driver)
            db.commit()
            return True
        return False
    
    @staticmethod
    def get_driver_by_rfid(db: Session, rfid_card_id: str):
        rfid_card = db.query(RFIDCard).filter(
            RFIDCard.RFIDCardId == rfid_card_id,
            RFIDCard.RFIDCardEnabled == True
        ).first()
        
        if rfid_card:
            return db.query(Driver).filter(
                Driver.DriverCompanyId == rfid_card.RFIDCardCompanyId,
                Driver.DriverId == rfid_card.RFIDCardDriverId,
                Driver.DriverEnabled == True
            ).first()
        
        return None

# RFIDCard Repository
class RFIDCardRepository:
    @staticmethod
    def get_rfid_cards(
        db: Session, 
        company_id: Optional[str] = None,
        driver_id: Optional[str] = None,
        skip: int = 0, 
        limit: int = 100
    ):
        query = db.query(RFIDCard)
        if company_id:
            query = query.filter(RFIDCard.RFIDCardCompanyId == company_id)
        if driver_id:
            query = query.filter(RFIDCard.RFIDCardDriverId == driver_id)
        return query.offset(skip).limit(limit).all()
    
    @staticmethod
    def get_rfid_card(db: Session, company_id: str, driver_id: str, card_id: str):
        return db.query(RFIDCard).filter(
            RFIDCard.RFIDCardCompanyId == company_id,
            RFIDCard.RFIDCardDriverId == driver_id,
            RFIDCard.RFIDCardId == card_id
        ).first()
    
    @staticmethod
    def get_rfid_card_by_id(db: Session, card_id: str):
        return db.query(RFIDCard).filter(
            RFIDCard.RFIDCardId == card_id
        ).first()
    
    @staticmethod
    def create_rfid_card(db: Session, card_data: Dict[str, Any]):
        rfid_card = RFIDCard(**card_data)
        db.add(rfid_card)
        db.commit()
        db.refresh(rfid_card)
        return rfid_card
    
    @staticmethod
    def update_rfid_card(db: Session, company_id: str, driver_id: str, card_id: str, card_data: Dict[str, Any]):
        rfid_card = db.query(RFIDCard).filter(
            RFIDCard.RFIDCardCompanyId == company_id,
            RFIDCard.RFIDCardDriverId == driver_id,
            RFIDCard.RFIDCardId == card_id
        ).first()
        if rfid_card:
            for key, value in card_data.items():
                setattr(rfid_card, key, value)
            rfid_card.RFIDCardUpdated = datetime.now()
            db.commit()
            db.refresh(rfid_card)
        return rfid_card
    
    @staticmethod
    def delete_rfid_card(db: Session, company_id: str, driver_id: str, card_id: str):
        rfid_card = db.query(RFIDCard).filter(
            RFIDCard.RFIDCardCompanyId == company_id,
            RFIDCard.RFIDCardDriverId == driver_id,
            RFIDCard.RFIDCardId == card_id
        ).first()
        if rfid_card:
            db.delete(rfid_card)
            db.commit()
            return True
        return False

# Connector Repository
class ConnectorRepository:
    @staticmethod
    def get_connectors(
        db: Session, 
        company_id: Optional[str] = None,
        site_id: Optional[str] = None,
        charger_id: Optional[str] = None,
        skip: int = 0, 
        limit: int = 100
    ):
        query = db.query(Connector)
        if company_id:
            query = query.filter(Connector.ConnectorCompanyId == company_id)
        if site_id:
            query = query.filter(Connector.ConnectorSiteId == site_id)
        if charger_id:
            query = query.filter(Connector.ConnectorChargerId == charger_id)
        return query.offset(skip).limit(limit).all()
    
    @staticmethod
    def get_connector(db: Session, company_id: str, site_id: str, charger_id: str, connector_id: str):
        return db.query(Connector).filter(
            Connector.ConnectorCompanyId == company_id,
            Connector.ConnectorSiteId == site_id,
            Connector.ConnectorChargerId == charger_id,
            Connector.ConnectorId == connector_id
        ).first()
    
    @staticmethod
    def create_connector(db: Session, connector_data: Dict[str, Any]):
        connector = Connector(**connector_data)
        db.add(connector)
        db.commit()
        db.refresh(connector)
        return connector
    
    @staticmethod
    def update_connector(
        db: Session, 
        company_id: str, 
        site_id: str, 
        charger_id: str, 
        connector_id: str, 
        connector_data: Dict[str, Any]
    ):
        connector = db.query(Connector).filter(
            Connector.ConnectorCompanyId == company_id,
            Connector.ConnectorSiteId == site_id,
            Connector.ConnectorChargerId == charger_id,
            Connector.ConnectorId == connector_id
        ).first()
        if connector:
            for key, value in connector_data.items():
                setattr(connector, key, value)
            connector.ConnectorUpdated = datetime.now()
            db.commit()
            db.refresh(connector)
        return connector
    
    @staticmethod
    def update_connector_status(
        db: Session, 
        company_id: str, 
        site_id: str, 
        charger_id: str, 
        connector_id: str, 
        status: str
    ):
        connector = db.query(Connector).filter(
            Connector.ConnectorCompanyId == company_id,
            Connector.ConnectorSiteId == site_id,
            Connector.ConnectorChargerId == charger_id,
            Connector.ConnectorId == connector_id
        ).first()
        if connector:
            connector.ConnectorStatus = status
            connector.ConnectorUpdated = datetime.now()
            db.commit()
            db.refresh(connector)
        return connector
    
    @staticmethod
    def delete_connector(db: Session, company_id: str, site_id: str, charger_id: str, connector_id: str):
        connector = db.query(Connector).filter(
            Connector.ConnectorCompanyId == company_id,
            Connector.ConnectorSiteId == site_id,
            Connector.ConnectorChargerId == charger_id,
            Connector.ConnectorId == connector_id
        ).first()
        if connector:
            db.delete(connector)
            db.commit()
            return True
        return False