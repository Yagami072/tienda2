from app import app, db, User
from werkzeug.security import generate_password_hash
import os
import sys

def init_database():
    base_dir = os.path.abspath(os.path.dirname(__file__))
    db_path = os.path.join(base_dir, 'instance', 'tienda.db')
    
    print("Iniciando configuración de la base de datos...")
    
    # Eliminar base de datos existente
    if os.path.exists(db_path):
        try:
            os.remove(db_path)
            print("Base de datos anterior eliminada")
        except PermissionError:
            print("Error: Cierra todas las aplicaciones y vuelve a intentar")
            sys.exit(1)

    with app.app_context():
        try:
            # Crear tablas
            db.create_all()
            print("Tablas creadas en la base de datos")

            # Crear usuarios
            users_to_create = [
                {
                    'username': 'admin',
                    'password': 'admin123',
                    'is_admin': True
                },
                {
                    'username': 'cliente',
                    'password': 'cliente123',
                    'is_admin': False
                }
            ]

            for user_data in users_to_create:
                user = User(
                    username=user_data['username'],
                    password=generate_password_hash(user_data['password']),
                    is_admin=user_data['is_admin']
                )
                db.session.add(user)
                print(f"\nCreando usuario: {user_data['username']}")
                print(f"Es administrador: {user_data['is_admin']}")

            db.session.commit()
            
            # Verificar la creación
            for user_data in users_to_create:
                user = User.query.filter_by(username=user_data['username']).first()
                if user:
                    print(f"\nUsuario {user_data['username']} creado exitosamente:")
                    print(f"ID: {user.id}")
                    print(f"Username: {user.username}")
                    print(f"Password: {user_data['password']}")
                    print(f"Es admin: {user.is_admin}")
                else:
                    print(f"\n¡Error! No se pudo crear el usuario {user_data['username']}")

        except Exception as e:
            print(f"Error: {str(e)}")
            sys.exit(1)

if __name__ == "__main__":
    init_database()
    print("\n¡Configuración completada!")
