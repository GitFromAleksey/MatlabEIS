import json
import numpy as np
import matplotlib.pyplot as plt
from common_constants import *

FILE = 'Эксперимент_04.10.2025T18.19.01.result'
SIGNAL_FREQ = 20000 # Hz

# 1000
Fs = 87099.71 # Частота дискритизация-

def ConvertStrListToInt(data_str_list):
    data_int_list = [int(x) for x in data_str_list]
    return data_int_list


def SaveDataTable(data, time_stamp):
    data_to_save = {}
    data_to_save[KEY_TIME_STAMP] = time_stamp
    data_to_save['data'] = data
    f = open('data.table', 'wt')
    json.dump([data_to_save], fp=f, indent=2)
    f.close()

def main():

    f = open(FILE, 'rt', encoding='utf-8')
    d = json.load(f)
    print(f'Exsperiment name: {d[KEY_EXPERIMENT_NAME]}')
    print(f'Exsperiment date: {d[KEY_EXPERIMENT_DATE]}')
    data_collection = d[KEY_PARSED_DATA]
    f.close()

    for data in data_collection:
        print(f'Signal freq: {data[KEY_FREQ]}, Hz')
        samples = data[KEY_DATA]



if __name__ == '__main__':
    main()