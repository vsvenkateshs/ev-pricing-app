from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String, nullable=False)  # 'station_owner' or 'ev_owner'

    stations = relationship("Station", back_populates="owner")
    requests = relationship("ChargingRequest", back_populates="user")

class Station(Base):
    __tablename__ = "stations"

    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"))
    name = Column(String, nullable=False)
    location_km = Column(Float, nullable=False)
    energy_cost_eta = Column(Float, nullable=False)
    expected_wait_hr = Column(Float, nullable=False)
    terminal_cost = Column(Float, nullable=False)
    published_price = Column(Float, default=0.10)

    owner = relationship("User", back_populates="stations")

class MarketParams(Base):
    __tablename__ = "market_params"

    id = Column(Integer, primary_key=True, index=True)
    L = Column(Float, default=100.0)
    rho = Column(Float, default=1.0)
    mu1 = Column(Float, default=1.0)
    sigma = Column(Float, default=0.5)
    C_min = Column(Float, default=1.0)
    C_max = Column(Float, default=10.0)
    Cw = Column(Float, default=5.0)

class EquilibriumRun(Base):
    __tablename__ = "equilibrium_runs"

    id = Column(Integer, primary_key=True, index=True)
    run_at = Column(DateTime, default=datetime.utcnow)
    station_id = Column(Integer, ForeignKey("stations.id"))
    ne_price = Column(Float, nullable=False)
    ne_profit = Column(Float, nullable=False)

class ChargingRequest(Base):
    __tablename__ = "charging_requests"

    id = Column(Integer, primary_key=True, index=True)
    ev_user_id = Column(Integer, ForeignKey("users.id"))
    location_km = Column(Float, nullable=False)
    energy_kwh = Column(Float, nullable=False)
    travel_cost_per_km = Column(Float, nullable=False)
    chosen_station_id = Column(Integer, ForeignKey("stations.id"))
    total_cost = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="requests")