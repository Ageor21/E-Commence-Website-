Project Summary: E-Commerce Application with Admin Panel
This project is a Flask-based e-commerce application designed to allow users to browse and purchase products while providing administrators with tools to manage the platform.

Key Features
User-Facing Features
Home Page:

Displays a list of products with options to view details, add to cart, or search for specific items.
Product Details:

Detailed view of a product, including name, price, description, and stock availability.
Allows users to add items to their cart.
Cart Management:

Users can view their cart, update quantities, and remove items.
Displays the total price of the items in the cart.
Checkout:

Allows users to place an order and clear their cart.
Sends an order confirmation email to the user.
User Authentication:

Users can register, log in, and log out securely.
Passwords are hashed using werkzeug.security.
Order Tracking:

Users can view their order history and track the status of their orders.
Admin Features
Admin Panel:

A dedicated dashboard for administrators to manage the platform.
Product Management:

Admins can add, edit, or delete products from the catalog.
Order Management:

Admins can view all orders and update their status (e.g., "Pending", "Shipped", "Completed").
User Management:

View all registered users and their roles (admin or regular user).
Technical Details
Backend
Framework: Flask (Python)
Database: SQLite (with SQLAlchemy ORM for database interactions)
Email Notifications: Flask-Mail for sending order confirmation emails.
Authentication: User authentication with session-based login and hashed passwords.
Frontend
HTML & CSS:
Clean and responsive design with consistent styles.
Forms for login, registration, cart management, and admin tasks.
JavaScript (Optional Enhancements):
AJAX for dynamic updates (e.g., updating cart items without refreshing).
Form validation and live previews for admin tasks.
Admin Access
Admin accounts are identified by the is_admin flag in the User model.
The /admin panel is protected, allowing access only to users with admin privileges.
