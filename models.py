from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'user'
    __table_args__ = (
        db.UniqueConstraint('username', name='uq_user_username'),
        db.UniqueConstraint('email', name='uq_user_email'),
        db.UniqueConstraint('verification_token', name='uq_user_verification_token'),
    )
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(80))
    last_name = db.Column(db.String(80))
    phone = db.Column(db.String(20))
    is_admin = db.Column(db.Boolean, default=False)
    is_verified = db.Column(db.Boolean, default=False)
    verification_token = db.Column(db.String(100), unique=True)
    token_expiry = db.Column(db.DateTime)
    cart_items = db.relationship('Cart', backref='user', lazy=True)

class Product(db.Model):
    __tablename__ = 'product'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text)
    specifications = db.Column(db.Text, nullable=True)  # Nueva columna
    additional_images = db.Column(db.Text, nullable=True)  # Nueva columna
    image = db.Column(db.String(255))
    image_hover = db.Column(db.String(255))
    cart_items = db.relationship('Cart', backref='product', lazy=True)

class Cart(db.Model):
    __tablename__ = 'cart'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, 
                       db.ForeignKey('user.id', name='fk_cart_user', ondelete='CASCADE'),
                       nullable=False)
    product_id = db.Column(db.Integer, 
                          db.ForeignKey('product.id', name='fk_cart_product', ondelete='CASCADE'),
                          nullable=False)
    quantity = db.Column(db.Integer, default=1)
    date_added = db.Column(db.DateTime, default=datetime.utcnow)

class Category(db.Model):
    __tablename__ = 'category'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    image = db.Column(db.String(255))
    description = db.Column(db.Text)
    order = db.Column(db.Integer, default=0)  # Para ordenar las categorías
    is_active = db.Column(db.Boolean, default=True)
