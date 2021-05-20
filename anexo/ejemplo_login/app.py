#!/usr/bin/env python
'''
API Monitor cardíaco
---------------------------
Autor: Inove Coding School
Version: 1.0
 
Descripcion:
Se utiliza Flask para crear un WebServer que levanta los datos de
las personas que registran su ritmo cardíaco.

Ejecución: Lanzar el programa y abrir en un navegador la siguiente dirección URL
NOTA: Si es la primera vez que se lanza este programa crear la base de datos
entrando a la siguiente URL
http://127.0.0.1:5000/reset

Ingresar a la siguiente URL para ver los endpoints disponibles
http://127.0.0.1:5000/
'''

__author__ = "Inove Coding School"
__email__ = "INFO@INOVE.COM.AR"
__version__ = "1.0"

import traceback
import io
import sys
import os
import base64
import json
import sqlite3
from datetime import datetime, timedelta

import numpy as np
from flask import Flask, request, jsonify, render_template, Response, redirect , url_for, session
import matplotlib
matplotlib.use('Agg')   # For multi thread, non-interactive backend (avoid run in main loop)
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.image as mpimg

import heart
import user

from config import config

# Crear el server Flask
app = Flask(__name__)

# Clave que utilizaremos para encriptar los datos
app.secret_key = "flask_session_key_inventada"

# Obtener la path de ejecución actual del script
script_path = os.path.dirname(os.path.realpath(__file__))

# Obtener los parámetros del archivo de configuración
config_path_name = os.path.join(script_path, 'config.ini')
db_config = config('db', config_path_name)
server_config = config('server', config_path_name)

# Indicamos al sistema (app) de donde leer la base de datos
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_config['database']}"
# Asociamos nuestro controlador de la base de datos con la aplicacion
heart.db.init_app(app)
user.db.init_app(app)

# Ruta que se ingresa por la ULR 127.0.0.1:5000
@app.route("/")
def index():
    try:

        if os.path.isfile(db_config['database']) == False:
            # Sino existe la base de datos la creo
            heart.create_schema()
            user.create_schema()

        # En el futuro se podria realizar una página de bienvenida
        return redirect(url_for('pulsaciones'))
    except:
        return jsonify({'trace': traceback.format_exc()})

@app.route("/api")
def api():
    try:
        # Imprimir los distintos endopoints disponibles
        api_data = "<h2>Endpoints disponibles:</h2>"
        api_data += "<h3>[GET] /reset --> borrar y crear la base de datos</h3>"
        api_data += "<h3>[GET] /pulsaciones?limit=[]&offset=[] --> mostrar últimas pulsaciones registradas (limite and offset are optional)</h3>"
        api_data += "<h3>[GET] /pulsaciones/tabla?limit=[]&offset=[] --> mostrar últimas pulsaciones registradas (limite and offset are optional)</h3>"
        api_data += "<h3>[GET] /pulsaciones/{name}/historico --> mostrar el histórico de pulsaciones de una persona</h3>"
        api_data += "<h3>[GET] /registro --> HTML con el formulario de registro de pulsaciones</h3>"
        api_data += "<h3>[POST] /registro --> ingresar nuevo registro de pulsaciones por JSON</h3>"
        api_data += "<h3>[GET] /login --> HTML con el formulario de ingreso de usuario</h3>"
        api_data += "<h3>[POST] /login --> ingresar el nombre de usuario por JSON</h3>"
        api_data += "<h3>[GET] /logout --> Terminar la sesion</h3>"
        api_data += "<h3>[GET] /usuario --> Paginade bienvenida del usuario</h3>"
        return render_template('api.html', api_html=api_data)
    except:
        return jsonify({'trace': traceback.format_exc()})


@app.route("/reset")
def reset():
    try:
        # Borrar y crear la base de datos
        heart.create_schema()
        user.create_schema()
        result = "<h3>Base de datos re-generada!</h3>"
        return (result)
    except:
        return jsonify({'trace': traceback.format_exc()})


