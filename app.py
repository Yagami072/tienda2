from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os

# Crear el directorio de uploads si no existe
if not os.path.exists('static/uploads'):
    os.makedirs('static/uploads')

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tienda.db'
app.config['UPLOAD_FOLDER'] = 'static/uploads'
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    image = db.Column(db.String(200))
    description = db.Column(db.Text)

class Cart(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, default=1)

@app.route('/')
def index():
    products = Product.query.all()
    return render_template('index.html', products=products)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        try:
            username = request.form.get('username')
            password = request.form.get('password')
            
            print(f"\nIntento de login:")
            print(f"Username recibido: {username}")
            
            user = User.query.filter_by(username=username).first()
            
            if user:
                print(f"Usuario encontrado en BD - ID: {user.id}")
                if check_password_hash(user.password, password):
                    session['user_id'] = user.id
                    session['is_admin'] = user.is_admin
                    print("Login exitoso")
                    flash('Inicio de sesión exitoso', 'success')
                    return redirect(url_for('admin' if user.is_admin else 'index'))
                else:
                    print("Contraseña incorrecta")
                    flash('Contraseña incorrecta')
            else:
                print(f"Usuario '{username}' no encontrado")
                flash('Usuario no encontrado')
        except Exception as e:
            print(f"Error en login: {str(e)}")
            flash(f'Error: {str(e)}')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/admin')
def admin():
    if not session.get('is_admin'):
        return redirect(url_for('login'))
    products = Product.query.all()
    return render_template('admin.html', products=products)

@app.route('/add_product', methods=['GET', 'POST'])
def add_product():
    if not session.get('is_admin'):
        return redirect(url_for('login'))
    if request.method == 'POST':
        file = request.files['image']
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        
        product = Product(
            name=request.form['name'],
            price=float(request.form['price']),
            image=filename,
            description=request.form['description']
        )
        db.session.add(product)
        db.session.commit()
        return redirect(url_for('admin'))
    return render_template('add_product.html')

@app.route('/edit_product/<int:id>', methods=['GET', 'POST'])
def edit_product(id):
    if not session.get('is_admin'):
        return redirect(url_for('login'))
    
    product = Product.query.get_or_404(id)
    
    if request.method == 'POST':
        product.name = request.form['name']
        product.price = float(request.form['price'])
        product.description = request.form['description']
        
        if 'image' in request.files and request.files['image'].filename:
            file = request.files['image']
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            product.image = filename
            
        db.session.commit()
        flash('Producto actualizado exitosamente', 'success')
        return redirect(url_for('admin'))
        
    return render_template('edit_product.html', product=product)

@app.route('/delete_product/<int:id>', methods=['POST'])
def delete_product(id):
    if not session.get('is_admin'):
        return redirect(url_for('login'))
    
    product = Product.query.get_or_404(id)
    
    # Eliminar la imagen si existe
    if product.image:
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], product.image)
        if os.path.exists(image_path):
            os.remove(image_path)
    
    db.session.delete(product)
    db.session.commit()
    flash('Producto eliminado exitosamente', 'success')
    return redirect(url_for('admin'))

@app.route('/add_to_cart/<int:product_id>', methods=['POST'])
def add_to_cart(product_id):
    if not session.get('user_id'):
        flash('Por favor inicia sesión para comprar', 'warning')
        return redirect(url_for('login'))
    
    cart_item = Cart.query.filter_by(
        user_id=session['user_id'],
        product_id=product_id
    ).first()
    
    if cart_item:
        cart_item.quantity += 1
    else:
        cart_item = Cart(user_id=session['user_id'], product_id=product_id)
        db.session.add(cart_item)
    
    db.session.commit()
    flash('Producto agregado al carrito', 'success')
    return redirect(url_for('index'))

@app.route('/cart')
def view_cart():
    if not session.get('user_id'):
        return redirect(url_for('login'))
    
    cart_items = Cart.query.filter_by(user_id=session['user_id']).all()
    total = sum(item.quantity * Product.query.get(item.product_id).price for item in cart_items)
    
    return render_template('cart.html', 
                         cart_items=cart_items, 
                         products={p.id: p for p in Product.query.all()},
                         total=total)

@app.route('/remove_from_cart/<int:product_id>', methods=['POST'])
def remove_from_cart(product_id):
    if not session.get('user_id'):
        return redirect(url_for('login'))
    
    Cart.query.filter_by(
        user_id=session['user_id'],
        product_id=product_id
    ).delete()
    
    db.session.commit()
    flash('Producto eliminado del carrito', 'success')
    return redirect(url_for('view_cart'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(port=5000, debug=True)
