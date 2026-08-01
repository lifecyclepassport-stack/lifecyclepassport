import os
from fastapi import FastAPI, HTTPException
from fastapi.responses import Response
import qrcode
import io
from sqlalchemy import create_engine, Column, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL")

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

# Droši izveido tabulu, ja tādas vēl nav
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Battery DPP API")

@app.get("/")
def read_root():
    return {"message": "Bateriju DPP datubāzes sistēma darbojas!"}

@app.post("/battery/add")
def add_battery(battery_id: str, model: str, manufacturer: str, chemistry: str, carbon_footprint: float):
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
            carbon_footprint=carbon_footprint
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
            "carbon_footprint": battery.carbon_footprint
        }
    finally:
        db.close()

@app.get("/generate-qr/{battery_id}")
def generate_qr(battery_id: str):
    url = f"https://battery-dpp-api-production-a9d8.up.railway.app/battery/{battery_id}"
    img = qrcode.make(url)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return Response(content=buf.getvalue(), media_type="image/png")
