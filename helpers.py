"""
Helpers Module - Infrastructure & Support Utilities
--------------------------------------------------
This module provides low-level support for the application, including:
- Database schema initialization (Auto-setup on startup).
- System-level error logging for debugging and maintenance.
- Cross-functional utility tools used by the Service Layer.
"""

# Import os for files manipulation
import os
from cs50 import SQL

# Init the database if it's the first time you use the program
def init_db():
    try:
        # Database name and schema file
        db_path = "inventory.db"
        schema_path = os.path.join("sql", "schema.sql")

        # Create database if doesn't exist
        if not os.path.exists(db_path):
            open(db_path, "w").close()
            print(f"File {db_path} created")

        # Connect with CS50 host
        db_connection = SQL(f"sqlite:///{db_path}")

    # If something goes wrong
    except Exception as e:
        print(f"Critical error during DB creation: {e}")

    if os.path.exists(schema_path):
        with open(schema_path, "r") as f:
            # Separate commands by ; to execute them one by one
            commands = f.read().split(";")

            # Execute every command
            for command in commands:
                # Clean command and execute it
                clean_command = command.strip()
                if clean_command:
                    db_connection.execute(clean_command)

        # Return the database connection to app.py
        print("Database initialized from schema.sql.")
        return db_connection

    else:
        # If someway you delete schema.sql, and it's int the roor directory
        print(f"Warning: {schema_path} not found. Ensure the file exists in the root directory.")


# Centralized function to record technical failures
# Inputs: Database connection, the exception object captures in the try/except block
# and a string label to identify the error's source
def log_system_error(db, error, action="GENERAL_ERROR"):
    try:
        # Convert the error object to a string to store it
        error_details = str(error)

        # Attempt to insert into the logs table
        # We use 'SYSTEM' type to distinguish these from manual user actions
        db.execute("""
            INSERT INTO logs (type, action, description)
            VALUES (?, ?, ?)
        """, 'SYSTEM', action, f"Technical Failure: {error_details}")

        # Also print to the server console for immediate debugging during development
        print(f"\n[SYSTEM LOG] {action}: {error_details}\n")

    except Exception as e:
        # This block only runs if the database itself is unreachable or the logs table fails
        print("\n!!! CRITICAL INFRASTRUCTURE ERROR !!!")
        print(f"Could not write log to DB. Original error: {error}")
        print(f"Logging attempt failed due to: {e}\n")
