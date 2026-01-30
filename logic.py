"""
Logic Module - Inventory Business Engine
----------------------------------------
This module handles all state-changing operations (Write/Update) for the
inventory system. It ensures data integrity and enforces business rules.

Key Responsibilities:
- Transactional Integrity: Manages IN/OUT movements and prevents negative stock.
- Product Lifecycle: Handles creation, updates, and soft-deletion (deactivation).
- Input Sanitization: Protects against XSS and ensures data types are valid.
- Audit Logging: Records every human-initiated action for accountability.

Note: All functions return a (Boolean, String) tuple for easy feedback in Flask.
"""
# Import a Flask function for security
import markupsafe

# Import helpers functions
from helpers import log_system_error

# Manually add inventory movement (IN/OUT)
def add_transaction(db, product_id, quantity, type):
    try:
        # 1. A- Validate the product id
        rows = db.execute("""
            SELECT p.name, p.sku, p.is_active, p.reorder_level, COALESCE(SUM(t.quantity), 0) AS current_stock
            FROM products p
            LEFT JOIN transactions t ON p.id = t.product_id
            WHERE p.id = ?
            GROUP BY p.id
        """, product_id)

        if len(rows) == 0:
            return False, "Product does not exist.", None, None

        elif len(rows) != 1:
            return False, "Invalid ID.", None, None

        product = rows[0]

        # 1. B- Validate type and quantity
        if type not in ['IN', 'OUT']:
            raise ValueError("Transaction type must be 'IN' or 'OUT'")

        try:
            quantity = int(quantity)

        except (ValueError, TypeError):
            return False, "Quantity must be a valid whole number.", None, None

        if quantity <= 0:
            return False, "Quantity must be a positive number (greater than zero).", None, None,

        # 1. C- Validate product status (Business Rule)
        if product["is_active"] == 0:
            return False, "Cannot move stock: Product is deactivated.", None, None

        # 1. D- Validate stock for OUT operations
        if type == 'OUT' and quantity > product["current_stock"]:
            return False, f"Insufficient stock. Current: {product['current_stock']}", None, None

        # 2. A- Business rule: Quantity sign based on type
        quantity = -abs(quantity) if type == 'OUT' else abs(quantity)

        # 2. B- Gets the new stock value and reorder_level
        new_stock = product["current_stock"] + quantity
        reorder_level = product['reorder_level']

        if new_stock < 0:
            return False, "Error: Stock cannot be negative", None, None

        # 3. A- Insert transaction record into the transactions table (product by id, quantity, and it´s type by quantity sign)
        db.execute(""" INSERT INTO transactions (product_id, quantity, type)
                    VALUES (?, ?, ?) """,
                    product_id, quantity, type)

        # 3. B- Log the human action into logs table
        action_description = f"{type} {abs(quantity)} units for {product['name']} (SKU: {product['sku']})"
        db.execute(""" INSERT INTO logs (type, action, description)
                    VALUES (?, ?, ?) """,
                    'USER', 'MANUAL_MOVE', action_description)

        # Return true for validate operation on app.py
        return True, "Success", new_stock, reorder_level

    except ValueError as ve:
        # Print for developer
        print(f"Error in add_transaction: {ve}")

        # Returns false for validate operation on app.py
        return False, str(ve), None, None

    except Exception as e:
        # Print for developer
        print(f"Error in add_transaction: {e}")

        # Log the error and try to introduce in logs table
        log_system_error(db, e, action="ADD_TRANSACTION_FAIL")

        # Return error message with None values to avoid errors
        return False, "Internal Server Error", None, None

# Create a new product
def add_product(db, name, sku, price, initial_stock = 0, reorder_level = 5):
    try:
        try:
            # Check the price, initial stock and reorder values
            price = float(price)
            reorder_level = int(reorder_level)
            initial_stock = int(initial_stock)

        except (ValueError, TypeError):
            # Return false and error's reason
            return False, "Price, initial stock and reorder must be valid numbers.", None

        # Validate non negative values
        if price < 0 or reorder_level < 0 or initial_stock < 0:
            return False, "Numeric values cannot be negative.", None

        # Validate the name and sku values
        name = name.strip()
        sku = sku.strip().upper()

        if not name or not sku:
            return False, "Name and SKU cannot be empty", None

        # Prevent script running
        name = markupsafe.escape(name)

        # Database has an index on SKU, so it's not necessary to handle duplicates
        # The variable it's ID of the new product
        new_id = db.execute("""
            INSERT INTO products (name, sku, price, reorder_level)
            VALUES (?, ?, ?, ?)
        """, name, sku, price, reorder_level)

        # Log the stock value into transactions and register in logs table
        if initial_stock > 0:
            db.execute("""INSERT INTO transactions
                       (product_id, quantity, type)
                       VALUES (?, ?, ?)""",
                       new_id, initial_stock, 'IN')
            action_description = f"Added new product {name} (SKU: {sku}) with initial stock: {initial_stock}"
            db.execute(""" INSERT INTO logs (type, action, description)
                    VALUES (?, ?, ?) """,
                    'USER', 'ADD_INITIAL_STOCK', action_description)

        # Log the succesful move if doesn't have initial stock
        elif initial_stock == 0:
            action_description = f"Added new product: {name} (SKU: {sku}) with initial stock: 0"
            db.execute(""" INSERT INTO logs (type, action, description)
                        VALUES (?, ?, ?) """,
                        'USER', 'PRODUCT_CREATE', action_description)

        # Return true to app.py and a success message
        return True, "Product created successfully", new_id

    except Exception as e:
        # Automathic message of SQLite if sku is already in use
        if "UNIQUE constraint failed" in str(e):
            return False, f"The SKU '{sku}' is already in use. Please use a different one.", None

        # If it's another error type
        # Print for developer
        print(f"Error in add_product: {e}")

        # Register into logs table
        log_system_error(db, e, action="ADD_PRODUCT_FAIL")
        return False, "An internal error occurred while creating the product.", None
