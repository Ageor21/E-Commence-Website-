from flask import Flask, request, jsonify, session, render_template, flash, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import logging
from flask_mail import Mail, Message

# Initialize Flask app
app = Flask(__name__)
app.secret_key = "SECERT_KEY"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ecommerce.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
# Email configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'  # Use your email provider's SMTP server
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'kanzensekai@gmail.com'  # Your email address
app.config['MAIL_PASSWORD'] = 'tonc exrx rmrw wmep'  # Your email password
app.config['MAIL_DEFAULT_SENDER'] = 'kanzensekai@gmail.com'  # Default sender address

mail = Mail(app)


# Configure logging
logging.basicConfig(filename='error.log', level=logging.ERROR)



# Database Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    price = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, nullable=False)
    image_url = db.Column(db.String(200), nullable=True)

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    total_price = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(50), default='Pending')
    created_at = db.Column(db.DateTime, default=db.func.now())

    user = db.relationship('User', backref='orders')


class OrderDetails(db.Model):
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), primary_key=True)
    quantity = db.Column(db.Integer, nullable=False)

class CartItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)

    user = db.relationship('User', backref='cart_items')
    product = db.relationship('Product', backref='cart_items')

class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.now())

    user = db.relationship('User', backref='reviews')
    product = db.relationship('Product', backref='reviews')

# Initialize database
with app.app_context():
    db.create_all()

def calculate_cart_total(user_id):
    """
    Calculate the total price of items in the cart for a given user.
    """
    cart_items = CartItem.query.filter_by(user_id=user_id).all()  # Assuming a Cart model exists
    total = sum(item.quantity * item.product.price for item in cart_items)
    return total


# Routes
@app.route('/')
def home():
    products = Product.query.all()
    return render_template('home.html', products=products)


@app.route('/search')
def search():
    query = request.args.get('query')
    if not query or len(query) < 3:
        flash("Search query must be at least 3 characters long.", "warning")
        return redirect(url_for('home'))

    products = Product.query.filter(Product.name.ilike(f"%{query}%")).all()
    return render_template('search_results.html', products=products, query=query)

@app.route('/cart/add/<int:product_id>', methods=['POST'])
def add_to_cart(product_id):
    quantity = int(request.form['quantity'])
    product = Product.query.get_or_404(product_id)

    # Check if product stock is sufficient
    if product.stock < quantity:
        flash(f"Only {product.stock} items of {product.name} are available.", "danger")
        return redirect(url_for('home'))

    # If user is logged in, save to database
    if 'user_id' in session:
        user_id = session['user_id']

        # Check if the item is already in the user's cart
        cart_item = CartItem.query.filter_by(user_id=user_id, product_id=product_id).first()
        if cart_item:
            cart_item.quantity += quantity  # Update quantity
        else:
            cart_item = CartItem(user_id=user_id, product_id=product_id, quantity=quantity)
            db.session.add(cart_item)

        db.session.commit()
        flash(f"{product.name} added to your cart!", "success")
    else:
        # Fallback: Save to session
        cart = session.get('cart', {})
        if str(product_id) in cart:
            cart[str(product_id)] += quantity
        else:
            cart[str(product_id)] = quantity
        session['cart'] = cart
        flash(f"{product.name} added to your cart (temporary storage)!", "info")

    return redirect(url_for('home'))

@app.route('/cart')
def cart():
    if 'user_id' in session:
        # Retrieve cart items for the logged-in user
        user_id = session['user_id']
        cart_items = CartItem.query.filter_by(user_id=user_id).all()

        # Calculate total price
        total_price = sum(item.product.price * item.quantity for item in cart_items)
        return render_template('cart.html', cart_items=cart_items, total_price=total_price)

    # Fallback: Retrieve cart items from session
    cart = session.get('cart', {})
    product_ids = [int(pid) for pid in cart.keys()]
    products = Product.query.filter(Product.id.in_(product_ids)).all()
    total_price = sum(product.price * cart[str(product.id)] for product in products)
    return render_template('cart.html', products=products, cart=cart, total_price=total_price)

