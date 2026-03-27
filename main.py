import sqlite3
import os
import math
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import uvicorn

app = FastAPI()

# 1. НАЛАШТУВАННЯ CORS (Дозволяє запити з будь-якого домену, включаючи GitHub Pages)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_PATH = "shelters.db"

# 2. ІНІЦІАЛІЗАЦІЯ БАЗИ ДАНИХ
def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    # Таблиця загроз
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS hazards (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            radius INTEGER,
            lat REAL,
            lon REAL
        )
    ''')
    # Таблиця укриттів
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS shelters (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            capacity INTEGER,
            lat REAL,
            lon REAL
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# 3. МОДЕЛЬ ДАНИХ
class Hazard(BaseModel):
    name: str
    radius: int
    lat: float
    lon: float

# 4. ДОПОМІЖНА ФУНКЦІЯ: Формула Гаверсину для розрахунку відстані на сфері
def get_distance(lat1, lon1, lat2, lon2):
    R = 6371000  # Радіус Землі в метрах
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
    return 2 * R * math.atan2(math.sqrt(a), math.sqrt(1-a))

# --- МАРШРУТИ (ENDPOINTS) ---

# Отримати всі укриття
@app.get("/shelters")
async def get_shelters():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM shelters")
        data = [dict(row) for row in cursor.fetchall()]
    except sqlite3.OperationalError:
        data = []
    finally:
        conn.close()
    return data

# Отримати всі загрози
@app.get("/hazards")
async def get_hazards():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM hazards")
    data = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return data

# Створити нову загрозу
@app.post("/hazards")
async def create_hazard(h: Hazard):
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

# Оновити існуючу загрозу (Радіус, координати тощо)
@app.put("/hazards/{h_id}")
async def update_hazard(h_id: int, h: Hazard):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE hazards SET name=?, radius=?, lat=?, lon=? WHERE id=?",
        (h.name, h.radius, h.lat, h.lon, h_id)
    )
    conn.commit()
    conn.close()
    # Повертаємо об'єкт із ID для коректного оновлення карти на фронтенді
    return {**h.dict(), "id": h_id, "status": "updated"}

# Видалити загрозу
@app.delete("/hazards/{h_id}")
async def delete_hazard(h_id: int):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM hazards WHERE id = ?", (h_id,))
    conn.commit()
    # Команда VACUUM очищує місце в БД та видаляє кешовані записи
    try:
        conn.execute("VACUUM")
    except:
        pass
    conn.close()
    return {"status": "deleted", "id": h_id}

# Пошук найближчого укриття за координатами користувача
@app.get("/nearest_shelter")
async def nearest(lat: float, lon: float):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM shelters")
    shelters = cursor.fetchall()
    conn.close()

    if not shelters:
        raise HTTPException(status_code=404, detail="Укриття не знайдені")

    nearest_s = None
    min_dist = float('inf')

    for s in shelters:
        d = get_distance(lat, lon, s['lat'], s['lon'])
        if d < min_dist:
            min_dist = d
            nearest_s = dict(s)
    
    nearest_s['distance_m'] = round(min_dist, 2)
    return nearest_s

# 5. ЗАПУСК СЕРВЕРА
if __name__ == "__main__":
    # Render динамічно призначає порт через змінну середовища
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
