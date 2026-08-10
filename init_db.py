import sqlite3

def init_database():
    conn = sqlite3.connect('erp_database.db')
    cursor = conn.cursor()

    sql_schema = """
    CREATE TABLE IF NOT EXISTS partners (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        code VARCHAR(50) UNIQUE NOT NULL,
        name VARCHAR(150) NOT NULL,
        type VARCHAR(20) NOT NULL CHECK (type IN ('CUSTOMER', 'VENDOR', 'BOTH')),
        email VARCHAR(100),
        phone VARCHAR(50)
    );

    CREATE TABLE IF NOT EXISTS items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        code VARCHAR(50) UNIQUE NOT NULL,
        name VARCHAR(150) NOT NULL,
        type VARCHAR(30) NOT NULL CHECK (type IN ('RAW_MATERIAL', 'SUBASSEMBLY', 'FINISHED_GOOD')),
        unit_of_measure VARCHAR(20) DEFAULT 'BUC',
        min_stock REAL DEFAULT 0,
        cost_price REAL DEFAULT 0
    );

    CREATE TABLE IF NOT EXISTS boms (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        parent_item_id INTEGER NOT NULL,
        child_item_id INTEGER NOT NULL,
        quantity REAL NOT NULL,
        FOREIGN KEY (parent_item_id) REFERENCES items(id) ON DELETE CASCADE,
        FOREIGN KEY (child_item_id) REFERENCES items(id)
    );
    """

    cursor.executescript(sql_schema)
    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_database()
