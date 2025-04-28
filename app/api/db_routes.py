from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import logging

from ..database.database import get_db
from ..database.schemas import (
    CompanyCreate, CompanyUpdate, CompanyResponse,
    SiteCreate, SiteUpdate, SiteResponse,
    ChargerCreate, ChargerUpdate, ChargerResponse,
    ConnectorCreate, ConnectorUpdate, ConnectorResponse,
    DriverCreate, DriverUpdate, DriverResponse,
    RFIDCardCreate, RFIDCardUpdate, RFIDCardResponse,
    ChargeSessionCreate, ChargeSessionUpdate, ChargeSessionResponse,
    EventsDataCreate, EventsDataResponse
)
from ..database.repositories.repositories import (
    CompanyRepository, SiteRepository, ChargerRepository,
    ConnectorRepository, DriverRepository, RFIDCardRepository,
    ChargeSessionRepository
)

router = APIRouter(prefix="/db", tags=["database"])
logger = logging.getLogger("ocpp.db_routes")

# Company endpoints
@router.get("/companies/", response_model=List[CompanyResponse])
async def get_companies(
    skip: int = 0, 
    limit: int = 100,
    db: Session = Depends(get_db)
):
    companies = CompanyRepository.get_companies(db, skip=skip, limit=limit)
    return companies

@router.get("/companies/{company_id}", response_model=CompanyResponse)
async def get_company(company_id: str, db: Session = Depends(get_db)):
    company = CompanyRepository.get_company(db, company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    return company

@router.post("/companies/", response_model=CompanyResponse)
async def create_company(company: CompanyCreate, db: Session = Depends(get_db)):
    existing_company = CompanyRepository.get_company(db, company.CompanyId)
    if existing_company:
        raise HTTPException(status_code=400, detail="Company ID already registered")
    return CompanyRepository.create_company(db, company.dict())

@router.put("/companies/{company_id}", response_model=CompanyResponse)
async def update_company(company_id: str, company: CompanyUpdate, db: Session = Depends(get_db)):
    db_company = CompanyRepository.get_company(db, company_id)
    if not db_company:
        raise HTTPException(status_code=404, detail="Company not found")
    return CompanyRepository.update_company(db, company_id, company.dict(exclude_unset=True))

@router.delete("/companies/{company_id}")
async def delete_company(company_id: str, db: Session = Depends(get_db)):
    db_company = CompanyRepository.get_company(db, company_id)
    if not db_company:
        raise HTTPException(status_code=404, detail="Company not found")
    result = CompanyRepository.delete_company(db, company_id)
    return {"success": result}

# Site endpoints
@router.get("/sites/", response_model=List[SiteResponse])
async def get_sites(
    company_id: Optional[str] = None,
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db)
):
    sites = SiteRepository.get_sites(db, company_id=company_id, skip=skip, limit=limit)
    return sites

@router.get("/companies/{company_id}/sites/", response_model=List[SiteResponse])
async def get_company_sites(company_id: str, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    sites = SiteRepository.get_sites(db, company_id=company_id, skip=skip, limit=limit)
    return sites

@router.get("/companies/{company_id}/sites/{site_id}", response_model=SiteResponse)
async def get_site(company_id: str, site_id: str, db: Session = Depends(get_db)):
    site = SiteRepository.get_site(db, company_id, site_id)
    if not site:
        raise HTTPException(status_code=404, detail="Site not found")
    return site

@router.post("/sites/", response_model=SiteResponse)
async def create_site(site: SiteCreate, db: Session = Depends(get_db)):
    company = CompanyRepository.get_company(db, site.SiteCompanyID)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    
    existing_site = SiteRepository.get_site(db, site.SiteCompanyID, site.SiteId)
    if existing_site:
        raise HTTPException(status_code=400, detail="Site ID already registered for this company")
    
    return SiteRepository.create_site(db, site.dict())

@router.put("/companies/{company_id}/sites/{site_id}", response_model=SiteResponse)
async def update_site(
    company_id: str, 
    site_id: str, 
    site: SiteUpdate, 
    db: Session = Depends(get_db)
):
    db_site = SiteRepository.get_site(db, company_id, site_id)
    if not db_site:
        raise HTTPException(status_code=404, detail="Site not found")
    return SiteRepository.update_site(db, company_id, site_id, site.dict(exclude_unset=True))

@router.delete("/companies/{company_id}/sites/{site_id}")
async def delete_site(company_id: str, site_id: str, db: Session = Depends(get_db)):
    db_site = SiteRepository.get_site(db, company_id, site_id)
    if not db_site:
        raise HTTPException(status_code=404, detail="Site not found")
    result = SiteRepository.delete_site(db, company_id, site_id)
    return {"success": result}

# Charger endpoints
@router.get("/chargers/", response_model=List[ChargerResponse])
async def get_chargers(
    company_id: Optional[str] = None,
    site_id: Optional[str] = None,
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db)
):
    chargers = ChargerRepository.get_chargers(
        db, company_id=company_id, site_id=site_id, skip=skip, limit=limit
    )
    return chargers

