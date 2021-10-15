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
from flask import Flask, request, jsonify, render_template, Response, redirect, url_for

# Crear el server Flask
app = Flask(__name__)

# Ruta que se ingresa por la ULR 127.0.0.1:5000
@app.route("/")
def index():
    try:
        # Renderizar el temaplate HTML index.html
        print("Renderizar index.html")
        return render_template('index.html')
    except:
        return jsonify({'trace': traceback.format_exc()})


# Ruta que se ingresa por la ULR 127.0.0.1:5000/user/<nombre>
@app.route("/user/<name>")
def user_name(name):
    try:
        # Renderizar el temaplate HTML user.html
        print("Renderizar user.html con le nombre", name)
        return render_template('user.html', name=name)
    except:
        return jsonify({'trace': traceback.format_exc()})


# Ruta que se ingresa por la ULR 127.0.0.1:5000/login/
@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        # Si entré por "GET" es porque acabo de cargar la página
        try:
            # Renderizar el temaplate HTML login.html para registrar el usuario
            return render_template('login.html')
        except:
            return jsonify({'trace': traceback.format_exc()})

    if request.method == 'POST':
        # Se captura la petición de registrar un usuario
        # Obtener del HTTP POST JSON el nombre
        name = str(request.form.get('name'))

        if(name is None):
            # Datos ingresados incorrectos
            return Response(status=400)

        # Redireccionar el servidor a la URL del endpoint user_name
        # con el campo de "name" que se capturó en el POST
        return redirect(url_for('user_name', name=name))

if __name__ == '__main__':
    print('Inove@Server start!')

    # Lanzar server
    app.run(host="127.0.0.1", port=5000)
