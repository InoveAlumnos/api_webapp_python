#!/usr/bin/env python
'''
API Monitor cardíaco
---------------------------
Autor: Inove Coding School
Version: 1.0
 
Descripcion:
Se utiliza Flask para crear un WebServer que levanta los datos de
las personas que registran su ritmo cardíaco.

Ingresar a la siguiente URL para ver los gráficos de ejemplo
http://127.0.0.1:5000/
'''

__author__ = "Inove Coding School"
__email__ = "INFO@INOVE.COM.AR"
__version__ = "1.0"

import traceback
import io
import sys
import os
import json

from flask import Flask, request, jsonify, render_template, Response, redirect , url_for, session

from graficos import *

# Crear el server Flask
app = Flask(__name__)

# Ruta que se ingresa por la ULR 127.0.0.1:5000
@app.route("/")
def index():
    try:
        # Imprimir los distintos gráficos disponibles       
        return render_template('index.html')
    except:
        return jsonify({'trace': traceback.format_exc()})


@app.route("/grafico/<id>")
def grafico(id):
    try:
        # Según el gráfico deseado se llama a una
        # u otra función dentro de graficos.py
        id = int(id)
        if id == 1:
            plot_div = plot1d()
        if id == 2:
            plot_div = plot2d()
        if id == 3:
            plot_div = plot3d()
        # Se renderiza el html "plot" junto con los datos
        return render_template('plot.html', plot=plot_div)

    except:
        return jsonify({'trace': traceback.format_exc()})


if __name__ == '__main__':
    print('Inove Plotly!')
    app.run(host="127.0.0.1", port=5000, debug=True)