@router.get(
    "/companies/{company_id}/sites/{site_id}/chargers/", 
    response_model=List[ChargerResponse]
)
async def get_site_chargers(
    company_id: str, 
    site_id: str, 
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db)
):
    chargers = ChargerRepository.get_chargers(
        db, company_id=company_id, site_id=site_id, skip=skip, limit=limit
    )
    return chargers

@router.get(
    "/companies/{company_id}/sites/{site_id}/chargers/{charger_id}", 
    response_model=ChargerResponse
)
async def get_charger(
    company_id: str, 
    site_id: str, 
    charger_id: str, 
    db: Session = Depends(get_db)
):
    charger = ChargerRepository.get_charger(db, company_id, site_id, charger_id)
    if not charger:
        raise HTTPException(status_code=404, detail="Charger not found")
    return charger

@router.post("/chargers/", response_model=ChargerResponse)
async def create_charger(charger: ChargerCreate, db: Session = Depends(get_db)):
    site = SiteRepository.get_site(db, charger.ChargerCompanyId, charger.ChargerSiteId)
    if not site:
        raise HTTPException(status_code=404, detail="Site not found")
    
    existing_charger = ChargerRepository.get_charger(
        db, charger.ChargerCompanyId, charger.ChargerSiteId, charger.ChargerId
    )
    if existing_charger:
        raise HTTPException(status_code=400, detail="Charger ID already registered for this site")
    
    return ChargerRepository.create_charger(db, charger.dict())

@router.put(
    "/companies/{company_id}/sites/{site_id}/chargers/{charger_id}", 
    response_model=ChargerResponse
)
async def update_charger(
    company_id: str, 
    site_id: str, 
    charger_id: str, 
    charger: ChargerUpdate, 
    db: Session = Depends(get_db)
):
    db_charger = ChargerRepository.get_charger(db, company_id, site_id, charger_id)
    if not db_charger:
        raise HTTPException(status_code=404, detail="Charger not found")
    return ChargerRepository.update_charger(
        db, company_id, site_id, charger_id, charger.dict(exclude_unset=True)
    )

@router.delete("/companies/{company_id}/sites/{site_id}/chargers/{charger_id}")
async def delete_charger(
    company_id: str, 
    site_id: str, 
    charger_id: str, 
    db: Session = Depends(get_db)
):
    db_charger = ChargerRepository.get_charger(db, company_id, site_id, charger_id)
    if not db_charger:
        raise HTTPException(status_code=404, detail="Charger not found")
    result = ChargerRepository.delete_charger(db, company_id, site_id, charger_id)
    return {"success": result}

