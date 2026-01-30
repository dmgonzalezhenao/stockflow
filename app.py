"""
Main Application Controller - Inventory Management System
---------------------------------------------------------
This module serves as the central hub (Controller) for the Flask-based
Single Page Application (SPA). It manages the web routing, request
handling, and connects the user interface with the underlying service layers.

Key Responsibilities:
- Route Orchestration: Defines GET/POST endpoints for dashboard and CRUD actions.
- Dependency Injection: Initializes the SQL database and integrates 'logic',
  'reports', and 'importer' modules.
- Request Processing: Extracts and validates user input from web forms.
- Session Feedback: Manages user notifications via Flask's flashing system.

Design Principle:
The application follows a clean separation of concerns, keeping the routes
lightweight by delegating business rules to 'logic.py' and data retrieval
to 'reports.py'.
"""

# Import necessary libraries for Flask, SQLite
from flask import Flask, flash, redirect, render_template, request, url_for, jsonify

# Import the other modules for business logic
import logic
import reports
import helpers

# Configure Flask app
app = Flask(__name__)

# Secret Key to use flash
app.secret_key = "my_s3cr3t_k3y_f0r_cs50"

# Ensure templates are auto-reloaded when changed
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Initialize the CS50 SQL object to connect to your local database file
# If it doesn't exist, init_db will create it
db = helpers.init_db()

if not db:
    # If something goes wrong with Database creation, print an error
    raise RuntimeError("Cannot be possible es")

# Index route (Only get method, but with many data)
@app.route('/')
def index():
    # Validate type and page value
    page = request.args.get('page', 1, type=int)

    # Detect if it's an ajax request
    is_ajax = request.args.get('ajax')

    try:
        # Get the stock of products data (10 products selected)
        stock_data = reports.get_stock_report(db, page=page)

        # Redirect to the main page if page doesn't equal to the stock data page
        if page != stock_data["current_page"]:
            return redirect(url_for('index', page=stock_data["current_page"]))

        # Use a little HTMl file that contains products table and it's into index
        if is_ajax:
            return render_template("partials/stock_table.html",
                                   stock=stock_data["products"],
                                   total_pages=stock_data["total_pages"],
                                   current_page=stock_data["current_page"])

        # Gets summary to show in dashboard
        summary = reports.get_inventory_summary(db)

        # Gets the full stock list to select into buy and sell modals (Use a big value to select most products possible)
        full_stock_list = reports.get_stock_report(db, page=1, per_page=1000000)

        # Render index with summary, products to show in table and products to select
        return render_template("index.html",
                               summary=summary,
                               stock=stock_data["products"],
                               full_stock_list=full_stock_list["products"],
                               total_pages=stock_data["total_pages"],
                               current_page=stock_data["current_page"])

    # Flash error if something goes wrong on dashboard loading
    except Exception as e:
        print(f"Error loading dashboard: {e}")
        flash("Could not load latest data.", "danger")

        # Tries to log the error into logs table
        try:
            helpers.log_system_error(db, e, action="GET_INDEX_FAIL")

        except:
        # Else print for developer
            print("Double Fault: Could not write error to logs table.")

        # Show error for ajax case
        if is_ajax:
            return "<div class='alert alert-danger'>Error al cargar los datos.</div>", 500

        # Return index without data
        return render_template("index.html",
                               summary={},
                               stock=[],
                               full_stock_list=[],
                               total_pages=1,
                               current_page=1)

# Function to add a new product
@app.route("/add_product", methods=["POST"])
def add_product():
    # Get data from form
    name = request.form.get("name")
    sku = request.form.get("sku")
    price = request.form.get("price")
    initial_stock = request.form.get("initial_stock") or 0
    reorder_level = request.form.get("reorder_level") or 5

    # Get the values from add product function
    success, message, product_id = logic.add_product(db, name, sku, price, initial_stock, reorder_level)

    # Success is a boolean that it's True if everything goes good on product insertion
    if success:
        # Get the new summary values to show them in the page
        new_summary = reports.get_inventory_summary(db)

        # Return JSON to send them to script.js
        return jsonify({
            "success": True,
            "message": message,
            "product": {
                "id": product_id,
                "name": name.strip(),
                "sku": sku.strip().upper(),
                "price": float(price if price else 0),
                "current_stock": int(initial_stock if initial_stock else 0),
                "reorder_level": int(reorder_level if reorder_level else 5)
            },
            "summary": new_summary
        })

    # Returns error message and error code (400)
    return jsonify({
        "success": False,
        "message": message
    }), 400

# Route for buy stock
@app.route("/buy", methods=["POST"])
def buy_product():
    # Get the values from index form
    product_id = request.form.get("product_id")
    quantity = request.form.get("quantity")

    # String type to validate transaction in logic.py
    type = 'IN'

    # Inserts transaction and get success, message, new stock, a validation for lower stock, and a buy description
    success, message, new_stock, reorder_level = logic.add_transaction(db, product_id, quantity, type)

    # If everything goes good
    if success:
        return jsonify({
            "success": True,
            "message": message,
            "product_id": int(product_id),
            "new_stock": new_stock,
            "status": "Ok" if new_stock > reorder_level else "Pedir más",
            "summary": reports.get_inventory_summary(db),
        })

    # Else return these values to scripts
    return jsonify({"success": False, "message": message}), 400

# Route to sell products
@app.route("/sell", methods=["POST"])
def sell_product():
    # Get the values from index form
    product_id = request.form.get("product_id")
    quantity = request.form.get("quantity")

    # String to validate transaction into logic.py (Quantity must be lower than actual stock)
    type = 'OUT'

    # Inserts transaction and get success, message, new stock, a validation for low stock and log description
    success, message, new_stock, reorder_level = logic.add_transaction(db, product_id, quantity, type)

    # If everything goes good
    if success:
        return jsonify({
            "success": True,
            "message": message,
            "product_id": int(product_id),
            "new_stock": new_stock,
            "status": "Ok" if new_stock > reorder_level else "Pedir más",
            "summary": reports.get_inventory_summary(db),
        })

    # Else return these values to scripts
    return jsonify({"success": False, "message": message}), 400

# Function to logs page
@app.route('/logs')
def view_logs():
    try:
        # Gets the actual page
        page = request.args.get('page', 1, type=int)

        # Gets ajax for SPA function
        is_ajax = request.args.get('ajax')

        # Gets logs, total values and page to show them in the logs page
        logs, total_pages, current_page = reports.get_transaction_logs(db, page = page)

        # Use a new little template that only shows the logs table
        if is_ajax:
        # Returns just this template
            return render_template("partials/logs_table.html", logs=logs, total_pages=total_pages, current_page=current_page)

        # Returns all logs page
        return render_template("logs.html", logs=logs, total_pages=total_pages, current_page=current_page)


    except Exception as e:
        # If something goes wrong, redirect to index and flash the error
        print(f"Error loading logs: {e}")
        flash("Could not load history.", "danger")
        return redirect(url_for('index'))
