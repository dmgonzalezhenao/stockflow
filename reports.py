"""
Inventory Reporting and Analytics Module
----------------------------------------
This module centralizes all data retrieval logic for the dashboard and
monitoring sections of the application.

Key Responsibilities:
- Data Aggregation: Calculates real-time stock levels and inventory valuation.
- Audit Visibility: Provides full access to the system logs and transaction history.
- KPI Generation: Summarizes complex data into simple metrics (Key Performance Indicators)
  for the Single Page Application (SPA) frontend.
"""
# Import math library for calculate logs quantity to show
import math

# Import the function to log system errors
from helpers import log_system_error

# Get all the products, it's current stock, value
def get_stock_report(db, page = 1, per_page = 10):
    try:
        # Validate input and equals to 1
        if page < 1: page = 1

        # Get count of pagination if product is active}
        total_res = db.execute("SELECT COUNT(*) as count FROM products WHERE is_active = 1")

        # Get the numeric value
        total_count = total_res[0]["count"] if total_res else 0

        # Show the product in a new page even is it's only one
        total_pages = math.ceil(total_count / per_page)

        # If user inputs a page bigger than the existing
        if page > total_pages and total_pages > 0:
            # Return the last one
            page = total_pages

        # Skip calculation
        offset = (page - 1) * per_page

        # Get the stock, quantity total and limit and offset

        stock = db.execute("""
            SELECT p.id, p.name, p.sku, p.price, p.reorder_level,
                   COALESCE(SUM(t.quantity), 0) AS current_stock
            FROM products p
            LEFT JOIN transactions t ON p.id = t.product_id
            WHERE p.is_active = 1
            GROUP BY p.id, p.name, p.sku, p.price, p.reorder_level
            ORDER BY p.name ASC
            LIMIT ? OFFSET ?
        """, per_page, offset)

        # Alerts processes
        for item in stock:
            current = item["current_stock"] or 0
            reorder = item["reorder_level"] or 0

            # Alert if stock <= to reorder level
            item["alert"] = current <= reorder

            # Out of stock: stock is exactly 0
            item["out_of_stock"] = current == 0

        # Return the values to show them in the index
        return {
            "products": stock,
            "total_pages": total_pages,
            "current_page": page
        }

    except Exception as e:
        # Try to log the error into logs table
        print(f"Error in get_stock_report: {e}")

        # Return empty data for not breaking the page
        return {"products": [], "total_pages": 1, "current_page": 1}

# Get the complete activity history for the logs table (Gets only a few by page)
def get_transaction_logs(db, page=1):
    try:
        # Logs number to show per page
        PER_PAGE = 10

        # Skip value
        offset = (page - 1) * PER_PAGE

        # Get the logs with limit and skip
        logs = db.execute(""" SELECT id, type, action, description, timestamp
                        FROM logs
                        ORDER BY "timestamp" DESC
                        LIMIT ? OFFSET ?
                        """, PER_PAGE, offset)

        # Total pages calculation and total rows or actual page
        total_rows = db.execute("SELECT COUNT(*) as count FROM logs")[0]['count']
        total_pages = (total_rows + PER_PAGE - 1) // PER_PAGE

        # Return logs, total pages and actual page
        return logs, total_pages, page

    except Exception as e:
        # Print for developer
        print(f"Error in get_transaction_logs: {e}")

        # Log the error and try to introduce in logs table (Returns the first page)
        log_system_error(db, e, action="GET_TRANSACTION_LOGS_FAIL")
        return [], 1, 1

# Calculates KPI cards data for dashboard
def get_inventory_summary(db):
    try:
        # Complete query of total_items, total_value and low_stock_count
        query = """
            SELECT
                COUNT(*) as total_items,
                SUM(current_stock * price) as total_value,
                SUM(CASE WHEN current_stock <= reorder_level THEN 1 ELSE 0 END) as low_stock_count
            FROM (
                SELECT p.price, p.reorder_level, COALESCE(SUM(t.quantity), 0) AS current_stock
                FROM products p
                LEFT JOIN transactions t ON p.id = t.product_id
                WHERE p.is_active = 1
                GROUP BY p.id
            )
        """

        # Gets the first element
        res = db.execute(query)[0]

        # Return the values into a dictionarie
        return {
            "total_items": res["total_items"] or 0,
            "total_value": round(res["total_value"] or 0, 2),
            "low_stock_count": res["low_stock_count"] or 0
        }

    except Exception as e:
        # Print for developer
        print(f"Error in get_inventory_summary: {e}")

        #Try to log into logs table
        log_system_error(db, e, action="GET_INVENTORY_SUMMARY_FAIL")

        # Return empty values
        return {"total_items": 0, "total_value": 0.0, "low_stock_count": 0}
