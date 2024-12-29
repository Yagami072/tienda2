from app import app, db
from models import User, Product, Category
from werkzeug.security import generate_password_hash
import os

def init_db():
    with app.app_context():
        # Recrear todas las tablas
        db.drop_all()
        db.create_all()
        
        print("Iniciando configuración de la base de datos...")

        # Crear categorías de ejemplo
        categories = [
            Category(
                name='Categoría 1',
                description='Descripción de la categoría 1',
                image='category1.jpg',
                order=1,
                is_active=True
            ),
            Category(
                name='Categoría 2',
                description='Descripción de la categoría 2',
                image='category2.jpg',
                order=2,
                is_active=True
            ),
            Category(
                name='Categoría 3',
                description='Descripción de la categoría 3',
                image='category3.jpg',
                order=3,
                is_active=True
            )
        ]
        
        for category in categories:
            db.session.add(category)

        # Crear usuario administrador
        admin = User(
            username='admin',
            email='admin@example.com',
            password=generate_password_hash('admin123'),
            first_name='Admin',
            last_name='Sistema',
            is_admin=True,
            is_verified=True
        )
        
        # Crear productos de ejemplo
        products = [
            Product(
                name='Producto 1',
                price=19.99,
                description='Descripción del producto 1',
                image='product1.jpg',
                image_hover='product1-hover.jpg'
            ),
            Product(
                name='Producto 2',
                price=29.99,
                description='Descripción del producto 2',
                image='product2.jpg',
                image_hover='product2-hover.jpg'
            )
        ]
        
        try:
            # Agregar admin
            db.session.add(admin)
            
            # Agregar productos
            for product in products:
                db.session.add(product)
            
            db.session.commit()
            print("Base de datos inicializada correctamente!")
            
        except Exception as e:
            print(f"Error: {e}")
            db.session.rollback()

if __name__ == '__main__':
    init_db()
