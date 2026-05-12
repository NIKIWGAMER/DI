import os
import json
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_bcrypt import Bcrypt
from models import db, User, Product, Brand, CartItem, Favorite, Order, OrderItem, PCBuild
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here-change-in-production'
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'postgresql://postgres:12345678@localhost:5432/electronics_store')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Context processors for global template variables
@app.context_processor
def utility_processor():
    cart_count = 0
    favorites_count = 0
    
    if current_user.is_authenticated:
        cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
        cart_count = sum(item.quantity for item in cart_items)
        favorites_count = Favorite.query.filter_by(user_id=current_user.id).count()
    else:
        cart = session.get('cart', {})
        cart_count = sum(cart.values())
        favorites = session.get('favorites', [])
        favorites_count = len(favorites)
    
    return dict(cart_count=cart_count, favorites_count=favorites_count)

# Главная страница
@app.route('/')
def index():
    # Персональная подборка
    smartphones = Product.query.filter_by(category='Смартфоны').limit(8).all()
    monitors = Product.query.filter_by(category='Мониторы').limit(8).all()
    notebooks = Product.query.filter_by(category='Ноутбуки').limit(8).all()
    videocards = Product.query.filter_by(category='Видеокарты').limit(8).all()
    motherboards = Product.query.filter_by(category='Материнские платы').limit(8).all()
    
    # Сезонные товары
    fans = Product.query.filter_by(category='Вентиляторы').limit(8).all()
    trimmer_line = Product.query.filter_by(category='Леска для триммеров').limit(8).all()
    scooters = Product.query.filter_by(category='Электросамокаты').limit(8).all()
    conditioners = Product.query.filter_by(category='Мобильные кондиционеры').limit(8).all()
    trimmers = Product.query.filter_by(category='Триммеры бензиновые').limit(8).all()
    
    # Умный дом
    sensors = Product.query.filter_by(category='Датчики').limit(8).all()
    lighting = Product.query.filter_by(category='Освещение').limit(8).all()
    control_centers = Product.query.filter_by(category='Центры управления').limit(8).all()
    sockets = Product.query.filter_by(category='Розетки').limit(8).all()
    switches = Product.query.filter_by(category='Выключатели').limit(8).all()
    
    # Комплектующие ПК
    cpus = Product.query.filter_by(category='Процессоры').limit(8).all()
    rams = Product.query.filter_by(category='Оперативная память').limit(8).all()

    brands = Brand.query.all()
    recently_viewed = session.get('recently_viewed', [])
    recent_products = Product.query.filter(Product.id.in_(recently_viewed)).all() if recently_viewed else []
    
    return render_template('index.html',
                           smartphones=smartphones, monitors=monitors, notebooks=notebooks,
                           videocards=videocards, motherboards=motherboards,
                           fans=fans, trimmer_line=trimmer_line, scooters=scooters,
                           conditioners=conditioners, trimmers=trimmers,
                           sensors=sensors, lighting=lighting, control_centers=control_centers,
                           sockets=sockets, switches=switches,
                           cpus=cpus, rams=rams,
                           brands=brands, recent_products=recent_products)

# Регистрация и вход
@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
        
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = bcrypt.generate_password_hash(request.form['password']).decode('utf-8')
        
        if User.query.filter_by(email=email).first():
            flash('Пользователь с таким email уже существует.', 'danger')
            return redirect(url_for('register'))
            
        user = User(username=username, email=email, password=password)
        db.session.add(user)
        db.session.commit()
        
        # Transfer session cart to user cart
        if 'cart' in session:
            for product_id, quantity in session['cart'].items():
                cart_item = CartItem(user_id=user.id, product_id=int(product_id), quantity=quantity)
                db.session.add(cart_item)
            session.pop('cart')
            db.session.commit()
        
        flash('Регистрация прошла успешно! Теперь вы можете войти.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
        
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        
        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user)
            
            # Transfer session cart to user cart
            if 'cart' in session:
                for product_id, quantity in session['cart'].items():
                    existing = CartItem.query.filter_by(user_id=user.id, product_id=int(product_id)).first()
                    if existing:
                        existing.quantity += quantity
                    else:
                        cart_item = CartItem(user_id=user.id, product_id=int(product_id), quantity=quantity)
                        db.session.add(cart_item)
                session.pop('cart')
                db.session.commit()
            
            flash('Вы успешно вошли в систему.', 'success')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('index'))
        else:
            flash('Неверный email или пароль.', 'danger')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Вы вышли из системы.', 'info')
    return redirect(url_for('index'))

# Профиль
@app.route('/profile')
@login_required
def profile():
    orders = Order.query.filter_by(user_id=current_user.id).order_by(Order.created_at.desc()).all()
    return render_template('profile.html', user=current_user, orders=orders)

