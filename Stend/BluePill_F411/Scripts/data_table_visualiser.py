import json
import matplotlib.pyplot as plt
import numpy as np

FILE_NAME = 'YAT.log.tables'


class cDataTableAnaliser:

    def __init__(self, file_name: str, time_stamp_key: str) -> None:
        ''' file_name - имя файла с таблицами
            time_stamp_key - ключ штампа времени, определённого для данных таблиц '''
        self.data_for_plot = None
        self.time_stamp_key = time_stamp_key
        data_tables = self.ReadTablesFromFile(file_name)
        all_keys = self.GetAllKeysFromTables(data_tables)
        # print(f'Reading keys: {all_keys}')
        for t in data_tables:
            self.TimeStampSequenceFilter(t, self.time_stamp_key)
            # print(self.CheckForEqualsCountOfTableDatas(t))
        self.data_for_plot = self.PrepareDataForPlot(data_tables, time_stamp_key)
        # self.PlotSeparateGraphs()

    def ReadTablesFromFile(self, file_name: str):
        ''' чтение и парсинг таблиц из файла '''
        file_content = None
        print(f'Try read from file: "{file_name}"')
        try:
            f = open(file_name, 'rt')
            file_content = f.read()
        except:
            return None
        data_tables = json.loads(file_content)
        print(f'Tables count was read: {len(data_tables)}')
        return data_tables

    def GetTableKeysList(self, one_table):
        ''' возвращает список ключей одной таблицы '''
        keys_list = list(one_table.keys())
        return keys_list

    def GetAllKeysFromTables(self, data_tables):
        ''' возвращает список всех ключей всех таблиц '''
        all_keys = []
        for table in data_tables:
            all_keys += self.GetTableKeysList(table)
        return all_keys

    def CheckForEqualsCountOfTableDatas(self, table):
        ''' проверяет совпадает ли количество данных по каждому ключу в таблице '''
        count = None
        for key in self.GetTableKeysList(table):
            if count == None:
                count = len(table[key])
                continue
            if count != len(table[key]):
                return False
        return True

    def TimeStampSequenceFilter(self, table, time_stamp_key):
        ''' фильтр на последовательность меток времени '''
        index = 0
        time_stamps = table[time_stamp_key]
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

    def DataDiffFiltr(self, tables_for_plot, delta:float):
        
        index = 0
        x_set = tables_for_plot['x']
        y_set = tables_for_plot['y']
        x_prev = x_set[0]
        y_prev = y_set[0]
        filtr_div = 50
        filtr_accum = y_prev*filtr_div
        filtr_aver = y_prev
        for y in y_set:
            filtr_accum += y
            filtr_aver = filtr_accum/filtr_div
            filtr_accum -= filtr_aver

            x = x_set[index]
            x_diff = abs(x-x_prev)
            y_diff = abs(y-y_prev)
            dy_dx = 0
            if x_diff > 0:
                dy_dx = y_diff/x_diff
            if dy_dx > 0.003:
                tables_for_plot['y'][index] = filtr_aver # filtr_aver

            x_prev = x
            y_prev = tables_for_plot['y'][index]
            index += 1
        return tables_for_plot

    def DataAverFiltr(self, table_column:list[float], delta:float):
        index = 0
        filtr_div = 10
        filtr_accum = table_column[0]*filtr_div
        filtr_aver = table_column[0]
        for next_element in table_column:
            if filtr_aver != 0 and next_element/filtr_aver > 1.027:
                next_element = filtr_aver
            filtr_accum += next_element
            filtr_aver = filtr_accum/filtr_div
            filtr_accum -= filtr_aver
            table_column[index] = next_element
            index += 1

    def DataJumpFilter(self, table_column:list[float], delta:float):
        index = 0
        prev_element = table_column[0]
        filtr_div = 10
        filtr_accum = table_column[0]*filtr_div
        filtr_aver = table_column[0]
        for element in table_column:
            filtr_accum += element
            filtr_aver = filtr_accum/filtr_div
            filtr_accum -= filtr_aver
            if abs(element - prev_element) > delta:
                table_column[index] = prev_element
                index += 1
                continue
            prev_element = element
            index += 1

    def DataColumnIsNumber(self, table_column:list) -> bool:
        ''' проверяет колонку на то, что в ней только цифры '''
        for element in table_column:
            try:
                float(element)
            except:
                return False
        return True

    def PrepareDataForPlot(self, tables, time_stamp_key: str):
        ''' создаёт из таблиц пары { 'name' : 'имя параметра', 'x':[метки времени...],'y' : [данные...] }
         для удобства вывода графиков по осям x, y '''
        tables_for_plot = []
        for table in tables:
            keys = self.GetTableKeysList(table)
            keys.remove(time_stamp_key)
            for key in keys:
                tb = {}
                tb['name'] = key
                if self.DataColumnIsNumber(table[key]):
                    y = [float(strValue) for strValue in table[key]]
                    #self.DataAverFiltr(y,5) # DataJumpFilter(y, 10)
                    tb['y'] = y
                else:
                    continue # текстовые данные игнорируем
                tb['x'] = [int(strValue) for strValue in table[time_stamp_key]]
                # self.DataDiffFiltr(tb, 10)
                # self.DataDiffFiltr(tb, 10)
                tables_for_plot.append(tb)
        return tables_for_plot

    def PlotSeparateGraphs(self, data_names: list[str], in_relative_units=False):
        ''' выводит отдельный график для каждого параметра '''
        data_for_plot = self.data_for_plot

        for table in data_for_plot:
            name = table['name']
            if name not in data_names:
                continue
            x = np.array(table['x'])
            y = np.array(table['y'])
            if in_relative_units:
                y = y/y.max()
            fig, ax = plt.subplots()
            ax.set_title(name)
            ax.set_ylim(ymin=0, ymax=y.max()+y.max()/10)
            ax.plot(x, y, linewidth=1.0)
            ax.set_ylabel(name)
            ax.set_xlabel('time, ms')
            ax.grid(True)

        plt.show()

    def PlotDataInOneGraph(self, data_names: list[str], in_relative_units=False):
        ''' выводит несколько графиков на одном
            in_relative_units=True - в относительных единицах
          '''
        data_for_plot = self.data_for_plot

        fig, ax = plt.subplots()
        ax.set_title(data_names)
        ax.set_xlabel('time, ms')
        ax.grid(True)
        for table in data_for_plot:
            name = table['name']
            if name not in data_names:
                continue
            x = np.array(table['x'])
            y = np.array(table['y'])
            if in_relative_units:
                y = y/y.max()
            ax.plot(x, y, label=name, linewidth=1.0)
        plt.legend()
        plt.show()

    def GetAvailableParamsForPlot(self):
        ''' возвращает список доступных ключей для построения графиков '''
        available_keys = []
        if self.data_for_plot:
            for data in self.data_for_plot:
                available_keys.append(data['name'])
        return available_keys

def main():
    dta = cDataTableAnaliser(FILE_NAME, 'TIME_STAMP')
    avail_data = dta.GetAvailableParamsForPlot()

    index = 0
    for d in avail_data:
        print(f'{index}. {d}')
        index += 1
    params_indexes = input('Введи через запятую номера параметров для вывода:').split(',')
    params_keys = []
    for index in params_indexes:
        params_keys.append(avail_data[int(index)])
    one_multi = input('Введи 0, для вывода на разных графиках, 1 - на одном:')
    relative_units = input('Введи 1 для вывода в относительных единицах:')
    if one_multi == '0':
        dta.PlotSeparateGraphs(params_keys, in_relative_units=(relative_units=='1'))
    elif one_multi == '1':
        dta.PlotDataInOneGraph(params_keys, in_relative_units=(relative_units=='1'))


if __name__ == '__main__':
    main()