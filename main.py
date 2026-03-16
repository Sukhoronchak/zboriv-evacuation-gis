import sqlite3
import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import uvicorn

app = FastAPI()

# Дозволяємо всі запити (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_PATH = "shelters.db"

# Функція ініціалізації бази (щоб нічого не пропадало)
def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    # Створюємо таблицю загрози, якщо її забули додати
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS hazards (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            radius INTEGER,
            lat REAL,
            lon REAL
        )
    ''')
    conn.commit()
    conn.close()

init_db()

class Hazard(BaseModel):
    name: str
    radius: int
    lat: float
    lon: float

@app.get("/shelters")
async def get_shelters():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM shelters")
    data = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return data

@app.get("/hazards")
async def get_hazards():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM hazards")
    data = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return data

@app.post("/hazards")
async def create_hazard(h: Hazard):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO hazards (name, radius, lat, lon) VALUES (?, ?, ?, ?)",
            (h.name, h.radius, h.lat, h.lon)
        )
        new_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return {**h.dict(), "id": new_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/hazards/{h_id}")
async def delete_hazard(h_id: int):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM hazards WHERE id = ?", (h_id,))
    conn.commit()
    conn.close()
    return {"status": "deleted"}

@app.get("/nearest_shelter")
async def nearest(lat: float, lon: float):
    # Тут залишається ваша логіка розрахунку відстані (з попереднього коду)
    pass 

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
