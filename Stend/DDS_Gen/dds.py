

CMD_TERMINATOR = '\n'
# Output
CMD_SET_WMW = 'WMW' # Set the CH1 waveform WMW xxxxxxxx 0x0a 0x0a 
CMD_GET_RMW = 'RMW' # Read the CH1 waveform RMW 0x0a xxxxxxxx 0x0a
CMD_SET_WMF = 'WMF' # Set the CH1 Frequency WMF xxxxxxxx 0x0a 0x0a 
CMD_GET_RMF = 'RMF' # Read CH1 Frequency RMF 0x0a xxxxxxxx 0x0a
CMD_SET_WMA = 'WMA' # Set the CH1 Amplitude WMA xxxxxxxx 0x0a 0x0a 
CMD_GET_RMA = 'RMA' # Read CH1 Amplitude RMA 0x0a xxxxxxxx 0x0a
CMD_SET_WMO = 'WMO' # Set the CH1 Off = '' # Set WMO xxxxxxxx 0x0a 0x0a 
CMD_GET_RMO = 'RMO' # Read CH1 Off = '' # Set RMO 0x0a xxxxxxxx 0x0a
CMD_SET_WMD = 'WMD' # Set the CH1 Duty WMD xxxxxxxx 0x0a 0x0a 
CMD_GET_RMD = 'RMD' # Read CH1 Duty RMD 0x0a xxxxxxxx 0x0a
CMD_SET_WMP = 'WMP' # Set the CH1 Phase WMP xxxxxxxx 0x0a 0x0a 
CMD_GET_RMP = 'RMP' # Read CH1 Phase RMP 0x0a xxxxxxxx 0x0a
CMD_SET_WMN = 'WMN' # Set the CH1 On/Off of output WMN xxxxxxxx 0x0a 0x0a 
CMD_GET_RMN = 'RMN' # Read CH1 on/off output RMN 0x0a xxxxxxxx 0x0a
CMD_SET_WFW = 'WFW' # Set the CH2 waveform WFW xxxxxxxx 0x0a 0x0a 
CMD_GET_RFW = 'RFW' # Read CH2 waveform RFW 0x0a xxxxxxxx 0x0a
CMD_SET_WFF = 'WFF' # Set the CH2 Frequency WFF xxxxxxxx 0x0a 0x0a 
CMD_GET_RFF = 'RFF' # Read CH2 Frequency RFF 0x0a xxxxxxxx 0x0a
CMD_SET_WFA = 'WFA' # Set the CH2 Amplitude WFA xxxxxxxx 0x0a 0x0a 
CMD_GET_RFA = 'RFA' # Read CH2 Amplitude RFA 0x0a xxxxxxxx 0x0a
CMD_SET_WFO = 'WFO' # Set the CH2 off = '' # Set WFO xxxxxxxx 0x0a 0x0a 
CMD_GET_RFO = 'RFO' # Read CH2 Off = '' # Set RFO 0x0a xxxxxxxx 0x0a
CMD_SET_WFD = 'WFD' # Set the CH2 Duty WFD xxxxxxxx 0x0a 0x0a 
CMD_GET_RFD = 'RFD' # Read CH2 Duty RFD 0x0a xxxxxxxx 0x0a
CMD_SET_WFP = 'WFP' # Set the CH2 Phase WFP xxxxxxxx 0x0a 0x0a 
CMD_GET_RFP = 'RFP' # Read CH2 Phase RFP 0x0a xxxxxxxx 0x0a
CMD_SET_WFN = 'WFN' # Set the CH2 on/off output WFN xxxxxxxx 0x0a 0x0a 
CMD_GET_RFN = 'RFN' # Read CH2 off/on output RFN 0x0a xxxxxxxx 0x0a
CMD_SET_TFW = 'TFW' # Set the CH3 waveform TFW xxxxxxxx 0x0a 0x0a 
CMD_GET_RTW = 'RTW' # Read CH3 waveform RTW 0x0a xxxxxxxx 0x0a
CMD_SET_TFF = 'TFF' # Set the CH3 Frequency TFF xxxxxxxx 0x0a 0x0a 
CMD_GET_RTF = 'RTF' # Read CH3 Frequency RTF 0x0a xxxxxxxx 0x0a
CMD_SET_TFA = 'TFA' # Set the CH3 Amplitude TFA xxxxxxxx 0x0a 0x0a 
CMD_GET_RTA = 'RTA' # Read CH3 Amplitude RTA 0x0a xxxxxxxx 0x0a
CMD_SET_TFO = 'TFO' # Set the CH3 Off = '' # Set TFO xxxxxxxx 0x0a 0x0a 
CMD_GET_RTO = 'RTO' # Read CH3 Off = '' # Set RTO 0x0a xxxxxxxx 0x0a
CMD_SET_TFD = 'TFD' # Set the CH3 Duty TFD xxxxxxxx 0x0a 0x0a 
CMD_GET_RTD = 'RTD' # Read CH3 Duty RTD 0x0a xxxxxxxx 0x0a
CMD_SET_TFP = 'TFP' # Set the CH3 Phase TFP xxxxxxxx 0x0a 0x0a 
CMD_GET_RTP = 'RTP' # Read CH3 Phase RTP 0x0a xxxxxxxx 0x0a
CMD_SET_TFN = 'TFN' # Set the CH3 on/off output TFN xxxxxxxx 0x0a 0x0a 
CMD_GET_RTN = 'RTN' # Read CH3 Output on/off RTN 0x0a xxxxxxxx 0x0a


