from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from flask_mail import Mail, Message
from flask_migrate import Migrate
from models import db, User, Product, Cart, Category  # Asegúrate de importar Category
import os
import secrets
import datetime
from functools import wraps
from sqlalchemy import desc

# Crear el directorio de uploads si no existe
if not os.path.exists('static/uploads'):
    os.makedirs('static/uploads')

# Crear los directorios necesarios si no existen
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static/uploads')
CATEGORIES_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static/categories')

for folder in [UPLOAD_FOLDER, CATEGORIES_FOLDER]:
    if not os.path.exists(folder):
        os.makedirs(folder, exist_ok=True)

app = Flask(__name__)
app.config.from_object('config.Config')

db.init_app(app)
migrate = Migrate(app, db)
mail = Mail(app)

UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static/uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

app.config['UPLOAD_FOLDER'] = '/home/tuusuario/tienda2/static/uploads'
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'chinito01263000@gmail.com'  # Cambia esto
app.config['MAIL_PASSWORD'] = 'kueh cwag jepd kgoa'  # Cambia esto
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Definir el decorador login_required
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Por favor inicia sesión para acceder a esta página')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    products = Product.query.all()
    categories = Category.query.filter_by(is_active=True).order_by(Category.order).all()
    return render_template('index.html', products=products, categories=categories)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        try:
            # Verificar que todos los campos requeridos estén presentes
            required_fields = ['username', 'email', 'password', 'first_name', 'last_name', 'phone']
            for field in required_fields:
                if field not in request.form or not request.form[field].strip():
                    flash(f'El campo {field} es requerido')
                    return render_template('register.html')
            
            # Verificar si el usuario o email ya existe
            if User.query.filter_by(username=request.form['username'].strip()).first():
                flash('El nombre de usuario ya existe')
                return render_template('register.html')
            if User.query.filter_by(email=request.form['email'].strip()).first():
                flash('El correo electrónico ya está registrado')
                return render_template('register.html')
            
            # Crear token de verificación
            token = secrets.token_urlsafe(32)
            expiry = datetime.datetime.now() + datetime.timedelta(hours=24)
            
            # Crear nuevo usuario
            user = User(
                username=request.form['username'].strip(),
                email=request.form['email'].strip(),
                password=generate_password_hash(request.form['password']),
                first_name=request.form['first_name'].strip(),
                last_name=request.form['last_name'].strip(),
                phone=request.form['phone'].strip(),
                verification_token=token,
                token_expiry=expiry
            )
            db.session.add(user)
            db.session.commit()
            
            # Enviar email de verificación
            try:
                verification_url = url_for('verify_email', token=token, _external=True)
                msg = Message('Verifica tu correo electrónico',
                            sender=app.config['MAIL_USERNAME'],
                            recipients=[user.email])
                msg.body = f'''Para verificar tu correo electrónico, visita el siguiente enlace:
{verification_url}

Este enlace expirará en 24 horas.'''
                mail.send(msg)
                flash('Se ha enviado un correo de verificación a tu dirección de email')
            except Exception as e:
                print(f"Error enviando email: {str(e)}")
                flash('Usuario registrado pero hubo un problema enviando el email de verificación')
            
            return redirect(url_for('login'))
            
        except Exception as e:
            db.session.rollback()
            print(f"Error en registro: {str(e)}")
            flash(f'Error en el registro. Por favor intenta nuevamente.')
            
    return render_template('register.html')

