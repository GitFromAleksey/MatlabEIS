import re
import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import lsq_linear  # Добавлен импорт для решения NNLS с регуляризацией Тихонова

# Имя файла с данными
file_name = "calib.txt"

frequencies = []
real_parts = []
imag_parts = []

# Исправленное регулярное выражение для извлечения Freq, Real и Imag частей (с учетом возможных знаков)
pattern = re.compile(
    r"Freq:\s*([\d.]+)\s*RcalVolt:\s*\(([-+]?[\d.]+),([-+]?[\d.]+)\)"
)

# Чтение и разбор файла
with open(file_name, "r", encoding="utf-8") as f:
    for line in f:
        match = pattern.search(line)
        if match:
            freq = float(match.group(1))
            real = float(match.group(2))
            imag = float(match.group(3))

            frequencies.append(freq)
            real_parts.append(real)
            imag_parts.append(imag)

# Конвертация в массивы numpy
real_parts = np.array(real_parts)
imag_parts = np.array(imag_parts)
frequencies = np.array(frequencies)

# Сортировка данных по возрастанию частоты (критически важно для корректного алгоритма DRT)
sort_idx = np.argsort(frequencies)
frequencies = frequencies[sort_idx]
real_parts = real_parts[sort_idx]
imag_parts = imag_parts[sort_idx]

# --- Расчет параметров для графика Боде ---
# Модуль (амплитуда)
magnitude = np.sqrt(real_parts**2 + imag_parts**2)
# Фаза в градусах
phase = np.degrees(np.arctan2(imag_parts, real_parts))


# =========================================================================
# РАСЧЕТ DRT (МЕТОД ТИХОНОВА + NNLS)
# =========================================================================
omega = 2 * np.pi * frequencies

# Задаем сетку времен релаксации tau на основе ваших частотных границ
tau_min = 1.0 / (max(omega))
tau_max = 1.0 / (min(omega))
# Равномерная логарифмическая сетка времен (80 точек)
tau_grid = np.logspace(np.log10(tau_min), np.log10(tau_max), 80)

N_freq = len(frequencies)
N_tau = len(tau_grid)

# Создание матрицы ядер A для мнимой части импеданса
A = np.zeros((N_freq, N_tau))
for i, w in enumerate(omega):
    for j, t in enumerate(tau_grid):
        A[i, j] = - (w * t) / (1 + (w * t)**2)

# Вектор правой части — мнимая часть ваших данных
b = imag_parts

# Параметр регуляризации Тихонова (лямбда)
# Если итоговый график DRT будет казаться зашумленным ("гребенка"), увеличьте до 0.1 - 0.2.
# Если пики окажутся слишком смазанными, уменьшите параметр до 0.005.
reg_param = 0.02 

# Модификация системы уравнений под штрафной член Тихонова
A_reg = np.vstack([A, reg_param * np.eye(N_tau)])
b_reg = np.concatenate([b, np.zeros(N_tau)])

# Линейный метод наименьших квадратов с ограничением неотрицательности (DRT >= 0)
res = lsq_linear(A_reg, b_reg, bounds=(0, np.inf))
drt_spectrum = res.x


# =========================================================================
# ГРАФИК 1: Годограф Найквиста
# =========================================================================
plt.figure(figsize=(10, 8))

# Строим точки, цвет которых зависит от частоты
scatter = plt.scatter(
    real_parts,
    imag_parts,
    c=frequencies,
    cmap="jet",
    norm=plt.Normalize(vmin=frequencies.min(), vmax=frequencies.max()),
    edgecolors="k",
    zorder=3,
)

# Соединяем точки линией
plt.plot(real_parts, imag_parts, color="gray", linestyle="-", alpha=0.6, zorder=2)

# Добавление текстовых подписей частоты для точек
step = 1
for i in range(0, len(frequencies), step):
    f_val = frequencies[i]
    f_text = f"{f_val/1000:.1f} кГц" if f_val >= 1000 else f"{f_val:.1f} Гц"
    
    plt.annotate(
        f_text,
        xy=(real_parts[i], imag_parts[i]),
        xytext=(5, 5),               
        textcoords="offset points",
        fontsize=7,
        alpha=0.85,
        bbox=dict(boxstyle="round,pad=0.2", fc="white", alpha=0.6, ec="none") 
    )

# Добавляем цветовую шкалу для частот
cbar = plt.colorbar(scatter)
cbar.set_label("Частота (Гц)", rotation=270, labelpad=15)

# Подписи осей и заголовок
plt.title("Годограф Найквиста (AD5941 RcalVolt)", fontsize=14)
plt.xlabel("Re(Z)", fontsize=12)
plt.ylabel("-Im(Z) (Емкостная составляющая сверху)", fontsize=12)

plt.gca().invert_yaxis()
plt.axhline(0, color="black", linewidth=0.8, linestyle="--")
plt.axvline(0, color="black", linewidth=0.8, linestyle="--")
plt.grid(True, linestyle=":", alpha=0.6)
plt.axis("equal")


# =========================================================================
# ГРАФИК 2: Расширенная диаграмма Боде + График DRT (3 подграфика)
# =========================================================================
# Создаем 3 строки графиков
fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(10, 10))

# 1. Модуль (Амплитуда)
ax1.plot(frequencies, magnitude,  color="blue",      marker="o", markersize=4, linestyle="-", label='|Z|')
ax1.plot(frequencies, real_parts, color="darkgreen", marker="^", markersize=4, linestyle="-", label='Re(Z)')
ax1.plot(frequencies, imag_parts, color="purple",    marker="v", markersize=4, linestyle="-", label='Im(Z)')
ax1.set_ylabel("Амплитуда |Z|,\nДействительная часть Re(Z),\nМнимая часть Im(Z)", fontsize=11, color="black")
ax1.tick_params(axis='y', labelcolor="black")
ax1.grid(True, which="both", linestyle=":", alpha=0.6)
ax1.legend()
ax1.set_xscale("log")
ax1.set_title("Расширенная диаграмма Боде и спектр DRT (RcalVolt)", fontsize=14)

# 2. Фаза
ax2.plot(frequencies, phase, color="red", marker="s", markersize=4, linestyle="-")
ax2.set_ylabel("Фаза (градусы)", fontsize=11, color="black")
ax2.tick_params(axis='y', labelcolor="black")
ax2.grid(True, which="both", linestyle=":", alpha=0.6)
ax2.set_xscale("log")

# 3. НОВЫЙ ПОДГРАФИК: Спектр DRT (Распределение времен релаксации)
ax3.plot(tau_grid, drt_spectrum, color="orangered", lw=2, linestyle="-")
ax3.fill_between(tau_grid, 0, drt_spectrum, color="orangered", alpha=0.15)
ax3.set_xscale("log")
ax3.set_xlabel("Время релаксации \u03c4 (секунды)", fontsize=12)
ax3.set_ylabel("Интенсивность\nDRT", fontsize=11, color="black")
ax3.tick_params(axis='y', labelcolor="black")
ax3.grid(True, which="both", linestyle=":", alpha=0.6)

plt.tight_layout()
plt.show()
