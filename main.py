import shutil
import requests
import os
from requests.auth import HTTPBasicAuth
import urllib3
import sqlite3
import json
from ColumnReferences import *

master_list = []
pkmn_list = []
trainer_list = []
attacks_list = []


def download_card_images(card_id: str, png_url: str) -> None:
    req = requests.get(png_url, stream=True, headers={'User-Agent': 'Mozilla/5.0'})
    if req.status_code == 200:
        with open(f'{card_id}.png', 'wb') as f:
            req.raw.decode_content = True
            shutil.copyfileobj(req.raw, f)


def generate_image_path(pkmn_id: str) -> str:
    return 'cardImages\\' + pkmn_id + '.png'


def eliminate_nested_lists(pkmn: dict) -> None:
    if len(pkmn['subtypes']) > 0:
        pkmn['subtypes'] = pkmn['subtypes'][0]

    if len(pkmn['types']) > 0:
        pkmn['types'] = pkmn['types'][0]

    try:
        if len(pkmn['evolvesTo']) > 0:
            pkmn['evolvesTo'] = pkmn['evolvesTo'][0]
    except KeyError:
        pkmn['evolvesTo'] = 'NULL'

    try:
        if len(pkmn['weaknesses']) > 0:
            pkmn['weaknesses'] = pkmn['weaknesses'][0]['type']
    except KeyError:
        pkmn['weaknesses'] = 'NULL'

    try:
        if len(pkmn['resistances']) > 0:
            pkmn['resistances'] = pkmn['resistances'][0]['type']
    except KeyError:
        pkmn['resistances'] = 'NULL'

    try:
        if len(pkmn['retreatCost']) > 0:
            pkmn['retreatCost'] = convert_energy_list(pkmn['retreatCost'])
    except KeyError:
        pkmn['retreatCost'] = 'NULL'


def convert_energy_list(energy_list: list) -> str:
    final_string = ''
    energy_list_as_set = set(energy_list)
    for item in energy_list_as_set:
        final_string += item + '_' + str(energy_list.count(item)) + ' '

    final_string = final_string[:-1]
    return final_string


def attack_is_duplicate(single_attack: dict) -> bool:
    duplicate_attack = False
    for atk in attacks_list:
        if single_attack['name'] == atk['name']:
            duplicate_attack = True
            break
    return duplicate_attack


def assign_nulls(temp_dict: dict) -> None:
    for k, v in temp_dict.items():
        if v == '':
            k[v] = 'NULL'


def dispatch_formatted_attack(single_attack: dict) -> None:
    if not attack_is_duplicate(single_attack):

        temp_attack = {k: 'NULL' for k in attacks_key_list}
        for k, v in temp_attack.items():
            if k != 'cost' and single_attack[k] != '':
                temp_attack[k] = single_attack[k]

        if single_attack['cost'] != '':
            temp_attack['cost'] = convert_energy_list(single_attack['cost'])

        attacks_list.append(temp_attack)


def change_to_ints(temp_dict: dict) -> None:
    for k, v in temp_dict.items():
        if k == 'level' or k == 'hp':
            try:
                v = int(v)
            except ValueError:
                continue


def get_relevant_info(entry: dict) -> None:
    if entry['supertype'] == 'Pokémon':
        eliminate_nested_lists(entry)

        temp_dict = {k: 'NULL' for k in pkmn_key_list}
        for k, v in temp_dict.items():

            try:
                temp_dict[k] = entry[k]
            except KeyError:
                continue


        temp_dict['imagePath'] = generate_image_path(entry['id'])

        try:
            for cnt, atk in enumerate(entry['attacks'], 1):
                temp_dict[f'attack{cnt}'] = atk['name']
                dispatch_formatted_attack(atk)
        except KeyError:
            pass

        change_to_ints(temp_dict)
        pkmn_list.append(temp_dict)

    elif entry['supertype'] == 'Trainer':
        entry['rules'] = entry['rules'][0]
        entry['imagePath'] = generate_image_path(entry['id'])
        temp_dict = {k: entry[k] for k in trainer_key_list}
        assign_nulls(temp_dict)
        trainer_list.append(temp_dict)


def format_pkmn_for_db_insertion(pkmn_row: dict) -> tuple:
    temp_row_dict = pkmn_key_dict.copy()
    for k, v in pkmn_row.items():
        if v == '':
            v = 'NULL'
        if k == 'level' or k == 'hp':
            try:
                v = int(v)
            except ValueError:
                continue
        temp_row_dict[k] = v
    return tuple(temp_row_dict.values())

# ----------------------- API ---------------------- #


method = "get"
api_key = os.environ.get("API_KEY")
endpoint = "https://api.pokemontcg.io/v2/cards"
auth = HTTPBasicAuth('apikey', api_key)

parameters = {
    'orderBy': 'set',
    'page': '1'
}

response = requests.get(url=endpoint, auth=auth, params=parameters)
response.raise_for_status()
all_cards_page_1 = response.json()
all_data_page_1 = all_cards_page_1['data']
for data_page_1 in all_data_page_1:
    master_list.append(data_page_1)

parameters['page'] = '2'
response = requests.get(url=endpoint, auth=auth, params=parameters)
response.raise_for_status()
all_cards_page_2 = response.json()
all_data_page_2 = [i for i in all_cards_page_2['data'] if i['set']['name'] != 'Team Rocket' and
                   i['set']['name'] != 'Legendary Collection']
for data_page_2 in all_data_page_2:
    master_list.append(data_page_2)

for card in master_list:
    get_relevant_info(card)

for atk in attacks_list:
    atk['damage'] = atk['damage'].replace('×', '_x')
    atk['damage'] = atk['damage'].replace('+', '_+')
    atk['text'] = atk['text'].replace('é', 'e')

for trnr in trainer_list:
    trnr['rules'] = trnr['rules'].replace('é', 'e')
    trnr['name'] = trnr['rules'].replace('é', 'e')


# -------------------------- SQL --------------------------#

connection = sqlite3.connect('PkmnCards.db')
connection.execute("PRAGMA foreign_keys = 1")
cursor = connection.cursor()

pkmn_table_columns = ','.join(db_pkmn_col_list)
attack_table_columns = ','.join(db_attacks_col_list)
trainer_table_columns = ','.join(db_trainer_col_list)

cursor.execute(f"CREATE TABLE IF NOT EXISTS PokemonTable({pkmn_table_columns})")
cursor.execute(f"CREATE TABLE IF NOT EXISTS AttacksTable({attack_table_columns})")
cursor.execute(f"CREATE TABLE IF NOT EXISTS TrainerTable({trainer_table_columns})")

entire_formatted_pkmn_list = [tuple(row.values()) for row in pkmn_list]
entire_formatted_attacks_list = [tuple(row.values()) for row in attacks_list]
entire_formatted_trainer_list = [tuple(row.values()) for row in trainer_list]

cursor.executemany("INSERT INTO TrainerTable VALUES(?, ?, ?, ?)",
                   entire_formatted_trainer_list)

cursor.executemany("INSERT INTO AttacksTable VALUES(?, ?, ?, ?)",
                   entire_formatted_attacks_list)
cursor.execute("INSERT INTO AttacksTable VALUES('NULL', 'NULL', 'NULL', 'NULL')")

cursor.executemany("INSERT OR IGNORE INTO PokemonTable VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                   entire_formatted_pkmn_list)

connection.commit()
