from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from calculator import TariffInput, calculate_tariffs

app = FastAPI(title="Калькулятор страховых тарифов")

# Подключаем папку static для CSS/JS/картинок
app.mount("/static", StaticFiles(directory="static"), name="static")

# 👇 ГЛАВНОЕ: говорим FastAPI отдавать index.html при заходе на /
@app.get("/")
def read_root():
    return FileResponse("static/index.html")

# Эндпоинт для расчёта
@app.post("/api/calculate")
def calculate( TariffInput):
    result = calculate_tariffs(data)
    return {"status": "ok", "data": result}
