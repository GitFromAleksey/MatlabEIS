import os
import sys # import argparse # 
import json
import cmath
from pathlib import Path
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from common_constants import *

FILE = '5_battery_10.28.31_19.02.2026.result.fft'

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

    def GetFrequency(self):
        return self.freq

    def GetRawSamlpes(self):
        ''' возвращает сырые отсчёты исходного сигнала '''
        return self.raw_samples_list

    def GetAbsFftForPlot(self):
        ''' возвращает список модулей fft и список частот '''
        abs_fft = [abs(_fft) for _fft in self.fft_list]
        end = int(len(abs_fft)/2)
        abs_fft = abs_fft[0: end]
        end = int(len(self.freq_axis_list)/2)
        freq_axis = self.freq_axis_list[0: end]
        return abs_fft, freq_axis

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

    def GetSignalsSamplesByFrequency(self, freq:int=0):
        ''' Возвращает сырые данные напряжения и тока для определённой частоты '''
        v_samples = None
        c_samples = None
        for v,c in zip(self.voltage,self.current):
            if v.GetFrequency() == freq:
                v_samples = v.GetRawSamlpes()
            if c.GetFrequency() == freq:
                c_samples = c.GetRawSamlpes()
        return v_samples, c_samples

    def GetFftSpectrByFrequency(self, freq:int=0):
        ''' Возвращает спектры напряжения и тока в абсолютных значениях '''
        v_fft = None
        c_fft = None
        freq_ax = None # значения частоты для оси X
        for v,c in zip(self.voltage,self.current):
            if v.GetFrequency() == freq:
                v_fft = v.GetAbsFftForPlot()
            if c.GetFrequency() == freq:
                c_fft = c.GetAbsFftForPlot()
        return v_fft, c_fft

    def GetFrequencies(self):
        ''' Возвращает список частот всех сигналов '''
        freqs = []
        for v in self.voltage:
            freqs.append(v.GetFrequency())
        return freqs

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
        # self.PlotEis()

    def GetFrequensys(self):
        return self.eis.GetFrequencies()

    # def PlotFft(self, freq:int=0):
    #     ''' выводит график FFT для частоты '''

    def PlotFrequency(self, freq:int=0):
        ''' выводит графики напряжения и тока для заданной частоты '''
        v_samples, c_samples = self.eis.GetSignalsSamplesByFrequency(freq)
        v_fft, c_fft = self.eis.GetFftSpectrByFrequency(freq)

        if v_samples == None or c_samples == None:
            print(f'Нест такой частота: {freq}')
            return

        mpl.rcParams['savefig.directory'] = '.'
        fig, (ax_smpl,ax_fft) = plt.subplots(2, 1)
        ax_smpl.set_ylabel('Samples')
        ax_smpl.set_xlabel('ticks')
        ax_smpl.plot(v_samples, label='Voltage')
        ax_smpl.plot(c_samples, label='Current')
        ax_smpl.legend()
        ax_smpl.grid(True)

        ax_fft.set_ylabel('abs')
        ax_fft.set_xlabel('freq')
        ax_fft.stem(v_fft[1], v_fft[0], label='Voltage', linefmt='r-')
        ax_fft.stem(c_fft[1], c_fft[0], label='Current', linefmt='g-')
        ax_fft.legend()
        ax_fft.grid(True)

        # plt.legend()
        plt.show()

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

        mpl.rcParams['savefig.directory'] = '.'
        fig, ax = plt.subplots()

        ax.set_title('Nyquist plot')
        ax.set_ylabel('image')
        ax.set_xlabel('real')
        ax.grid(True)
        ax.set_xlim(-1, 1.5)
        ax.set_ylim(-1, 1.5)
        for e, f in zip(eis, freqs):
            ax.text(e.real, -e.imag, str(f), fontsize=6)
        ax.scatter(real, imag)
        ax.plot(real, imag, '-r', label='EIS')
        plt.legend()
        plt.show()

commands = [ 'f - file_name', 
            'peis - plot EIS', 
            'prs - print all frequencies', 
            'pf - print frequency samlpes',
            'q - exit']
# 5_battery_10.28.31_19.02.2026.result.fft
def main():

    parser = None
    if len(sys.argv) > 1:
        parser = FftResultFile(sys.argv[1])

    while True:
        cmd = input(commands)

        if cmd == 'prs':
            print(parser.GetFrequensys())
        elif cmd == 'f':
            freq = input('enter file name:')
            parser = FftResultFile(freq)
        elif cmd == 'peis':
            parser.PlotEis()
        elif cmd == 'pf':
            print(parser.GetFrequensys())
            freq = int(input('enter frequency:'))
            parser.PlotFrequency(freq)
        elif cmd == 'q':
            return

if __name__ == '__main__':
    main()
