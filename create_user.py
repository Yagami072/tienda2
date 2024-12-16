from app import app, db, User
from werkzeug.security import generate_password_hash

print("Iniciando creación de usuarios...")

with app.app_context():
    try:
        # Crear las tablas si no existen
        db.create_all()
        
        # Crear usuario cliente
        cliente = User(
            username='cliente',
            password=generate_password_hash('cliente123'),
            is_admin=False
        )
        db.session.add(cliente)
        print("Usuario cliente creado")
        
        # Crear usuario admin
        admin = User(
            username='admin',
            password=generate_password_hash('admin123'),
            is_admin=True
        )
        db.session.add(admin)
        print("Usuario admin creado")
        
        # Guardar los cambios
        db.session.commit()
        
        print("\n=== Usuarios creados exitosamente ===")
        print("\nCredenciales de cliente:")
        print("Usuario: cliente")
        print("Contraseña: cliente123")
        print("\nCredenciales de administrador:")
        print("Usuario: admin")
        print("Contraseña: admin123")
        
    except Exception as e:
        print(f"Error: {str(e)}")
