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

# Создание графика
plt.figure(figsize=(10, 8))

# Строим точки, цвет которых зависит от частоты (шкала jet от синего к красному)
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

# Добавляем световую шкалу для частот
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

# Одинаковый масштаб по осям X и Y, чтобы полуокружности не искажались в овалы
plt.axis("equal")

plt.show()