@app.route('/cart/remove/<int:product_id>', methods=['POST'])
def remove_from_cart(product_id):
    user_id = session.get('user_id')
    cart_item = CartItem.query.filter_by(user_id=user_id, product_id=product_id).first()

    if cart_item:
        db.session.delete(cart_item)
        db.session.commit()
        flash("Item removed from cart.", "success")
    else:
        flash("Item not found in cart.", "danger")

    return redirect(url_for('cart'))


@app.route('/place_order', methods=['POST'])
def place_order():
    user_id = session.get('user_id')
    if not user_id:
        flash("You need to log in to place an order.", "danger")
        return redirect(url_for('login'))

    # Fetch user and calculate total price
    user = User.query.get(user_id)
    cart_items = CartItem.query.filter_by(user_id=user_id).all()
    if not cart_items:
        flash("Your cart is empty. Add items to your cart before placing an order.", "warning")
        return redirect(url_for('cart'))

    total_price = sum(item.quantity * item.product.price for item in cart_items)

    # Create the order
    order = Order(user_id=user_id, total_price=total_price)
    db.session.add(order)
    db.session.commit()

    # Clear the cart
    CartItem.query.filter_by(user_id=user_id).delete()
    db.session.commit()

    # Send confirmation email
    send_email(
        "Order Confirmation",
        [user.email],
        f"Hi {user.name},\n\nYour order has been placed successfully. Order ID: {order.id}.\n\nThank you for shopping with us!\nThe ShopEase Team"
    )

    flash("Order placed successfully! Your cart has been cleared.", "success")
    return redirect(url_for('order_confirmation', order_id=order.id))

@app.route('/order_confirmation/<int:order_id>')
def order_confirmation(order_id):
    order = Order.query.get_or_404(order_id)
    return render_template('order_confirmation.html', order=order)


