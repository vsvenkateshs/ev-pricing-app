from pydantic import BaseModel, EmailStr, field_validator
from typing import List, Optional

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    role: str

    @field_validator("role")
    @classmethod
    def role_must_be_valid(cls, v: str) -> str:
        if v not in ("station_owner", "ev_owner"):
            raise ValueError("role must be 'station_owner' or 'ev_owner'")
        return v

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
    L: float = 12.0
    rho: float = 50.0
    mu1: float = 60.0
    sigma: float = 5.77
    C_min: float = 0.5
    C_max: float = 1.5
    Cw: float = 4.0
    class Config:
        from_attributes = True

class EVSelectionRequest(BaseModel):
    location_km: float
    energy_kwh: float
    travel_cost_per_km: float
    waiting_cost_per_hr: float