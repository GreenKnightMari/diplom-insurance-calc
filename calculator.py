# calculator.py
import numpy as np
from scipy.stats import gamma
from decimal import Decimal
from pydantic import BaseModel, Field

class TariffInput(BaseModel):
    """Валидация входных параметров"""
    n_enterprises: int = Field(..., gt=0, le=10000, description="Количество предприятий")
    lam: float = Field(..., gt=0, le=1, description="Интенсивность ущерба (λ)")
    term_years: float = Field(..., gt=0, le=50, description="Срок накопления, лет")
    s_max: float = Field(..., gt=0, description="Макс. ответственность, руб.")
    reliability: float = Field(..., gt=0.5, lt=1.0, description="Надежность (вероятность)")
    loading: float = Field(..., ge=0, lt=1, description="Нагрузка, доля")
    discount_rate: float = Field(..., ge=0, le=0.2, description="Норма дисконтирования")
    use_discounting: bool = Field(default=False, description="Учитывать разновременность")

def calculate_tariffs(params: TariffInput) -> dict:
    """
    Основная расчётная функция.
    Возвращает словарь с результатами и параметрами распределения.
    """
    N = params.n_enterprises
    lam = params.lam
    T = params.term_years
    S_vos = params.s_max
    P_gamma = params.reliability
    f = params.loading
    delta = params.discount_rate

    # Параметры равномерного распределения ущерба
    m0 = S_vos / 2
    D0 = (S_vos**2) / 12

    if not params.use_discounting:
        # Модель 1: без дисконтирования
        eta = N * lam * T
        chi1 = eta * m0
        chi2 = eta * (m0**2 + D0)
    else:
        # Модель 2: с дисконтированием (формула 25)
        chi1 = N * lam * m0 * (1 - np.exp(-delta * T)) / delta
        chi2 = N * lam * (m0**2 + D0) * (1 - np.exp(-2 * delta * T)) / (2 * delta)

    # Аппроксимация Гамма-распределением
    beta_param = chi1 / chi2 if chi2 != 0 else 1e-10
    alpha_param = chi1 * beta_param if beta_param != 0 else 1e-10

    # Нетто-премия (начальный капитал/резерв)
    Pr = gamma.ppf(P_gamma, a=alpha_param, scale=1/beta_param) if alpha_param > 0 else 0

    # Нетто-тариф (%)
    denominator = N * S_vos * T
    Tr_n = (Pr * 100) / denominator if denominator != 0 else 0

    # Брутто-тариф (%)
    if not params.use_discounting:
        Tr_br = (Tr_n / (1 - f)) * np.exp(delta * T) if (1 - f) != 0 else 0
    else:
        Tr_br = Tr_n / (1 - f) if (1 - f) != 0 else 0

    # Сравнение моделей (если нужно)
    if params.use_discounting:
        # Пересчитаем Модель 1 для сравнения
        params_no_disc = params.model_copy(update={"use_discounting": False})
        _, _, tr_br_m1, _, _ = calculate_tariffs(params_no_disc).values()
        savings = (1 - Tr_br / tr_br_m1) * 100 if tr_br_m1 != 0 else 0
        better_model = "Модель 2 (с дисконтированием)" if Tr_br < tr_br_m1 else "Модель 1"
    else:
        savings = None
        better_model = None

    return {
        "initial_capital": round(Pr, 2),
        "net_tariff_percent": round(Tr_n, 4),
        "gross_tariff_percent": round(Tr_br, 4),
        "gamma_alpha": round(alpha_param, 4),
        "gamma_beta": round(beta_param, 8),
        "better_model": better_model,
        "savings_percent": round(savings, 2) if savings is not None else None
    }
