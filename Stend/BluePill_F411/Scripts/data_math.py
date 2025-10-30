import json
import numpy as np

FILE = 'YAT-Log-20kHz.log.tables'
SIGNAL_FREQ = 20000 # Hz

def ConvertStrListToInt(data_str_list):
    data_int_list = [int(x) for x in data_str_list]
    return data_int_list

def CalcAver(data) -> float:
    aver = sum(data)/len(data)
    return aver

def CalcPointPerPeriod(data):
    aver = CalcAver(data)
    wave_hi_lo = data[0] > aver
    points_per_period = 0
    points_per_period_list = []
    first_period_start = False
    for d in data:
        points_per_period += 1
        if wave_hi_lo != (d > aver):
            wave_hi_lo = d > aver
            if first_period_start:
                points_per_period_list.append(points_per_period)
            points_per_period = 0
            first_period_start = True
    points_per_period = 2 * CalcAver(points_per_period_list)
    return points_per_period

def main():
    table_file = open(FILE)
    table = json.load(table_file)[0]
    table_file.close()

    print(f'{table.keys()}')

    ch0 = ConvertStrListToInt(table['Ch0'])
    ch1 = ConvertStrListToInt(table['Ch1'])

    points_per_period = CalcPointPerPeriod(ch0)
    T = 1/SIGNAL_FREQ
    Tc = T/points_per_period
    Fc = 1/Tc
    print(f'Freq:{SIGNAL_FREQ}, T:{T}, Tc:{Tc}, Fc:{Fc}')

    X = np.fft.fft(ch0)
    N = len(ch0)

    Xabs = np.abs(X)

    pass

if __name__ == '__main__':
    main()