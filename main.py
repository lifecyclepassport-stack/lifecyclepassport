import os
from fastapi import FastAPI, HTTPException
from fastapi.responses import Response
import qrcode
import io
from sqlalchemy import create_engine, Column, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

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

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Battery DPP API")

@app.get("/")
def read_root():
    return {"message": "Bateriju DPP datubāzes sistēma darbojas!"}

@app.post("/battery/add")
def add_battery(battery_id: str, model: str, manufacturer: str, chemistry: str, carbon_footprint: float):
    db = SessionLocal()
    existing = db.query(BatteryModel).filter(BatteryModel.battery_id == battery_id).first()
    if existing:
        db.close()
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
    db.close()
    return {"status": "success", "battery_id": battery_id}

@app.get("/battery/{battery_id}")
def get_battery(battery_id: str):
    db = SessionLocal()
    battery = db.query(BatteryModel).filter(BatteryModel.battery_id == battery_id).first()
    db.close()
    if not battery:
        raise HTTPException(status_code=404, detail="Battery not found")
    return {
        "battery_id": battery.battery_id,
        "model": battery.model,
        "manufacturer": battery.manufacturer,
        "chemistry": chemistry if 'chemistry' in locals() else battery.chemistry,
        "carbon_footprint": battery.carbon_footprint
    }

@app.get("/generate-qr/{battery_id}")
def generate_qr(battery_id: str):
    # Izveido saiti, uz kuru QR kods vedīs (izmantojot tavu Railway domēnu)
    url = f"https://battery-dpp-api-production-a9d8.up.railway.app/battery/{battery_id}"
    
    img = qrcode.make(url)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    
    return Response(content=buf.getvalue(), media_type="image/png")
