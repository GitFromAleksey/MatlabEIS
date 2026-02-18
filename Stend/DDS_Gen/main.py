import serial
import time
from dds import DDS_Generator

SERIAL_PORT = 'COM10' 
BAUD_RATE   = 115200

CHANNEL_NUM = 1

AMPLITUDE  = 24.00 # Volt

FREQ_START = 'FREQ_START'
FREQ_STOP  = 'FREQ_STOP'
FREQ_STEP  = 'FREQ_STEP'
FREQ_RANGE = {
    FREQ_START : 100,
    FREQ_STOP  : 20000,
    FREQ_STEP  : 100
}

SER = None

def OpenPort():
    global SER
    try:
        SER = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1) 
        time.sleep(2) # Wait for the connection to establish

        print(f"Port {SERIAL_PORT} opened successfully.")

        # data_to_send = b"WMN1\n\n"
        # ser.write(data_to_send)
        # dec = data_to_send.decode().strip()
        # print(f"Sent: {data_to_send.decode()}")
        # ser.close() # Close the port
        # print("Port closed.")

    except serial.SerialException as e:
        print(f"Error opening serial port: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

def CB_DataSend(tx_data: str=''):
    global SER
    if len(tx_data) == 0:
        return
    data_to_send = tx_data.encode()
    SER.write(data_to_send)
    print(f"Sent: {data_to_send.decode()}")
    time.sleep(0.2)

def main():

    print('Hi!!!')
    OpenPort()
    gen = DDS_Generator(CB_DataSend)

    gen.ChannelOn(CHANNEL_NUM)

    gen.SetAmplitude(chan=CHANNEL_NUM, ampl=AMPLITUDE)

    for freq in range(FREQ_RANGE[FREQ_START], FREQ_RANGE[FREQ_STOP], FREQ_RANGE[FREQ_STEP]):
        gen.SetFrequensy(chan=CHANNEL_NUM, freq=freq)

    gen.SetAmplitude(chan=CHANNEL_NUM, ampl=12.3456)

    gen.ChannelOff(CHANNEL_NUM)

    SER.close() # Close the port
    print("Port closed.")


if __name__ == '__main__':
    main()