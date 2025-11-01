import json
import numpy as np

FILE = 'YAT-Log-1kHz.log.tables'
SIGNAL_FREQ = 1000 # Hz

KEY_TIME_STAMP = 'TIME_STAMP'

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

    filtred_ch0 = FilterAver(ch0)
    SaveDataTable(filtred_ch0, table[KEY_TIME_STAMP])

    half_periods, points_per_period = CalcSamplesPerPeriod(ch0)
    T = 1/SIGNAL_FREQ
    Tc = T/points_per_period
    Fc = 1/Tc
    print(f'Freq: {SIGNAL_FREQ} - Частота сигнала,\nT: {T} - Период')
    print(f'Tc: {Tc} - Период дискретизации,\nFc: {Fc} - Частота дискритизация')

    X = np.fft.fft(ch0)
    N = len(ch0)

    Xabs = np.abs(X)

    pass

if __name__ == '__main__':
    main()