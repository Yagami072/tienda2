from app import app, db, User
from werkzeug.security import generate_password_hash
import os

# Asegurarse de que la base de datos existe
if os.path.exists('instance/tienda.db'):
    os.remove('instance/tienda.db')
    print("Base de datos anterior eliminada")

with app.app_context():
    try:
        # Crear las tablas
        db.create_all()
        print("Base de datos creada")

        # Crear usuario admin
        admin_user = User(
            username='admin',
            password=generate_password_hash('admin123'),
            is_admin=True
        )
        db.session.add(admin_user)
        db.session.commit()
        print("\nUsuario admin creado exitosamente:")
        print("Username: admin")
        print("Password: admin123")
        
        # Verificar la creación
        admin = User.query.filter_by(username='admin').first()
        if admin:
            print("\nVerificación exitosa:")
            print(f"- Usuario encontrado en la base de datos")
            print(f"- Es administrador: {admin.is_admin}")
            print(f"- ID del usuario: {admin.id}")
        else:
            print("ERROR: No se pudo encontrar el usuario después de crearlo")
            
    except Exception as e:
        print(f"Error: {str(e)}")
