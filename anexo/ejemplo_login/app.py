#!/usr/bin/env python
'''
API Monitor cardíaco
---------------------------
Autor: Inove Coding School
Version: 2.0
 
Descripcion:
Se utiliza Flask para crear un WebServer que levanta los datos de
las personas que registran su ritmo cardíaco.

Ingresar a la siguiente URL para ver los endpoints disponibles
http://127.0.0.1:5000/
'''

__author__ = "Inove Coding School"
__email__ = "INFO@INOVE.COM.AR"
__version__ = "2.0"

import traceback
import io
import sys
import os
import base64
import json
from datetime import datetime, timedelta

import numpy as np
from flask import Flask, request, jsonify, render_template, Response, redirect , url_for, session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user

import utils
import heart
import user

# Crear el server Flask
app = Flask(__name__)

# Clave que utilizaremos para encriptar los datos
app.secret_key = "flask_session_key_inventada"

# Configurar el sistema de login
# Referencia:
# https://www.digitalocean.com/community/tutorials/how-to-add-authentication-to-your-app-with-flask-login-es
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return user.User.query.get(int(user_id))

# Indicamos al sistema (app) de donde leer la base de datos
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///heart.db"
# Asociamos nuestro controlador de la base de datos con la aplicacion
heart.db.init_app(app)
user.db.init_app(app)

# Ruta que se ingresa por la ULR 127.0.0.1:5000
@app.route("/")
def index():
    try:
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
        name = name.lower()
        # Obtener el historial de la persona de la DB 
        print("Obtener gráfico de la persona", name)       
        time, heartrate = heart.chart(name)

        # Transformar los datos en una imagen HTML con matplotlib
        image_html = utils.graficar(time, heartrate)
        return Response(image_html.getvalue(), mimetype='image/png')
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
            nombre = str(request.form.get('name')).lower()
            pulsos = str(request.form.get('heartrate'))

            if(nombre is None or pulsos is None or pulsos.isdigit() is False):
                # Datos ingresados incorrectos
                return Response(status=400)
            time = datetime.now()

            print("Registrar persona", nombre, "con pulsaciones", pulsos)
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

        usr = user.get_user(name)
        if usr is None:
            # No existe el user
            return render_template('login.html')

        user_validated = user.check_password(name, password)

        if user_validated is False:
            # Datos ingresados incorrectos
            return render_template('login.html')

        login_user(usr)
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
            
        usr = user.insert(name, email, password)
        if usr is not None:
            return render_template('login.html')
        else:
            # Datos ingresados incorrectos
            return render_template('signup.html')


@app.route("/logout")
@login_required
def logout():
    try:
        # Deslogarse
        logout_user()
        return redirect(url_for('login'))
    except:
        return jsonify({'trace': traceback.format_exc()})


@app.route("/usuario")
@login_required
def usuario():
    try:
        # Si el usuario esta logeado se muestra su nombre
        return render_template('usuario.html', name=current_user.name)
    except:
        return jsonify({'trace': traceback.format_exc()})


# Este método se ejecutará solo una vez
# la primera vez que ingresemos a un endpoint
@app.before_first_request
def before_first_request_func():
    # Crear aquí todas las bases de datos
    heart.db.create_all()
    user.db.create_all()
    print("Base de datos generada")


if __name__ == '__main__':
    print('Inove@Monitor Cardíaco start!')

    # Lanzar server
    app.run(host="127.0.0.1", port=5000)