# Modulation
CMD_SET_WPF = 'WPF' # Set the CH1 Modulation function WPF xxxxxxxx 0x0a 0x0a 
CMD_GET_RPF = 'RPF' # Read CH1 trigger function RPF 0x0a xxxxxxxx 0x0a
CMD_SET_WPM = 'WPM' # Set the CH1 Modulation function WPM xxxxxxxx 0x0a 0x0a 
CMD_GET_RPM = 'RPM' # Read CH1 trigger function RPM 0x0a xxxxxxxx 0x0a
CMD_SET_WFK = 'WFK' # Set CH1 FSK second frequency WFK xxxxxxxx 0x0a 0x0a
CMD_GET_RFK = 'WFK' # Read FSK secondary frequency RFK 0x0a xxxxxxxx 0x0a
CMD_SET_WPN = 'WPN' # Set the number of CH1 trigger pulses WPN xxxxxxxx 0x0a 0x0a
CMD_GET_RPN = 'RPN' # Read CH1 pulse amount triggered RPN 0x0a xxxxxxxx 0x0a 
CMD_SET_WPO = 'WPO' # Generate manual trigger source WPO xxxxxxxx 0x0a 0x0a
CMD_SET_WPR = 'WPR' # Set CH1AM modulation rate WPR xxxxxxxx 0x0a 0x0a
CMD_GET_RPR = 'RPR' # Read the Modulation Rate of CH1 AM RPR 0x0a xxxxxxxx 0x0a
CMD_SET_WFM = 'WFM' # Set the CH1FM Modulation frequency off = '' # Set WFM xxxxxxxx 0x0a 0x0a 
CMD_GET_RFM = 'RFM' # Read FM Modulation Frequency Off = '' # Set of CH1 RFM 0x0a xxxxxxxx 0x0a
CMD_SET_WPP = 'WPP' # Set the CH1PM Modulation phase off = '' # Set WPP xxxxxxxx 0x0a 0x0a
CMD_GET_RPP = 'RPP' # Read PM Modulation Phase Off = '' # Set of CH1 PM RPP 0x0a xxxxxxxx 0x0a

# Measurement
CMD_SET_WCC = 'WCC' # Set measurement input coupling mode WCC xxxxxxxx 0x0a 0x0a
CMD_SET_WCZ = 'WCZ' # Set count clear WCZ xxxxxxxx 0x0a 0x0a
CMD_SET_WCP = 'WCP' # Set measurement pause WCP xxxxxxxx 0x0a 0x0a
CMD_SET_WCG = 'WCG' # Set measurement gate time WCG xxxxxxxx 0x0a 0x0a
CMD_GET_RCG = 'RCG' # Read measuring gate time RCG 0x0a xxxxxxxx 0x0a
CMD_GET_RCF = 'RCF' # Read frequency of external measurement RCF 0x0a xxxxxxxx 0x0a
CMD_GET_RCC = 'RCC' # Read external RCC 0x0a xxxxxxxx 0x0a

class DDS_Generator:

    def __init__(self, cb_data_tx=None):
        self.data_tx = cb_data_tx

    def SendCommand(self, data: str=''):
        if self.data_tx == None:
            print(f'Не задана функция отправки данных.')
            return
        data += CMD_TERMINATOR
        self.data_tx(data)

    def ChannelOn(self, chan_num: int=-1 ):
        if chan_num == -1:
            print(f'ChannelOn Неправильный номер канала: {chan_num}')
            return

        if chan_num == 1:
            data = CMD_SET_WMN
        elif chan_num == 2:
            data = CMD_SET_WFN
        elif chan_num == 3:
            data = CMD_SET_TFN
        
        data += '1'

        self.SendCommand(data)


    def ChannelOff(self, chan_num: int=-1 ):
        if chan_num == -1:
            print(f'ChannelOff Неправильный номер канала: {chan_num}')
            return
        
        if chan_num == 1:
            data = CMD_SET_WMN
        elif chan_num == 2:
            data = CMD_SET_WFN
        elif chan_num == 3:
            data = CMD_SET_TFN
        
        data += '0'

        self.SendCommand(data)

    def SetFrequensy(self, chan:int=0, freq:float=0):
        if chan == 0 or chan > 3:
            print(f'SetFrequensy Неправильный номер канала: {chan_num}')
            return
        elif chan == 1:
            data = CMD_SET_WMF
        elif chan == 2:
            data = CMD_SET_WFF
        elif chan == 3:
            data = CMD_SET_TFF

        # freq = freq*1000000
        freq_uhz = int(freq)
        data += str(freq_uhz)

        self.SendCommand(data)

    def SetAmplitude(self, chan:int=0, ampl:float=0):
        if chan == 0 or chan > 3:
            print(f'SetFrequensy Неправильный номер канала: {chan_num}')
            return
        elif chan == 1:
            data = CMD_SET_WMA
        elif chan == 2:
            data = CMD_SET_WFA
        elif chan == 3:
            data = CMD_SET_TFA

        data += str(ampl)

        self.SendCommand(data)