@app.route("/pulsaciones")
def pulsaciones():
    try:
        #data = show(show_type='table')
        # Obtener de la query string los valores de limit y offset
        limit_str = str(request.args.get('limit'))
        offset_str = str(request.args.get('offset'))

        limit = 0
        offset = 0

        if(limit_str is not None) and (limit_str.isdigit()):
            limit = int(limit_str)

        if(offset_str is not None) and (offset_str.isdigit()):
            offset = int(offset_str)

        # Obtener el reporte
        data = heart.report(limit=limit, offset=offset)

        return render_template('tabla.html', data=data)
    except:
        return jsonify({'trace': traceback.format_exc()})


@app.route("/pulsaciones/<name>/historico")
def pulsaciones_historico(name):
    try:
        # Obtener el historial de la persona
        time, heartrate = heart.chart(name)

        # Crear el grafico que se desea mostrar
        fig, ax = plt.subplots(figsize=(16, 9))
        ax.plot(time, heartrate)
        ax.get_xaxis().set_visible(False)

        output = plot_to_canvas(fig)
        plt.close(fig)  # Cerramos la imagen para que no consuma memoria del sistema
        return Response(output.getvalue(), mimetype='image/png')
    except:
        return jsonify({'trace': traceback.format_exc()})


@app.route("/registro", methods=['GET', 'POST'])
def registro():
    if request.method == 'GET':
        # Si entré por "GET" es porque acabo de cargar la página
        try:
            return render_template('registro.html')
        except:
            return jsonify({'trace': traceback.format_exc()})

    if request.method == 'POST':
        try:
            # Obtener del HTTP POST JSON los pulsos
            nombre = str(request.form.get('name'))
            pulsos = str(request.form.get('heartrate'))

            if(nombre is None or pulsos is None or pulsos.isdigit() is False):
                # Datos ingresados incorrectos
                return Response(status=400)
            time = datetime.now()
            heart.insert(time, nombre, int(pulsos))

            # Como respuesta al POST devolvemos la tabla de valores
            return redirect(url_for('pulsaciones'))
        except:
            return jsonify({'trace': traceback.format_exc()})


@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        # Si entré por "GET" es porque acabo de cargar la página
        try:
            return render_template('login.html')
        except:
            return jsonify({'trace': traceback.format_exc()})

    if request.method == 'POST':
        name = str(request.form.get('name'))
        password = request.form.get('password')

        user_validated = user.check_password(name, password)

        if user_validated is False:
            # Datos ingresados incorrectos
            return render_template('login.html')

        session['user'] = name
        return redirect(url_for('usuario'))


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'GET':
        # Si entré por "GET" es porque acabo de cargar la página
        try:
            return render_template('signup.html')
        except:
            return jsonify({'trace': traceback.format_exc()})

    if request.method == 'POST':
        name = str(request.form.get('name'))
        email = request.form.get('email')
        password = request.form.get('password')
            
        user_id = user.insert(name, email, password)
        if user_id is not None:
            return render_template('login.html')
        else:
            # Datos ingresados incorrectos
            return render_template('signup.html')


@app.route("/logout")
def logout():
    try:
        # Borrar y cerrar la sesion
        session.clear()
        return redirect(url_for('login'))
    except:
        return jsonify({'trace': traceback.format_exc()})


@app.route("/usuario")
def usuario():
    try:
        # De esta forma verifico si se ha registro el nombre del usuario
        # en la sesion, en caso negativo se solicita el login
        if 'user' in session:
            name = session['user']
            return render_template('usuario.html', name=name)
        else:
            return redirect(url_for('login'))
    except:
        return jsonify({'trace': traceback.format_exc()})


def plot_to_canvas(fig):
    # Convertir ese grafico en una imagen para enviar por HTTP
    # y mostrar en el HTML
    output = io.BytesIO()
    FigureCanvas(fig).print_png(output)
    return output


if __name__ == '__main__':
    print('Inove@Monitor Cardíaco start!')

    app.run(host=server_config['host'],
            port=server_config['port'],
            debug=True)
