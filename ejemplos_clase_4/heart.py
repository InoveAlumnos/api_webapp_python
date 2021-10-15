'''
Heart DB manager
---------------------------
Autor: Inove Coding School
Version: 1.1

Descripcion:
Programa creado para administrar la base de datos de registro
de pulsaciones de personas
'''

from datetime import datetime

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()

# NOTA: Por un bug en el linter de Visual verán problemas con
# el tipo de dato "db". No le den importancia

class HeartRate(db.Model):
    __tablename__ = "heartrate"
    id = db.Column(db.Integer, primary_key=True)
    time = db.Column(db.DateTime)
    name = db.Column(db.String)
    value = db.Column(db.Integer)
    
    def __repr__(self):
        return f"Paciente {self.name} ritmo cardíaco {self.value}"


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


if __name__ == "__main__":
    print("Test del modulo heart.py")

    # Crear una aplicación Flask para testing
    # y una base de datos fantasma (auxiliar o dummy)
    # Referencia:
    # https://stackoverflow.com/questions/17791571/how-can-i-test-a-flask-application-which-uses-sqlalchemy
    app = Flask(__name__)
    app.config['TESTING'] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///testdatabase.db"
    # Bindear la DB con nuestra app Flask
    db.init_app(app)
    app.app_context().push()

    db.create_all()

    # Aquí se puede ensayar todo lo que necesitemos con nuestra DB

    # Test "insert"
    # Generamos datos inventados y probamos si funciona correctamente
    # la función insert
    insert(time=datetime.now(), name="Inove", heartrate=70)

    # Test "report"
    # Ahora que nuestra base de datos tiene datos, podemos probar
    # las funciones que acceden a esos datos y ver si funcionan correctamente
    datos = report()
    print(datos)

    db.session.remove()
    db.drop_all()