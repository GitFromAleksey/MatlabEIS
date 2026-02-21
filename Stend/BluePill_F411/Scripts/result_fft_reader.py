import os
# import sys # import argparse # 
import json
import cmath
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from common_constants import *

FILE = 'YATLog0_19.11.2025T17.48.00.result.fft'

def ListToComplexNumber(complex_number_list):
    real = complex_number_list[0]
    imag = complex_number_list[1]
    return complex(real=real, imag=imag)

class Signal:
    ''' класс сигнал со всеми своими характеристиками '''
    def __init__(self, freq, raw_data, fft_data):
        self.freq              = freq # частота сигнала
        self.offset            = fft_data[KEY_SIGNAL_OFFSET] # смещение сигнала относительно нуля
        self.raw_samples_list  = raw_data # отсчёты исходного сигнала
        self.fft_              = Signal.ListToComplexNumber(fft_data[KEY_SIGNAL_COMPLEX_VAL]) # амплитуда сигнала в комплексном виде
        self.abs_amplitude     = fft_data[KEY_SIGNAL_ABS_VAL] # амплитуда сигнала абсолютная
        self.fft_list          = Signal.NumListToComplexNumbersList(fft_data[KEY_SIGNAL_FFT]) # fft сигнала
        self.freq_axis_list    = fft_data[KEY_SIGNAL_X_AX] # ось частот сигнала

    def GetRawSamlpes(self):
        ''' возвращает сырые отсчёты исходного сигнала '''
        return self.raw_samples_list

    def GetAbsFftForPlot(self):
        ''' возвращает список модулей fft и список частот '''
        abs_fft = [abs(_fft) for _fft in self.fft_list]
        return abs_fft, self.freq_axis_list

    def GetPhase(self):
        ''' фаза амплитуды сигнала '''
        return cmath.phase(self.fft_)

    def ListToComplexNumber(complex_number_pare):
        ''' переводит пару чисел в комплексное число '''
        real = complex_number_pare[0]
        imag = complex_number_pare[1]
        return complex(real=real, imag=imag)

    def NumListToComplexNumbersList(complex_numbers_list):
        ''' переводит список пар чисел в список комплексных чисел '''
        complex_numbers = []
        for num in complex_numbers_list:
            complex_numbers.append(Signal.ListToComplexNumber(num))
        return complex_numbers

    def __lt__(self, other):
        ''' для сортировки списка классов по частоте '''
        return self.freq < other.freq

class EIS:
    ''' класс электроскопии '''
    def __init__(self):
        self.voltage = []
        self.current = []

    def AppendSignals(self, voltage:Signal=None, current:Signal=None):
        self.voltage.append(voltage)
        self.voltage.sort()
        self.current.append(current)
        self.current.sort()

    def EisCalc(self):
        ''' рассчёт EIS '''
        freqs = []

        volt_phases = []
        volt_amplitudes = []
        # for v in self.voltage:
        #     volt_phases.append(v.GetPhase())
        #     volt_amplitudes.append(v.abs_amplitude)
        current_phases = []
        current_amplitudes = []
        # for c in self.current:
        #     current_phases.append(c.GetPhase())
        #     current_amplitudes.append(c.abs_amplitude)
        for v, c in zip(self.voltage, self.current):
            freqs.append(v.freq)
            volt_phases.append(v.GetPhase())
            volt_amplitudes.append(v.abs_amplitude)
            current_phases.append(c.GetPhase())
            current_amplitudes.append(c.abs_amplitude)

        # рассчёт тока относительно напряжению
        current_oe = [v/c for v, c in zip(volt_amplitudes, current_amplitudes)]
        # разница фаз напряжения и тока
        phases_diff = [v_ph-c_ph for v_ph, c_ph in zip(volt_phases, current_phases)]
        # комплексное значение с новым углом
        current_shift = [cmath.rect(c, ph) for c, ph in zip(current_oe, phases_diff)]
        return current_shift, freqs

class FftResultFile:

    def __init__(self, file_path: str = ''):
        '''  '''
        self.eis = EIS()

        if not self.FileNameCheck(file_path):
            print(f'Какой-то неправильный файл: {file_path}')
            return
        
        self.ReadFromFile(self.file_path)

    def FileNameCheck(self, file_path:str = ''):
        ''' проверяет существование файла и получает его параметры '''
        if not Path(file_path).is_file():
            print(f'Файл {file_path} не существует.')
            return False
        self.file_path = file_path
        p = Path(file_path)
        self.abs_path = str(p.parent) # p.parent._str
        self.file_name_with_ext = Path(file_path).name
        self.file_name_without_ext, extension = os.path.splitext(self.file_name_with_ext)
        return True

    def ReadFromFile(self, file_path: str = ''):
        '''  '''
        print(f'Read data from file: {file_path}')
        f = open(FILE, 'rt', encoding='utf-8')
        data_from_file = json.load(f)
        f.close()

        for data in data_from_file:
            freq = data[KEY_FREQ]

            volt_raw_data    = data[KEY_DATA][KEY_CHANNEL0]
            current_raw_data = data[KEY_DATA][KEY_CHANNEL1]

            volt_fft_data    = data[KEY_CHANNEL0]
            current_fft_data = data[KEY_CHANNEL1]

            voltage = Signal(freq, volt_raw_data, volt_fft_data)
            current = Signal(freq, current_raw_data, current_fft_data)

            self.eis.AppendSignals(voltage=voltage, current=current)

        # self.eis.EisCalc()
        self.PlotEis()

    def PlotEis(self):
        '''  '''
        eis, freqs = self.eis.EisCalc()
        real = []
        imag = []
        labels = []
        for e in eis:
            labels.append(str(e))
            real.append(e.real)
            imag.append(-e.imag)

        fig, ax = plt.subplots()

        ax.set_title('chanel_0')
        ax.set_ylabel('amplitude')
        ax.set_xlabel('frequency')
        ax.grid(True)
        for e, f in zip(eis, freqs):
            ax.text(e.real, -e.imag, str(f))
        ax.scatter(real, imag, label='EIS')
        ax.plot(real, imag, '-r', label='EIS')
        plt.legend()
        plt.show()

