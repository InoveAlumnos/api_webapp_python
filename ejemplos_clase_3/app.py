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

import traceback
from flask import Flask, request, jsonify, render_template, Response, redirect

# Crear el server Flask
app = Flask(__name__)

# Variable global para poner a prueba el método [GET]
# IMPORTANTE: Esta no es una buena forma de manejar datos,
# se debe usar base de dato (se verá en otro ejemplo más adelante)
base_de_datos = [
    {
        "name": "Inove",
        "heartrate": 80
    },
    {
        "name": "Python",
        "heartrate": 65
    },
    {
        "name": "Max",
        "heartrate": 110
    }
]

# Ruta que se ingresa por la ULR 127.0.0.1:5000
@app.route("/")
def index():
    try:
        # Renderizar el temaplate HTML index.html
        print("Renderizar index.html")
        return render_template('index.html')
    except:
        return jsonify({'trace': traceback.format_exc()})


# Ruta que se ingresa por la ULR 127.0.0.1:5000/pulsaciones
@app.route("/pulsaciones")
def pulsaciones():
    try:
        data = []

        limit_str = str(request.args.get('limit'))
        offset_str = str(request.args.get('offset'))

        limit = len(base_de_datos)
        offset = 0

        if(limit_str is not None) and (limit_str.isdigit()):
            limit = int(limit_str)

        if(offset_str is not None) and (offset_str.isdigit()):
            offset = int(offset_str)

        # Obtener el reporte
        inicio = offset
        fin = offset + limit
        data = base_de_datos[inicio:fin]

        print("Dato solicitados")
        print(data)

        # Renderizar el temaplate HTML pulsaciones.html
        print("Renderizar tabla.html")
        return render_template('tabla.html', data=data)
    except:
        return jsonify({'trace': traceback.format_exc()})

if __name__ == '__main__':
    print('Inove@Server start!')

    # Lanzar server
    app.run(host="127.0.0.1", port=5000)
