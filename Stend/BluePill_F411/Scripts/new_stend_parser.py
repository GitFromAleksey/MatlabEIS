import os
import sys # import argparse # 
import re
import json
from pathlib import Path
import datetime
import matplotlib.pyplot as plt
import numpy as np
from common_constants import *

# FILE_NAME = 'C:/Users/Admini/Documents/MATLAB/MatlabEIS/Stend/BluePill_F411/Scripts/NewStand_18.02.2026/calib/1NewStandCalib_18.02.2026T13.29.56.log'
FILE_NAME = '1NewStandCalib_18.02.2026T13.29.56.log'


KEY_VOLT_DATA        = KEY_CHANNEL0
KEY_CURRENT_DATA     = KEY_CHANNEL1

# регулярка для парсинга строк лога
RE_PATTERN = r'{"'+KEY_TIME_STAMP+r'":\d+,"freq":\d+,"'+KEY_VOLT_DATA+r'":\d+,"'+KEY_CURRENT_DATA+r'":\d+}'
# регулярки для парсинга имени файла
RE_EXPERIMENT = r'(\w+)_'
RE_DATE = r'\d{2}.\d{2}.\d{4}T\d{2}.\d{2}.\d{2}'
RE_EXT  = r'.(\w+)'
RE_FILE_NAME = RE_EXPERIMENT+RE_DATE+RE_EXT

PARSED_FILE_EXTENCION = '.result'

class Parser:

    def __init__(self, file_path:str=''):
        if not self.FileNameCheck(file_path):
            return

        self.parsed_data = self.FileParser(self.file_path)
        self.sorted_data_dict = self.DataSortByFreq(self.parsed_data)
        self.table_data = self.CreateTablesForEachFreq(self.sorted_data_dict)
        # self.SaveTableData(self.table_data)
        # self.PlotTableData(self.table_data)

    def FileNameCheck(self, file_path:str = ''):
        ''' проверяет существование файла и получает его параметры '''

        if not Path(file_path).is_file():
            print(f'Файл {file_path} не существует.')
            return False
        self.file_path = file_path
        p = Path(file_path)
        self.abs_path = p.parent._str
        self.mod_time = os.path.getmtime(file_path)
        self.mod_time = datetime.datetime.fromtimestamp(self.mod_time).strftime('%H.%M.%S_%d.%m.%Y')
        self.file_name_with_ext = Path(file_path).name
        self.file_name_without_ext, extension = os.path.splitext(self.file_name_with_ext)

        return True

    def FileParser(self, file_name:str=''):
        ''' ищет и парсит строки с данными '''
        f = open(file_name, 'r')
        content = f.readlines()
        f.close()
        parsed_data = []
        for line in content:
            search = re.search(RE_PATTERN, line)
            if search:
                search_res = search.group(0)
                deser = json.loads(search_res)
                parsed_data.append(deser)
        return parsed_data

    def DataSortByFreq(self, parsed_data):
        ''' сортирует данные по частотам '''
        sorted_data_dict = {}
        for data in parsed_data:
            freq_key = str(data['freq'])

            if freq_key not in sorted_data_dict: # если такого ключа нет в словаре
                sorted_data_dict[freq_key] = []
                # print(f'find frequency: {freq_key}')

            sorted_data_dict[freq_key].append(data)

        for key in sorted_data_dict.keys():
            print(f'Freq:{key}, points: {len(sorted_data_dict[key])}')

        return sorted_data_dict

    def CreateTablesForEachFreq(self, sorted_data_dict):
        ''' создаёт типа таблц данных для каждой частоты '''
        table_data = {}
        table_data[KEY_EXPERIMENT_NAME] = 'exp name'
        table_data[KEY_EXPERIMENT_DATE] = '25.11.2025T10.22.00'
        table_data[KEY_PARSED_DATA] = []
        for key in sorted_data_dict.keys():
            # table_data[key] = []
            freq_data = {}
            freq_data[KEY_FREQ] = key
            freq_data[KEY_DATA] = []
            time_stamp = []
            ch0 = []
            ch1 = []
            for data in sorted_data_dict[key]:
                time_stamp.append(data[KEY_TIME_STAMP])
                ch0.append(data[KEY_VOLT_DATA])
                ch1.append(data[KEY_CURRENT_DATA])
            freq_data[KEY_DATA].append({KEY_TIME_STAMP   : time_stamp,
                                     KEY_VOLT_DATA    : ch0,
                                     KEY_CURRENT_DATA : ch1})
            table_data[KEY_PARSED_DATA].append(freq_data)
        return table_data

    def SaveTableData(self):
        ''' сохраняет таблицу с расширением .result '''
        # f_name = self.file_path.split('.')[0] + OUTPUT_FILE_EXTENCION
        # f_name = self.abs_path + self.mod_time + self.file_name_without_ext + OUTPUT_FILE_EXTENCION
        f_name = self.abs_path+'/'+self.file_name_without_ext+'_'+self.mod_time+PARSED_FILE_EXTENCION
        print(f_name)
        f = open(f_name, 'wt')
        json.dump(self.table_data, f, indent=' ')
        f.close()

    def PlotTableData(self, req_freq):
        '''  '''
        data_table = self.table_data
        for data in data_table[KEY_PARSED_DATA]:
            freq = data[KEY_FREQ]
            if req_freq != freq:
                continue
            d = data[KEY_DATA][0]
            time = d[KEY_TIME_STAMP]
            volt = d[KEY_VOLT_DATA]
            current = d[KEY_CURRENT_DATA]
            fig, ax = plt.subplots()
            ax.set_title(f'freq: {freq}')
            # ax.set_ylim(ymin=0, ymax=y.max()+y.max()/10)
            ax.plot(time, volt, linewidth=1.0)
            ax.plot(time, current, linewidth=1.0)
            ax.set_ylabel('volt')
            ax.set_xlabel('time')
            ax.grid(True)
            plt.show()

commands = [ 'f - file_name', 'p - plot', 's - save file', 'q - exit']

def main():
    parser = None
    if len(sys.argv) > 1:
        p = Parser(sys.argv[1])
        p.SaveTableData()
        return
    while True:
        cmd = input(commands)

        if cmd == 's':
            parser.SaveTableData()
        elif cmd == 'f':
            name = input('enter file name:')
            parser = Parser(name)
        elif cmd == 'p':
            freq = input('enter frequensy:')
            parser.PlotTableData(freq)
        elif cmd == 'q':
            return

if __name__ == '__main__':
    main()
