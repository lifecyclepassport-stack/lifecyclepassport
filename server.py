import os
from fastapi import FastAPI, HTTPException
from fastapi.responses import Response
import qrcode
import io
from sqlalchemy import create_engine, Column, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Drošs URL, kas nekad neizraisīs NameError kļūdu
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./test.db")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class BatteryModel(Base):
    __tablename__ = "batteries"
    
    battery_id = Column(String, primary_key=True, index=True)
    model = Column(String)
    manufacturer = Column(String)
    chemistry = Column(String)
    carbon_footprint = Column(Float)
    manufacturing_date = Column(String, default="2026-01-01")
    status = Column(String, default="Active")

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Battery DPP API")

@app.get("/")
def read_root():
    return {"message": "Bateriju sistēma darbojas bez kļūdām!"}

@app.post("/battery/add")
def add_battery(battery_id: str, model: str, manufacturer: str, chemistry: str, carbon_footprint: float, manufacturing_date: str = "2026-01-01", status: str = "Active"):
    db = SessionLocal()
    try:
        existing = db.query(BatteryModel).filter(BatteryModel.battery_id == battery_id).first()
        if existing:
            raise HTTPException(status_code=400, detail="Battery already exists")
        
        new_battery = BatteryModel(
            battery_id=battery_id,
            model=model,
            manufacturer=manufacturer,
            chemistry=chemistry,
            carbon_footprint=carbon_footprint,
            manufacturing_date=manufacturing_date,
            status=status
        )
        db.add(new_battery)
        db.commit()
        return {"status": "success", "battery_id": battery_id}
    finally:
        db.close()

@app.get("/battery/{battery_id}")
def get_battery(battery_id: str):
    db = SessionLocal()
    try:
        battery = db.query(BatteryModel).filter(BatteryModel.battery_id == battery_id).first()
        if not battery:
            raise HTTPException(status_code=404, detail="Battery not found")
        return {
            "battery_id": battery.battery_id,
            "model": battery.model,
            "manufacturer": battery.manufacturer,
            "chemistry": battery.chemistry,
            "carbon_footprint": battery.carbon_footprint,
            "manufacturing_date": battery.manufacturing_date,
            "status": battery.status
        }
    finally:
        db.close()
