from pathlib import Path
import datetime
import sys
import gzip
import re

banner_list = {}


def file_search_date(data, current_date):
    if current_date == datetime.datetime.fromtimestamp(data.st_mtime).date():
        return True
    else:
        return False


def parse_str(log_str):
    scroll = 1 if not log_str.find('scrollaudit') == -1 else 0
    # day,mouth,year = re.findall(r'\[[^\:]*',str)[0][1:].split("/")
    # datetime.date(year,mouth,day),
    try:
        id_baner = re.findall(r'banner=\w*', log_str)[0].split("=")[1]
    except:
        id_baner = -1
    return id_baner, scroll


def count_str(file_line_str):
    """ Чистотный счетчик через глобальную переменную """
    id_baner, scroll = parse_str(file_line_str)
    try:
        banner_list[id_baner][scroll] += 1
    except KeyError:
        banner_list[id_baner] = [0, 0]
        banner_list[id_baner][scroll] += 1


def file_read(file_obj):
    """ Читает фаил """
    abs_path = file_obj.absolute().__str__()
    if file_obj.name.split('.')[-1] == 'gz':
        with gzip.open(abs_path) as f:
            for readline in f:
                count_str(readline.decode('utf-8'))
    elif file_obj.name.split('.')[-1] == 'log' or file_obj.name.split('.')[-2] == 'log':
        with open(abs_path, 'r') as f:
            for readline in f:
                count_str(readline)


if __name__ == '__main__':
    if not len(sys.argv) - 1:
        print("not args for script \n\r User pythom script.py year/mouth/day baner_id")
    else:
        date_str = sys.argv[1]
        date = datetime.date(*map(lambda x: int(x), date_str.split('/')))
        """ Поиск файла требуемой даты """
        p = Path('log')
        files = [x for x in p.iterdir() if not x.is_dir() and file_search_date(x.stat(), date) and (
                    x.name.split('.')[-1] == 'gz' or x.name.split('.')[-1] == 'log' or x.name.split('.')[-2] == 'log')]
        """ Обработка массива файлов """
        for file in files:
            file_read(file)

        # print all baners
        # for obj in banner_list:
        #     print(f"[ids={obj} scroll = {banner_list[obj][0]} not scroll = {banner_list[obj][1]}]")

        # search baner_id in array
        baner_id = str(sys.argv[2])
        print(
            f"baner id = {baner_id}\n\r\tдоскроллов = {banner_list[baner_id][0]}\n\r\tпросмотров = {banner_list[baner_id][1]}")
