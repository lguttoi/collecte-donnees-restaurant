import sqlite3
import os
import hashlib

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "restaurant.db")

def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = get_conn()
    c = conn.cursor()

    c.executescript("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role TEXT NOT NULL DEFAULT 'staff',
        full_name TEXT,
        phone TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        active INTEGER DEFAULT 1
    );

    CREATE TABLE IF NOT EXISTS categories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        color TEXT DEFAULT '#FF6B35'
    );

    CREATE TABLE IF NOT EXISTS menu_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        description TEXT,
        price REAL NOT NULL,
        category_id INTEGER,
        available INTEGER DEFAULT 1,
        FOREIGN KEY (category_id) REFERENCES categories(id)
    );

    CREATE TABLE IF NOT EXISTS tables (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        number INTEGER UNIQUE NOT NULL,
        capacity INTEGER DEFAULT 4,
        status TEXT DEFAULT 'libre',
        section TEXT DEFAULT 'Salle Principale'
    );

    CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        table_id INTEGER,
        user_id INTEGER,
        client_name TEXT,
        status TEXT DEFAULT 'en_cours',
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
        notes TEXT,
        total REAL DEFAULT 0,
        FOREIGN KEY (table_id) REFERENCES tables(id),
        FOREIGN KEY (user_id) REFERENCES users(id)
    );

    CREATE TABLE IF NOT EXISTS order_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id INTEGER NOT NULL,
        menu_item_id INTEGER NOT NULL,
        quantity INTEGER DEFAULT 1,
        unit_price REAL NOT NULL,
        notes TEXT,
        status TEXT DEFAULT 'en_attente',
        FOREIGN KEY (order_id) REFERENCES orders(id),
        FOREIGN KEY (menu_item_id) REFERENCES menu_items(id)
    );

    CREATE TABLE IF NOT EXISTS reservations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        client_name TEXT NOT NULL,
        phone TEXT,
        email TEXT,
        date TEXT NOT NULL,
        time TEXT NOT NULL,
        guests INTEGER DEFAULT 2,
        table_id INTEGER,
        status TEXT DEFAULT 'confirmee',
        notes TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (table_id) REFERENCES tables(id)
    );

    CREATE TABLE IF NOT EXISTS invoices (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id INTEGER NOT NULL,
        invoice_number TEXT UNIQUE NOT NULL,
        total_ht REAL NOT NULL,
        tva REAL DEFAULT 0,
        total_ttc REAL NOT NULL,
        payment_method TEXT DEFAULT 'especes',
        paid_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (order_id) REFERENCES orders(id)
    );

    CREATE TABLE IF NOT EXISTS expenses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        label TEXT NOT NULL,
        amount REAL NOT NULL,
        category TEXT DEFAULT 'General',
        date TEXT DEFAULT CURRENT_DATE,
        notes TEXT
    );
    """)

    c.execute("SELECT id FROM users WHERE username='admin'")
    if not c.fetchone():
        c.execute("INSERT INTO users (username,password,role,full_name,phone) VALUES (?,?,?,?,?)",
                  ('admin', hash_password('admin123'), 'admin', 'Administrateur', '+237 000 000 000'))
        c.execute("INSERT INTO users (username,password,role,full_name,phone) VALUES (?,?,?,?,?)",
                  ('serveur1', hash_password('1234'), 'staff', 'Marie Ngono', '+237 655 000 001'))
        c.execute("INSERT INTO users (username,password,role,full_name,phone) VALUES (?,?,?,?,?)",
                  ('caissier', hash_password('1234'), 'caissier', 'Paul Ndongo', '+237 655 000 002'))

    c.execute("SELECT id FROM categories LIMIT 1")
    if not c.fetchone():
        cats = [('Entrees','#4CAF50'),('Plats Principaux','#FF6B35'),
                ('Desserts','#E91E8C'),('Boissons','#2196F3'),
                ('Vins et Alcools','#9C27B0'),('Menus Speciaux','#FF9800')]
        c.executemany("INSERT INTO categories (name,color) VALUES (?,?)", cats)

    c.execute("SELECT id FROM menu_items LIMIT 1")
    if not c.fetchone():
        items = [
            ('Salade Cesar','Salade romaine, parmesan, croutons',8500,1,1),
            ('Soupe du Jour','Soupe maison du jour',5500,1,1),
            ('Crevettes Grillees','Crevettes marinees aux herbes',12000,1,1),
            ('Nems au Poulet','4 nems croustillants sauce aigre-douce',9000,1,1),
            ('Poulet Roti','Demi-poulet, frites maison, salade',15000,2,1),
            ('Poisson Braise','Tilapia braise, riz, plantain frit',18000,2,1),
            ('Cote de Boeuf','300g cote de boeuf, legumes de saison',28000,2,1),
            ('Ndole Complet','Ndole aux crevettes, viande, miondo',16000,2,1),
            ('Eru Traditionnel','Eru avec waterfufu',14000,2,1),
            ('Spaghetti Bolognaise','Pates fraiches, sauce bolognaise',12000,2,1),
            ('Mousse au Chocolat','Mousse legere au chocolat noir',6000,3,1),
            ('Tarte Tropicale','Tarte aux fruits de saison',5500,3,1),
            ('Glace 3 Boules','Choix de parfums',4500,3,1),
            ('Eau Minerale 50cl','Eau minerale plate ou gazeuse',1000,4,1),
            ('Coca-Cola 33cl','Boisson gazeuse',1500,4,1),
            ('Jus Naturel','Jus de fruit presse frais',2500,4,1),
            ('Biere Castel 33cl','Biere locale fraiche',2000,4,1),
            ('Cafe Expresso','Cafe arabica premium',2000,4,1),
            ('Vin Rouge Maison','Verre 15cl',4500,5,1),
            ('Vin Blanc Maison','Verre 15cl',4500,5,1),
            ('Bouteille Bordeaux','75cl, AOC Bordeaux',35000,5,1),
            ('Menu Dejeuner','Entree + Plat + Dessert',18000,6,1),
            ('Menu Famille','2 adultes + 2 enfants',45000,6,1),
        ]
        c.executemany("INSERT INTO menu_items (name,description,price,category_id,available) VALUES (?,?,?,?,?)", items)

    c.execute("SELECT id FROM tables LIMIT 1")
    if not c.fetchone():
        tables = []
        for i in range(1, 9):
            tables.append((i, 4, 'libre', 'Salle Principale'))
        for i in range(9, 13):
            tables.append((i, 2, 'libre', 'Terrasse'))
        for i in range(13, 16):
            tables.append((i, 8, 'libre', 'Salon Prive'))
        c.executemany("INSERT INTO tables (number,capacity,status,section) VALUES (?,?,?,?)", tables)

    conn.commit()
    conn.close()

def authenticate(username, password):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username=? AND password=? AND active=1",
              (username, hash_password(password)))
    user = c.fetchone()
    conn.close()
    return dict(user) if user else None
