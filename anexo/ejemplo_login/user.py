#!/usr/bin/env python
'''
Usuario DB manager
---------------------------
Autor: Inove Coding School
Version: 1.1

Descripcion:
Programa creado para administrar la base de datos de registro
de usuarios
'''

__author__ = "Inove Coding School"
__email__ = "alumnos@inove.com.ar"
__version__ = "2.0"

import os
from datetime import datetime, timedelta

# pip3 install Flask-Login
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from models import db

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True) # primary keys are required by SQLAlchemy
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(1000))


def insert(name, email, password):
    # Verificar si ya existe el usuario
    user = User.query.filter_by(name=name).first()

    # Si el usuario existe no puedo crearlo
    if user:
        return None

    # create a new user with the form data. Hash the password so the plaintext version isn't saved.
    new_user = User(email=email, name=name, password=generate_password_hash(password, method='sha256'))

    # add the new user to the database
    db.session.add(new_user)
    db.session.commit()

    return new_user

def get_user(name):
    return User.query.filter_by(name=name).first()

def check_password(name, password):
    user = User.query.filter_by(name=name).first()

    # Verificamos si el usuario existe
    if not user:
        return False

    # Verificamos la password
    if check_password_hash(user.password, password):
        return True
    else:
        return False


