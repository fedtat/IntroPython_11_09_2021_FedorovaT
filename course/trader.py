from argparse import ArgumentParser
import json
import csv
from random import uniform

configs = "config.json"
status = "balance.csv"


# считываем начальные данные из файла конфигурации
def get_data_from_config():
    with open(configs) as json_file:
        data = json.load(json_file)
    return data


# сохраняем стартовый баланс в csv в первой строке, а также используется для рестарта программы
def start_restart():
    start_balance = get_data_from_config()
    start_balance = {key: start_balance[key] for key in start_balance.keys() & {"rate", "usd_balance", "uah_balance"}}
    with open(status, "w", encoding="utf-8") as csv_file:
        fieldnames = ["rate", "usd_balance", "uah_balance"]
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerow(start_balance)


# генерируем случайный курс
def get_rate():
    data = get_data_from_config()
    rate = round(uniform((data["rate"] - data["delta"]), (data["rate"] + data["delta"])), 2)
    return rate


# функция для сохранения каждой транзакцию в csv (лог транзакций)
def log_balance_to_csv(new_balance, filename=status):
    with open(filename, "a", encoding="utf-8") as csv_file:
        fieldnames = ["rate", "usd_balance", "uah_balance"]
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writerow(new_balance)


# получаем из файла с логом транзакций последнюю запись
def get_balance():
    with open(status, "r", encoding="utf-8") as file:
        reader = csv.reader(file)
        result = [row for row in reader]
        result = dict(zip(result[0], result[-1]))
    return result


# функция для покупки USD и записи об этой транзакции в лог
def buy_usd(amount):
    res = get_balance()
    usd_balance = float(res["usd_balance"])
    uah_balance = float(res["uah_balance"])
    result_b = 0
    curr_rate = get_rate()
    if amount * curr_rate <= uah_balance > 0:
        usd_balance += amount
        uah_balance -= amount * curr_rate
        result_b = {"rate": curr_rate, "usd_balance": usd_balance, "uah_balance": uah_balance}
        return log_balance_to_csv(result_b)
    else:
        print(f"UNAVAILABLE, REQUIRED BALANCE UAH {amount * curr_rate}, AVAILABLE {uah_balance}")
    # return log_balance_to_csv(result_b)


# функция для продажи USD и записи об этой транзакции в лог
def sell_usd(amount):
    res = get_balance()
    usd_balance = float(res["usd_balance"])
    uah_balance = float(res["uah_balance"])
    result_s = 0
    curr_rate = get_rate()
    if amount <= usd_balance > 0:
        usd_balance -= amount
        uah_balance += amount * curr_rate
        result_s = {"rate": curr_rate, "usd_balance": usd_balance, "uah_balance": uah_balance}
        return log_balance_to_csv(result_s)
    else:
        print(f"UNAVAILABLE, REQUIRED BALANCE USD {amount}, AVAILABLE {usd_balance}")
    # return log_balance_to_csv(result_s)


# функция для покупки USD на все доступные гривны и записи об этой транзакции в лог
def buy_all_usd():
    res = get_balance()
    usd_balance = float(res["usd_balance"])
    uah_balance = float(res["uah_balance"])
    result_b = 0
    curr_rate = get_rate()
    if uah_balance > 0:
        usd_balance += uah_balance / curr_rate
        uah_balance = 0
        result_b = {"rate": curr_rate, "usd_balance": usd_balance, "uah_balance": uah_balance}
        return log_balance_to_csv(result_b)
    else:
        pass
        # print(f"UNAVAILABLE, REQUIRED BALANCE UAH > 0, AVAILABLE {uah_balance}")
    # return log_balance_to_csv(result_b)


# функция для продажи всех доступных USD и записи об этой транзакции в лог
def sell_all_usd():
    res = get_balance()
    usd_balance = float(res["usd_balance"])
    uah_balance = float(res["uah_balance"])
    result_s = 0
    curr_rate = get_rate()
    if usd_balance > 0:
        uah_balance += usd_balance * curr_rate
        usd_balance = 0
        result_s = {"rate": curr_rate, "usd_balance": usd_balance, "uah_balance": uah_balance}
        return log_balance_to_csv(result_s)
    else:
        pass
        # print(f"UNAVAILABLE, REQUIRED BALANCE USD > 0, AVAILABLE {usd_balance}")
    # return log_balance_to_csv(result_s)


# операции для самопроверки:
# start = start_restart()
# amount = 150
# new_balance = buy_usd(amount)
# amount = 200
# new_balance = buy_usd(amount)
# amount = 400
# new_balance = buy_usd(amount)
# print(new_balance)
# amount = 300
# new_balance = sell_usd(amount)
# new_balance = sell_all_usd()
# new_balance = buy_all_usd()
# restart = start_restart()


parser = ArgumentParser()
subparsers = parser.add_subparsers(dest="command")
rate = subparsers.add_parser("RATE")
available = subparsers.add_parser("AVAILABLE")
buy = subparsers.add_parser("BUY")
sell = subparsers.add_parser("SELL")
buy_all = subparsers.add_parser("BUY_ALL")
sell_all = subparsers.add_parser("SELL_ALL")
next = subparsers.add_parser("NEXT")
restart = subparsers.add_parser("RESTART")

buy.add_argument("amount", type=int, help="Input amount of USD to buy")
sell.add_argument("amount", type=int, help="Input amount of USD to sell")

args = parser.parse_args()

if args.command == "RATE":
    res_rate = get_rate()
    print(res_rate)
elif args.command == "AVAILABLE":
    res_balance = get_balance()
    usd_balance = res_balance["usd_balance"]
    uah_balance = res_balance["uah_balance"]
    print(f"USD {usd_balance} UAH {uah_balance}")
elif args.command == "BUY":
    buy_usd(args.amount)
elif args.command == "SELL":
    sell_usd(args.amount)
elif args.command == "BUY_ALL":
    buy_all_usd()
elif args.command == "SELL_ALL":
    sell_all_usd()
elif args.command == "NEXT":
    get_rate()
elif args.command == "RESTART":
    start_restart()