@app.route('/verify_email/<token>')
def verify_email(token):
    user = User.query.filter_by(verification_token=token).first()
    
    if not user:
        flash('Token de verificación inválido')
        return redirect(url_for('login'))
        
    if datetime.datetime.now() > user.token_expiry:
        flash('El token de verificación ha expirado')
        return redirect(url_for('login'))
        
    user.is_verified = True
    user.verification_token = None
    user.token_expiry = None
    db.session.commit()
    
    flash('Tu correo ha sido verificado exitosamente')
    return redirect(url_for('login'))

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
                    if not user.is_verified:
                        flash('Por favor verifica tu correo electrónico antes de iniciar sesión')
                        return render_template('login.html')
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
@login_required
def add_product():
    if request.method == 'POST':
        name = request.form.get('name')
        price = request.form.get('price')
        description = request.form.get('description')

        # Manejar imagen principal
        image_file = request.files.get('image')
        if image_file and allowed_file(image_file.filename):
            filename = secure_filename(image_file.filename)
            image_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            main_image = filename
        else:
            main_image = None

        # Manejar imagen hover
        hover_file = request.files.get('image_hover')
        if hover_file and allowed_file(hover_file.filename):
            hover_filename = secure_filename(hover_file.filename)
            hover_file.save(os.path.join(app.config['UPLOAD_FOLDER'], hover_filename))
            hover_image = hover_filename
        else:
            hover_image = None

        product = Product(
            name=name,
            price=float(price),
            description=description,
            image=main_image,
            image_hover=hover_image
        )
        db.session.add(product)
        db.session.commit()
        flash('Producto agregado exitosamente', 'success')
        return redirect(url_for('admin'))

    return render_template('add_product.html')

