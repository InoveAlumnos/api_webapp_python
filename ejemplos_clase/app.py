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
from config import config


app = Flask(__name__)

# Clave que utilizaremos para encriptar los datos
app.secret_key = "flask_session_key_inventada"

# Obtener la path de ejecución actual del script
script_path = os.path.dirname(os.path.realpath(__file__))

# Obtener los parámetros del archivo de configuración
config_path_name = os.path.join(script_path, 'config.ini')
db = config('db', config_path_name)
server = config('server', config_path_name)

heart.db = db


@app.route("/")
def index():
    try:
        # Imprimir los distintos endopoints disponibles
        result = "<h1>Bienvenido!!</h1>"
        result += "<h2>Endpoints disponibles:</h2>"
        result += "<h3>[GET] /reset --> borrar y crear la base de datos</h3>"
        result += "<h3>[GET] /pulsaciones?limit=[]&offset=[] --> mostrar últimas pulsaciones registradas (limite and offset are optional)</h3>"
        result += "<h3>[GET] /pulsaciones/tabla?limit=[]&offset=[] --> mostrar últimas pulsaciones registradas (limite and offset are optional)</h3>"
        result += "<h3>[GET] /pulsaciones/{name}/historico --> mostrar el histórico de pulsaciones de una persona</h3>"
        result += "<h3>[GET] /registro --> HTML con el formulario de registro de pulsaciones</h3>"
        result += "<h3>[POST] /registro --> ingresar nuevo registro de pulsaciones por JSON</h3>"
        result += "<h3>[GET] /login --> HTML con el formulario de ingreso de usuario</h3>"
        result += "<h3>[POST] /login --> ingresar el nombre de usuario por JSON</h3>"
        result += "<h3>[GET] /logout --> Terminar la sesion</h3>"
        result += "<h3>[GET] /user --> Paginade bienvenida del usuario</h3>"

        return(result)
    except:
        return jsonify({'trace': traceback.format_exc()})


@app.route("/reset")
def reset():
    try:
        # Borrar y crear la base de datos
        heart.create_schema()
        result = "<h3>Base de datos re-generada!</h3>"
        return (result)
    except:
        return jsonify({'trace': traceback.format_exc()})


@app.route("/pulsaciones")
def pulsaciones():
    try:
        return render_template('tabla.html')
    except:
        return jsonify({'trace': traceback.format_exc()})


@app.route("/pulsaciones/tabla")
def pulsaciones_tabla():
    try:
        # Mostrar todos los registros en formato tabla
        result = show()
        return (result)
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
            time = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
            heart.insert(time, nombre, int(pulsos))

            # Como respuesta al POST devolvemos el gráfico
            # de pulsacionesde la persona
            time, heartrate = heart.chart(nombre)

            # Crear el grafico que se desea mostrar
            fig, ax = plt.subplots(figsize=(16, 9))
            ax.plot(time, heartrate)
            ax.get_xaxis().set_visible(False)

            output = plot_to_canvas(fig)
            encoded_img = base64.encodebytes(output.getvalue())
            plt.close(fig)  # Cerramos la imagen para que no consuma memoria del sistema
            return Response(encoded_img, mimetype='image/png')
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
        # Obtener del HTTP POST JSON el nombre
        nombre = str(request.form.get('name'))

        if(nombre is None):
            # Datos ingresados incorrectos
            return Response(status=400)

        session['user'] = nombre
        return url_for('user')


@app.route("/logout")
def logout():
    try:
        # Borrar y cerrar la sesion
        session.clear()
        return redirect(url_for('login'))
    except:
        return jsonify({'trace': traceback.format_exc()})


@app.route("/user")
def user():
    try:
        # De esta forma verifico si se ha registro el nombre del usuario
        # en la sesion, en caso negativo se solicita el login
        if 'user' in session:
            nombre = session['user']
            return f'<h1>Hola {nombre}</h1>'
        else:
            return redirect(url_for('login'))
    except:
        return jsonify({'trace': traceback.format_exc()})


def show(show_type='json'):

    # Obtener de la query string los valores de limit y offset
    limit_str = str(request.args.get('limit'))
    offset_str = str(request.args.get('offset'))

    limit = 0
    offset = 0

    if(limit_str is not None) and (limit_str.isdigit()):
        limit = int(limit_str)

    if(offset_str is not None) and (offset_str.isdigit()):
        offset = int(offset_str)

    if show_type == 'json':
        data = heart.report(limit=limit, offset=offset, dict_format=True)
        return jsonify(data)
    elif show_type == 'table':
        data = heart.report(limit=limit, offset=offset)
        return html_table(data)
    else:
        data = heart.report(limit=limit, offset=offset, dict_format=True)
        return jsonify(data)


def html_table(data):

    # Tabla HTML, header y formato
    result = '<table border="1">'
    result += '<thead cellpadding="1.0" cellspacing="1.0">'
    result += '<tr>'
    result += '<th>Nombre</th>'
    result += '<th>Fecha</th>'
    result += '<th>Último registro</th>'
    result += '<th>Nº de registros</th>'
    result += '</tr>'

    for row in data:
        # Fila de una tabla HTML
        result += '<tr>'
        result += '<td>' + str(row[0]) + '</td>'
        result += '<td>' + str(row[1]) + '</td>'
        result += '<td>' + str(row[2]) + '</td>'
        result += '<td>' + str(row[3]) + '</td>'
        result += '</tr>'

    # Fin de la tabla HTML
    result += '</thead cellpadding="0" cellspacing="0" >'
    result += '</table>'

    return result


def plot_to_canvas(fig):
    # Convertir ese grafico en una imagen para enviar por HTTP
    # y mostrar en el HTML
    output = io.BytesIO()
    FigureCanvas(fig).print_png(output)
    return output


if __name__ == '__main__':
    print('Inove@Monitor Cardíaco start!')

    app.run(host=server['host'],
            port=server['port'],
            debug=True)