# Update status for charger
@router.put(
    "/companies/{company_id}/sites/{site_id}/chargers/{charger_id}/status", 
    response_model=ChargerResponse
)
async def update_charger_status(
    company_id: str, 
    site_id: str, 
    charger_id: str, 
    status: str = Query(..., description="New status of the charger"),
    is_online: Optional[bool] = Query(None, description="Online status of the charger"),
    db: Session = Depends(get_db)
):
    db_charger = ChargerRepository.get_charger(db, company_id, site_id, charger_id)
    if not db_charger:
        raise HTTPException(status_code=404, detail="Charger not found")
    
    return ChargerRepository.update_charger_status(
        db, company_id, site_id, charger_id, status, is_online
    )

# Connector endpoints
@router.get(
    "/companies/{company_id}/sites/{site_id}/chargers/{charger_id}/connectors/", 
    response_model=List[ConnectorResponse]
)
async def get_charger_connectors(
    company_id: str, 
    site_id: str, 
    charger_id: str, 
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db)
):
    connectors = ConnectorRepository.get_connectors(
        db, company_id=company_id, site_id=site_id, charger_id=charger_id, skip=skip, limit=limit
    )
    return connectors

@router.get(
    "/companies/{company_id}/sites/{site_id}/chargers/{charger_id}/connectors/{connector_id}", 
    response_model=ConnectorResponse
)
async def get_connector(
    company_id: str, 
    site_id: str, 
    charger_id: str, 
    connector_id: str, 
    db: Session = Depends(get_db)
):
    connector = ConnectorRepository.get_connector(db, company_id, site_id, charger_id, connector_id)
    if not connector:
        raise HTTPException(status_code=404, detail="Connector not found")
    return connector

@router.post("/connectors/", response_model=ConnectorResponse)
async def create_connector(connector: ConnectorCreate, db: Session = Depends(get_db)):
    charger = ChargerRepository.get_charger(
        db, connector.ConnectorCompanyId, connector.ConnectorSiteId, connector.ConnectorChargerId
    )
    if not charger:
        raise HTTPException(status_code=404, detail="Charger not found")
    
    existing_connector = ConnectorRepository.get_connector(
        db, connector.ConnectorCompanyId, connector.ConnectorSiteId, 
        connector.ConnectorChargerId, connector.ConnectorId
    )
    if existing_connector:
        raise HTTPException(status_code=400, detail="Connector ID already registered for this charger")
    
    return ConnectorRepository.create_connector(db, connector.dict())

