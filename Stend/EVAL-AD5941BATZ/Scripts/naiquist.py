import re
import matplotlib.pyplot as plt
import numpy as np

# Имя файла с данными
file_name = "31.log"

frequencies = []
real_parts = []
imag_parts = []

# Регулярное выражение для извлечения Freq, Real и Imag частей
pattern = re.compile(
    r"Freq:\s*([\d.]+)\s*RcalVolt:\s*\(([-?\d.]+),([-?\d.]+)\)"
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

# --- Расчет параметров для графика Боде ---
# Модуль (амплитуда)
magnitude = np.sqrt(real_parts**2 + imag_parts**2)
# Фаза в градусах
phase = np.degrees(np.arctan2(imag_parts, real_parts))


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

# Добавляем цветовую шкалу для частот
cbar = plt.colorbar(scatter)
cbar.set_label("Частота (Гц)", rotation=270, labelpad=15)

# Подписи осей и заголовок
plt.title("Годограф Найквиста (AD5941 RcalVolt)", fontsize=14)
plt.xlabel("Re(Z)", fontsize=12)
plt.ylabel("-Im(Z) (Емкостная составляющая сверху)", fontsize=12)

# В электрохимии принято инвертировать ось Y, чтобы -Im(Z) росла вверх
plt.gca().invert_yaxis()

# Отображение координатных сеток через ноль
plt.axhline(0, color="black", linewidth=0.8, linestyle="--")
plt.axvline(0, color="black", linewidth=0.8, linestyle="--")
plt.grid(True, linestyle=":", alpha=0.6)

# Одинаковый масштаб по осям X и Y
plt.axis("equal")


# =========================================================================
# ГРАФИК 2: Диаграмма Боде (Амплитуда и Фаза)
# =========================================================================
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8), sharex=True)

# Верхний подграфик: Модуль (Амплитуда)
ax1.plot(frequencies, magnitude, color="blue", marker="o", markersize=4, linestyle="-")
ax1.set_ylabel("Амплитуда (Модуль)", fontsize=12, color="blue")
ax1.tick_params(axis='y', labelcolor="blue")
ax1.set_xscale("log")  # Логарифмическая шкала частот
ax1.grid(True, which="both", linestyle=":", alpha=0.6)
ax1.set_title("Диаграмма Боде (AD5941 RcalVolt)", fontsize=14)

# Нижний подграфик: Фаза
ax2.plot(frequencies, phase, color="red", marker="s", markersize=4, linestyle="-")
ax2.set_xlabel("Частота (Гц)", fontsize=12)
ax2.set_ylabel("Фаза (градусы)", fontsize=12, color="red")
ax2.tick_params(axis='y', labelcolor="red")
ax2.set_xscale("log")  # Логарифмическая шкала частот
ax2.grid(True, which="both", linestyle=":", alpha=0.6)

# Автоматическое выравнивание отступов
plt.tight_layout()

# Показываем оба окна
plt.show()
