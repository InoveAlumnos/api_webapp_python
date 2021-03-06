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
from datetime import datetime, timedelta

from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()

class HeartRate(db.Model):
    __tablename__ = "heartrate"
    id = db.Column(db.Integer, primary_key=True)
    time = db.Column(db.DateTime)
    name = db.Column(db.String)
    value = db.Column(db.Integer)
    
    def __repr__(self):
        return f"Paciente {self.name} ritmo cardíaco {self.value}"


def create_schema():
    # Borrar todos las tablas existentes en la base de datos
    # Esta linea puede comentarse sino se eliminar los datos
    db.drop_all()

    # Crear las tablas
    db.create_all()


def insert(time, name, heartrate):
    # Crear un nuevo registro de pulsaciones
    pulsaciones = HeartRate(time=time, name=name, value=heartrate)

    # Agregar el registro de pulsaciones a la DB
    db.session.add(pulsaciones)
    db.session.commit()


def report(limit=0, offset=0):
    json_result_list = []

    # Obtener el ultimo registor de cada paciente
    # y ademas la cantidad (count) de registros por paciente
    # Esta forma de realizar el count es más avanzada pero más óptima
    # porque de lo contrario debería realizar una query + count  por persona
    # with_entities --> especificamos que queremos que devuelva la query,
    # por defecto retorna un objeto HeartRate, nosotros estamos solicitando
    # que además devuelva la cantidad de veces que se repite cada nombre
    query = db.session.query(HeartRate).with_entities(HeartRate, db.func.count(HeartRate.name))

    # Agrupamos por paciente (name) para que solo devuelva
    # un valor por paciente
    query = query.group_by(HeartRate.name)

    # Ordenamos por fecha para obtener el ultimo registro
    query = query.order_by(HeartRate.time)

    if limit > 0:
        query = query.limit(limit)
        if offset > 0:
            query = query.offset(offset)

    for result in query:
        pulsaciones = result[0]
        cantidad = result[1]
        json_result = {}
        json_result['time'] = pulsaciones.time.strftime("%Y-%m-%d %H:%M:%S.%f")
        json_result['name'] = pulsaciones.name
        json_result['last_heartrate'] = pulsaciones.value
        json_result['records'] = cantidad
        json_result_list.append(json_result)

    return json_result_list


def chart(name):
    # Obtener los últimos 250 registros del paciente
    # ordenado por fecha, obteniedo los últimos 250 registros
    query = db.session.query(HeartRate).filter(HeartRate.name == name).order_by(HeartRate.time.desc())
    query = query.limit(250)
    query_results = query.all()

    if query_results is None or len(query_results) == 0:
        # No data register
        # Bug a proposito dejado para poner a prueba el traceback
        # ya que el sistema espera una tupla
        return []

    # De los resultados obtenidos tomamos el tiempo y las puslaciones pero
    # en el orden inverso, para tener del más viejo a la más nuevo registro
    time = [x.time.strftime("%Y-%m-%d %H:%M:%S.%f") for x in reversed(query_results)]
    heartrate = [x.value for x in reversed(query_results)]

    return time, heartrate