def main():
    fft_res = FftResultFile(FILE)
    return

    print(f'Read data from file: {FILE}')
    f = open(FILE, 'rt', encoding='utf-8')
    data_from_file = json.load(f)
    f.close()

    channels_data = {}
    ch0_data_list = []
    ch1_data_list = []

    for data in data_from_file:
        channel_0 = {}
        channel_1 = {}
        # print(f'Freq: {data[KEY_FREQ]}, Hz')
        ch0_data = data[KEY_CHANNEL0]
        ch1_data = data[KEY_CHANNEL1]

        channel_0[KEY_SIGNAL_ABS_VAL] = ch0_data[KEY_SIGNAL_ABS_VAL]
        ch0cplx = ListToComplexNumber(ch0_data[KEY_SIGNAL_COMPLEX_VAL])
        ch0phi = np.angle(ch0cplx) # угол 1-го канала напряжения
        ch0_oe = abs(ch0cplx)/abs(ch0cplx) # амплитуда 1-го канала в О.Е. единицах от напряжения
        channel_0[KEY_SIGNAL_COMPLEX_VAL] = cmath.rect(abs(ch0cplx)/abs(ch0cplx), 0) # сдвижка фазы 1-го канала в 0
        channel_1[KEY_SIGNAL_ABS_VAL] = ch1_data[KEY_SIGNAL_ABS_VAL]
        ch1cplx = ListToComplexNumber(ch1_data[KEY_SIGNAL_COMPLEX_VAL])
        ch1phi = np.angle(ch1cplx) # угол 2-го канала тока
        ch1_oe = abs(ch1cplx)/abs(ch0cplx) # амплитуда 2-го канала в О.Е. единицах от напряжения
        phi1_delta = abs(ch1phi-ch0phi) # сдвижка угла второго канала тока относительно напряжения
        channel_1[KEY_SIGNAL_COMPLEX_VAL] = cmath.rect(ch1_oe, phi1_delta) # сдвижка фазы 2-го канала относительно 1-го 

        ch0_data_list.append(channel_0[KEY_SIGNAL_COMPLEX_VAL])
        ch1_data_list.append(channel_1[KEY_SIGNAL_COMPLEX_VAL])
        channels_data[data[KEY_FREQ]] = [ channel_0[KEY_SIGNAL_COMPLEX_VAL],channel_1[KEY_SIGNAL_COMPLEX_VAL] ]

        print(f'{ch0phi};{ch1phi},')
        # print(f'CH0 ABS_VAL: {ch0_data[KEY_SIGNAL_ABS_VAL]}')
        # print(f'CH0 COMPLEX_VAL: {ch0_data[KEY_SIGNAL_COMPLEX_VAL]}')
        # print(f'CH1 ABS_VAL: {ch1_data[KEY_SIGNAL_ABS_VAL]}')
        # print(f'CH1 COMPLEX_VAL: {ch1_data[KEY_SIGNAL_COMPLEX_VAL]}')


    sort_freqs = sorted(channels_data)

    _abs_0 = []
    _image_0 = []
    _real_0 = []
    _angle_0 = []

    _abs_1 = []
    _image_1 = []
    _real_1 = []
    _angle_1 = []

    eis_abs = []
    eis_image = []
    eis_real = []
    eis_angle = []
    for fr in sort_freqs:
        vals = channels_data[fr]
        _abs_0.append(np.abs(vals[0]))
        _image_0.append(np.imag(vals[0]))
        _real_0.append(np.real(vals[0]))
        _angle_0.append(np.angle(vals[0]))

        _abs_1.append(np.abs(vals[1]))
        _image_1.append(np.imag(vals[1]))
        _real_1.append(np.real(vals[1]))
        _angle_1.append(np.angle(vals[1]))

        eis_abs.append(np.abs(vals[0]-vals[1]))
        eis_image.append(-np.imag(vals[0]-vals[1]))
        eis_real.append(np.real(vals[0]-vals[1]))
        eis_angle.append(np.angle(vals[0]-vals[1]))

    fig, ax = plt.subplots()
    ax.set_title('chanel_0')
    ax.set_ylabel('amplitude')
    ax.set_xlabel('frequency')
    ax.grid(True)

    ax.plot(sort_freqs, _abs_0, label='abs')
    ax.plot(sort_freqs, _image_0, label='image')
    ax.plot(sort_freqs, _real_0, label='real')
    ax.plot(sort_freqs, _angle_0, label='angle')
    plt.legend()

    fig, ax = plt.subplots()
    ax.set_title('chanel_1')
    ax.set_ylabel('amplitude')
    ax.set_xlabel('frequency')
    ax.grid(True)

    ax.plot(sort_freqs, _abs_1, label='abs')
    ax.plot(sort_freqs, _image_1, label='image')
    ax.plot(sort_freqs, _real_1, label='real')
    ax.plot(sort_freqs, _angle_1, label='angle')
    plt.legend()

    fig, ax = plt.subplots()
    ax.set_title('EIS')
    ax.set_ylabel('imag')
    ax.set_xlabel('real')
    ax.grid(True)

    # ax.plot(_image_0, _real_0, label='EIS_0')
    ax.plot(_real_1, _image_1, label='EIS_1') # как буд-то это и есть график EIS
    # ax.plot(eis_image, eis_real, label='EIS')
    plt.legend()

    plt.show()

    pass

if __name__ == '__main__':
    main()