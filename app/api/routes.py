from fastapi import APIRouter, HTTPException
from app.ws.connection_manager import manager

router = APIRouter()

@router.get("/")
async def root():
    return {"status": "running", "message": "OCPP Server is running"}

@router.get("/charge_points")
async def get_charge_points():
    charge_points = manager.get_charge_points()
    return {"count": len(charge_points), "charge_points": list(charge_points.keys())}

@router.post("/charge_points/{charge_point_id}/reset")
async def reset_charge_point(charge_point_id: str, type: str = "Soft"):
    charge_point = manager.get_charge_points().get(charge_point_id)
    if not charge_point:
        raise HTTPException(status_code=404, detail=f"Charge point '{charge_point_id}' not connected.")
    
    try:
        response = await charge_point.reset_req(type=type)
        return {"status": "success", "command_result": response.status}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Reset command failed: {str(e)}")
