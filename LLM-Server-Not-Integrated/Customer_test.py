import requests
import time

# Set the Ngrok-exposed API endpoint (STATIC)
NGROK_URL = "https://quiet-vigorously-squirrel.ngrok-free.app"

# API Key (Replace with your assigned key)
API_KEY = "mysecretkey123"

# Common request headers
HEADERS = {
    "Content-Type": "application/json",
    "X-API-Key": API_KEY
}

def measure_time(func, *args):
    """
    Measures the execution time of a function.
    """
    start_time = time.time()
    result = func(*args)
    end_time = time.time()
    elapsed_time = end_time - start_time
    return result, elapsed_time

def summarize_code_blocks(code_blocks):
    """
    Sends a request to summarize given code blocks (structured version).
    """
    payload = {"code_blocks": code_blocks}
    response = requests.post(f"{NGROK_URL}/summarize_code", json=payload, headers=HEADERS)
    return response.json().get("summary", "Error: No response")

def baseline_summarize_code_blocks(code_blocks):
    """
    Sends a request to summarize given code blocks (baseline version).
    """
    payload = {"code_blocks": code_blocks}
    response = requests.post(f"{NGROK_URL}/baseline_summarize_code", json=payload, headers=HEADERS)
    return response.json().get("summary", "Error: No response")

def analyze_repo_structure(repo_tree):
    """
    Sends a request to analyze the repository structure (structured version).
    """
    payload = {"repo_tree": repo_tree}
    response = requests.post(f"{NGROK_URL}/analyze_repo", json=payload, headers=HEADERS)
    return response.json().get("analysis", "Error: No response")

def baseline_analyze_repo_structure(repo_tree):
    """
    Sends a request to analyze the repository structure (baseline version).
    """
    payload = {"repo_tree": repo_tree}
    response = requests.post(f"{NGROK_URL}/baseline_analyze_repo", json=payload, headers=HEADERS)
    return response.json().get("analysis", "Error: No response")

