from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, Product, Cart, Category
from dotenv import load_dotenv
import os
from flask_migrate import Migrate

load_dotenv()

app = Flask(__name__)

# Configuración para PythonAnywhere
app.config['SECRET_KEY'] = 'tu_clave_secreta_aqui'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://tuUsuario:tuContraseña@tuUsuario.mysql.pythonanywhere-services.com/tuUsuario$tienda'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = '/home/tuUsuario/tienda2/static/uploads'

db.init_app(app)
migrate = Migrate(app, db)

with app.app_context():
    db.create_all()

# Importar rutas después de crear la aplicación
from app import *

if __name__ == '__main__':
    app.run()
