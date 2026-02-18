import os
import re
import json
import matplotlib.pyplot as plt
import numpy as np


FILE_NAME = '3_YAT-Log-20260218-134651.log'

RE_PATTERN = r'{"TIME_STAMP":\d+,"freq":\d+,"Ch0":\d+,"Ch1":\d+}'

KEY_EXPERIMENT_NAME  = 'EXPERIMENT_NAME' # "KeyStart",
KEY_EXPERIMENT_DATE  = 'EXPERIMENT_DATE' # "25.11.2025T10.22.00",
KEY_FREQ = 'FREQ'
KEY_DATA = 'DATA'
KEY_TIME_STAMP       = 'TIME_STAMP'
KEY_VOLT_DATA        = 'Ch0'
KEY_CURRENT_SATA     = 'Ch1'
KEY_PARSED_DATA      = 'PARSED_DATA'

class Parser:

    def __init__(self, file_name:str=''):
        self.file_name = file_name
        self.parsed_data = self.FileParser(file_name)
        self.sorted_data_dict = self.DataSortByFreq(self.parsed_data)
        self.table_data = self.CreateTablesForEachFreq(self.sorted_data_dict)
        self.SaveTableData(self.table_data)
        # self.PlotTableData(self.table_data)
        # self.SaveSortedDataDict(self.sorted_data_dict)

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
                ch1.append(data[KEY_CURRENT_SATA])
            freq_data[KEY_DATA].append({KEY_TIME_STAMP   : time_stamp,
                                     KEY_VOLT_DATA    : ch0,
                                     KEY_CURRENT_SATA : ch1})
            table_data[KEY_PARSED_DATA].append(freq_data)
        return table_data

    def SaveTableData(self, table_data):
        ''' сохраняет таблицу с расширением .result '''
        f_name = self.file_name.split('.')[0] + '.result'
        f = open(f_name, 'wt')
        json.dump(table_data, f, indent=' ')
        f.close()

    def PlotTableData(self, data_table):
        '''  '''
        for data in data_table[KEY_PARSED_DATA]:
            freq = data[KEY_FREQ]
            d = data[KEY_DATA][0]
            time = d[KEY_TIME_STAMP]
            volt = d[KEY_VOLT_DATA]
            current = d[KEY_CURRENT_SATA]
            fig, ax = plt.subplots()
            ax.set_title(f'freq: {freq}')
            # ax.set_ylim(ymin=0, ymax=y.max()+y.max()/10)
            ax.plot(time, volt, linewidth=1.0)
            ax.plot(time, current, linewidth=1.0)
            ax.set_ylabel('volt')
            ax.set_xlabel('time')
            ax.grid(True)
            plt.show()

    def SaveSortedDataDict(self, sorted_data_dict):
        ''' сохраняет данные в файлы для дальнейшей обработки '''
        folder_name = self.file_name.split('.')[0] + '15.44.00_18.02.2026'
        try:
            os.mkdir(folder_name)
        except:
            pass

        for key in sorted_data_dict.keys():
            file_name = folder_name + '/YAT-Log-' + str(key) + 'Hz.log'
            f = open(file_name, 'a')
            for data in sorted_data_dict[key]:
                data_to_save = {}
                data_to_save['TIME_STAMP'] = data['TIME_STAMP']
                data_to_save['Ch0'] = data['Ch0']
                data_to_save['Ch1'] = data['Ch1']
                save_str = json.dumps(data_to_save) + '\n'
                f.write(save_str)
            f.close()

def main():
    p = Parser(FILE_NAME)

if __name__ == '__main__':
    main()
