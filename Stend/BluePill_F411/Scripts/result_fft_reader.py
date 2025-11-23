import json
import cmath
import numpy as np
import matplotlib.pyplot as plt
from common_constants import *

FILE = 'YATLog2_20.11.2025T19.00.00.result.fft'

def ListToComplexNumber(complex_number_list):
        real = complex_number_list[0]
        imag = complex_number_list[1]
        return complex(real=real, imag=imag)

def main():

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
        print(f'Freq: {data[KEY_FREQ]}, Hz')
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
        phi1_delta = ch1phi-ch0phi # сдвижка угла второго канала тока относительно напряжения
        channel_1[KEY_SIGNAL_COMPLEX_VAL] = cmath.rect(ch1_oe, phi1_delta) # сдвижка фазы 2-го канала относительно 1-го 

        ch0_data_list.append(channel_0[KEY_SIGNAL_COMPLEX_VAL])
        ch1_data_list.append(channel_1[KEY_SIGNAL_COMPLEX_VAL])
        channels_data[data[KEY_FREQ]] = [ channel_0[KEY_SIGNAL_COMPLEX_VAL],channel_1[KEY_SIGNAL_COMPLEX_VAL] ]

        print(f'CH0 ABS_VAL: {ch0_data[KEY_SIGNAL_ABS_VAL]}')
        print(f'CH0 COMPLEX_VAL: {ch0_data[KEY_SIGNAL_COMPLEX_VAL]}')
        print(f'CH1 ABS_VAL: {ch1_data[KEY_SIGNAL_ABS_VAL]}')
        print(f'CH1 COMPLEX_VAL: {ch1_data[KEY_SIGNAL_COMPLEX_VAL]}')


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