-- Schema for Inventory Management System

-- Products table: Information about products in inventory
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sku TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    reorder_level INTEGER DEFAULT 5,
    price REAL NOT NULL,
    is_active INTEGER DEFAULT 1
);

-- Transactions table: Records of stock movements
CREATE TABLE IF NOT EXISTS transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL,
    type TEXT CHECK(type IN ('IN', 'OUT')) NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products(id),
    -- Integrity checks
    CONSTRAINT check_quantity_logic CHECK (
        (type = 'IN' AND quantity > 0) OR
        (type = 'OUT' AND quantity < 0)
    )
);

-- Logs table: All logs of system and user actions
CREATE TABLE IF NOT EXISTS logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    type TEXT CHECK(type IN ('SYSTEM', 'USER')) NOT NULL,
    action TEXT NOT NULL,
    description TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Extra index for faster execution
CREATE INDEX IF NOT EXISTS idx_transactions_product ON transactions(product_id);
