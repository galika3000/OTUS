#!usr/bin/python3
import pandas as pd
import argparse
import os
import json
import re
from collections import Counter


def parse_log(text):
    pattern = r'(?P<ip>\d+\.\d+\.\d+\.\d+) \S+ \S* \[(?P<date>\d{2}/\w{3}/\d{4}:\d{2}:\d{2}:\d{2} ([\+\-]\d{4}))\] "(?P<method>\w+) (?P<protocol_version>.+?) HTTP/\d\.\d" (?P<status>\d{3}) (?P<size>\S+) "(?P<url>.*?)" "(?P<user_agent>.*?)" (?P<duration>\d+)'
    match = re.match(pattern, text)

    if match:
        result_dict = match.groupdict()
        return result_dict
    else:
        raise ValueError(f"Невозможно разобрать строку: {text}")


def create_list(log_):
    result_array = []

    if os.path.exists(log_):
        with open(log_) as log:        
            for log_line in log:
                pandas_line=[] 
                parsed_data = parse_log(log_line)
                if parsed_data:
                    pandas_line.append(parsed_data['ip'])
                    pandas_line.append(parsed_data['date'])
                    pandas_line.append(parsed_data['method'])
                    pandas_line.append(parsed_data['url'])
                    pandas_line.append(parsed_data['duration'])
                    
                    result_array.append(pandas_line)
                
                else:
                    print("Не удалось разобрать строку.", log_line)
    
    # Собираем полученную статистику в один словарь
    result={}
    result['top_ips'] = top_ips(result_array)
    result['top_longest'] = top_longest(result_array)
    result['total_stat'] = total_stat(result_array)
    result['total_requests'] = len(result_array)

    #Выводим полученные результаты на экран
    print(result)

    # Сохраняем полученные результаты в JSON-файл
    with open("result.json", "w") as outfile:
        json.dump(result, outfile, indent=4)

def top_ips(result_array):

    # Извлекаем все IP-адреса из списка
    ip_list = [row[0] for row in result_array]

    # Считаем частоту каждого IP-адреса с помощью Counter
    ip_counter = Counter(ip_list)

    # Получаем 3 самых частых IP-адреса
    most_common_ips = ip_counter.most_common(3)

    top_ips = {ip: count for ip, count in most_common_ips}

    return top_ips

def top_longest(result_array):
    sorted_result_array = sorted(result_array, key=lambda x: (x[4]), reverse=True)

    # Выбираем первые 3 строки с наибольшими duration
    top_3_durations = sorted_result_array[:3]

    # Сохраняем результат в словарь
    top_longest = {
        i: {
            "ip": row[0],
            "date": row[1],
            "method": row[2],
            "url": row[3],
            "duration": row[4],
        }
        for i, row in enumerate(top_3_durations)
    }
    return top_longest
    
def total_stat(result_array):
    total_stat = {
        "GET": 0,
        "POST": 0,
        "PUT": 0,
        "DELETE": 0,
        "OPTIONS": 0,
        "HEAD": 0,
    }

    # Перебираем каждый элемент массива
    for row in result_array:
        # Проверяем, содержится ли текущий метод в строке
        for method in total_stat:
            if method in row:
                # Если содержится, увеличиваем счётчик для этого метода
                total_stat[method] += 1
    return total_stat

if __name__ == '__main__': 
    
    default_file = os.path.join(os.getcwd(), 'access.log')

    parser = argparse.ArgumentParser(description='Поиск логов.')
    parser.add_argument('-d', '--dir', help='Директория или файл с логами.', default=default_file)
    args = parser.parse_args()
    
    if os.path.isdir(args.dir):
        list_files = os.listdir(args.dir)
        for current_flie in list_files:
            if current_flie.endswith('.log'):
                # Собираем полный путь к файлу
                full_path = os.path.join(current_flie, args.dir)
                result_array = create_list(full_path)
    elif os.path.isfile(args.dir):
        result_array = create_list(args.dir)
    else:
        print("Не указаны ни файл с логами, ни директория где они находятся")
