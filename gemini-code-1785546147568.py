from datetime import datetime
import io
import os
import qrcode
from fastapi import FastAPI, Response

app = FastAPI()

BASE_URL = os.getenv("BASE_URL", "https://tava-sistema.lv")


@app.get("/")
def home():
  return {"message": "Bateriju DPP sistēma darbojas!"}


@app.get("/generate-qr/{battery_id}")
def generate_qr(battery_id: str):
  current_date = datetime.now().strftime("%Y-%m-%d")
  data_to_encode = f"{BASE_URL}/battery/{battery_id}?date={current_date}"

  img = qrcode.make(data_to_encode)
  buf = io.BytesIO()
  img.save(buf, format="PNG")
  buf.seek(0)

  return Response(content=buf.getvalue(), media_type="image/png")


@app.get("/battery/{battery_id}")
def get_battery_info(battery_id: str, date: str = None):
  today = datetime.now().strftime("%Y-%m-%d")
  return {
      "battery_id": battery_id,
      "accessed_date": today,
      "status": "Aktīva un pārbaudīta",
      "message": f"Dati veiksmīgi ielādēti datumā: {today}",
  }