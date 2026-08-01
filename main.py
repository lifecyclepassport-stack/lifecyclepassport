import os
from fastapi import FastAPI, HTTPException
from fastapi.responses import Response
import qrcode
import io
from sqlalchemy import create_engine, Column, String, Float, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

# Datubāzes pieslēgums no Railway vides mainīgajiem (DATABASE_URL)
DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Baterijas datubāzes modelis
class BatteryModel(Base):
    __tablename__ = "batteries"
    
    battery_id = Column(String, primary_key=True, index=True)
    model = Column(String)
    manufacturer = Column(String)
    chemistry = Column(String)
    carbon_footprint = Column(Float)
    manufacturing_date = Column(Date)
    status = Column(String)

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Battery DPP API")

BASE_URL = os.getenv("BASE_URL", "https://battery-dpp-api-production-a9d8.up.railway.app")

@app.get("/")
def read_root():
    return {"message": "Bateriju DPP datubāzes sistēma darbojas!"}

@app.post("/battery/add")
def add_battery(battery_id: str, model: str, manufacturer: str, chemistry: str, carbon_footprint: float):
    db = SessionLocal()
    existing = db.query(BatteryModel).filter(BatteryModel.battery_id == battery_id).first()
    if existing:
        db.close()
        raise HTTPException(status_code=400, detail="Šāda baterija jau eksistē datubāzē!")
    
    new_battery = BatteryModel(
        battery_id=battery_id,
        model=model,
        manufacturer=manufacturer,
        chemistry=chemistry,
        carbon_footprint=carbon_footprint,
        manufacturing_date=datetime.now().date(),
        status="Active"
    )
    db.add(new_battery)
    db.commit()
    db.close()
    return {"status": "success", "battery_id": battery_id, "message": f"Baterija {battery_id} veiksmīgi saglabāta datubāzē!"}

@app.get("/battery/{battery_id}")
def get_battery(battery_id: str):
    db = SessionLocal()
    battery = db.query(BatteryModel).filter(BatteryModel.battery_id == battery_id).first()
    db.close()
    if not battery:
        raise HTTPException(status_code=404, detail="Baterija nav atrasta datubāzē")
    return {
        "battery_id": battery.battery_id,
        "model": battery.model,
        "manufacturer": battery.manufacturer,
        "manufacturing_date": str(battery.manufacturing_date),
        "chemistry": battery.chemistry,
        "carbon_footprint_kg_co2": battery.carbon_footprint,
        "status": battery.status,
        "accessed_date": datetime.now().strftime("%Y-%m-%d")
    }

@app.get("/generate-qr/{battery_id}")
def generate_qr(battery_id: str):
    current_date = datetime.now().strftime("%Y-%m-%d")
    url = f"{BASE_URL}/battery/{battery_id}?date={current_date}"
    
    img = qrcode.make(url)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    
    return Response(content=buf.getvalue(), media_type="image/png")
