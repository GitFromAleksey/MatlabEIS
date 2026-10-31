import re
import matplotlib.pyplot as plt
import numpy as np

# Имя файла с новыми данными
file_name = "mes3.txt"

frequencies = []
real_parts = []
imag_parts = []

# Регулярное выражение под новый формат логов:
# Freq: [число] (real, image) = ,[число] , [число] ,mOhm
pattern = re.compile(
    r"Freq:\s*([\d.]+)[^=]+=\s*,\s*([^,]+)\s*,\s*([^,]+)"
)

# Чтение и разбор файла
with open(file_name, "r", encoding="utf-8") as f:
    for line in f:
        match = pattern.search(line)
        if match:
            freq = float(match.group(1))
            real = float(match.group(2))
            imag = float(match.group(3))

            # Фильтрация явных аппаратных сбоев (выбросов)
            # Например, убираем огромные значения порядка 10^10 и выше
            if abs(real) > 1e6 or abs(imag) > 1e6:
                continue

            frequencies.append(freq)
            real_parts.append(real)
            imag_parts.append(imag)

# Конвертация в массивы numpy
real_parts = np.array(real_parts)
imag_parts = np.array(imag_parts)
frequencies = np.array(frequencies)

# --- Расчет параметров для графика Боде ---
# Модуль (амплитуда в мОм)
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

# -------------------------------------------------------------------------
# НОВЫЙ БЛОК: Добавление текстовых подписей частоты для точек
# -------------------------------------------------------------------------
# Шаг прореживания (выводить каждую N-ю точку). 
# Если точек мало, измените step на 1, чтобы подписать абсолютно все.
step = 1

for i in range(0, len(frequencies), step):
    # Форматируем вывод частоты: если >= 1000 Гц, переводим в кГц для компактности
    f_val = frequencies[i]
    f_text = f"{f_val/1000:.1f} кГц" if f_val >= 1000 else f"{f_val:.1f} Гц"
    
    # Добавляем подпись с небольшим смещением (xytext)
    plt.annotate(
        f_text,
        xy=(real_parts[i], imag_parts[i]),
        xytext=(5, 5),               # Смещение текста в пунктах по (X, Y)
        textcoords="offset points",
        fontsize=7,
        alpha=0.85,
        bbox=dict(boxstyle="round,pad=0.2", fc="white", alpha=0.6, ec="none") # Подложка для читаемости
    )
# -------------------------------------------------------------------------


# Добавляем цветовую шкалу для частот
cbar = plt.colorbar(scatter)
cbar.set_label("Частота (Гц)", rotation=270, labelpad=15)

# Подписи осей и заголовок
plt.title("Годограф Найквиста (AD5941 Батарея)", fontsize=14)
plt.xlabel("Re(Z), мОм", fontsize=12)
plt.ylabel("-Im(Z), мОм (Емкостная составляющая сверху)", fontsize=12)

# В электрохимии принято инвертировать ось Y, чтобы -Im(Z) росла вверх
plt.gca().invert_yaxis()

# Отображение координатных сеток через ноль
plt.axhline(0, color="black", linewidth=0.8, linestyle="--")
plt.axvline(0, color="black", linewidth=0.8, linestyle="--")
plt.grid(True, linestyle=":", alpha=0.6)

# Одинаковый масштаб по осям X и Y
plt.axis("equal")


# =========================================================================
# ГРАФИК 2: Расширенная диаграмма Боде (4 подграфика)
# =========================================================================
# Создаем 4 строки графиков с общей осью X (sharex=True)
fig, (ax1, ax2, ax3, ax4) = plt.subplots(4, 1, figsize=(10, 12), sharex=True)

# 1. Модуль (Амплитуда)
ax1.plot(frequencies, magnitude, color="blue", marker="o", markersize=4, linestyle="-")
ax1.set_ylabel("Амплитуда\n|Z|, мОм", fontsize=11, color="blue")
ax1.tick_params(axis='y', labelcolor="blue")
ax1.grid(True, which="both", linestyle=":", alpha=0.6)
ax1.set_title("Расширенная диаграмма Боде (Импеданс, мОм)", fontsize=14)

# 2. Фаза
ax2.plot(frequencies, phase, color="red", marker="s", markersize=4, linestyle="-")
ax2.set_ylabel("Фаза (градусы)", fontsize=11, color="red")
ax2.tick_params(axis='y', labelcolor="red")
ax2.grid(True, which="both", linestyle=":", alpha=0.6)

# 3. Действительная часть (Real)
ax3.plot(frequencies, real_parts, color="darkgreen", marker="^", markersize=4, linestyle="-")
ax3.set_ylabel("Действительная\nчасть Re(Z), мОм", fontsize=11, color="darkgreen")
ax3.tick_params(axis='y', labelcolor="darkgreen")
ax3.grid(True, which="both", linestyle=":", alpha=0.6)

# 4. Мнимая часть (Imag)
ax4.plot(frequencies, imag_parts, color="purple", marker="v", markersize=4, linestyle="-")
ax4.set_xlabel("Частота (Гц)", fontsize=12)
ax4.set_ylabel("Мнимая\nчасть Im(Z), мОм", fontsize=11, color="purple")
ax4.tick_params(axis='y', labelcolor="purple")
ax4.grid(True, which="both", linestyle=":", alpha=0.6)

# Включаем логарифмический масштаб для оси частот на самом нижнем графике
ax4.set_xscale("log")

# Автоматическое распределение элементов во избежание наложения текстов
plt.tight_layout()

# Показываем оба окна
plt.show()
