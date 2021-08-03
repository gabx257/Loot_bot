import json


def add_money(name, amount):
    with open("wallet.json", "r") as file:
        person_list = json.load(file)
    person_list[name] += int(amount)
    with open("wallet.json", "w") as file:
        json.dump(person_list, file, indent=4)


def sub_money(name, amount):
    with open("wallet.json", "r") as file:
        person_list = json.load(file)
    person_list[name] -= int(amount)
    if person_list[name] < 0:
        person_list[name] = 0
    with open("wallet.json", "w") as file:
        json.dump(person_list, file, indent=4)


def create_wallet(name):
    with open("wallet.json", "r") as file:
        person_list = json.load(file)
    if name not in person_list.keys():
        person_list[name] = 0
    with open("wallet.json", "w") as file:
        json.dump(person_list, file, indent=4)


def delete_wallet(name):
    with open("wallet.json", "r") as file:
        person_list = json.load(file)
    if name in person_list.keys() and person_list[name] == 0:
        person_list.pop(name)
    with open("wallet.json", "w") as file:
        json.dump(person_list, file, indent=4)


def check_funds(name):
    with open("wallet.json", "r") as file:
        person_list = json.load(file)
    if name in person_list:
        return person_list[name]
