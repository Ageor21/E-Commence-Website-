from app import app, db, User, Product

with app.app_context():
    products = [
        Product(name="Laptop", description="High-performance laptop", price=999.99, stock=10, image_url=""),
        Product(name="Smartphone", description="Latest model smartphone", price=799.99, stock=20, image_url=""),
        Product(name="Headphones", description="Noise-cancelling headphones", price=199.99, stock=15, image_url=""),
        Product(name="Gaming PC", description="High Specs", price=1999.99, stock=5, image_url=""),
    ]
    db.session.add_all(products)
    db.session.commit()


    print("Database populated successfully!")

