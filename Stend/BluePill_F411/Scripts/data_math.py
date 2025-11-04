import json
import numpy as np
import matplotlib.pyplot as plt

FILE = 'YAT-Log-20kHz.log.tables'
SIGNAL_FREQ = 20000 # Hz

KEY_TIME_STAMP = 'TIME_STAMP'
# 1000
Fs = 87099.71 # Частота дискритизация

def ConvertStrListToInt(data_str_list):
    data_int_list = [int(x) for x in data_str_list]
    return data_int_list

def CalcAver(data) -> float:
    aver = sum(data)/len(data)
    return aver

def FilterAver(data: list) -> list:
    filtred_data = []
    accum = data[0]
    div = 50
    for d in data:
        accum += d
        filtr_d = accum/div
        accum -= filtr_d
        filtred_data.append(filtr_d)
    return filtred_data

def CalcSamplesPerPeriod(data):
    aver = CalcAver(data)
    wave_hi_lo = data[0] > aver
    points_per_period = 0
    points_per_period_list = []
    first_period_start = False
    half_periods = 0 # счётчик полупериодов
    for d in data:
        points_per_period += 1
        if wave_hi_lo != (d > aver):
            half_periods += 1
            wave_hi_lo = d > aver
            if first_period_start:
                points_per_period_list.append(points_per_period)
            points_per_period = 0
            first_period_start = True
    points_per_period = 2 * CalcAver(points_per_period_list)
    return half_periods, points_per_period

def SaveDataTable(data, time_stamp):
    data_to_save = {}
    data_to_save[KEY_TIME_STAMP] = time_stamp
    data_to_save['data'] = data
    f = open('data.table', 'wt')
    json.dump([data_to_save], fp=f, indent=2)
    f.close()

def main():
    table_file = open(FILE)
    table = json.load(table_file)[0]
    table_file.close()

    print(f'{table.keys()}')

    ch0 = ConvertStrListToInt(table['Ch0'])
    ch1 = ConvertStrListToInt(table['Ch1'])

    # filtred_ch0 = FilterAver(ch0)
    # SaveDataTable(filtred_ch0, table[KEY_TIME_STAMP])

    half_periods, points_per_period = CalcSamplesPerPeriod(ch0)
    T = 1/SIGNAL_FREQ
    Ts = 1/Fs
    # Fs = 1/Ts

    Ych0 = np.fft.fft(ch0)/len(ch0)
    Ych1 = np.fft.fft(ch1)/len(ch1)
    N = len(ch0) # общее кол-во сэмплов (sample_rate)
    n = np.arange(N) # массив отсчётов
    sample_duration = Ts * N
    freq_ax = n/sample_duration # массив частот для оси частот
    t = np.arange(0, sample_duration, Ts) # массив отсчётов времени каждого сэмпла
    Ych0abs = np.abs(Ych0)
    Ych0real = np.real(Ych0)
    Ych0imag = np.imag(Ych0)
    Ych0angle = np.angle(Ych0)
    Ych1abs = np.abs(Ych1)
    Ych1real = np.real(Ych1)
    Ych1imag = np.imag(Ych1)
    Ych1angle = np.angle(Ych1)

    offset_ch0 = Ych0real[0]

    print(f'Freq: {SIGNAL_FREQ} - Частота сигнала [Гц],\nT: {T} - Период [сек]')
    print(f'Tc: {Ts} - Период дискретизации [сек],\nFc: {Fs} - Частота дискритизация [Гц]')
    print(f'Кол-во сэмплов: {N}')

    xlimit = SIGNAL_FREQ # 1100

    f = plt.figure()
    f.canvas.manager.set_window_title('ABSOLUTE')
    plt.stem(freq_ax, Ych0abs, linefmt='r-')
    plt.stem(freq_ax, Ych1abs, linefmt='g-')
    plt.grid(visible=True)
    plt.xlim(0, xlimit*1.1)
    # plt.xticks(np.arange(0,xlimit,1))

    plt.show()
    pass

if __name__ == '__main__':
    main()