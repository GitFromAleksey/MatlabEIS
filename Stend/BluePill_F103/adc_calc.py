f_adcclk = 6000000 # частота тактирования ADC
T_selekt = 1.5 # кол-во тактов выборки
T_conv   = 12.5 # кол-во тактов преобразования


T_sample = (T_selekt + T_conv)/f_adcclk
f_sample = 1/T_sample

f_signal = 100 # минимальная частота сигнала
min_signal_sampls = f_sample/f_signal


print(f'Период сэмплирования: {T_sample} сек')
print(f'Частота сэмплирования: {f_sample} Гц')
print(f'Кол-во сэмплов для сигнала {f_signal} Гц: {min_signal_sampls}')
