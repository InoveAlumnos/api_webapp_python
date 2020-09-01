#!/usr/bin/env python
'''
Heart DB manager
---------------------------
Autor: Inove Coding School
Version: 1.1

Descripcion:
Programa creado para administrar la base de datos de registro
de pulsaciones de personas
'''

__author__ = "Inove Coding School"
__email__ = "alumnos@inove.com.ar"
__version__ = "1.1"

import os
import sqlite3

db = {}


def create_schema():

    # Conectarnos a la base de datos
    # En caso de que no exista el archivo se genera
    # como una base de datos vacia
    conn = sqlite3.connect(db['database'])

    # Crear el cursor para poder ejecutar las querys
    c = conn.cursor()

    # Obtener el path real del archivo de schema
    script_path = os.path.dirname(os.path.realpath(__file__))
    schema_path_name = os.path.join(script_path, db['schema'])

    # Crar esquema desde archivo
    c.executescript(open(schema_path_name, "r").read())

    # Para salvar los cambios realizados en la DB debemos
    # ejecutar el commit, NO olvidarse de este paso!
    conn.commit()

    # Cerrar la conexión con la base de datos
    conn.close()


def insert(time, name, heartrate):
    conn = sqlite3.connect(db['database'])
    c = conn.cursor()

    values = [time, name, heartrate]

    c.execute("""
        INSERT INTO heartrate (time, name, value)
        VALUES (?,?,?);""", values)

    conn.commit()
    # Cerrar la conexión con la base de datos
    conn.close()


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


def report(limit=0, offset=0, dict_format=False):
    # Conectarse a la base de datos
    conn = sqlite3.connect(db['database'])
    if dict_format is True:
        conn.row_factory = dict_factory
    c = conn.cursor()

    query = 'SELECT h_order.time, h_order.name, h_order.value as last_heartrate, \
             COUNT(name) as records \
             FROM (SELECT time, name, value FROM heartrate ORDER BY time) as h_order \
             GROUP BY name ORDER BY time'

    if limit > 0:
        query += ' LIMIT {}'.format(limit)
        if offset > 0:
            query += ' OFFSET {}'.format(offset)

    query += ';'

    c.execute(query)
    query_results = c.fetchall()

    # Cerrar la conexión con la base de datos
    conn.close()
    return query_results


def chart(name):
    # Conectarse a la base de datos
    conn = sqlite3.connect(db['database'])
    c = conn.cursor()

    # Busco los ultimos 250 registro a nombre de name

    c.execute('''SELECT * FROM (SELECT time FROM heartrate
                 WHERE name =? ORDER by time desc LIMIT 250)
                 ORDER by time''', [name])

    query_output = c.fetchone()
    if query_output is None:
        # No data register
        # Bug a proposito dejado para poner a prueba el traceback
        # ya que el sistema espera una tupla
        return []

    time = query_output[0]
    # Extraigo el "time" del registro 250, y busco todos los registros
    # a su nombre cuyo tiempo sea mayor o igual al de ese registro
    c.execute('''SELECT time, value FROM heartrate
                WHERE name =? AND time >=?''', [name, time])

    query_results = c.fetchall()

    # Cerrar la conexión con la base de datos
    conn.close()

    # Extraigo la informacion en listas
    time = [x[0] for x in query_results]
    heartrate = [x[1] for x in query_results]

    return time, heartrate
