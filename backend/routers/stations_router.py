from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from database import get_db
import models
import schemas
import auth
from algorithms.ev_selection import select_station
from algorithms.nash_pricing import solve_nash

router = APIRouter(tags=["Stations & Operations"])

@router.post("/stations", response_model=schemas.StationResponse)
def create_station(
    station_data: schemas.StationCreate,
    db: Session = Depends(get_db),
    user: models.User = Depends(auth.require_role("station_owner"))
):
    station = models.Station(**station_data.dict(), owner_id=user.id)
    db.add(station)
    db.commit()
    db.refresh(station)
    return station

@router.get("/stations/my", response_model=List[schemas.StationResponse])
def get_my_stations(
    db: Session = Depends(get_db),
    user: models.User = Depends(auth.require_role("station_owner"))
):
    return db.query(models.Station).filter(models.Station.owner_id == user.id).all()

@router.get("/stations/public", response_model=List[schemas.StationResponse])
def get_public_stations(db: Session = Depends(get_db)):
    return db.query(models.Station).all()

@router.get("/market", response_model=schemas.MarketParamsSchema)
def get_market_params(db: Session = Depends(get_db)):
    params = db.query(models.MarketParams).first()
    if not params:
        params = models.MarketParams()
        db.add(params)
        db.commit()
        db.refresh(params)
    return params

@router.post("/pricing/run")
def run_pricing(
    db: Session = Depends(get_db),
    user: models.User = Depends(auth.require_role("station_owner"))
):
    stations = db.query(models.Station).all()
    if len(stations) < 2:
        raise HTTPException(status_code=400, detail="At least 2 stations are required to solve Nash Equilibrium")
    
    market = get_market_params(db)
    mp_dict = {
        "rho": market.rho, "mu1": market.mu1, "sigma": market.sigma,
        "C_min": market.C_min, "C_max": market.C_max, "Cw": market.Cw
    }
    
    st_input = [
        {
            "id": s.id, "location_km": s.location_km, "eta": s.energy_cost_eta,
            "wait_hr": s.expected_wait_hr, "terminal_cost": s.terminal_cost
        }
        for s in stations
    ]
    
    sorted_st, prices, profits = solve_nash(market.L, st_input, mp_dict)
    
    output = []
    for s_dict, p, prof in zip(sorted_st, prices, profits):
        st_obj = db.query(models.Station).filter(models.Station.id == s_dict["id"]).first()
        st_obj.published_price = round(p, 4)
        
        run_record = models.EquilibriumRun(
            station_id=st_obj.id, ne_price=round(p, 4), ne_profit=round(prof, 2)
        )
        db.add(run_record)
        output.append({
            "station_id": st_obj.id, "name": st_obj.name,
            "location_km": st_obj.location_km, "ne_price": round(p, 4),
            "ne_profit": round(prof, 2)
        })
    
    db.commit()
    return {"status": "success", "results": output}

@router.post("/ev/recommend")
def recommend_station(req: schemas.EVSelectionRequest, db: Session = Depends(get_db)):
    stations = db.query(models.Station).all()
    if not stations:
        raise HTTPException(status_code=404, detail="No stations available")
    
    st_input = [
        {
            "id": s.id, "name": s.name, "location_km": s.location_km,
            "price": s.published_price, "eta": s.energy_cost_eta, "wait_hr": s.expected_wait_hr
        }
        for s in stations
    ]
    
    rankings = select_station(req.dict(), st_input)
    return {"ev_request": req.dict(), "rankings": rankings}