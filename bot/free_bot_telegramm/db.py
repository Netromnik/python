from typing import Dict, List, Tuple

import sqlite3


conn = sqlite3.connect("bot_bd.bd")
cursor = conn.cursor()

TABLE_NAME = "task_q"

def insert(table: str, column_values: Dict):
    columns = ', '.join( column_values.keys() )
    values = [tuple(column_values.values())]
    placeholders = ", ".join( "?" * len(column_values.keys()) )
    cursor.executemany(
        f"INSERT INTO {table} "
        f"({columns}) "
        f"VALUES ({placeholders})",
        values)
    conn.commit()

def update(table: str, column_and_data: Dict,conditional:List):
    sql_pars = []
    for i in column_and_data:
        if type(column_and_data[i]) == int:
            sql_pars.append(f'{i} = {column_and_data[i]}')
        else:
            sql_pars.append(f" {i} = '{column_and_data[i]}'")
    sql_pars = ','.join(sql_pars)
    sql_raw =f"UPDATE {table}  SET {sql_pars} WHERE {conditional[0]} = {conditional[1]}"
    cursor.execute(sql_raw)
    conn.commit()

def fetchall(table: str, columns: List[str]) -> List[Dict]:
    columns_joined = ", ".join(columns)
    cursor.execute(f"SELECT {columns_joined} FROM {table}")
    rows = cursor.fetchall()
    result = []
    for row in rows:
        dict_row = {}
        for index, column in enumerate(columns):
            dict_row[column] = row[index]
        result.append(dict_row)
    return result

def get_row(table:str,columns:List[str],conditional:List)->List[Dict]:
    columns_joined = ", ".join(columns)
    sql_raw = f"SELECT {columns_joined} FROM {table} where  {conditional[0]} = {conditional[1]}"
    cursor.execute(sql_raw)
    rows = cursor.fetchall()
    result = []
    for row in rows:
        dict_row = {}
        for i in range(len(columns)):
            dict_row[columns[i]] =row[i]
        result.append(dict_row)
    return result

def delete(table: str, row_id: int) -> None:
    row_id = int(row_id)
    cursor.execute(f"delete from {table} where user_id={row_id}")
    conn.commit()


def get_cursor():
    return cursor


def _init_db():
    """Инициализирует БД"""
    with open("db.sql", "r") as f:
        sql = f.read()
    cursor.executescript(sql)
    conn.commit()


def check_db_exists():
    """Проверяет, инициализирована ли БД, если нет — инициализирует"""
    cursor.execute("SELECT name FROM sqlite_master "
                   "WHERE type='table' AND name='task_q'")
    table_exists = cursor.fetchall()
    if table_exists:
        return
    _init_db()

check_db_exists()
# update(TABLE_NAME,column_and_data={"user_id":23,},conditional=['user_id',12])
# t = get_row(TABLE_NAME,['user_id','body_text','photo','locate','state'],['user_id', 12])
# print(t)