@app.route('/profile/update', methods=['POST'])
@login_required
def update_profile():
    username = request.form.get('username')
    email = request.form.get('email')
    
    if email != current_user.email and User.query.filter_by(email=email).first():
        flash('Этот email уже используется.', 'danger')
        return redirect(url_for('profile'))
    
    current_user.username = username
    current_user.email = email
    db.session.commit()
    
    flash('Профиль обновлен.', 'success')
    return redirect(url_for('profile'))

# Товар
@app.route('/product/<int:product_id>')
def product(product_id):
    product = Product.query.get_or_404(product_id)
    
    # Сохраняем в историю просмотров
    recently = session.get('recently_viewed', [])
    if product_id in recently:
        recently.remove(product_id)
    recently.insert(0, product_id)
    recently = recently[:20]
    session['recently_viewed'] = recently
    
    # Get related products
    related = Product.query.filter_by(category=product.category).filter(Product.id != product.id).limit(4).all()
    
    return render_template('product.html', product=product, related=related)

# Корзина
@app.route('/add_to_cart/<int:product_id>')
def add_to_cart(product_id):
    if current_user.is_authenticated:
        cart_item = CartItem.query.filter_by(user_id=current_user.id, product_id=product_id).first()
        if cart_item:
            cart_item.quantity += 1
        else:
            cart_item = CartItem(user_id=current_user.id, product_id=product_id)
            db.session.add(cart_item)
        db.session.commit()
    else:
        cart = session.get('cart', {})
        cart[str(product_id)] = cart.get(str(product_id), 0) + 1
        session['cart'] = cart
    
    flash('Товар добавлен в корзину.', 'success')
    return redirect(request.referrer or url_for('index'))

@app.route('/cart')
def cart():
    products = []
    total = 0
    
    if current_user.is_authenticated:
        cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
        for item in cart_items:
            products.append({'product': item.product, 'quantity': item.quantity, 'id': item.id})
            total += item.product.price * item.quantity
    else:
        cart = session.get('cart', {})
        for pid, qty in cart.items():
            product = Product.query.get(int(pid))
            if product:
                products.append({'product': product, 'quantity': qty, 'id': None})
                total += product.price * qty
    
    return render_template('cart.html', products=products, total=total)

@app.route('/update_cart/<int:item_id>', methods=['POST'])
@login_required
def update_cart(item_id):
    quantity = int(request.form.get('quantity', 1))
    cart_item = CartItem.query.get_or_404(item_id)
    
    if cart_item.user_id != current_user.id:
        flash('Ошибка доступа.', 'danger')
        return redirect(url_for('cart'))
    
    if quantity > 0:
        cart_item.quantity = quantity
    else:
        db.session.delete(cart_item)
    
    db.session.commit()
    return redirect(url_for('cart'))

@app.route('/remove_from_cart/<int:product_id>')
def remove_from_cart(product_id):
    if current_user.is_authenticated:
        cart_item = CartItem.query.filter_by(user_id=current_user.id, product_id=product_id).first()
        if cart_item:
            db.session.delete(cart_item)
            db.session.commit()
    else:
        cart = session.get('cart', {})
        cart.pop(str(product_id), None)
        session['cart'] = cart
    
    flash('Товар удален из корзины.', 'info')
    return redirect(url_for('cart'))

# Избранное
@app.route('/add_to_favorites/<int:product_id>')
def add_to_favorites(product_id):
    if current_user.is_authenticated:
        existing = Favorite.query.filter_by(user_id=current_user.id, product_id=product_id).first()
        if not existing:
            favorite = Favorite(user_id=current_user.id, product_id=product_id)
            db.session.add(favorite)
            db.session.commit()
            flash('Добавлено в избранное.', 'success')
        else:
            flash('Товар уже в избранном.', 'info')
    else:
        favs = session.get('favorites', [])
        if product_id not in favs:
            favs.append(product_id)
            session['favorites'] = favs
            flash('Добавлено в избранное.', 'success')
        else:
            flash('Товар уже в избранном.', 'info')
    
    return redirect(request.referrer or url_for('index'))

@app.route('/favorites')
def favorites():
    products = []
    if current_user.is_authenticated:
        favorites = Favorite.query.filter_by(user_id=current_user.id).all()
        products = [fav.product for fav in favorites]
    else:
        favs = session.get('favorites', [])
        products = Product.query.filter(Product.id.in_(favs)).all() if favs else []
    
    return render_template('favorites.html', products=products)

@app.route('/remove_from_favorites/<int:product_id>')
def remove_from_favorites(product_id):
    if current_user.is_authenticated:
        favorite = Favorite.query.filter_by(user_id=current_user.id, product_id=product_id).first()
        if favorite:
            db.session.delete(favorite)
            db.session.commit()
    else:
        favs = session.get('favorites', [])
        if product_id in favs:
            favs.remove(product_id)
        session['favorites'] = favs
    
    flash('Удалено из избранного.', 'info')
    return redirect(url_for('favorites'))

