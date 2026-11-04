from pydantic import BaseModel, EmailStr
from typing import List, Optional

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    role: str

class UserResponse(BaseModel):
    id: int
    email: EmailStr
    role: str
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str
    role: str

class StationCreate(BaseModel):
    name: str
    location_km: float
    energy_cost_eta: float
    expected_wait_hr: float
    terminal_cost: float

class StationResponse(StationCreate):
    id: int
    owner_id: int
    published_price: float
    class Config:
        from_attributes = True

class MarketParamsSchema(BaseModel):
    L: float
    rho: float
    mu1: float
    sigma: float
    C_min: float
    C_max: float
    Cw: float
    class Config:
        from_attributes = True

class EVSelectionRequest(BaseModel):
    location_km: float
    energy_kwh: float
    travel_cost_per_km: float
    waiting_cost_per_hr: float