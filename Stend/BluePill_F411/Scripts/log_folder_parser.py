import os
import re
import datetime
import json
from log_file_parser import cLogFileParser

LOGS_FOLDER = 'Эксперимент_18.19.01_04.10.2025'

RE_EXPERIMENT = r'(\w+)_'
RE_DATE = r'\d{2}.\d{2}.\d{2}_\d{2}.\d{2}.\d{4}'
RE_FOLDER_NAME = RE_EXPERIMENT+RE_DATE
RE_LOG_NAME = r'\d+Hz.log' # YAT-Log-4000Hz.log


def ParseFolderName(folder_name:str = ''):
    '''  '''
    f_name = re.search(RE_FOLDER_NAME, folder_name)
    if f_name == None:
        return None
    search = re.search(RE_EXPERIMENT, folder_name)
    experiment_name = search.group(0).replace('_','')
    search = re.search(RE_DATE, folder_name)
    date = search.group(0)
    dt = datetime.datetime.strptime(date, '%H.%M.%S_%d.%m.%Y')
    return experiment_name, dt

def ParseLogFileName(log_name:str=''):
    res = re.search(RE_LOG_NAME, log_name)
    if res == None:
        return None
    res = re.search(r'\d+Hz', log_name)
    if res:
        freq = re.search(r'\d+', res.group(0)).group(0)
    return freq

def main():
    logs_folder = LOGS_FOLDER

    res = ParseFolderName(logs_folder)
    if res == None:
        print(f'Неправильное название папки логов: {logs_folder}')
        return

    experiment_name, date_time = res

    parsed_data = []
    log_files = os.listdir(logs_folder)
    for log_name in log_files:
        print(f'Parse log file: {log_name}')
        file_data = {}
        freq = ParseLogFileName(log_name)
        print(f'Signal frequency: {freq}')
        helper = cLogFileParser(logs_folder+'/'+log_name)
        data = helper.parse_result
        file_data['FREQ'] = freq
        file_data['DATA'] = data
        parsed_data.append(file_data)

    print(f'Save parsing result...')
    date_time_str = date_time.strftime('%d.%m.%YT%H.%M.%S') # 04.02.2025T18:21:00
    parse_result_file_name = experiment_name+'_'+date_time_str+'.result'
    print(f'Save parsing file: {parse_result_file_name}')
    with open(parse_result_file_name, 'wt') as f:
        json.dump(parsed_data, f, indent=1)
        f.close()



if __name__ == '__main__':
    main()