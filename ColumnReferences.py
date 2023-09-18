
pkmn_key_dict = {
    'id': '',
    'name': '',
    'subtypes': '',
    'level': '',
    'hp': '',
    'types': '',
    'evolvesFrom': '',
    'evolvesTo': '',
    'attack1': '',
    'attack2': '',
    'weaknesses': '',
    'resistances': '',
    'retreatCost': '',
    'imagePath': ''
}

pkmn_key_list = [
    'id',
    'name',
    'subtypes',
    'level',
    'hp',
    'types',
    'evolvesFrom',
    'evolvesTo',
    'attack1',
    'attack2',
    'weaknesses',
    'resistances',
    'retreatCost',
    'imagePath'
]

attacks_key_list = [
    'name',
    'cost',
    'damage',
    'text'
]

trainer_key_list = [
    'id',
    'name',
    'rules',
    'imagePath'
]

db_pkmn_col_list = [
    'id TEXT NOT NULL PRIMARY KEY',
    'name TEXT',
    'subtypes TEXT',
    'level INTEGER',
    'hp INTEGER',
    'types TEXT',
    'evolvesFrom TEXT',
    'evolvesTo TEXT',
    'attack1 TEXT',
    'attack2 TEXT',
    'weaknesses TEXT',
    'resistances TEXT',
    'retreatCost TEXT',
    'imagePath TEXT',
    'FOREIGN KEY (attack1) REFERENCES AttacksTable(name)',
    'FOREIGN KEY (attack2) REFERENCES AttacksTable(name)'
]

db_attacks_col_list = [
    'name TEXT NOT NULL PRIMARY KEY',
    'cost TEXT',
    'damage TEXT',
    'text TEXT'
]

db_trainer_col_list = [
    'id TEXT NOT NULL PRIMARY KEY',
    'name TEXT',
    'rules TEXT',
    'imagePath TEXT'
]