@router.get("/charge-sessions/", response_model=List[ChargeSessionResponse])
async def get_charge_sessions(
    company_id: Optional[str] = None,
    site_id: Optional[str] = None,
    charger_id: Optional[str] = None,
    driver_id: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    sessions = ChargeSessionRepository.get_sessions(
        db, company_id=company_id, site_id=site_id, charger_id=charger_id,
        driver_id=driver_id, start_date=start_date, end_date=end_date,
        skip=skip, limit=limit
    )
    return sessions

@router.get("/charge-sessions/{session_id}", response_model=ChargeSessionResponse)
async def get_charge_session(session_id: int, db: Session = Depends(get_db)):
    session = ChargeSessionRepository.get_session(db, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Charge session not found")
    return session

@router.post("/charge-sessions/", response_model=ChargeSessionResponse)
async def create_charge_session(session: ChargeSessionCreate, db: Session = Depends(get_db)):
    # Validate company, site, charger, connector
    charger = ChargerRepository.get_charger(
        db, session.ChargerSessionCompanyId, session.ChargerSessionSiteId, session.ChargerSessionChargerId
    )
    if not charger:
        raise HTTPException(status_code=404, detail="Charger not found")
    
    # Create the charge session
    return ChargeSessionRepository.create_session(db, session.dict())

@router.put("/charge-sessions/{session_id}", response_model=ChargeSessionResponse)
async def update_charge_session(
    session_id: int, 
    session: ChargeSessionUpdate, 
    db: Session = Depends(get_db)
):
    db_session = ChargeSessionRepository.get_session(db, session_id)
    if not db_session:
        raise HTTPException(status_code=404, detail="Charge session not found")
    
    return ChargeSessionRepository.update_session(db, session_id, session.dict(exclude_unset=True))

@router.put("/charge-sessions/{session_id}/end", response_model=ChargeSessionResponse)
async def end_charge_session(
    session_id: int,
    end_time: datetime,
    energy_kwh: int,
    reason: str = "Completed",
    cost: Optional[float] = None,
    db: Session = Depends(get_db)
):
    db_session = ChargeSessionRepository.get_session(db, session_id)
    if not db_session:
        raise HTTPException(status_code=404, detail="Charge session not found")
    
    if db_session.ChargerSessionEnd:
        raise HTTPException(status_code=400, detail="Charge session already ended")
    
    return ChargeSessionRepository.end_session(
        db, session_id, end_time, energy_kwh, reason, cost
    )

# Driver endpoints
@router.get("/drivers/", response_model=List[DriverResponse])
async def get_drivers(
    company_id: Optional[str] = None,
    group_id: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    drivers = DriverRepository.get_drivers(
        db, company_id=company_id, group_id=group_id, skip=skip, limit=limit
    )
    return drivers

@router.get("/companies/{company_id}/drivers/", response_model=List[DriverResponse])
async def get_company_drivers(
    company_id: str,
    group_id: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    drivers = DriverRepository.get_drivers(
        db, company_id=company_id, group_id=group_id, skip=skip, limit=limit
    )
    return drivers

@router.get("/companies/{company_id}/drivers/{driver_id}", response_model=DriverResponse)
async def get_driver(company_id: str, driver_id: str, db: Session = Depends(get_db)):
    driver = DriverRepository.get_driver(db, company_id, driver_id)
    if not driver:
        raise HTTPException(status_code=404, detail="Driver not found")
    return driver

@router.post("/drivers/", response_model=DriverResponse)
async def create_driver(driver: DriverCreate, db: Session = Depends(get_db)):
    company = CompanyRepository.get_company(db, driver.DriverCompanyId)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    
    existing_driver = DriverRepository.get_driver(db, driver.DriverCompanyId, driver.DriverId)
    if existing_driver:
        raise HTTPException(status_code=400, detail="Driver ID already registered for this company")
    
    return DriverRepository.create_driver(db, driver.dict())

@router.put("/companies/{company_id}/drivers/{driver_id}", response_model=DriverResponse)
async def update_driver(
    company_id: str,
    driver_id: str,
    driver: DriverUpdate,
    db: Session = Depends(get_db)
):
    db_driver = DriverRepository.get_driver(db, company_id, driver_id)
    if not db_driver:
        raise HTTPException(status_code=404, detail="Driver not found")
    
    return DriverRepository.update_driver(
        db, company_id, driver_id, driver.dict(exclude_unset=True)
    )

@router.delete("/companies/{company_id}/drivers/{driver_id}")
async def delete_driver(company_id: str, driver_id: str, db: Session = Depends(get_db)):
    db_driver = DriverRepository.get_driver(db, company_id, driver_id)
    if not db_driver:
        raise HTTPException(status_code=404, detail="Driver not found")
    
    result = DriverRepository.delete_driver(db, company_id, driver_id)
    return {"success": result}

# RFID Card endpoints
@router.get("/rfid-cards/", response_model=List[RFIDCardResponse])
async def get_rfid_cards(
    company_id: Optional[str] = None,
    driver_id: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    cards = RFIDCardRepository.get_rfid_cards(
        db, company_id=company_id, driver_id=driver_id, skip=skip, limit=limit
    )
    return cards

@router.get(
    "/companies/{company_id}/drivers/{driver_id}/rfid-cards/", 
    response_model=List[RFIDCardResponse]
)
async def get_driver_rfid_cards(
    company_id: str,
    driver_id: str,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    cards = RFIDCardRepository.get_rfid_cards(
        db, company_id=company_id, driver_id=driver_id, skip=skip, limit=limit
    )
    return cards

@router.get(
    "/companies/{company_id}/drivers/{driver_id}/rfid-cards/{card_id}", 
    response_model=RFIDCardResponse
)
async def get_rfid_card(
    company_id: str, 
    driver_id: str, 
    card_id: str, 
    db: Session = Depends(get_db)
):
    card = RFIDCardRepository.get_rfid_card(db, company_id, driver_id, card_id)
    if not card:
        raise HTTPException(status_code=404, detail="RFID card not found")
    return card

@router.get("/rfid-cards/by-id/{card_id}", response_model=RFIDCardResponse)
async def get_rfid_card_by_id(card_id: str, db: Session = Depends(get_db)):
    card = RFIDCardRepository.get_rfid_card_by_id(db, card_id)
    if not card:
        raise HTTPException(status_code=404, detail="RFID card not found")
    return card

@router.post("/rfid-cards/", response_model=RFIDCardResponse)
async def create_rfid_card(card: RFIDCardCreate, db: Session = Depends(get_db)):
    driver = DriverRepository.get_driver(db, card.RFIDCardCompanyId, card.RFIDCardDriverId)
    if not driver:
        raise HTTPException(status_code=404, detail="Driver not found")
    
    existing_card = RFIDCardRepository.get_rfid_card(
        db, card.RFIDCardCompanyId, card.RFIDCardDriverId, card.RFIDCardId
    )
    if existing_card:
        raise HTTPException(status_code=400, detail="RFID card ID already registered for this driver")
    
    return RFIDCardRepository.create_rfid_card(db, card.dict())

@router.put(
    "/companies/{company_id}/drivers/{driver_id}/rfid-cards/{card_id}",
    response_model=RFIDCardResponse
)
async def update_rfid_card(
    company_id: str,
    driver_id: str,
    card_id: str,
    card: RFIDCardUpdate,
    db: Session = Depends(get_db)
):
    db_card = RFIDCardRepository.get_rfid_card(db, company_id, driver_id, card_id)
    if not db_card:
        raise HTTPException(status_code=404, detail="RFID card not found")
    
    return RFIDCardRepository.update_rfid_card(
        db, company_id, driver_id, card_id, card.dict(exclude_unset=True)
    )

@router.delete("/companies/{company_id}/drivers/{driver_id}/rfid-cards/{card_id}")
async def delete_rfid_card(
    company_id: str,
    driver_id: str,
    card_id: str,
    db: Session = Depends(get_db)
):
    db_card = RFIDCardRepository.get_rfid_card(db, company_id, driver_id, card_id)
    if not db_card:
        raise HTTPException(status_code=404, detail="RFID card not found")
    
    result = RFIDCardRepository.delete_rfid_card(db, company_id, driver_id, card_id)
    return {"success": result}

# OCPP-DB integration endpoints

@router.post("/ocpp/charger/register")
async def register_charger_from_ocpp(
    charger_id: str,
    vendor: str,
    model: str,
    serial_number: str = None,
    firmware_version: str = None,
    company_id: str = "DEF01",  # Default company ID
    site_id: str = "MAIN",      # Default site ID
    db: Session = Depends(get_db)
):
    """Register or update a charger from OCPP boot notification"""
    
    logger.info(f"Registering/updating charger from OCPP: {charger_id}")
    
    # Check if charger exists
    charger = ChargerRepository.get_charger(db, company_id, site_id, charger_id)
    
    if charger:
        # Update existing charger
        update_data = {
            "ChargerBrand": vendor,
            "ChargerModel": model,
            "ChargerSerial": serial_number,
            "ChargerFirmwareVersion": firmware_version,
            "ChargerIsOnline": True,
            "ChargerLastConn": datetime.now(),
            "ChargerStatusNow": "Available"
        }
        
        logger.info(f"Updating existing charger: {charger_id}")
        return ChargerRepository.update_charger(db, company_id, site_id, charger_id, update_data)
    else:
        # Create new charger
        new_charger = {
            "ChargerCompanyId": company_id,
            "ChargerSiteId": site_id,
            "ChargerId": charger_id,
            "ChargerName": f"{vendor} {model} - {charger_id}",
            "ChargerBrand": vendor,
            "ChargerModel": model,
            "ChargerSerial": serial_number,
            "ChargerFirmwareVersion": firmware_version,
            "ChargerIsOnline": True,
            "ChargerLastConn": datetime.now(),
            "ChargerEnabled": True,
            "ChargerStatusNow": "Available",
            "Charger_Type": "OCPP",
            "Charger_Availability": "Operative"
        }
        
        logger.info(f"Creating new charger: {charger_id}")
        return ChargerRepository.create_charger(db, new_charger)

@router.post("/ocpp/connector/status")
async def update_connector_status_from_ocpp(
    charger_id: str,
    connector_id: str,
    status: str,
    company_id: str = "DEF01",  # Default company ID
    site_id: str = "MAIN",      # Default site ID
    db: Session = Depends(get_db)
):
    """Update connector status from OCPP status notification"""
    
    logger.info(f"Updating connector status from OCPP: {charger_id}/{connector_id} to {status}")
    
    # Check if connector exists
    connector = ConnectorRepository.get_connector(db, company_id, site_id, charger_id, connector_id)
    
    if connector:
        # Update existing connector
        logger.info(f"Updating existing connector status: {charger_id}/{connector_id}")
        return ConnectorRepository.update_connector_status(
            db, company_id, site_id, charger_id, connector_id, status
        )
    else:
        # Create new connector
        new_connector = {
            "ConnectorCompanyId": company_id,
            "ConnectorSiteId": site_id,
            "ConnectorChargerId": charger_id,
            "ConnectorId": connector_id,
            "ConnectorName": f"Connector {connector_id}",
            "ConnectorType": "Unknown",  # Can be updated later with proper type
            "ConnectorEnabled": True,
            "ConnectorStatus": status
        }
        
        logger.info(f"Creating new connector: {charger_id}/{connector_id}")
        return ConnectorRepository.create_connector(db, new_connector)

@router.post("/ocpp/session/start")
async def start_charging_session_from_ocpp(
    charger_id: str,
    connector_id: str,
    id_tag: str = None,
    transaction_id: int = None,
    company_id: str = "DEF01",  # Default company ID
    site_id: str = "MAIN",      # Default site ID
    db: Session = Depends(get_db)
):
    """Start a charging session from OCPP StartTransaction"""
    
    logger.info(f"Starting charging session from OCPP: {charger_id}/{connector_id}")
    
    # Find driver by RFID tag if provided
    driver_id = None
    if id_tag:
        driver = DriverRepository.get_driver_by_rfid(db, id_tag)
        if driver:
            driver_id = driver.DriverId
    
    # Create new session
    new_session = {
        "ChargerSessionCompanyId": company_id,
        "ChargerSessionSiteId": site_id,
        "ChargerSessionChargerId": charger_id,
        "ChargerSessionConnectorId": connector_id,
        "ChargerSessionDriverId": driver_id,
        "ChargerSessionRFIDCard": id_tag,
        "ChargerSessionStart": datetime.now(),
        "ChargerSessionStatus": "In Progress",
        "ChargerSessionEnergyKWH": 0
    }
    
    # Create the session
    session = ChargeSessionRepository.create_session(db, new_session)
    
    # Update connector status
    ConnectorRepository.update_connector_status(
        db, company_id, site_id, charger_id, connector_id, "Charging"
    )
    
    return {
        "session_id": session.ChargeSessionId,
        "transaction_id": transaction_id or session.ChargeSessionId
    }

@router.post("/ocpp/session/end")
async def end_charging_session_from_ocpp(
    charger_id: str,
    connector_id: str,
    transaction_id: int,
    meter_value: int = 0,
    reason: str = "Remote",
    company_id: str = "DEF01",  # Default company ID
    site_id: str = "MAIN",      # Default site ID
    db: Session = Depends(get_db)
):
    """End a charging session from OCPP StopTransaction"""
    
    logger.info(f"Ending charging session from OCPP: {charger_id}/{connector_id}, transaction: {transaction_id}")
    
    # Find active session
    # Note: In a real implementation, you might need to query by transaction_id if that's what the OCPP client returns
    sessions = ChargeSessionRepository.get_sessions(
        db, company_id=company_id, site_id=site_id, 
        charger_id=charger_id
    )
    
    active_session = None
    for session in sessions:
        if (session.ChargerSessionChargerId == charger_id and 
            session.ChargerSessionConnectorId == connector_id and 
            not session.ChargerSessionEnd):
            active_session = session
            break
    
    if not active_session:
        logger.warning(f"No active session found for {charger_id}/{connector_id}")
        raise HTTPException(status_code=404, detail="No active session found")
    
    # End the session
    end_time = datetime.now()
    ended_session = ChargeSessionRepository.end_session(
        db, active_session.ChargeSessionId, end_time, meter_value, reason
    )
    
    # Update connector status
    ConnectorRepository.update_connector_status(
        db, company_id, site_id, charger_id, connector_id, "Available"
    )
    
    return {
        "session_id": ended_session.ChargeSessionId,
        "energy_kwh": ended_session.ChargerSessionEnergyKWH,
        "duration_seconds": ended_session.ChargerSessionDuration
    }

@router.post("/ocpp/meter-values")
async def record_meter_values_from_ocpp(
    charger_id: str,
    connector_id: str,
    transaction_id: int,
    meter_value: int,
    company_id: str = "DEF01",  # Default company ID
    site_id: str = "MAIN",      # Default site ID
    db: Session = Depends(get_db)
):
    """Record meter values from OCPP MeterValues"""
    
    logger.info(f"Recording meter values from OCPP: {charger_id}/{connector_id}, value: {meter_value}")
    
    # Find session by transaction_id or active session
    session = ChargeSessionRepository.get_session(db, transaction_id)
    
    if not session:
        logger.warning(f"No session found for transaction {transaction_id}")
        raise HTTPException(status_code=404, detail="No session found")
    
    # Update energy value
    session_data = {
        "ChargerSessionEnergyKWH": meter_value
    }
    
    updated_session = ChargeSessionRepository.update_session(db, session.ChargeSessionId, session_data)
    
    # Record event data
    event_data = {
        "EventsDataSessionId": session.ChargeSessionId,
        "EventsDataCompanyId": company_id,
        "EventsDataSiteId": site_id,
        "EventsDataChargerId": charger_id,
        "EventsDataConnectorId": connector_id,
        "EventsDataDateTime": datetime.now(),
        "EventsDataType": "Meter",
        "EventsDataTriggerReason": "MeterValues",
        "EventsDataOrigin": "OCPP",
        "EventsDataMeterValue": str(meter_value)
    }
    
    # In a real implementation, you would have a repository method for this
    # For now, we'll just return the event data
    
    return {
        "session_id": updated_session.ChargeSessionId,
        "meter_value": updated_session.ChargerSessionEnergyKWH,
        "event_data": event_data
    }

@router.post("/ocpp/charger/heartbeat")
async def record_heartbeat_from_ocpp(
    charger_id: str,
    company_id: str = "DEF01",  # Default company ID
    site_id: str = "MAIN",      # Default site ID
    db: Session = Depends(get_db)
):
    """Record heartbeat from OCPP Heartbeat"""
    
    logger.info(f"Recording heartbeat from OCPP: {charger_id}")
    
    # Update charger's last heartbeat
    charger = ChargerRepository.get_charger(db, company_id, site_id, charger_id)
    
    if not charger:
        logger.warning(f"Charger not found: {charger_id}")
        raise HTTPException(status_code=404, detail="Charger not found")
    
    charger_data = {
        "ChargerLastHeartbeat": datetime.now(),
        "ChargerIsOnline": True
    }
    
    updated_charger = ChargerRepository.update_charger(
        db, company_id, site_id, charger_id, charger_data
    )
    
    return {
        "charger_id": updated_charger.ChargerId,
        "last_heartbeat": updated_charger.ChargerLastHeartbeat,
        "is_online": updated_charger.ChargerIsOnline
    }