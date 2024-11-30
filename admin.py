from app import app, db, User
from werkzeug.security import generate_password_hash


app.app_context().push()

admin_user = User(
    name="Admin",
    email="admin@example.com",
    password=generate_password_hash("adminpassword"),  # Securely hash the password
    is_admin=True
)
db.session.add(admin_user)
db.session.commit()
print("Admin user created successfully!")