# Оформление заказа
@app.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    if request.method == 'POST':
        cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
        if not cart_items:
            flash('Корзина пуста.', 'warning')
            return redirect(url_for('cart'))
        
        total = sum(item.product.price * item.quantity for item in cart_items)
        
        order = Order(
            user_id=current_user.id,
            total=total,
            address=request.form.get('address'),
            phone=request.form.get('phone'),
            status='Обрабатывается'
        )
        db.session.add(order)
        db.session.flush()
        
        for item in cart_items:
            order_item = OrderItem(
                order_id=order.id,
                product_id=item.product_id,
                quantity=item.quantity,
                price=item.product.price
            )
            db.session.add(order_item)
            db.session.delete(item)
        
        db.session.commit()
        flash('Заказ успешно оформлен! Номер заказа: #{}'.format(order.id), 'success')
        return redirect(url_for('order_confirmation', order_id=order.id))
    
    cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
    if not cart_items:
        flash('Корзина пуста.', 'warning')
        return redirect(url_for('cart'))
    
    total = sum(item.product.price * item.quantity for item in cart_items)
    return render_template('checkout.html', cart_items=cart_items, total=total)

@app.route('/order/<int:order_id>')
@login_required
def order_confirmation(order_id):
    order = Order.query.get_or_404(order_id)
    if order.user_id != current_user.id:
        flash('Доступ запрещен.', 'danger')
        return redirect(url_for('index'))
    return render_template('order_confirmation.html', order=order)

# Каталог
@app.route('/catalog')
def catalog():
    query = request.args.get('query', '')
    category = request.args.get('category', '')
    sort = request.args.get('sort', 'name')
    min_price = request.args.get('min_price', type=float)
    max_price = request.args.get('max_price', type=float)
    
    products_query = Product.query
    
    if category:
        products_query = products_query.filter_by(category=category)
    
    if query:
        products_query = products_query.filter(Product.name.ilike(f'%{query}%'))
    
    if min_price is not None:
        products_query = products_query.filter(Product.price >= min_price)
    
    if max_price is not None:
        products_query = products_query.filter(Product.price <= max_price)
    
    # Sorting
    if sort == 'price_asc':
        products_query = products_query.order_by(Product.price.asc())
    elif sort == 'price_desc':
        products_query = products_query.order_by(Product.price.desc())
    else:
        products_query = products_query.order_by(Product.name.asc())
    
    products = products_query.all()
    
    categories = db.session.query(Product.category).distinct().all()
    categories = [c[0] for c in categories]
    
    return render_template('catalog.html', products=products, categories=categories,
                         current_category=category, current_sort=sort)

# Поиск
@app.route('/search')
def search():
    query = request.args.get('query', '')
    products = Product.query.filter(Product.name.ilike(f'%{query}%')).all() if query else []
    return render_template('search.html', products=products, query=query)

# Сборка ПК
@app.route('/build-pc')
def build_pc():
    cpus = Product.query.filter_by(category='Процессоры').all()
    gpus = Product.query.filter_by(category='Видеокарты').all()
    motherboards = Product.query.filter_by(category='Материнские платы').all()
    rams = Product.query.filter_by(category='Оперативная память').all()
    
    return render_template('build_pc.html', cpus=cpus, gpus=gpus, 
                         motherboards=motherboards, rams=rams)

@app.route('/api/calculate-build', methods=['POST'])
def calculate_build():
    data = request.json
    total = 0
    components = []
    
    for component_id in data.get('components', []):
        product = Product.query.get(component_id)
        if product:
            total += product.price
            components.append({
                'id': product.id,
                'name': product.name,
                'price': product.price
            })
    
    return jsonify({
        'total': total,
        'components': components
    })

@app.route('/save-build', methods=['POST'])
@login_required
def save_build():
    build = PCBuild(
        user_id=current_user.id,
        name=request.form.get('name', 'Моя сборка'),
        cpu=request.form.get('cpu'),
        gpu=request.form.get('gpu'),
        motherboard=request.form.get('motherboard'),
        ram=request.form.get('ram'),
        total_price=float(request.form.get('total', 0))
    )
    db.session.add(build)
    db.session.commit()
    
    flash('Сборка сохранена!', 'success')
    return redirect(url_for('profile'))

# Статические страницы
@app.route('/payment')
def payment():
    return render_template('payment.html')

@app.route('/help')
def help_page():
    return render_template('help.html')

# API для получения информации о товаре
@app.route('/api/product/<int:product_id>')
def api_product(product_id):
    product = Product.query.get_or_404(product_id)
    return jsonify({
        'id': product.id,
        'name': product.name,
        'price': product.price,
        'category': product.category,
        'description': product.description,
        'image_url': product.image_url
    })

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000, debug=True)