@app.route('/order/<int:order_id>/update_status', methods=['POST'])
def update_order_status(order_id):
    # Get the new status from the form
    new_status = request.form.get('status')

    # Fetch the order by ID
    order = Order.query.get_or_404(order_id)

    # Update the status
    order.status = new_status
    db.session.commit()

    flash(f"Order {order_id} status updated to {new_status}.", "success")
    return redirect(url_for('admin_orders'))  # Redirect to the admin orders page or a suitable location


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')

        if not name or not email or not password:
            flash("All fields are required.", "warning")
            return redirect(url_for('register'))

        if len(password) < 6:
            flash("Password must be at least 6 characters long.", "warning")
            return redirect(url_for('register'))

        if User.query.filter_by(email=email).first():
            flash("Email is already registered.", "danger")
            return redirect(url_for('register'))

        hashed_password = generate_password_hash(password)
        new_user = User(name=name, email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        flash("Registration successful! Please log in.", "success")
        return redirect(url_for('login'))

    # For GET requests, render the registration page
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # Check if the user exists and password is correct
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['is_admin'] = user.is_admin
            flash(f"Welcome back, {user.name}!", "success")  # Flash message
            return redirect(url_for('home'))
        else:
            flash("Invalid email or password. Please try again.", "danger")
            return redirect(url_for('login'))

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('user_id', None)  # Remove the user's session
    flash("You have been logged out successfully.", "info")
    return redirect(url_for('home'))

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'user_id' not in session:
        flash("You need to log in to view your profile.", "danger")
        return redirect(url_for('login'))

    user = User.query.get_or_404(session['user_id'])

    if request.method == 'POST':
        # Update user details
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')

        if name:
            user.name = name
        if email:
            user.email = email
        if password and len(password) >= 6:
            user.password = generate_password_hash(password)

        db.session.commit()
        flash("Profile updated successfully!", "success")
        return redirect(url_for('profile'))

    # Fetch user's order history
    orders = Order.query.filter_by(user_id=user.id).order_by(Order.created_at.desc()).all()
    return render_template('profile.html', user=user, orders=orders)

@app.route('/product/<int:product_id>', methods=['GET', 'POST'])
def product_view(product_id):
    product = Product.query.get_or_404(product_id)

    # Handle new review submission
    if request.method == 'POST':
        if 'user_id' not in session:
            flash("You need to log in to submit a review.", "danger")
            return redirect(url_for('login'))

        content = request.form['content']
        rating = int(request.form['rating'])

        if not content or rating not in range(1, 6):
            flash("Please provide a valid review and rating (1-5 stars).", "warning")
            return redirect(url_for('product_view', product_id=product_id))

        review = Review(
            product_id=product_id,
            user_id=session['user_id'],
            content=content,
            rating=rating
        )
        db.session.add(review)
        db.session.commit()
        flash("Your review has been submitted.", "success")
        return redirect(url_for('product_view', product_id=product_id))

    sort_by = request.args.get('sort', 'most_recent')
    if sort_by == 'highest_rated':
        reviews = Review.query.filter_by(product_id=product_id).order_by(Review.rating.desc()).all()
    else:
        reviews = Review.query.filter_by(product_id=product_id).order_by(Review.created_at.desc()).all()

    total_reviews = len(reviews)
    avg_rating = sum([r.rating for r in reviews]) / total_reviews if total_reviews > 0 else 0

    return render_template('product_view.html', product=product, reviews=reviews, avg_rating=avg_rating, total_reviews=total_reviews)


@app.route('/product/<int:product_id>/review/<int:review_id>/edit', methods=['GET', 'POST'])
def edit_review(product_id, review_id):
    if 'user_id' not in session:
        flash("You need to log in to edit your review.", "danger")
        return redirect(url_for('login'))

    review = Review.query.get_or_404(review_id)

    # Ensure the logged-in user is the author of the review
    if review.user_id != session['user_id']:
        flash("You are not authorized to edit this review.", "danger")
        return redirect(url_for('product_view', product_id=product_id))

    if request.method == 'POST':
        review.content = request.form['content']
        review.rating = int(request.form['rating'])
        db.session.commit()
        flash("Your review has been updated.", "success")
        return redirect(url_for('product_view', product_id=product_id))

    return render_template('edit_review.html', review=review, product_id=product_id)

@app.route('/product/<int:product_id>/review/<int:review_id>/delete', methods=['POST'])
def delete_review(product_id, review_id):
    if 'user_id' not in session:
        flash("You need to log in to delete your review.", "danger")
        return redirect(url_for('login'))

    review = Review.query.get_or_404(review_id)

    # Ensure the logged-in user is the author of the review
    if review.user_id != session['user_id']:
        flash("You are not authorized to delete this review.", "danger")
        return redirect(url_for('product_view', product_id=product_id))

    db.session.delete(review)
    db.session.commit()
    flash("Your review has been deleted.", "success")
    return redirect(url_for('product_view', product_id=product_id))

@app.route('/admin')
def admin_dashboard():
    if 'user_id' not in session or not session.get('is_admin'):  # Check if user is an admin
        flash("You are not authorized to access the admin panel.", "danger")
        return redirect(url_for('login'))

    users = User.query.all()
    orders = Order.query.all()
    products = Product.query.all()
    return render_template('admin_orders.html', users=users, orders=orders, products=products)

@app.route('/admin/add_product', methods=['GET', 'POST'])
def add_product():
    if request.method == 'POST':
        name = request.form['name']
        price = float(request.form['price'])
        stock = int(request.form['stock'])

        product = Product(name=name, price=price, stock=stock)
        db.session.add(product)
        db.session.commit()
        flash("Product added successfully.", "success")
        return redirect(url_for('admin_dashboard'))

    return render_template('add_product.html')

@app.route('/admin/edit_product/<int:product_id>', methods=['GET', 'POST'])
def edit_product(product_id):
    product = Product.query.get_or_404(product_id)

    if request.method == 'POST':
        product.name = request.form['name']
        product.price = float(request.form['price'])
        product.stock = int(request.form['stock'])
        db.session.commit()
        flash("Product updated successfully.", "success")
        return redirect(url_for('admin_dashboard'))

    return render_template('edit_product.html', product=product)

@app.route('/admin/delete_product/<int:product_id>', methods=['POST'])
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    flash("Product deleted successfully.", "success")
    return redirect(url_for('admin_dashboard'))


@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(error):
    logging.error(f"Internal server error: {error}")
    flash("An unexpected error occurred. Please try again later.", "danger")
    return redirect(url_for('home'))

def send_email(subject, recipients, body):
    msg = Message(subject, recipients=recipients)
    msg.body = body
    mail.send(msg)

# Run the application
if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
