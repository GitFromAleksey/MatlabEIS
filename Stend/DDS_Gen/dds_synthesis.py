import numpy as np
import matplotlib.pyplot as plt

TARGET_FREQ = 1000

# настройки таймера
Fapb1     = 84000000 # частота тактирования таймера
Prescaler = 0 # 16bit
Period    = 63 # Auto reload register ARR 16bit
Fsample   = Fapb1 / (Period + 1) # 1312500 частота дискретизации = частота вызова таймера

UINT32_MAX_VALUE = 0xFFFFFFFF + 1 # 4 294 967 295 + 1 = 4 294 967 296

LUT_SIZE  = 1024 # размер таблицы синуса
SINE_LUT  = []    # таблица синуса

# переменные DDS
PHASE_ACCUMULATOR = 0
PHASE_INCREMENT   = 0

def SinusDataGenerate(sine_lut: list, lut_size: int = 0):
    ''' генерация таблицы периода синуса '''
    for i in range(lut_size):
        new_value = (np.uint16)( (1+(np.sin(2*np.pi*i/lut_size))) * 2047.5 )
        sine_lut.append(new_value)

def CalcDdsFreq(target_freq: int = 0, f_sample: int = 1) -> int:
    ''' функция для установки частоты сигнала '''

    phase_increment = (target_freq * UINT32_MAX_VALUE)/f_sample

    return (int)(phase_increment)

def TimerIRQ() -> int:
    ''' имитация прерывания таймера '''
    global PHASE_ACCUMULATOR
    global PHASE_INCREMENT

    phase_inc = (np.uint32)(PHASE_INCREMENT)
    phase_accum = (np.uint32)(PHASE_ACCUMULATOR)
    phase_accum += phase_inc

    index = phase_accum>>22

    PHASE_ACCUMULATOR = phase_accum
    PHASE_INCREMENT   = phase_inc

    return (int)(index)

def main():
    global PHASE_ACCUMULATOR
    global PHASE_INCREMENT

    print(f'Настройки таймера:')
    print(f'{Fapb1}\tFapb1 # частота тактирования таймера')
    print(f'{Prescaler}\t\tPrescaler # 16bit')
    print(f'{Period}\t\tPeriod # Auto reload register ARR 16bit')
    print(f'{Fsample}\tFsample # 1312500 частота дискретизации = частота вызова таймера')

    SinusDataGenerate(sine_lut=SINE_LUT, lut_size=LUT_SIZE)
    PHASE_INCREMENT = CalcDdsFreq(target_freq=TARGET_FREQ, f_sample=Fsample)

    target_sin_lut = []
    for i in range(LUT_SIZE):
        index = TimerIRQ()
        target_sin_lut.append(SINE_LUT[index])

    fig, ax = plt.subplots()
    # ax.set_title(name)
    ax.plot(SINE_LUT, label='SINE_LUT',linewidth=2.0)
    ax.plot(target_sin_lut, label='target_sin_lut', linewidth=2.0)
    # ax.set_ylabel(name)
    # ax.set_xlabel('time, ms')
    ax.grid(True)

    plt.legend()
    plt.show()
    
    pass

if __name__ == '__main__':
    main()