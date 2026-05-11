# main.py
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse  # <-- Важно!
from calculator import TariffInput, calculate_tariffs

app = FastAPI(title="Калькулятор")

# Подключение статики
app.mount("/static", StaticFiles(directory="static"), name="static")

# ГЛАВНАЯ СТРАНИЦА (этого раньше не было)
@app.get("/")
def read_root():
    return FileResponse("static/index.html")

# API для расчёта
@app.post("/api/calculate")
def calculate( TariffInput):
    result = calculate_tariffs(data)
    return {"status": "ok", "data": result}
