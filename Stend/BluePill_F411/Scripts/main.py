import glob
from pathlib import Path
from common_constants import *
from new_stend_parser import LogParser
import consolemenu
from consolemenu import ConsoleMenu, SelectionMenu
from consolemenu.items import FunctionItem, SubmenuItem, CommandItem

# -----------------------------------------------------------------------------
def Init():
    '''  '''
    log_folder = Path(LOGS_FOLDER)
    if not log_folder.exists():
        log_folder.mkdir(parents=True, exist_ok=True)
    parse_folder = Path(PARSE_FOLDER)
    if not parse_folder.exists():
        parse_folder.mkdir(parents=True, exist_ok=True)
    calc_folder = Path(CALC_FOLDER)
    if not calc_folder.exists():
        calc_folder.mkdir(parents=True, exist_ok=True)
# -----------------------------------------------------------------------------
def LogParse():
    '''  '''
    idx = 0
    path = LOGS_FOLDER+'/*.log'
    files = glob.glob(path)
    files_dict = {}
    for file in files:
        files_dict[str(idx)] = file
        print(f'{idx}. {file}')
        idx += 1
    file_num = input('Введи номер файла: ')
    log_file = files_dict[file_num]
    print(f'{log_file}')
    parser = LogParser(log_path=log_file, res_path=PARSE_FOLDER)
    input()
# -----------------------------------------------------------------------------
def Calculate():
    '''  '''
    print(f'Calculate')
    input()
# -----------------------------------------------------------------------------
def ResultShow():
    '''  '''
    print(f'ResultShow')
    input()
# -----------------------------------------------------------------------------
def main():

    Init()

    menu = ConsoleMenu('Title', 'SubTitle', exit_menu_char='q')

    function_parse      = FunctionItem(function=LogParse,   text="Парсинг")
    function_calculate  = FunctionItem(function=Calculate,  text="Вычисления")
    function_resultshow = FunctionItem(function=ResultShow, text="Отображение результата")

    menu.append_item(function_parse)
    menu.append_item(function_calculate)
    menu.append_item(function_resultshow)

    menu.start()
    menu.join()
    menu.show()
# -----------------------------------------------------------------------------

if __name__ == '__main__':
    main()