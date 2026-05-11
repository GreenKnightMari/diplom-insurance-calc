# main.py
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import io, base64
import matplotlib
matplotlib.use('Agg')  # Не-GUI бэкенд для matplotlib
import matplotlib.pyplot as plt
from calculator import TariffInput, calculate_tariffs

app = FastAPI(title="📊 Калькулятор страховых тарифов")

@app.post("/api/calculate")
def api_calculate(data: TariffInput):
    """Расчёт тарифов по переданным параметрам"""
    try:
        result = calculate_tariffs(data)
        return JSONResponse(content={"status": "ok", "data": result})
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Ошибка расчёта: {str(e)}")

@app.post("/api/calculate-with-plot")
def api_calculate_plot(data: TariffInput):
    """Расчёт + генерация графика распределения"""
    try:
        result = calculate_tariffs(data)
        
        # Генерация графика CDF
        x = np.linspace(0, result["initial_capital"] * 1.5, 500)
        cdf = gamma.cdf(x, a=result["gamma_alpha"], scale=1/result["gamma_beta"])
        
        buf = io.BytesIO()
        plt.figure(figsize=(8, 5))
        plt.plot(x / 1e6, cdf, color='blue', linewidth=2)
        plt.axhline(y=data.reliability, color='gray', linestyle=':', 
                   label=f"Надежность {data.reliability}")
        plt.title("Функция распределения совокупного ущерба")
        plt.xlabel("Ущерб (млн. руб.)")
        plt.ylabel("Вероятность R(x)")
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig(buf, format='png', dpi=150)
        plt.close()
        
        buf.seek(0)
        img_base64 = base64.b64encode(buf.read()).decode('utf-8')
        
        return JSONResponse(content={
            "status": "ok", 
            "data": result,
            "plot_base64": img_base64
        })
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Ошибка: {str(e)}")

# Раздача статики (фронтенд)
app.mount("/static", StaticFiles(directory="static"), name="static")
