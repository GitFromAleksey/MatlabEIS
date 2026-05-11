from pathlib import Path
import json
from common_constants import *

FILE_NAME = 'robiton3.log'

# data = {'freq':1000, 'data':[(1,2),(3,4),(5,6)]}

class LogParser:

    def __init__(self, log_path:str='', res_path:str=''):
        self.parse_res = { 
            KEY_EXPERIMENT_NAME: "testgen_ph_-30", 
            KEY_EXPERIMENT_DATE: "14.12.36_02.03.2026"}
        self.parse_res[KEY_PARSED_DATA] = []
        content = self.ReadLog(log_path)
        self.Parse(content)
        res_name = Path(log_path).stem
        self.SaveParseResult(res_path+'/'+res_name)

    def ReadLog(self, log_path:str=''):
        ''' читает содержимое лога '''
        f = open(log_path, 'rt') # , encoding='utf-8')
        log_content = f.readlines()
        f.close()
        return log_content

    def SaveParseResult(self, res_path:str=''):
        ''' сохраняет в файл результат парсинга '''
        f_out = open(res_path+'.result', 'w')
        json.dump(self.parse_res, f_out, indent=2)
        f_out.close()

    def Parse(self, log_content):
        ''' парсит содержимое лога '''
        for line in log_content:
            try:
                j = json.loads(line)
                data = {}
                data[KEY_FREQ] = str(j['freq'])
                data[KEY_DATA] = []

                TIME_STAMP = []
                CH0 = []
                CH1 = []
                time_stamp = 0
                for ch0, ch1 in j['data']:
                    TIME_STAMP.append(time_stamp)
                    time_stamp += 1
                    CH0.append(ch0)
                    CH1.append(ch1)

                data[KEY_DATA] = [
                    {
                    KEY_TIME_STAMP : TIME_STAMP,
                    KEY_CHANNEL0 : CH0,
                    KEY_CHANNEL1 : CH1
                    }
                ]
                self.parse_res[KEY_PARSED_DATA].append(data)
            except Exception as e:
                print(f'Exception: {e}')

def main():
    # global data
    # d=json.dumps(data)

    f = open(FILE_NAME, 'rt') # , encoding='utf-8')
    content = f.readlines()
    f.close()

    result = { KEY_EXPERIMENT_NAME: "testgen_ph_-30", 
              KEY_EXPERIMENT_DATE: "14.12.36_02.03.2026"}
    result[KEY_PARSED_DATA] = []

    for line in content:
        try:
            j = json.loads(line)
            data = {}
            data[KEY_FREQ] = str(j['freq'])
            data[KEY_DATA] = []

            TIME_STAMP = []
            CH0 = []
            CH1 = []
            time_stamp = 0
            for ch0, ch1 in j['data']:
                TIME_STAMP.append(time_stamp)
                time_stamp += 1
                CH0.append(ch0)
                CH1.append(ch1)

            data[KEY_DATA] = [
                {
                KEY_TIME_STAMP : TIME_STAMP,
                KEY_CHANNEL0 : CH0,
                KEY_CHANNEL1 : CH1
                }
            ]
            result[KEY_PARSED_DATA].append(data)
        except:
            pass

    f_out = open(FILE_NAME+'.result', 'w')
    json.dump(result, f_out, indent=2)
    f_out.close()

    pass


if __name__ == '__main__':
    main()