# ========================= TESTING =========================
if __name__ == "__main__":
    code_samples = [
    """import sqlite3
import hashlib
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Database setup
DB_NAME = "ecommerce.db"

def create_tables():
    \"\"\"Initializes the database tables if they don't exist.\"\"\"    
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    c.execute(\"\"\"
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password_hash TEXT)\"\"\")

    c.execute(\"\"\"
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            price REAL,
            stock INTEGER)\"\"\")

    c.execute(\"\"\"
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            product_id INTEGER,
            quantity INTEGER,
            total_price REAL,
            order_date TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (product_id) REFERENCES products(id))\"\"\")

    conn.commit()
    conn.close()
""",
    """class User:
    \"\"\"Handles user registration and authentication.\"\"\"
    def __init__(self, username, password):
        self.username = username
        self.password_hash = self.hash_password(password)

    @staticmethod
    def hash_password(password):
        \"\"\"Returns SHA256 hash of a password.\"\"\"
        return hashlib.sha256(password.encode()).hexdigest()

    def register(self):
        \"\"\"Registers a new user.\"\"\"
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        try:
            c.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)",
                      (self.username, self.password_hash))
            conn.commit()
            logging.info(f"User {self.username} registered successfully.")
        except sqlite3.IntegrityError:
            logging.error(f"User {self.username} already exists.")
            return False
        finally:
            conn.close()
        return True

    @staticmethod
    def authenticate(username, password):
        \"\"\"Verifies user login credentials.\"\"\"
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        c.execute("SELECT * FROM users WHERE username = ? AND password_hash = ?",
                  (username, password_hash))
        user = c.fetchone()
        conn.close()
        if user:
            logging.info(f"User {username} authenticated successfully.")
            return True
        logging.warning(f"Authentication failed for {username}.")
        return False
""",
    """class Product:
    \"\"\"Handles product inventory management.\"\"\"
    def __init__(self, name, price, stock):
        self.name = name
        self.price = price
        self.stock = stock

    def add_product(self):
        \"\"\"Adds a new product to inventory.\"\"\"
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("INSERT INTO products (name, price, stock) VALUES (?, ?, ?)",
                  (self.name, self.price, self.stock))
        conn.commit()
        conn.close()
        logging.info(f"Product {self.name} added to inventory.")

    @staticmethod
    def list_products():
        \"\"\"Lists all available products.\"\"\"
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("SELECT * FROM products")
        products = c.fetchall()
        conn.close()
        return products
""",
    """class Order:
    \"\"\"Handles order processing.\"\"\"
    @staticmethod
    def place_order(username, product_id, quantity):
        \"\"\"Processes a new order.\"\"\"
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()

        # Verify user exists
        c.execute("SELECT id FROM users WHERE username = ?", (username,))
        user = c.fetchone()
        if not user:
            logging.error(f"User {username} not found.")
            return False
        user_id = user[0]

        # Check product availability
        c.execute("SELECT name, price, stock FROM products WHERE id = ?", (product_id,))
        product = c.fetchone()
        if not product:
            logging.error(f"Product ID {product_id} not found.")
            return False

        name, price, stock = product
        if stock < quantity:
            logging.warning(f"Insufficient stock for {name}. Requested: {quantity}, Available: {stock}.")
            return False

        # Process order
        total_price = price * quantity
        order_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        c.execute("INSERT INTO orders (user_id, product_id, quantity, total_price, order_date) VALUES (?, ?, ?, ?, ?)",
                  (user_id, product_id, quantity, total_price, order_date))
        c.execute("UPDATE products SET stock = stock - ? WHERE id = ?", (quantity, product_id))
        conn.commit()
        conn.close()
        logging.info(f"Order placed: {username} purchased {quantity} of {name} for ${total_price:.2f}.")
        return True

    @staticmethod
    def list_orders(username):
        \"\"\"Lists all orders for a given user.\"\"\"
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()

        c.execute("SELECT id FROM users WHERE username = ?", (username,))
        user = c.fetchone()
        if not user:
            logging.error(f"User {username} not found.")
            return []
        user_id = user[0]

        c.execute(\"\"\"
            SELECT orders.id, products.name, orders.quantity, orders.total_price, orders.order_date
            FROM orders JOIN products ON orders.product_id = products.id
            WHERE orders.user_id = ?
        \"\"\", (user_id,))
        orders = c.fetchall()
        conn.close()
        return orders
""",
    """# ====================== TESTING ======================
if __name__ == "__main__":
    create_tables()

    # Register users
    user1 = User("alice", "password123")
    user1.register()

    user2 = User("bob", "securepass")
    user2.register()

    # Authenticate users
    assert User.authenticate("alice", "password123") == True
    assert User.authenticate("alice", "wrongpass") == False

    # Add products
    product1 = Product("Laptop", 999.99, 10)
    product1.add_product()

    product2 = Product("Smartphone", 599.99, 15)
    product2.add_product()

    # List products
    print("\nAvailable Products:")
    for p in Product.list_products():
        print(f"{p[0]}: {p[1]} - ${p[2]:.2f} ({p[3]} in stock)")

    # Place orders
    Order.place_order("alice", 1, 2)  # Alice buys 2 Laptops
    Order.place_order("bob", 2, 1)  # Bob buys 1 Smartphone

    # List orders
    print("\nAlice's Orders:")
    for o in Order.list_orders("alice"):
        print(f"Order #{o[0]}: {o[1]} x{o[2]} - ${o[3]:.2f} (Ordered on {o[4]})")

    print("\nBob's Orders:")
    for o in Order.list_orders("bob"):
        print(f"Order #{o[0]}: {o[1]} x{o[2]} - ${o[3]:.2f} (Ordered on {o[4]})")
"""]

    repo_structure = """
backend/
    app.py
    database.py
    auth/
        __init__.py
        login.py
        register.py
    api/
        __init__.py
        user_routes.py
        product_routes.py
        order_routes.py
    models/
        __init__.py
        user.py
        product.py
        order.py
    utils/
        logging.py
        security.py
frontend/
    components/
        Navbar.js
        Footer.js
        Dashboard.js
        Profile.js
    pages/
        Home.js
        Checkout.js
        Orders.js
    styles/
        global.css
        themes.css
configs/
    config.json
    secrets.json
tests/
    test_auth.py
    test_api.py
    test_database.py
docs/
    README.md
    API_REFERENCE.md
    CHANGELOG.md
requirements.txt
Dockerfile
.env
"""






    print("\n======================== RUNNING TESTS ========================\n")

    # Test structured code summarization
    structured_summary, structured_time = measure_time(summarize_code_blocks, code_samples)
    print("\n🔹 **Structured Code Summarization:**")
    print(structured_summary)
    print(f"⏱ **Time Taken:** {structured_time:.2f} seconds")

    # # Test baseline code summarization
    # baseline_summary, baseline_time = measure_time(baseline_summarize_code_blocks, code_samples)
    # print("\n🔹 **Baseline Code Summarization:**")
    # print(baseline_summary)
    # print(f"⏱ **Time Taken:** {baseline_time:.2f} seconds")

    # Test structured repository analysis
    structured_analysis, structured_analysis_time = measure_time(analyze_repo_structure, repo_structure)
    print("\n🔹 **Structured Repository Analysis:**")
    print(structured_analysis)
    print(f"⏱ **Time Taken:** {structured_analysis_time:.2f} seconds")

    # # Test baseline repository analysis
    # baseline_analysis, baseline_analysis_time = measure_time(baseline_analyze_repo_structure, repo_structure)
    # print("\n🔹 **Baseline Repository Analysis:**")
    # print(baseline_analysis)
    # print(f"⏱ **Time Taken:** {baseline_analysis_time:.2f} seconds")

    print("\n======================== TESTS COMPLETED ========================\n")
