import sys
from pathlib import Path

# Explicitly add backend root directory to sys.path so all imports work cleanly
BACKEND_DIR = Path(__file__).resolve().parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base
from routers.auth_router import router as auth_router
from routers.stations_router import router as stations_router

# Initialize database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="EV Charging Pricing System API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(stations_router)

@app.get("/")
def read_root():
    return {"message": "EV Charging Pricing System API is running"}