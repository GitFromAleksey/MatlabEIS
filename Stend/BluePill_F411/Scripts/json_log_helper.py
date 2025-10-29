import json
import csv
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
from datetime import timedelta

FILE_NAME = 'YAT.log'
DATE_TIME_STAMP = 'DATE_TIME'
DATE_TIME_FORMAT = '%d.%m.%YT%H:%M:%S'
STARDATE_TIME = datetime.strptime('21.02.2025T17:28:10', DATE_TIME_FORMAT)

class cJsonLogHelper:

    KEY_TIME_STAMP = 'TIME_STAMP'

    def __init__(self, file_name: str = '', date_time_start: datetime = datetime.now()) -> None:
        content_json_str = self.ReadFromLogFile(file_name)
        data_tables = self.ParseContent(content_json_str)
        'проверка штампов времени на последовательность'
        for table in data_tables:
            self.TimeStampSequenceFilter(table)
        # делаем чтобы отсчёт времени был от нуля
        self.ShiftStartTimeStampToZero(data_tables)

        self.AddDateTime(data_tables, date_time_start)
        # сохраняем таблицы в файл в json формате для удобства дальнейшей обработки
        self.out_file_name = file_name+'.tables'
        with open(self.out_file_name, 'wt') as f:
            d = json.dumps(data_tables, indent=2)
            f.write(d)


    def ReadFromLogFile(self, file_name: str = '') -> list[str]:
        with open(file_name, 'r') as f:
            content = f.read()
        split_content = content.split('\n')
        return split_content

    def ParseContent(self, json_content: list[str]):
        '''  '''
        # парсим каждую строку json формата и добавляем в список
        parsed_json_list = []
        for json_str in json_content:
            parsed_json = self.ParseJsonStr(json_str)
            if parsed_json:
                parsed_json_list.append(parsed_json)
        # составляем список ключей, которые есть в списке распарсеных строк
        keys_list = []
        for parsed_json in parsed_json_list:
            keys = list(parsed_json.keys())
            if keys not in keys_list:
                keys_list.append(keys)
        # используя найденые ключи составляем по ним таблицы словари типа { 'key_1' : [1,5,9,7], 'key_2' : [1,5,9,7] }
        data_tables = []
        for keys in keys_list:
            data_table = {}
            for parsed_json in parsed_json_list:
                if keys == list(parsed_json.keys()):
                    for key in keys:
                        data = parsed_json.get(key)
                        if not data_table.get(key):
                            data_table[key] = []
                        data_table[key].append(data)
            data_tables.append(data_table)
        return data_tables

    def AddDateTime(self, data_tables, date_time_start):
        # DATE_TIME_STAMP
        
        
        time_stamp_key = cJsonLogHelper.KEY_TIME_STAMP
        for table in data_tables:
            real_time_list = []
            for time_stamp in table[time_stamp_key]:
                # t = datetime.fromtimestamp(int(time_stamp))
                t = timedelta(milliseconds=int(time_stamp))
                date_time = date_time_start + t
                date_time_str = date_time.strftime(DATE_TIME_FORMAT) # 04.02.2025T18:21:00
                real_time_list.append(date_time_str)
            table[DATE_TIME_STAMP] = real_time_list
        pass

    def ShiftStartTimeStampToZero(self, data_tables):
        # поиск наименьшего значения TIME_STAMP от которого будет отсчёт
        time_stamp_min = None
        time_stamp_key = cJsonLogHelper.KEY_TIME_STAMP
        for table in data_tables:
            time_stamp_0 = int(table[time_stamp_key][0])
            if time_stamp_min == None:
               time_stamp_min = time_stamp_0
            if time_stamp_0 < time_stamp_min:
                time_stamp_min = time_stamp_0
        # сдвигаем время влево относительно минимального начального времени
        for table in data_tables:
            for index in range(len(table[time_stamp_key])):
                time_stamp = int(table[time_stamp_key][index])
                table[time_stamp_key][index] = str(time_stamp-time_stamp_min)
        pass

    def ParseJsonStr(self, json_str: str = '') -> json:
        try:
            parsed = json.loads(json_str)
        except:
            parsed = None
        return parsed

    def WriteCSV(self, data_tables):
        file_counter = 0
        for table in data_tables:
            csv_file_name = '_'.join(table.keys()).replace(' ','_') + '.csv'
            with open(csv_file_name, 'w', newline='') as csvfile:
                file_counter += 1
                header = list(table.keys())
                csv_writer = csv.DictWriter(csvfile, fieldnames=header)
                csv_writer.writeheader()
                rows_number = len(table[header[0]])
                for row_num in range(rows_number):
                    row = {}
                    for cell_name in header:
                        row[cell_name] = table[cell_name][row_num]
                    csv_writer.writerow(row)

    def TimeStampSequenceFilter(self, table):
        ''' фильтр на последовательность меток времени '''
        index = 0
        time_stamps = table[cJsonLogHelper.KEY_TIME_STAMP]
        prev_t_st = 0
        for t_st in time_stamps:
            if (int(t_st) < prev_t_st): # если веремя меньше чем предыдущее
                time_stamps[index] = str(prev_t_st)
                t_st = str(prev_t_st)
            if (index+1) < len(time_stamps): # если веремя больше чем следущее
                if (int(t_st) > int(time_stamps[index+1])):
                    time_stamps[index] = str(prev_t_st)
                    t_st = str(prev_t_st)
            prev_t_st = int(t_st)
            index += 1

    def DataJumpFilter(self, table_column:list[float], delta:float):
        index = 0
        prev_element = table_column[0]
        for element in table_column:
            if abs(float(element) - float(prev_element)) > delta:
                table_column[index] = prev_element
                index += 1
                continue
            prev_element = element
            index += 1

    def CheckDataIsANumber(self, table_column:list) -> bool:
        for element in table_column:
            try:
                float(element)
            except:
                return False
        return True

    def Plot(self, data_tables):
        
        key_x = 'x'
        key_y = 'y'
        key_y_label = 'y_label'
        for table in data_tables:
            data_for_plot = { key_x: None, key_y: None, key_y_label: None }
            for key in table.keys():
                if key == cJsonLogHelper.KEY_TIME_STAMP:
                    self.TimeStampSequenceFilter(table)
                    x = [int(strValue) for strValue in table[cJsonLogHelper.KEY_TIME_STAMP]]
                    data_for_plot[key_x] = x
                else:
                    if self.CheckDataIsANumber(table[key]):
                        # self.DataJumpFilter(table[key], 200)
                        y = [float(strValue) for strValue in table[key]]
                        data_for_plot[key_y] = y
                        data_for_plot[key_y_label] = key

            fig, ax = plt.subplots()
            x = data_for_plot[key_x]
            y = data_for_plot[key_y]
            y_label = data_for_plot[key_y_label]
            if (x != None) and (y != None):
                ax.plot(x, y, linewidth=1.0)
                ax.set_ylabel(y_label)
                ax.set_xlabel('time, ms')
                ax.grid(True)
        
        plt.show()


def main():
    cJsonLogHelper(FILE_NAME, STARDATE_TIME)
    input('Eny key to exit.')

if __name__ == '__main__':
    main()
