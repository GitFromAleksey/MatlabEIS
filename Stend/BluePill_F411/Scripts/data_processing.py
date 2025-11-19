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

def FindSignalValueInFft(signal_freq, fft_spectrum, freq_ax):
    ''' Ищет в спектре амплитуду для определённой частоты '''
    index = 0
    # поиск индекса частоты на оси частот
    for f in freq_ax:
        # поиск заданной частоты на оси частот
        if f > signal_freq and f < signal_freq*1.1:
            start_index = int(index*0.9)
            stop_index = int(index*1.1)
            srez = fft_spectrum[start_index : stop_index]
            for s in srez:
                if int(abs(s)) == int(max(abs(srez))):
                    print(f'FindFreq: {f} Hz, Amplitude: {abs(s)}, maxcplx: {s}')
                    print(f'start_freq: {freq_ax[start_index]}, stop_freq: {freq_ax[stop_index]}')
                    return s
        index += 1   

def FftCalc(samples, signal_freq, Fs):
    ''' Рассчёт ДПФ сигнала
    Входные данные: 
        samples - данные с АЦП, signal_freq - частота подаваемого сигнала, 
        Fs - частотат сэмплирования (дискретизации)
    Возвращаемые параметры:
        Y - ДПФ, freq_ax - частоты для оси Х, signal_offset - постаянная составляющая
    '''
    T = 1/signal_freq # период оцифрованного сигнала
    Ts = 1/Fs # период сэмплирования
    Y = np.fft.fft(samples)/len(samples)
    N = len(samples) # общее кол-во сэмплов (sample_rate)
    n = np.arange(N) # массив отсчётов
    sample_duration = Ts * N
    freq_ax = n/sample_duration # массив частот для оси частот
    Ych0real = np.real(Y)
    # Ych0abs = np.abs(Y)
    # Ych0imag = np.imag(Y)
    # Ych0angle = np.angle(Y)
    # t = np.arange(0, sample_duration, Ts) # массив отсчётов времени каждого сэмпла
    signal_offset = Ych0real[0] # постоянная составляющая
    return Y, freq_ax, signal_offset

class NumpyEncoder(json.JSONEncoder):
    ''' Адаптор комплексных чисел numpy для json сереализации '''
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, np.int64) or isinstance(obj, np.int32):
            return int(obj)
        if isinstance(obj, np.float64) or isinstance(obj, np.float32):
            return float(obj)
        if np.iscomplexobj(obj):
            return [np.real(obj), np.imag(obj)]
        return super().default(obj)

def main():

    f = open(FILE, 'rt', encoding='utf-8')
    d = json.load(f)
    print(f'Exsperiment name: {d[KEY_EXPERIMENT_NAME]}')
    print(f'Exsperiment date: {d[KEY_EXPERIMENT_DATE]}')
    data_collection = d[KEY_PARSED_DATA]
    f.close()

    fft_results = []
    for data in data_collection:

        signal_freq = int(data[KEY_FREQ])
        print(f'Signal freq: {signal_freq}, Hz')
        samples = data[KEY_DATA][0]
        del samples[KEY_TIME_STAMP] # таймштамп нам больше не нужен

        # перевод данных в относительные единицы
        ch0_samples = []
        for smpl in samples[KEY_CHANNEL0]:
            ch0_samples.append(smpl/ADC_SCALE)
        ch1_samples = []
        for smpl in samples[KEY_CHANNEL1]:
            ch1_samples.append(smpl/ADC_SCALE)

        # вычисление ДПФ
        Ych0, freq_ax_ch0, signal_offset_ch0 = FftCalc(samples[KEY_CHANNEL0], signal_freq, Fs)
        Ych1, freq_ax_ch1, signal_offset_ch1 = FftCalc(samples[KEY_CHANNEL1], signal_freq, Fs)
        # Ych0, freq_ax_ch0, signal_offset_ch0 = FftCalc(ch0_samples, signal_freq, Fs)
        # Ych1, freq_ax_ch1, signal_offset_ch1 = FftCalc(ch1_samples, signal_freq, Fs)


        # комплексное значение сигнала в спектре для его частоты
        ch0_compl_val = FindSignalValueInFft(signal_freq, Ych0, freq_ax_ch0)
        ch1_compl_val = FindSignalValueInFft(signal_freq, Ych1, freq_ax_ch1)
        # амплитудное значение сигнала в спектре для его частоты
        ch0_ampl_val = abs(ch0_compl_val)
        ch1_ampl_val = abs(ch1_compl_val)

        # отображение графика спектра для контроля
        # fig, ax = plt.subplots()
        # ax.set_title(f'Frequency: {signal_freq} Hz')
        # ax.set_ylabel('amplitude')
        # ax.set_xlabel('frequency')
        # ax.grid(True)
        # ax.stem(freq_ax_ch0, abs(Ych0), label='abs_ch0', linefmt='r-')
        # ax.stem(freq_ax_ch1, abs(Ych1), label='abs_ch1', linefmt='g-')
        # plt.legend()
        # plt.show()

        # добавление вычисленных данных в структуру для дальнейшего сохранение в файл
        fft_result = {}
        fft_result[KEY_FREQ] = signal_freq
        fft_result[KEY_DATA] = samples

        ch0_results = {}
        ch0_results[KEY_SIGNAL_ABS_VAL]     = ch0_ampl_val
        ch0_results[KEY_SIGNAL_COMPLEX_VAL] = ch0_compl_val
        ch0_results[KEY_SIGNAL_OFFSET] = signal_offset_ch0
        ch0_results[KEY_SIGNAL_FFT]    = Ych0
        ch0_results[KEY_SIGNAL_X_AX]   = freq_ax_ch0

        ch1_results = {}
        ch1_results[KEY_SIGNAL_ABS_VAL]     = ch1_ampl_val
        ch1_results[KEY_SIGNAL_COMPLEX_VAL] = ch1_compl_val
        ch1_results[KEY_SIGNAL_OFFSET] = signal_offset_ch1
        ch1_results[KEY_SIGNAL_FFT]    = Ych1
        ch1_results[KEY_SIGNAL_X_AX]   = freq_ax_ch1

        fft_result[KEY_CHANNEL0] = ch0_results
        fft_result[KEY_CHANNEL1] = ch1_results
        fft_results.append(fft_result)
 
    print(f'Сохранение результатов в файл...')
    f = open(FILE+'.fft', 'wt')
    json.dump(fft_results, fp=f, indent=0, cls=NumpyEncoder)
    f.close()
    pass

if __name__ == '__main__':
    main()