@app.route('/edit_product/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_product(id):
    product = Product.query.get_or_404(id)
    if request.method == 'POST':
        product.name = request.form.get('name')
        product.price = float(request.form.get('price'))
        product.description = request.form.get('description')
        product.specifications = request.form.get('specifications')

        # Manejar imágenes principales
        image_file = request.files.get('image')
        if image_file and allowed_file(image_file.filename):
            filename = secure_filename(image_file.filename)
            image_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            product.image = filename

        hover_file = request.files.get('image_hover')
        if hover_file and allowed_file(hover_file.filename):
            hover_filename = secure_filename(hover_file.filename)
            hover_file.save(os.path.join(app.config['UPLOAD_FOLDER'], hover_filename))
            product.image_hover = hover_filename

        # Manejar imágenes adicionales
        additional_images = request.files.getlist('additional_images')
        if additional_images:
            image_names = []
            for img in additional_images:
                if img and allowed_file(img.filename):
                    filename = secure_filename(img.filename)
                    img.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    image_names.append(filename)
            if image_names:
                product.additional_images = ','.join(image_names)

        db.session.commit()
        flash('Producto actualizado exitosamente', 'success')
        return redirect(url_for('product_detail', id=product.id))

    return render_template('add_product.html', product=product)

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
@login_required
def add_to_cart(product_id):
    cart_item = Cart.query.filter_by(user_id=session['user_id'], product_id=product_id).first()
    
    if cart_item:
        cart_item.quantity += 1
    else:
        cart_item = Cart(user_id=session['user_id'], product_id=product_id)
        db.session.add(cart_item)
    
    db.session.commit()
    return jsonify({'success': True})

@app.route('/cart')
@login_required
def view_cart():
    cart_items = Cart.query.filter_by(user_id=session['user_id']).all()
    # Calculamos el total
    total = sum(item.product.price * item.quantity for item in cart_items)
    return render_template('cart.html', cart_items=cart_items, total=total)

@app.route('/remove_from_cart/<int:product_id>', methods=['POST'])
@login_required
def remove_from_cart(product_id):
    Cart.query.filter_by(user_id=session['user_id'], product_id=product_id).delete()
    db.session.commit()
    return redirect(url_for('view_cart'))

@app.route('/admin/categories')
@login_required
def admin_categories():
    if not session.get('is_admin'):
        return redirect(url_for('index'))
    categories = Category.query.order_by(Category.order).all()
    return render_template('admin_categories.html', categories=categories)

@app.route('/admin/categories/add', methods=['GET', 'POST'])
@login_required
def add_category():
    if not session.get('is_admin'):
        return redirect(url_for('index'))
        
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        order = request.form.get('order', 0)
        
        # Manejar la imagen
        image = request.files.get('image')
        filename = None
        if image and allowed_file(image.filename):
            filename = secure_filename(image.filename)
            # Cambiar la ruta para usar CATEGORIES_FOLDER
            image.save(os.path.join(CATEGORIES_FOLDER, filename))
        
        category = Category(
            name=name,
            description=description,
            image=filename,
            order=int(order),
            is_active=True
        )
        
        db.session.add(category)
        db.session.commit()
        flash('Categoría agregada exitosamente', 'success')
        return redirect(url_for('admin_categories'))
    
    return render_template('add_category.html')

@app.route('/admin/categories/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_category(id):
    if not session.get('is_admin'):
        return redirect(url_for('index'))
        
    category = Category.query.get_or_404(id)
    
    if request.method == 'POST':
        category.name = request.form.get('name')
        category.description = request.form.get('description')
        category.order = int(request.form.get('order', 0))
        
        image = request.files.get('image')
        if image and allowed_file(image.filename):
            filename = secure_filename(image.filename)
            # Cambiar la ruta para usar CATEGORIES_FOLDER
            image.save(os.path.join(CATEGORIES_FOLDER, filename))
            category.image = filename
        
        db.session.commit()
        flash('Categoría actualizada exitosamente', 'success')
        return redirect(url_for('admin_categories'))
    
    return render_template('add_category.html', category=category)

@app.route('/admin/categories/toggle/<int:id>', methods=['POST'])
@login_required
def toggle_category(id):
    if not session.get('is_admin'):
        return redirect(url_for('index'))
        
    category = Category.query.get_or_404(id)
    category.is_active = not category.is_active
    db.session.commit()
    return redirect(url_for('admin_categories'))

@app.route('/admin/categories/delete/<int:id>', methods=['POST'])
@login_required
def delete_category(id):
    if not session.get('is_admin'):
        return redirect(url_for('index'))
    
    category = Category.query.get_or_404(id)
    
    # Eliminar la imagen si existe
    if category.image:
        image_path = os.path.join(CATEGORIES_FOLDER, category.image)
        if os.path.exists(image_path):
            os.remove(image_path)
    
    db.session.delete(category)
    db.session.commit()
    flash('Categoría eliminada exitosamente', 'success')
    return redirect(url_for('admin_categories'))

@app.route('/api/search')
def search_products():
    query = request.args.get('q', '')
    products = Product.query.filter(
        Product.name.ilike(f'%{query}%') | 
        Product.description.ilike(f'%{query}%')
    ).limit(5).all()
    
    return jsonify([{
        'id': p.id,
        'name': p.name,
        'price': p.price,
        'image': p.image
    } for p in products])

@app.route('/api/products/filter')
def filter_products():
    filter_type = request.args.get('type', 'newest')
    
    if filter_type == 'newest':
        products = Product.query.order_by(desc(Product.id)).all()
    elif filter_type == 'popular':
        # Aquí podrías ordenar por número de ventas si tienes esa información
        products = Product.query.all()
    elif filter_type == 'price-asc':
        products = Product.query.order_by(Product.price).all()
    elif filter_type == 'price-desc':
        products = Product.query.order_by(desc(Product.price)).all()
    else:
        products = Product.query.all()
    
    return jsonify([{
        'id': p.id,
        'name': p.name,
        'price': p.price,
        'image': p.image,
        'description': p.description
    } for p in products])

@app.route('/product/<int:id>')
def product_detail(id):
    product = Product.query.get_or_404(id)
    return render_template('product_detail.html', product=product)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        # Crear usuario admin si no existe
        admin_user = User.query.filter_by(username='admin').first()
        if not admin_user:
            admin = User(
                username='admin',
                email='admin@example.com',
                password=generate_password_hash('admin123'),
                first_name='Admin',
                last_name='User',
                phone='0000000000',
                is_admin=True,
                is_verified=True
            )
            db.session.add(admin)
            db.session.commit()
            print('Usuario administrador creado:')
            print('Usuario: admin')
            print('Contraseña: admin123')
    # Cambia esto para producción
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
