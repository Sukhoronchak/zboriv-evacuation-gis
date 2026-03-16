import sqlite3
import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import uvicorn
import math

app = FastAPI(title="Eco-Evacuation System API")

# Налаштування CORS, щоб фронтенд міг звертатися до бекенду
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_PATH = "shelters.db"

def execute_query(query: str, params: Optional[dict] = None, fetch: bool = False):
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        
        if fetch or query.strip().upper().startswith("SELECT"):
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        
        conn.commit()
        return True
    except Exception as e:
        print(f"❌ Database Error: {e}")
        return None
    finally:
        if conn:
            conn.close()

def calculate_distance(lat1, lon1, lat2, lon2):
    R = 6371000 
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)
    a = math.sin(delta_phi / 2.0)**2 + \
        math.cos(phi1) * math.cos(phi2) * \
        math.sin(delta_lambda / 2.0)**2
    return R * (2 * math.atan2(math.sqrt(a), math.sqrt(1 - a)))

class Hazard(BaseModel):
    name: str
    radius: int
    lat: float
    lon: float

@app.get("/shelters")
async def get_shelters():
    data = execute_query('SELECT * FROM shelters', fetch=True)
    return data if data else []

@app.get("/hazards")
async def get_hazards():
    data = execute_query('SELECT * FROM hazards', fetch=True)
    return data if data else []

@app.get("/nearest_shelter")
async def get_nearest_shelter(lat: float, lon: float):
    shelters = execute_query('SELECT * FROM shelters', fetch=True)
    if not shelters:
        raise HTTPException(status_code=404, detail="Укриття не знайдені")
    nearest = min(shelters, key=lambda s: calculate_distance(lat, lon, s['lat'], s['lon']))
    nearest['distance_m'] = round(calculate_distance(lat, lon, nearest['lat'], nearest['lon']), 2)
    return nearest

@app.post("/hazards")
async def create_hazard(h: Hazard):
    sql = "INSERT INTO hazards (name, radius, lat, lon) VALUES (:n, :r, :la, :lo)"
    params = {"n": h.name, "r": h.radius, "la": h.lat, "lo": h.lon}
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(sql, params)
    new_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return {**h.dict(), "id": new_id}

@app.delete("/hazards/{h_id}")
async def delete_hazard(h_id: int):
    if execute_query("DELETE FROM hazards WHERE id = :id", {"id": h_id}):
        return {"status": "deleted"}
    raise HTTPException(status_code=404, detail="Not found")

if __name__ == "__main__":
    # Отримуємо порт від Render або використовуємо 8000 локально
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)