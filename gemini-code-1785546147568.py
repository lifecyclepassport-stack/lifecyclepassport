from datetime import datetime
import io
import os
import qrcode
from fastapi import FastAPI, HTTPException, Response
from sqlalchemy import Column, Date, Float, String, Text, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Iegūst PostgreSQL adresi no Railway vides mainīgajiem
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
  # Lokālai testēšanai, ja Railway mainīgais nav atrasts
  DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/batterydb"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# Datu bāzes tabulas struktūra baterijai
class BatteryModel(Base):
  __tablename__ = "batteries"

  battery_id = Column(String, primary_key=True, index=True)
  model = Column(String)
  manufacturer = Column(String)
  manufacturing_date = Column(Date)
  chemistry = Column(String)
  carbon_footprint = Column(Float)
  status = Column(String)


# Izveido tabulu, ja tā vēl neeksistē
Base.metadata.create_all(bind=engine)

app = FastAPI()
BASE_URL = os.getenv("BASE_URL", "https://tava-sistema.lv")


@app.get("/")
def home():
  return {"message": "Bateriju DPP datubāzes sistēma darbojas!"}


# Pievienot jaunu bateriju datubāzē (Parauga ievietošanai)
@app.post("/battery/add")
def add_battery(
    battery_id: str,
    model: str,
    manufacturer: str,
    chemistry: str,
    carbon_footprint: float,
):
  db = SessionLocal()
  existing = (
      db.query(BatteryModel)
      .filter(BatteryModel.battery_id == battery_id)
      .first()
  )
  if existing:
    db.close()
    raise HTTPException(
        status_code=400, detail="Šāda baterija jau eksistē datubāzē!"
    )

  new_battery = BatteryModel(
      battery_id=battery_id,
      model=model,
      manufacturer=manufacturer,
      manufacturing_date=datetime.now().date(),
      chemistry=chemistry,
      carbon_footprint=carbon_footprint,
      status="Active",
  )
  db.add(new_battery)
  db.commit()
  db.close()
  return {
      "message": f"Baterija {battery_id} veiksmīgi saglabāta datubāzē!",
      "date": str(datetime.now().date()),
  }


# Skenēt QR kodu un saņemt datus no datubāzes
@app.get("/battery/{battery_id}")
def get_battery_info(battery_id: str):
  db = SessionLocal()
  battery = (
      db.query(BatteryModel)
      .filter(BatteryModel.battery_id == battery_id)
      .first()
  )
  db.close()

  if not battery:
    raise HTTPException(status_code=404, detail="Baterija nav atrasta datubāzē")

  today = datetime.now().strftime("%Y-%m-%d")
  return {
      "battery_id": battery.battery_id,
      "model": battery.model,
      "manufacturer": battery.manufacturer,
      "manufacturing_date": str(battery.manufacturing_date),
      "chemistry": battery.chemistry,
      "carbon_footprint_kg_co2": battery.carbon_footprint,
      "status": battery.status,
      "accessed_date": today,
  }


# Ģenerēt QR kodu
@app.get("/generate-qr/{battery_id}")
def generate_qr(battery_id: str):
  current_date = datetime.now().strftime("%Y-%m-%d")
  data_to_encode = f"{BASE_URL}/battery/{battery_id}?date={current_date}"

  img = qrcode.make(data_to_encode)
  buf = io.BytesIO()
  img.save(buf, format="PNG")
  buf.seek(0)

  return Response(content=buf.getvalue(), media_type="image/png")
