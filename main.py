# main.py
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from calculator import TariffInput, calculate_tariffs

app = FastAPI(title="Калькулятор страховых тарифов")

# Подключаем папку со статикой (CSS, JS, картинки)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Главная страница: отдаём index.html при заходе на /
@app.get("/")
def read_root():
    return FileResponse("static/index.html")

# API-эндпоинт для расчёта
@app.post("/api/calculate")
def calculate(data: TariffInput):
    result = calculate_tariffs(data)
    return {"status": "ok", "data": result}
