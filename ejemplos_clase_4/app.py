'''
Flask [Python]
Ejemplos de clase

Autor: Inove Coding School
Version: 2.0

Descripcion:
Se utiliza Flask para crear un WebServer que levanta los datos de
las personas que registran su ritmo cardíaco.

Ingresar a la siguiente URL para ver los endpoints disponibles
http://127.0.0.1:5000/
'''

# Realizar HTTP POST con --> post.py

from datetime import datetime

import traceback
from flask import Flask, request, jsonify, render_template, Response, redirect, url_for

# Importar archivo con funciones de ayuda
import utils

# Crear el server Flask
app = Flask(__name__)

# Base de datos
from flask_sqlalchemy import SQLAlchemy

# Indicamos al sistema (app) de donde leer la base de datos
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///corazon.db"

# Asociamos nuestro controlador de la base de datos con la aplicacion
db = SQLAlchemy()
db.init_app(app)

# ------------ Tablas de la DB ----------------- #
class Pulsaciones(db.Model):
    __tablename__ = "pulsaciones"
    id = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.DateTime)
    nombre = db.Column(db.String)
    valor = db.Column(db.Integer)
    
    def __repr__(self):
        return f"Paciente {self.nombre} ritmo cardíaco {self.valor}"


# ------------ Rutas o endpoints ----------------- #
# Ruta que se ingresa por la ULR 127.0.0.1:5000
@app.route("/")
def index():
    try:
        # Imprimir los distintos endopoints disponibles
        # Renderizar el temaplate HTML index.html
        print("Renderizar index.html")
        return render_template('index.html')
    except:
        return jsonify({'trace': traceback.format_exc()})


# Ruta que se ingresa por la ULR 127.0.0.1:5000/pulsaciones
@app.route("/pulsaciones")
def pulsaciones():
    try:
        # Obtener de la query string los valores de limit y offset
        limit_str = str(request.args.get('limit'))
        offset_str = str(request.args.get('offset'))

        limit = 0
        offset = 0

        if(limit_str is not None) and (limit_str.isdigit()):
            limit = int(limit_str)

        if(offset_str is not None) and (offset_str.isdigit()):
            offset = int(offset_str)

        # Obtener todos los pacientes:
        query = db.session.query(Pulsaciones)     

        # Ordenamos por fecha para obtener primero el ultimo registro
        query = query.order_by(Pulsaciones.fecha.desc())     

        # Si se indica limit, debemos
        # limitar la cantidad de pacientes a mostrar
        if limit > 0:
            query = query.limit(limit)
            if offset > 0:
                query = query.offset(offset)

        # Obtener el reporte
        data = []

        for paciente in query:
            json_result = {}
            json_result['fecha'] = paciente.fecha.strftime("%Y-%m-%d %H:%M:%S.%f")
            json_result['nombre'] = paciente.nombre
            json_result['pulso'] = paciente.valor
            data.append(json_result)

        print("Pulsaciones almacenadas (historico):")
        print(data)

        # Renderizar el temaplate HTML pulsaciones.html
        print("Renderizar tabla.html")
        return render_template('tabla.html', data=data)
    except:
        return jsonify({'trace': traceback.format_exc()})


# Ruta que se ingresa por la ULR 127.0.0.1:5000/pulsaciones/<nombre>
@app.route("/pulsaciones/<nombre>")
def pulsaciones_historico(nombre):
    try:
        # Obtener el nombre en minúscula
        nombre = nombre.lower()
        # Obtener el historial de la persona de la DB 
        print("Obtener gráfico de la persona", nombre)       

        query = db.session.query(Pulsaciones).filter(Pulsaciones.nombre == nombre).order_by(Pulsaciones.fecha.desc())
        query = query.limit(250)
        query_results = query.all()

        if query_results is None or len(query_results) == 0:
            # No data registros
            # Bug a proposito dejado para poner a prueba el traceback
            # ya que el sistema espera una tupla
            return []

        # De los resultados obtenidos tomamos el tiempo y las puslaciones pero
        # en el orden inverso (revsersed), para tener del más viejo a la más nuevo registro
        fechas = [x.fecha.strftime("%Y-%m-%d %H:%M:%S.%f") for x in reversed(query_results)]
        pulsos = [x.valor for x in reversed(query_results)]

        # Transformar los datos en una imagen HTML con matplotlib
        image_html = utils.graficar(fechas, pulsos)
        return Response(image_html.getvalue(), mimetype='image/png')
    except:
        return jsonify({'trace': traceback.format_exc()})


# Ruta que se ingresa por la ULR 127.0.0.1:5000/registro
@app.route("/registro", methods=['GET', 'POST'])
def registro():
    if request.method == 'GET':
        # Si entré por "GET" es porque acabo de cargar la página
        try:
            # Renderizar el temaplate HTML registro.html
            print("Renderizar registro.html")
            return render_template('registro.html')
        except:
            return jsonify({'trace': traceback.format_exc()})

    if request.method == 'POST':
        try:
            # Obtener del HTTP POST JSON el nombre (en minisculas) y los pulsos
            nombre = str(request.form.get('nombre')).lower()
            pulso = str(request.form.get('pulso'))

            if(nombre is None or pulso is None or pulso.isdigit() is False):
                # Datos ingresados incorrectos
                return Response(status=400)
            
            # Obtener la fecha y hora actual
            fecha = datetime.now()

            # Crear un nuevo registro de pulsaciones
            pulsaciones = Pulsaciones(fecha=fecha, nombre=nombre, valor=int(pulso))

            # Agregar el registro de pulsaciones a la DB
            db.session.add(pulsaciones)
            db.session.commit()

            # Como respuesta al POST devolvemos la tabla de valores
            return redirect(url_for('pulsaciones'))
        except:
            return jsonify({'trace': traceback.format_exc()})


# Este método se ejecutará solo una vez
# la primera vez que ingresemos a un endpoint
@app.before_first_request
def before_first_request_func():
    # Crear aquí todas las bases de datos
    db.create_all()
    print("Base de datos generada")


if __name__ == '__main__':
    print('Inove@Server start!')

    # Lanzar server
    app.run(host="127.0.0.1", port=5000)