import streamlit as st
import sqlite3
import pandas as pd
import os
from datetime import datetime
import streamlit.components.v1 as components

# 1. Configurare Pagină
st.set_page_config(page_title="CAN Prod System", layout="wide", initial_sidebar_state="collapsed")

# 2. Reparare și Inițializare Bază de Date Completa
def init_and_repair_db():
    conn = sqlite3.connect('erp_database.db')
    cursor = conn.cursor()
    
    # Items
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        code VARCHAR(100) UNIQUE NOT NULL,
        name VARCHAR(255) NOT NULL,
        type VARCHAR(50) DEFAULT 'RAW_MATERIAL',
        unit_of_measure VARCHAR(20) DEFAULT 'pcs',
        storage_location VARCHAR(100) DEFAULT '-',
        current_stock REAL DEFAULT 0.0,
        min_stock REAL DEFAULT 0.0,
        cost_price REAL DEFAULT 0.0,
        selling_price REAL DEFAULT 0.0
    );
    """)

    # Product Groups
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS product_groups (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        number VARCHAR(50) UNIQUE NOT NULL,
        name VARCHAR(255) NOT NULL
    );
    """)

    # Units of Measurement
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS units_of_measurement (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name VARCHAR(50) UNIQUE NOT NULL
    );
    """)

    # Unit Conversions
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS unit_conversions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        uom_id INTEGER NOT NULL,
        target_uom VARCHAR(50) NOT NULL,
        rate REAL NOT NULL,
        FOREIGN KEY (uom_id) REFERENCES units_of_measurement(id) ON DELETE CASCADE
    );
    """)

    # Storage Locations / Clienți
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS storage_locations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name VARCHAR(100) UNIQUE NOT NULL,
        site VARCHAR(100) DEFAULT 'Main site',
        barcode VARCHAR(100) DEFAULT '-'
    );
    """)

    # Operations Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS operations_list (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name VARCHAR(255) NOT NULL,
        type VARCHAR(100) NOT NULL,
        hourly_rate REAL DEFAULT 0.0
    );
    """)

    # Customer Orders Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS customer_orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        number VARCHAR(50) UNIQUE NOT NULL,
        customer_number VARCHAR(50) NOT NULL,
        customer_name VARCHAR(255) NOT NULL,
        status VARCHAR(50) DEFAULT 'Confirmed',
        product_status VARCHAR(50) DEFAULT 'Not booked',
        invoice_status VARCHAR(50) DEFAULT 'Not invoiced',
        payment_status VARCHAR(50) DEFAULT 'Not paid',
        created_date DATE,
        delivery_date DATE
    );
    """)

    # Customers Table (Extinsă conform Pozei optiuni client.JPG)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS customers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        number VARCHAR(50) UNIQUE NOT NULL,
        name VARCHAR(255) NOT NULL,
        status VARCHAR(100) DEFAULT 'No contact',
        reg_no VARCHAR(100),
        vat_number VARCHAR(100),
        contact_started DATE,
        next_contact DATE,
        account_manager VARCHAR(255) DEFAULT 'General',
        phone VARCHAR(100),
        email VARCHAR(255),
        web VARCHAR(255),
        pricelist_number VARCHAR(50),
        pricelist_name VARCHAR(255) DEFAULT 'Default pricelist',
        tax_rate REAL DEFAULT 0.0,
        default_discount REAL DEFAULT 0.0,
        payment_period INTEGER DEFAULT 0,
        trade_credit_limit REAL DEFAULT 0.0,
        language VARCHAR(50) DEFAULT 'English',
        currency VARCHAR(10) DEFAULT '€'
    );
    """)

    # Customer Contacts
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS customer_contacts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id INTEGER NOT NULL,
        name VARCHAR(255) NOT NULL,
        position VARCHAR(100),
        phone VARCHAR(100),
        teams VARCHAR(100),
        email VARCHAR(255),
        FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE CASCADE
    );
    """)

    # Customer Notes
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS customer_notes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id INTEGER NOT NULL,
        note TEXT NOT NULL,
        created_date DATETIME DEFAULT CURRENT_TIMESTAMP,
        modified_date DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE CASCADE
    );
    """)

    # Populare implicită UoM
    cursor.execute("SELECT COUNT(*) FROM units_of_measurement")
    if cursor.fetchone()[0] == 0:
        default_uoms = ['kg', 'l', 'm2', 'Ml', 'Ore', 'pcs', 'SET', 'BUC']
        for u in default_uoms:
            cursor.execute("INSERT OR IGNORE INTO units_of_measurement (name) VALUES (?)", (u,))

    # Populare implicită Groups
    cursor.execute("SELECT COUNT(*) FROM product_groups")
    if cursor.fetchone()[0] == 0:
        default_groups = [
            ('1', 'RAW MATERIAL'),
            ('2', 'PRODUSE FINITE'),
            ('3', 'BUY PARTS'),
            ('4', 'Servici'),
            ('5', 'RFQ'),
            ('6', 'INOX'),
            ('7', 'RAW MATERIAL ZINCAT')
        ]
        for num, name in default_groups:
            cursor.execute("INSERT OR IGNORE INTO product_groups (number, name) VALUES (?, ?)", (num, name))

    # Populare implicită Operații
    cursor.execute("SELECT COUNT(*) FROM operations_list")
    if cursor.fetchone()[0] == 0:
        default_ops = [
            ('BUCSARE (1)', 'BUCSARE', 20.0),
            ('Debitare Fierastrau (1)', 'Debitare Fierastrau', 35.0),
            ('Gaurire/Zencuire (1)', 'Gaurire/Zencuire', 35.0),
            ('IMPACHETARE (1)', 'IMPACHETARE', 20.0),
            ('INDOIRE (1)', 'INDOIRE', 100.0),
            ('Lacuit MDF (1)', 'Lacuit MDF', 1200.0),
            ('Manipulare (1)', 'Manipulare', 15.0),
            ('Outsourcing (1)', 'Outsourcing', 60.0),
            ('Pipe Laser Cutting (1)', 'Pipe_Laser_Cutting', 100.0),
            ('Plate Laser Cutting (1)', 'Plate_Laser_Cutting', 100.0),
            ('Roluire_Teava (1)', 'Roluire_Teava', 30.0),
            ('Slefuire (1)', 'Slefuire', 28.0),
            ('Slefuire (2)', 'Slefuire', 28.0),
            ('Virolare_tabla (1)', 'Virolare_Tabla', 30.0),
            ('VOPSIRE (1)', 'VOPSIRE', 600.0),
            ('Vopsire Lichida', 'Vopsire Lichida', 420.0),
            ('Welding (1)', 'Welding', 35.0),
            ('Welding (2)', 'Welding', 35.0),
            ('Welding (3)', 'Welding', 35.0)
        ]
        for n, t, r in default_ops:
            cursor.execute("INSERT INTO operations_list (name, type, hourly_rate) VALUES (?, ?, ?)", (n, t, r))

    conn.commit()
    conn.close()

init_and_repair_db()

def get_connection():
    return sqlite3.connect('erp_database.db')

# Funcție Automată de Generare Cod de Bare MRPeasy
def generate_storage_barcode(conn, location_name):
    cursor = conn.cursor()
    cursor.execute("SELECT MAX(id) FROM storage_locations")
    res = cursor.fetchone()[0]
    next_id = (res + 1) if res else 1
    prefix_name = location_name.strip()[:10]
    return f"99{prefix_name}91loc92{next_id}"

# Funcție Import Customers din CSV
def process_customers_csv(df):
    cursor = conn.cursor()
    imported_count = 0
    updated_count = 0
    df.columns = [str(col).strip().lower() for col in df.columns]
    
    for _, row in df.iterrows():
        c_num = str(row.get('number', '')).strip()
        if not c_num or c_num == 'nan':
            continue
            
        c_name = str(row.get('name', c_num)).strip()
        c_status = str(row.get('status', 'No contact')).strip()
        if not c_status or c_status == 'nan':
            c_status = 'No contact'
            
        c_reg = str(row.get('reg. no.', row.get('reg_no', ''))).strip()
        if c_reg == 'nan': c_reg = None
        
        c_vat = str(row.get('tax/vat number', row.get('vat_number', ''))).strip()
        if c_vat == 'nan': c_vat = None

        c_manager = str(row.get('account manager', 'General')).strip()
        if not c_manager or c_manager == 'nan': c_manager = 'General'

        c_phone = str(row.get('phone', ''))
        if c_phone == 'nan': c_phone = None

        c_email = str(row.get('e-mail', row.get('email', ''))).strip()
        if c_email == 'nan': c_email = None

        c_web = str(row.get('web', '')).strip()
        if c_web == 'nan': c_web = None

        c_pnum = str(row.get('pricelist number', '')).strip()
        if c_pnum == 'nan': c_pnum = None

        c_pname = str(row.get('pricelist name', '')).strip()
        if c_pname == 'nan': c_pname = None

        cursor.execute("SELECT id FROM customers WHERE number = ?", (c_num,))
        existing = cursor.fetchone()
        
        if existing:
            cursor.execute("""
                UPDATE customers 
                SET name=?, status=?, reg_no=?, vat_number=?, account_manager=?, phone=?, email=?, web=?, pricelist_number=?, pricelist_name=?
                WHERE number=?
            """, (c_name, c_status, c_reg, c_vat, c_manager, c_phone, c_email, c_web, c_pnum, c_pname, c_num))
            updated_count += 1
        else:
            cursor.execute("""
                INSERT INTO customers (number, name, status, reg_no, vat_number, account_manager, phone, email, web, pricelist_number, pricelist_name)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (c_num, c_name, c_status, c_reg, c_vat, c_manager, c_phone, c_email, c_web, c_pnum, c_pname))
            imported_count += 1

    conn.commit()
    return imported_count, updated_count

# 3. Preluare Query Params
query_params = st.query_params
current_page = query_params.get("page", "Home")
current_subtab = query_params.get("subtab", "Items")
current_setting = query_params.get("setting", "Product_groups")
prod_tab = query_params.get("prod_tab", "Operations")
rfq_subtab = query_params.get("rfq_subtab", "Customer_orders")
rfq_inner_tab = query_params.get("rfq_inner", "Orders")
cust_inner_tab = query_params.get("cust_inner", "Companies")
edit_cust_id = query_params.get("cust_id", None)
edit_uom_id = query_params.get("uom_id", None)

# 4. CSS STILIZARE REPLICATĂ DUPĂ MRPEASY
st.markdown("""
<style>
    .stApp { background-color: #f8fafc; }
    [data-testid="stSidebar"] { display: none; }

    .top-bar {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 6px 20px;
        background-color: #ffffff;
        border-bottom: 1px solid #e2e8f0;
        margin-bottom: 10px;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }
    .top-bar-left { display: flex; align-items: center; gap: 12px; }
    .logo-text { font-size: 18px; font-weight: 800; color: #2563eb; }
    .top-info { font-size: 11px; color: #94a3b8; }
    .top-bar-right { display: flex; align-items: center; gap: 15px; font-size: 12px; color: #475569; font-weight: 600; }

    .mrp-icon-bar {
        display: flex;
        background-color: #1e62d0;
        padding: 5px 15px;
        gap: 12px;
        align-items: center;
        margin-bottom: 15px;
        border-radius: 4px;
    }
    .mrp-icon-item {
        color: #ffffff;
        font-size: 18px;
        text-decoration: none;
        padding: 4px 8px;
        border-radius: 4px;
        transition: background 0.15s;
    }
    .mrp-icon-item:hover { background-color: #1d4ed8; }

    .mrp-subtabs {
        display: flex;
        gap: 20px;
        border-bottom: 2px solid #e2e8f0;
        padding-bottom: 8px;
        margin-bottom: 15px;
        font-size: 13px;
        font-weight: 600;
    }
    .mrp-subtab-active { color: #2563eb; border-bottom: 2px solid #2563eb; padding-bottom: 8px; text-decoration: none; }
    .mrp-subtab { color: #64748b; text-decoration: none; }
    .mrp-subtab:hover { color: #1e293b; }

    .mrp-inner-subtabs {
        display: flex;
        gap: 15px;
        margin-bottom: 15px;
        font-size: 12px;
        font-weight: 600;
    }
    .mrp-inner-active { color: #2563eb; border-bottom: 2px solid #2563eb; padding-bottom: 4px; text-decoration: none; }
    .mrp-inner-tab { color: #64748b; text-decoration: none; }

    .settings-sidebar {
        background-color: #f1f5f9;
        border-radius: 4px;
        padding: 10px;
        display: flex;
        flex-direction: column;
        gap: 8px;
    }
    .settings-item {
        color: #475569;
        font-size: 13px;
        font-weight: 600;
        text-decoration: none;
        padding: 8px 12px;
        border-radius: 4px;
    }
    .settings-item-active {
        background-color: #e2e8f0;
        color: #2563eb;
        font-size: 13px;
        font-weight: 700;
        text-decoration: none;
        padding: 8px 12px;
        border-radius: 4px;
    }

    .mrp-launchpad {
        display: grid;
        grid-template-columns: repeat(8, 1fr);
        gap: 12px;
        padding: 0 10px;
        margin-bottom: 12px;
    }
    .mrp-card {
        background-color: #2563eb !important;
        border-radius: 4px !important;
        height: 135px !important;
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
        justify-content: center !important;
        text-decoration: none !important;
        padding: 10px !important;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1) !important;
        transition: all 0.15s ease-in-out !important;
        box-sizing: border-box !important;
    }
    .mrp-card-alt { background-color: #3b82f6 !important; }
    .mrp-card:hover { background-color: #1d4ed8 !important; transform: translateY(-2px) !important; }
    .mrp-circle {
        width: 48px !important;
        height: 48px !important;
        background-color: #ffffff !important;
        border-radius: 50% !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        font-size: 22px !important;
        margin-bottom: 10px !important;
    }
    .mrp-title { color: #ffffff !important; font-size: 12px !important; font-weight: 700 !important; text-align: center !important; }
</style>
""", unsafe_allow_html=True)

now_str = datetime.now().strftime("%d/%m/%Y %H:%M")
st.markdown(f"""
<div class="top-bar">
    <div class="top-bar-left">
        <span class="logo-text">CAN Prod System</span>
        <span class="top-info">V 10.26539 &nbsp;|&nbsp; {now_str} &nbsp;|&nbsp; Location: ROU</span>
    </div>
    <div class="top-bar-right">
        <span>🌐 ROU</span>
        <span>➕ CAN PROD COATING</span>
        <span>👤 General</span>
        <span>⚙️</span>
        <span>❓</span>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="mrp-icon-bar">
    <a href="?page=Home" target="_self" class="mrp-icon-item" title="Main Menu">🏠</a>
    <a href="?page=Dashboard" target="_self" class="mrp-icon-item" title="Dashboard">⏱️</a>
    <a href="?page=Order_and_RFQ" target="_self" class="mrp-icon-item" title="Order and RFQ">📊</a>
    <a href="?page=My_Production_Plan" target="_self" class="mrp-icon-item" title="My Production Plan">📅</a>
    <a href="?page=Production_Planning" target="_self" class="mrp-icon-item" title="Production Planning">📑</a>
    <a href="?page=Stock" target="_self" class="mrp-icon-item" title="Stock">📦</a>
    <a href="?page=Procurement" target="_self" class="mrp-icon-item" title="Procurement">🛒</a>
    <a href="?page=Accounting" target="_self" class="mrp-icon-item" title="Accounting">📁</a>
    <a href="?page=Settings" target="_self" class="mrp-icon-item" title="Settings">⚙️</a>
</div>
""", unsafe_allow_html=True)

conn = get_connection()

# Funcție Import Items CSV
def process_mrpeasy_csv(df):
    cursor = conn.cursor()
    imported_count = 0
    updated_count = 0
    df.columns = [str(col).strip().lower() for col in df.columns]
    
    for _, row in df.iterrows():
        code = str(row.get('part no.', row.get('part number', row.get('code', row.get('cod', ''))))).strip()
        if not code or code == 'nan':
            continue
            
        name = str(row.get('part description', row.get('description', row.get('name', row.get('denumire', code))))).strip()
        
        group = str(row.get('group number', row.get('group name', row.get('group', '')))).upper()
        is_procured = row.get('is procured item', 0)
        
        if 'BUY' in group or is_procured == 1 or 'MATERIA' in group:
            item_type = 'RAW_MATERIAL'
        elif 'SUB' in group or 'ANSAMBLU' in group:
            item_type = 'SUBASSEMBLY'
        else:
            item_type = 'FINISHED_GOOD'
            
        um = str(row.get('uom', row.get('unit of measure', row.get('unit', row.get('um', 'pcs'))))).strip()
        
        loc_raw = row.get('default storage location', row.get('storage location', row.get('location', '-')))
        if pd.notnull(loc_raw) and str(loc_raw).strip() != '' and str(loc_raw).strip().lower() != 'nan':
            storage_loc = str(loc_raw).strip()
            cursor.execute("SELECT id FROM storage_locations WHERE name = ?", (storage_loc,))
            if not cursor.fetchone():
                auto_bc = generate_storage_barcode(conn, storage_loc)
                cursor.execute("INSERT INTO storage_locations (name, site, barcode) VALUES (?, ?, ?)", (storage_loc, 'Main site', auto_bc))
        else:
            storage_loc = '-'
        
        try:
            val = row.get('in stock', row.get('available', row.get('stoc', 0)))
            current_stock = float(val) if pd.notnull(val) else 0.0
        except:
            current_stock = 0.0
            
        try:
            val = row.get('reorder point', row.get('min stock', row.get('stoc min', 0)))
            min_stock = float(val) if pd.notnull(val) else 0.0
        except:
            min_stock = 0.0
            
        try:
            val = row.get('cost', row.get('cost price', 0))
            cost_price = float(val) if pd.notnull(val) else 0.0
        except:
            cost_price = 0.0

        try:
            val = row.get('selling price', row.get('price', 0))
            selling_price = float(val) if pd.notnull(val) else 0.0
        except:
            selling_price = 0.0

        cursor.execute("SELECT id FROM items WHERE code = ?", (code,))
        existing = cursor.fetchone()
        
        if existing:
            cursor.execute("""
                UPDATE items 
                SET name=?, type=?, unit_of_measure=?, storage_location=?, current_stock=?, min_stock=?, cost_price=?, selling_price=?
                WHERE code=?
            """, (name, item_type, um, storage_loc, current_stock, min_stock, cost_price, selling_price, code))
            updated_count += 1
        else:
            cursor.execute("""
                INSERT INTO items (code, name, type, unit_of_measure, storage_location, current_stock, min_stock, cost_price, selling_price)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (code, name, item_type, um, storage_loc, current_stock, min_stock, cost_price, selling_price))
            imported_count += 1

    conn.commit()
    return imported_count, updated_count


# Funcție Import Storage Locations CSV
def process_storage_locations_csv(df):
    cursor = conn.cursor()
    imported_count = 0
    updated_count = 0
    df.columns = [str(col).strip().lower() for col in df.columns]
    
    for _, row in df.iterrows():
        loc_name = str(row.get('storage location', row.get('location', row.get('name', '')))).strip()
        if not loc_name or loc_name == 'nan':
            continue
            
        site = str(row.get('site', 'Main site')).strip()
        barcode_val = str(row.get('barcode', '')).strip()
        if not barcode_val or barcode_val == 'nan' or barcode_val == '-':
            barcode_val = generate_storage_barcode(conn, loc_name)

        cursor.execute("SELECT id FROM storage_locations WHERE name = ?", (loc_name,))
        existing = cursor.fetchone()
        
        if existing:
            cursor.execute("""
                UPDATE storage_locations 
                SET site=?, barcode=?
                WHERE name=?
            """, (site, barcode_val, loc_name))
            updated_count += 1
        else:
            cursor.execute("""
                INSERT INTO storage_locations (name, site, barcode)
                VALUES (?, ?, ?)
            """, (loc_name, site, barcode_val))
            imported_count += 1

    conn.commit()
    return imported_count, updated_count


# 5. ECRAN PRINCIPAL
if current_page == 'Home':
    st.markdown("""
    <div class="mrp-launchpad">
        <a href="?page=Dashboard" target="_self" class="mrp-card"><div class="mrp-circle">⏱️</div><div class="mrp-title">Dashboard</div></a>
        <a href="?page=Order_and_RFQ" target="_self" class="mrp-card"><div class="mrp-circle">📊</div><div class="mrp-title">Order and RFQ</div></a>
        <a href="?page=My_Production_Plan" target="_self" class="mrp-card"><div class="mrp-circle">📅</div><div class="mrp-title">My Production Plan</div></a>
        <a href="?page=Production_Planning" target="_self" class="mrp-card"><div class="mrp-circle">📑</div><div class="mrp-title">Production Planning</div></a>
        <a href="?page=Stock" target="_self" class="mrp-card"><div class="mrp-circle">📦</div><div class="mrp-title">Stock</div></a>
        <a href="?page=Procurement" target="_self" class="mrp-card"><div class="mrp-circle">🛒</div><div class="mrp-title">Procurement</div></a>
        <a href="?page=Accounting" target="_self" class="mrp-card"><div class="mrp-circle">📁</div><div class="mrp-title">Accounting</div></a>
        <a href="?page=Settings" target="_self" class="mrp-card mrp-card-alt"><div class="mrp-circle">⚙️</div><div class="mrp-title">Settings</div></a>
    </div>
    <div class="mrp-launchpad">
        <a href="?page=Demo" target="_self" class="mrp-card"><div class="mrp-circle">🖥️</div><div class="mrp-title">Demo Data and Videos</div></a>
        <a href="?page=Free_Use" target="_self" class="mrp-card"><div class="mrp-circle">🎁</div><div class="mrp-title">Free Use</div></a>
        <a href="?page=Support" target="_self" class="mrp-card"><div class="mrp-circle">❓</div><div class="mrp-title">Support</div></a>
    </div>
    """, unsafe_allow_html=True)

# 6. MODUL ORDER AND RFQ
elif current_page == 'Order_and_RFQ' or current_page == 'CRM':
    
    rfq_subtabs = [
        ("Customer_orders", "Customer orders"),
        ("Customers", "Customers"),
        ("Todays_contacts", "Today's contacts"),
        ("Invoices", "Invoices"),
        ("Pricelists", "Pricelists"),
        ("Cash_flow", "Cash flow forecast"),
        ("Statistics", "Statistics"),
        ("Sales_management", "Sales management"),
        ("Customer_returns", "Customer returns (RMAs)")
    ]

    rfq_html = '<div class="mrp-subtabs">'
    for tab_key, tab_label in rfq_subtabs:
        active_class = "mrp-subtab-active" if rfq_subtab == tab_key else "mrp-subtab"
        rfq_html += f'<a href="?page=Order_and_RFQ&rfq_subtab={tab_key}" target="_self" class="{active_class}">{tab_label}</a>'
    rfq_html += '</div>'

    st.markdown(rfq_html, unsafe_allow_html=True)

    # ------------------ SUBTAB: CUSTOMER ORDERS ------------------
    if rfq_subtab == "Customer_orders":
        st.markdown(f"""
        <div class="mrp-inner-subtabs">
            <a href="?page=Order_and_RFQ&rfq_subtab=Customer_orders&rfq_inner=Orders" target="_self" class="{"mrp-inner-active" if rfq_inner_tab=="Orders" else "mrp-inner-tab"}">Customer orders</a>
            <a href="?page=Order_and_RFQ&rfq_subtab=Customer_orders&rfq_inner=Items" target="_self" class="{"mrp-inner-active" if rfq_inner_tab=="Items" else "mrp-inner-tab"}">Items</a>
        </div>
        """, unsafe_allow_html=True)

        if rfq_inner_tab == "Orders":
            top_co1, top_co2, top_co3, top_co4 = st.columns([3, 5, 1, 1])
            
            with top_co1:
                st.markdown("### Customer orders")
            
            with top_co2:
                with st.popover("➕ Create", use_container_width=False):
                    with st.form("add_customer_order_form"):
                        st.subheader("Creare Comandă Client / Oferta RFQ")
                        co_num = st.text_input("Number (ex: CO00856)")
                        co_cust_num = st.text_input("Customer number (ex: CU00009)")
                        co_cust_name = st.text_input("Customer name")
                        co_status = st.selectbox("Status", ["Confirmed", "Quoted", "Cancelled"])
                        co_prod_st = st.selectbox("Product status", ["Not booked", "Booked", "Shipped"])
                        co_inv_st = st.selectbox("Invoice status", ["Not invoiced", "Invoiced", "Partially invoiced"])
                        co_pay_st = st.selectbox("Payment status", ["Not paid", "Paid", "Partially paid"])
                        co_cdt = st.date_input("Created Date", datetime.now())
                        co_ddt = st.date_input("Delivery Date", datetime.now())

                        if st.form_submit_button("💾 Save Customer Order"):
                            try:
                                cursor = conn.cursor()
                                cursor.execute("""
                                    INSERT INTO customer_orders 
                                    (number, customer_number, customer_name, status, product_status, invoice_status, payment_status, created_date, delivery_date)
                                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                                """, (co_num, co_cust_num, co_cust_name, co_status, co_prod_st, co_inv_st, co_pay_st, co_cdt.strftime("%Y-%m-%d"), co_ddt.strftime("%Y-%m-%d")))
                                conn.commit()
                                st.success("Comanda a fost salvată!")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Eroare: {e}")

            with top_co3:
                st.button("↓ PDF", use_container_width=True)

            with top_co4:
                df_co_exp = pd.read_sql_query("SELECT number as 'Number', customer_number as 'Customer number', customer_name as 'Customer name', status as Status, product_status as 'Product status', invoice_status as 'Invoice status', payment_status as 'Payment status', created_date as Created, delivery_date as 'Delivery date' FROM customer_orders", conn)
                st.download_button("↓ CSV", data=df_co_exp.to_csv(index=False), file_name="customer_orders.csv", mime="text/csv", use_container_width=True)

            st.write("")

            col_co_num, col_co_cnum, col_co_cname, col_co_st, col_co_pst, col_co_inv, col_co_pay, col_co_cdt, col_co_ddt, col_co_btn = st.columns([1.5, 1.5, 2.5, 1.2, 1.5, 1.2, 1.2, 1.5, 1.5, 1.2])

            with col_co_num:
                f_co_num = st.text_input("Number ↑", "", placeholder="Filter Number", key="f_co_num")

            with col_co_cnum:
                f_co_cnum = st.text_input("Customer number", "", placeholder="Filter Cust No.", key="f_co_cnum")

            with col_co_cname:
                f_co_cname = st.text_input("Customer name", "", placeholder="Filter Cust Name", key="f_co_cname")

            with col_co_st:
                f_co_st = st.selectbox("Status", ["All", "Confirmed", "Quoted", "Cancelled"], key="f_co_st")

            with col_co_pst:
                f_co_pst = st.selectbox("Product status", ["All", "Not booked", "Booked", "Shipped"], key="f_co_pst")

            with col_co_inv:
                f_co_inv = st.selectbox("Invoice status", ["All", "Not invoiced", "Invoiced"], key="f_co_inv")

            with col_co_pay:
                f_co_pay = st.selectbox("Payment status", ["All", "Not paid", "Paid"], key="f_co_pay")

            with col_co_cdt:
                st.caption("Created min/max")

            with col_co_ddt:
                st.caption("Delivery min/max")

            with col_co_btn:
                btn_co_search = st.button("Search", type="primary", use_container_width=True)

            q_co = "SELECT id, number, customer_number, customer_name, status, product_status, invoice_status, payment_status, strftime('%m/%d/%Y', created_date) as created_fmt, strftime('%m/%d/%Y', delivery_date) as delivery_fmt FROM customer_orders WHERE 1=1"
            p_co = []

            if f_co_num:
                q_co += " AND number LIKE ?"
                p_co.append(f"%{f_co_num}%")

            if f_co_cnum:
                q_co += " AND customer_number LIKE ?"
                p_co.append(f"%{f_co_cnum}%")

            if f_co_cname:
                q_co += " AND customer_name LIKE ?"
                p_co.append(f"%{f_co_cname}%")

            if f_co_st != "All":
                q_co += " AND status = ?"
                p_co.append(f_co_st)

            if f_co_pst != "All":
                q_co += " AND product_status = ?"
                p_co.append(f_co_pst)

            if f_co_inv != "All":
                q_co += " AND invoice_status = ?"
                p_co.append(f_co_inv)

            if f_co_pay != "All":
                q_co += " AND payment_status = ?"
                p_co.append(f_co_pay)

            q_co += " ORDER BY id ASC"

            df_co_res = pd.read_sql_query(q_co, conn, params=p_co)

            st.write(f"**Total: {len(df_co_res)} orders**")

            rows_co_html = ""
            for idx, r in df_co_res.iterrows():
                rows_co_html += f"""
                <tr>
                    <td>{idx+1}</td>
                    <td><b>{r['number']}</b></td>
                    <td>{r['customer_number']}</td>
                    <td>{r['customer_name']}</td>
                    <td>{r['status']}</td>
                    <td style="color:#ef4444; font-weight:600;">{r['product_status']}</td>
                    <td style="color:#ef4444; font-weight:600;">{r['invoice_status']}</td>
                    <td style="color:#ef4444; font-weight:600;">{r['payment_status']}</td>
                    <td>{r['created_fmt'] if r['created_fmt'] else '-'}</td>
                    <td>{r['delivery_fmt'] if r['delivery_fmt'] else '-'}</td>
                    <td style="text-align: right;">✏️</td>
                    <td style="text-align: right;">📊</td>
                </tr>
                """

            iframe_co_html = f"""
            <!DOCTYPE html>
            <html>
            <head>
            <style>
                * {{ box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }}
                body {{ background-color: #ffffff; padding: 0; }}
                .mrp-table {{ width: 100%; border-collapse: collapse; font-size: 13px; }}
                .mrp-table th {{ background-color: #e2e8f0; color: #475569; font-weight: 600; padding: 8px 12px; text-align: left; border-bottom: 1px solid #cbd5e1; }}
                .mrp-table td {{ padding: 8px 12px; border-bottom: 1px solid #f1f5f9; color: #1e293b; }}
                .mrp-table tr:hover {{ background-color: #f8fafc; }}
            </style>
            </head>
            <body>
                <table class="mrp-table">
                    <thead>
                        <tr>
                            <th style="width: 30px;">+</th>
                            <th>Number ↑</th>
                            <th>Customer number</th>
                            <th>Customer name</th>
                            <th>Status</th>
                            <th>Product status</th>
                            <th>Invoice status</th>
                            <th>Payment status</th>
                            <th>Created</th>
                            <th>Delivery date</th>
                            <th style="width: 30px;">✏️</th>
                            <th style="width: 30px;">📊</th>
                        </tr>
                    </thead>
                    <tbody>
                        {rows_co_html}
                    </tbody>
                </table>
            </body>
            </html>
            """

            calc_h = max(250, len(df_co_res) * 38 + 50)
            components.html(iframe_co_html, height=calc_h, scrolling=True)

        else:
            st.info("Afișare articole comenzi clienți.")

    # ------------------ SUBTAB: CUSTOMERS (PAGINA PRINCIPALĂ SAU EDITARE DETALII) ------------------
    elif rfq_subtab == "Customers":
        
        # DACĂ ESTE SELECTAT UN CLIENT PENTRU EDITARE DETALII (REPLICAT EXACT POZA optiuni client.JPG)
        if edit_cust_id is not None:
            
            c_row = conn.cursor().execute("SELECT * FROM customers WHERE id = ?", (edit_cust_id,)).fetchone()
            if c_row:
                # Preluare date din tuple SQL
                c_id = c_row[0]
                c_num = c_row[1]
                c_name = c_row[2]
                c_status = c_row[3]
                c_reg = c_row[4] if c_row[4] else ""
                c_vat = c_row[5] if c_row[5] else ""
                c_manager = c_row[8] if c_row[8] else "General"
                c_phone = c_row[9] if c_row[9] else ""
                c_email = c_row[10] if c_row[10] else ""
                c_pname = c_row[13] if c_row[13] else "Default pricelist"
                c_tax = c_row[14] if c_row[14] else 0.0
                c_discount = c_row[15] if c_row[15] else 0.0
                c_pay_period = c_row[16] if c_row[16] else 0
                c_credit_limit = c_row[17] if c_row[17] else 0.0
                c_lang = c_row[18] if c_row[18] else "English"
                c_curr = c_row[19] if c_row[19] else "€"

                st.markdown(f"### Customer {c_num} {c_name} details")
                
                # BARA BUTOANE SUS (Back, Save, Delete, Reports)
                btn_c1, btn_c2, btn_c3, btn_c4, _ = st.columns([1, 1, 1, 1, 6])
                with btn_c1:
                    st.markdown(f'<a href="?page=Order_and_RFQ&rfq_subtab=Customers" target="_self"><button style="height:36px; background-color:#e2e8f0; color:#1e293b; border:none; border-radius:4px; padding:0 20px; font-weight:bold; cursor:pointer;">Back</button></a>', unsafe_allow_html=True)
                with btn_c2:
                    save_top = st.button("Save", type="primary", key="save_c_top")
                with btn_c3:
                    del_top = st.button("Delete", key="del_c_top")
                with btn_c4:
                    st.button("Reports", key="rep_c_top")

                st.write("")

                # FORMULAR DETALII CLIENT (2 COLOANE CONFORM POZEI)
                col_left, col_right = st.columns(2)

                with col_left:
                    val_num = st.text_input("Number *", value=c_num)
                    val_name = st.text_input("Name *", value=c_name)
                    val_status = st.selectbox("Status", ["No contact", "RFQ_TECH", "Permanent buyer", "No interest"], index=["No contact", "RFQ_TECH", "Permanent buyer", "No interest"].index(c_status) if c_status in ["No contact", "RFQ_TECH", "Permanent buyer", "No interest"] else 0)
                    val_reg = st.text_input("Reg. no.", value=c_reg)
                    val_vat = st.text_input("Tax/VAT number", value=c_vat)
                    
                    st.write("")
                    st.markdown("**Contact information**")
                    col_ci1, col_ci2 = st.columns([1.5, 2.5])
                    with col_ci1:
                        ci_type = st.selectbox("Type", ["Phone", "E-mail", "Web"], label_visibility="collapsed")
                    with col_ci2:
                        val_phone = st.text_input("Value", value=c_phone, label_visibility="collapsed")

                    st.markdown("**Files** 📁 ☁️ 🔗")

                with col_right:
                    val_c_started = st.date_input("Contact started *", datetime.now())
                    val_n_contact = st.date_input("Next contact", datetime.now())
                    val_manager = st.selectbox("Account manager", ["General", "a.neamtu@deimob.ro"], index=1 if c_manager=="a.neamtu@deimob.ro" else 0)
                    val_tax = st.number_input("Tax rate %", value=float(c_tax))
                    val_discount = st.number_input("Default discount %", value=float(c_discount))
                    val_pname = st.selectbox("Pricelist", ["Default pricelist"], index=0)
                    
                    col_pp1, col_pp2 = st.columns([2, 2])
                    with col_pp1:
                        val_pay_period = st.number_input("Payment period (days after)", value=int(c_pay_period))
                    with col_pp2:
                        st.selectbox("Invoicing Base", ["the invoice date"], label_visibility="collapsed")

                    val_credit_limit = st.number_input("Trade credit limit €", value=float(c_credit_limit))
                    val_lang = st.selectbox("Language", ["English", "Romanian"], index=0)
                    val_curr = st.selectbox("Currency", ["€", "$", "RON"], index=0)

                # BARA BUTOANE JOS
                st.write("")
                btn_b1, btn_b2, btn_b3, btn_b4, _ = st.columns([1, 1, 1, 1, 6])
                with btn_b1:
                    st.markdown(f'<a href="?page=Order_and_RFQ&rfq_subtab=Customers" target="_self"><button style="height:36px; background-color:#e2e8f0; color:#1e293b; border:none; border-radius:4px; padding:0 20px; font-weight:bold; cursor:pointer;">Back</button></a>', unsafe_allow_html=True)
                with btn_b2:
                    save_bot = st.button("Save", type="primary", key="save_c_bot")
                with btn_b3:
                    del_bot = st.button("Delete", key="del_c_bot")
                with btn_b4:
                    st.button("Reports", key="rep_c_bot")

                st.divider()

                # SECȚIUNEA CONTACTS
                st.markdown("### Contacts")
                df_cust_contacts = pd.read_sql_query("SELECT id, name as Name, position as Position, phone as Phone, teams as Teams, email as 'E-mail' FROM customer_contacts WHERE customer_id = ?", conn, params=[c_id])
                
                with st.popover("➕ Adaugă Persoană de Contact", use_container_width=False):
                    with st.form("add_contact_form"):
                        cnt_name = st.text_input("Name")
                        cnt_pos = st.text_input("Position")
                        cnt_phone = st.text_input("Phone")
                        cnt_teams = st.text_input("Teams")
                        cnt_email = st.text_input("E-mail")
                        if st.form_submit_button("Save Contact"):
                            conn.cursor().execute("INSERT INTO customer_contacts (customer_id, name, position, phone, teams, email) VALUES (?, ?, ?, ?, ?, ?)", (c_id, cnt_name, cnt_pos, cnt_phone, cnt_teams, cnt_email))
                            conn.commit()
                            st.rerun()

                if not df_cust_contacts.empty:
                    st.dataframe(df_cust_contacts, use_container_width=True, hide_index=True)
                else:
                    st.caption("Nicio persoană de contact adăugată.")

                st.divider()

                # SECȚIUNEA NOTES
                st.markdown("### Notes")
                df_cust_notes = pd.read_sql_query("SELECT id, created_date as Created, modified_date as Modified, note as Note FROM customer_notes WHERE customer_id = ?", conn, params=[c_id])
                
                with st.popover("➕ Adaugă Notă", use_container_width=False):
                    with st.form("add_note_form"):
                        note_text = st.text_area("Note")
                        if st.form_submit_button("Save Note"):
                            conn.cursor().execute("INSERT INTO customer_notes (customer_id, note) VALUES (?, ?)", (c_id, note_text))
                            conn.commit()
                            st.rerun()

                if not df_cust_notes.empty:
                    st.dataframe(df_cust_notes, use_container_width=True, hide_index=True)
                else:
                    st.caption("Nicio notă adăugată.")

                # SALVARE CLIENT
                if save_top or save_bot:
                    conn.cursor().execute("""
                        UPDATE customers SET 
                        number=?, name=?, status=?, reg_no=?, vat_number=?, account_manager=?, phone=?,
                        tax_rate=?, default_discount=?, pricelist_name=?, payment_period=?, trade_credit_limit=?, language=?, currency=?
                        WHERE id=?
                    """, (val_num, val_name, val_status, val_reg, val_vat, val_manager, val_phone, val_tax, val_discount, val_pname, val_pay_period, val_credit_limit, val_lang, val_curr, c_id))
                    conn.commit()
                    st.success("Datele clientului au fost salvate cu succes!")
                    st.rerun()

                # ȘTERGERE CLIENT
                if del_top or del_bot:
                    conn.cursor().execute("DELETE FROM customers WHERE id = ?", (c_id,))
                    conn.commit()
                    st.success("Clientul a fost șters!")
                    st.markdown('<meta http-equiv="refresh" content="0; url=?page=Order_and_RFQ&rfq_subtab=Customers">', unsafe_allow_html=True)

        # TABELUL PRINCIPAL DE CLIENȚI (Poza Customers.JPG)
        else:
            st.markdown(f"""
            <div class="mrp-inner-subtabs">
                <a href="?page=Order_and_RFQ&rfq_subtab=Customers&cust_inner=Companies" target="_self" class="{"mrp-inner-active" if cust_inner_tab=="Companies" else "mrp-inner-tab"}">Companies</a>
                <a href="?page=Order_and_RFQ&rfq_subtab=Customers&cust_inner=Contacts" target="_self" class="{"mrp-inner-active" if cust_inner_tab=="Contacts" else "mrp-inner-tab"}">Contacts</a>
            </div>
            """, unsafe_allow_html=True)

            if cust_inner_tab == "Companies":
                top_cust1, top_cust2, top_cust3, top_cust4, top_cust5 = st.columns([2, 4, 1, 1, 2])
                
                with top_cust1:
                    st.markdown("### Customers")
                
                with top_cust2:
                    with st.popover("➕ Create", use_container_width=False):
                        with st.form("add_customer_form"):
                            st.subheader("Adăugare Client Nou")
                            c_num = st.text_input("Number (ex: CU00092)")
                            c_name = st.text_input("Name")
                            c_status = st.selectbox("Status", ["No contact", "RFQ_TECH", "Permanent buyer", "No interest"])
                            c_manager = st.text_input("Account manager", "General")
                            c_phone = st.text_input("Phone")
                            c_email = st.text_input("E-mail")
                            c_pnum = st.text_input("Pricelist number")
                            c_pname = st.text_input("Pricelist name")

                            if st.form_submit_button("💾 Save Customer"):
                                try:
                                    cursor = conn.cursor()
                                    cursor.execute("""
                                        INSERT INTO customers (number, name, status, account_manager, phone, email, pricelist_number, pricelist_name)
                                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                                    """, (c_num, c_name, c_status, c_manager, c_phone, c_email, c_pnum, c_pname))
                                    conn.commit()
                                    st.success(f"Clientul {c_name} a fost salvat!")
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Eroare: {e}")

                with top_cust3:
                    st.button("↓ PDF", use_container_width=True)

                with top_cust4:
                    df_cust_exp = pd.read_sql_query("SELECT number as Number, name as Name, status as Status, account_manager as 'Account manager', phone as Phone, email as 'E-mail', pricelist_number as 'Pricelist number', pricelist_name as 'Pricelist name' FROM customers", conn)
                    st.download_button("↓ CSV", data=df_cust_exp.to_csv(index=False), file_name="customers_export.csv", mime="text/csv", use_container_width=True)

                with top_cust5:
                    with st.popover("↑ Import from CSV", use_container_width=True):
                        st.subheader("Import Customers din MRPeasy")
                        cust_csv = st.file_uploader("Încarcă customers_08_10_2026.csv", type=['csv'], key="cust_csv_up")
                        if cust_csv is not None:
                            try:
                                df_c_up = pd.read_csv(cust_csv)
                                st.write("Aperçu:")
                                st.dataframe(df_c_up.head(3))
                                if st.button("🚀 Execută Importul Clienți"):
                                    a, u = process_customers_csv(df_c_up)
                                    st.success(f"Import finalizat! Adăugați: {a}, Actualizați: {u}.")
                                    st.rerun()
                            except Exception as e:
                                st.error(f"Eroare: {e}")

                st.write("")

                # FILTRELE DIN ANTET (CONFORM POZEI Customers.JPG)
                status_opts = ["All"] + [r[0] for r in conn.cursor().execute("SELECT DISTINCT status FROM customers WHERE status IS NOT NULL AND status != '' ORDER BY status").fetchall()]
                manager_opts = ["All"] + [r[0] for r in conn.cursor().execute("SELECT DISTINCT account_manager FROM customers WHERE account_manager IS NOT NULL AND account_manager != '' ORDER BY account_manager").fetchall()]

                c_f_num, c_f_name, c_f_st, c_f_nxt, c_f_mgr, c_f_ph, c_f_em, c_f_pnum, c_f_pname, c_f_btn = st.columns([1.2, 2.5, 1.5, 1.2, 1.8, 1.2, 1.5, 1.2, 1.5, 1])

                with c_f_num:
                    f_c_num = st.text_input("Number ↑", "", placeholder="Filter Number", key="f_c_num")

                with c_f_name:
                    f_c_name = st.text_input("Name", "", placeholder="Filter Name", key="f_c_name")

                with c_f_st:
                    f_c_st = st.selectbox("Status", status_opts, key="f_c_st")

                with c_f_nxt:
                    st.caption("Next contact min/max")

                with c_f_mgr:
                    f_c_mgr = st.selectbox("Account manager", manager_opts, key="f_c_mgr")

                with c_f_ph:
                    f_c_ph = st.text_input("Phone", "", placeholder="Phone", key="f_c_ph")

                with c_f_em:
                    f_c_em = st.text_input("E-mail", "", placeholder="E-mail", key="f_c_em")

                with c_f_pnum:
                    f_c_pnum = st.text_input("Pricelist number", "", placeholder="Pricelist No.", key="f_c_pnum")

                with c_f_pname:
                    f_c_pname = st.text_input("Pricelist name ↓", "", placeholder="Pricelist Name", key="f_c_pname")

                with c_f_btn:
                    btn_c_search = st.button("Search", type="primary", use_container_width=True)

                q_c = "SELECT id, number, name, status, account_manager, phone, email, pricelist_number, pricelist_name FROM customers WHERE 1=1"
                p_c = []

                if f_c_num:
                    q_c += " AND number LIKE ?"
                    p_c.append(f"%{f_c_num}%")

                if f_c_name:
                    q_c += " AND name LIKE ?"
                    p_c.append(f"%{f_c_name}%")

                if f_c_st != "All":
                    q_c += " AND status = ?"
                    p_c.append(f_c_st)

                if f_c_mgr != "All":
                    q_c += " AND account_manager = ?"
                    p_c.append(f_c_mgr)

                if f_c_ph:
                    q_c += " AND phone LIKE ?"
                    p_c.append(f"%{f_c_ph}%")

                if f_c_em:
                    q_c += " AND email LIKE ?"
                    p_c.append(f"%{f_c_em}%")

                if f_c_pnum:
                    q_c += " AND pricelist_number LIKE ?"
                    p_c.append(f"%{f_c_pnum}%")

                if f_c_pname:
                    q_c += " AND pricelist_name LIKE ?"
                    p_c.append(f"%{f_c_pname}%")

                q_c += " ORDER BY id DESC"

                df_cust_res = pd.read_sql_query(q_c, conn, params=p_c)

                # AFIȘARE TABELARĂ CU LINK DIRECT CĂTRE DETALII CLIENT (✏️)
                rows_cust_html = ""
                for idx, r in df_cust_res.iterrows():
                    rows_cust_html += f"""
                    <tr>
                        <td>{idx+1}</td>
                        <td><b>{r['number']}</b></td>
                        <td>{r['name']}</td>
                        <td>{r['status']}</td>
                        <td>-</td>
                        <td>{r['account_manager']}</td>
                        <td>{r['phone'] if r['phone'] else ''}</td>
                        <td>{r['email'] if r['email'] else ''}</td>
                        <td>{r['pricelist_number'] if r['pricelist_number'] else ''}</td>
                        <td>{r['pricelist_name'] if r['pricelist_name'] else ''}</td>
                        <td style="text-align: right;">
                            <a href="?page=Order_and_RFQ&rfq_subtab=Customers&cust_id={r['id']}" target="_top" style="color:#64748b; text-decoration:none;" title="Edit details">✏️</a>
                        </td>
                        <td style="text-align: right;">📊</td>
                        <td style="text-align: right;"><input type="checkbox" /></td>
                    </tr>
                    """

                iframe_cust_html = f"""
                <!DOCTYPE html>
                <html>
                <head>
                <style>
                    * {{ box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }}
                    body {{ background-color: #ffffff; padding: 0; }}
                    .mrp-table {{ width: 100%; border-collapse: collapse; font-size: 13px; }}
                    .mrp-table th {{ background-color: #e2e8f0; color: #475569; font-weight: 600; padding: 8px 12px; text-align: left; border-bottom: 1px solid #cbd5e1; }}
                    .mrp-table td {{ padding: 8px 12px; border-bottom: 1px solid #f1f5f9; color: #1e293b; }}
                    .mrp-table tr:hover {{ background-color: #f8fafc; }}
                </style>
                </head>
                <body>
                    <table class="mrp-table">
                        <thead>
                            <tr>
                                <th style="width: 30px;">+</th>
                                <th>Number ↑</th>
                                <th>Name</th>
                                <th>Status</th>
                                <th>Next contact</th>
                                <th>Account manager</th>
                                <th>Phone</th>
                                <th>E-mail</th>
                                <th>Pricelist number</th>
                                <th>Pricelist name ↓</th>
                                <th style="width: 30px;">✏️</th>
                                <th style="width: 30px;">📊</th>
                                <th style="width: 30px;">+</th>
                            </tr>
                        </thead>
                        <tbody>
                            {rows_cust_html}
                        </tbody>
                    </table>
                </body>
                </html>
                """

                calc_h_cust = max(300, len(df_cust_res) * 38 + 50)
                components.html(iframe_cust_html, height=calc_h_cust, scrolling=True)

            else:
                st.info("Afișare persoane de contact clienți (Contacts).")

    else:
        st.subheader(f"📊 Order and RFQ - {rfq_subtab.replace('_', ' ')}")
        st.info(f"Sub-modulul **{rfq_subtab.replace('_', ' ')}** este pregătit.")

# 7. MODUL PRODUCTION PLANNING
elif current_page == 'Production_Planning':
    
    prod_tabs = [
        ("Operations", "⚙️ Operations"),
        ("Routings", "🔄 Routings"),
        ("BOM", "📋 Bills of Materials (BOM)"),
        ("Production_Orders", "🏭 Production Orders (MO)")
    ]

    prod_tabs_html = '<div class="mrp-subtabs">'
    for tab_key, tab_label in prod_tabs:
        active_class = "mrp-subtab-active" if prod_tab == tab_key else "mrp-subtab"
        prod_tabs_html += f'<a href="?page=Production_Planning&prod_tab={tab_key}" target="_self" class="{active_class}">{tab_label}</a>'
    prod_tabs_html += '</div>'

    st.markdown(prod_tabs_html, unsafe_allow_html=True)

    if prod_tab == "Operations":
        top_op1, top_op2 = st.columns([8, 2])
        
        with top_op1:
            st.markdown("### Operations")
        
        with top_op2:
            with st.popover("➕ Create Operation", use_container_width=True):
                with st.form("add_op_form"):
                    op_name = st.text_input("Name (ex: BUCSARE (1))")
                    op_type = st.text_input("Type (ex: BUCSARE)")
                    op_rate = st.number_input("Hourly rate (€)", min_value=0.0, value=20.0, step=5.0)

                    if st.form_submit_button("Save"):
                        if op_name and op_type:
                            cursor = conn.cursor()
                            cursor.execute("INSERT INTO operations_list (name, type, hourly_rate) VALUES (?, ?, ?)", (op_name, op_type, op_rate))
                            conn.commit()
                            st.success(f"Operația {op_name} a fost salvată!")
                            st.rerun()

        st.write("")

        type_options = ["All"] + [r[0] for r in conn.cursor().execute("SELECT DISTINCT type FROM operations_list WHERE type IS NOT NULL AND type != '' ORDER BY type").fetchall()]

        col_f_name, col_f_type, col_f_rate_min, col_f_rate_max, col_f_btn = st.columns([3, 3, 1.5, 1.5, 1])

        with col_f_name:
            f_op_name = st.text_input("Name ↑", "", placeholder="Filter by Name", key="f_op_n")

        with col_f_type:
            f_op_type = st.selectbox("Type", type_options, key="f_op_t")

        with col_f_rate_min:
            f_rate_min = st.number_input("Hourly rate min", value=0.0, step=5.0, key="f_r_min")

        with col_f_rate_max:
            f_rate_max = st.number_input("max", value=0.0, step=5.0, key="f_r_max")

        with col_f_btn:
            st.write("")
            st.write("")
            btn_op_search = st.button("Search", type="primary", use_container_width=True)

        q_op = "SELECT id, name, type, hourly_rate FROM operations_list WHERE 1=1"
        p_op = []

        if f_op_name:
            q_op += " AND name LIKE ?"
            p_op.append(f"%{f_op_name}%")

        if f_op_type != "All":
            q_op += " AND type = ?"
            p_op.append(f_op_type)

        if f_rate_min > 0:
            q_op += " AND hourly_rate >= ?"
            p_op.append(f_rate_min)

        if f_rate_max > 0:
            q_op += " AND hourly_rate <= ?"
            p_op.append(f_rate_max)

        q_op += " ORDER BY name ASC"

        df_ops = pd.read_sql_query(q_op, conn, params=p_op)

        st.write("")
        
        with st.form("edit_operations_form"):
            for idx, r in df_ops.iterrows():
                o_id = r['id']
                o_name = r['name']
                o_type = r['type']
                o_rate = r['hourly_rate']

                c1, c2, c3, c4 = st.columns([3, 3, 2, 1])
                with c1:
                    updated_name = st.text_input(f"Name #{o_id}", value=o_name, key=f"op_n_{o_id}", label_visibility="collapsed")
                with c2:
                    updated_type = st.text_input(f"Type #{o_id}", value=o_type, key=f"op_t_{o_id}", label_visibility="collapsed")
                with c3:
                    updated_rate = st.number_input(f"Rate #{o_id}", value=float(o_rate), step=1.0, key=f"op_r_{o_id}", label_visibility="collapsed")
                with c4:
                    del_op = st.checkbox("Delete", key=f"op_del_{o_id}")

                conn.cursor().execute("UPDATE operations_list SET name = ?, type = ?, hourly_rate = ? WHERE id = ?", (updated_name, updated_type, updated_rate, o_id))
                if del_op:
                    conn.cursor().execute("DELETE FROM operations_list WHERE id = ?", (o_id,))

            save_ops = st.form_submit_button("💾 Salvează Modificările Parametrilor")
            if save_ops:
                conn.commit()
                st.success("Parametrii operațiilor au fost actualizați!")
                st.rerun()

    else:
        st.subheader(f"📑 Production Planning - {prod_tab}")
        st.info(f"Sub-modulul **{prod_tab}** este pregătit pentru conectare.")

# 8. ECRAN MODUL STOCK
elif current_page == 'Stock':
    
    total_db_items = conn.cursor().execute("SELECT COUNT(*) FROM items").fetchone()[0]

    subtabs = [
        ("Items", f"Items ({total_db_items})"),
        ("Stock_settings", "Stock settings"),
        ("Stock_lots", "Stock lots"),
        ("Shipments", "Shipments"),
        ("Inventory", "Inventory"),
        ("Critical_on_hand", "Critical on-hand"),
        ("Write_offs", "Write-offs"),
        ("Stock_movement", "Stock movement"),
        ("Statistics", "Statistics")
    ]

    subtabs_html = '<div class="mrp-subtabs">'
    for tab_key, tab_label in subtabs:
        active_class = "mrp-subtab-active" if current_subtab == tab_key else "mrp-subtab"
        subtabs_html += f'<a href="?page=Stock&subtab={tab_key}" target="_self" class="{active_class}">{tab_label}</a>'
    subtabs_html += '</div>'

    st.markdown(subtabs_html, unsafe_allow_html=True)

    # ------------------ SUBTAB: ITEMS ------------------
    if current_subtab == "Items":
        top_c1, top_c2, top_c3, top_c4, top_c5 = st.columns([2, 5, 1, 1, 2])
        
        with top_c1:
            st.markdown("### Items")
        
        with top_c2:
            with st.popover("➕ Create", use_container_width=False):
                with st.form("add_item_form"):
                    st.subheader("Adăugare Repere în Stoc")
                    code = st.text_input("Part No.")
                    name = st.text_input("Part description")
                    item_type = st.selectbox("Group", ["RAW_MATERIAL", "SUBASSEMBLY", "FINISHED_GOOD"])
                    um = st.text_input("UoM", "pcs")
                    storage_loc = st.text_input("Default storage location (Client)", "General")
                    current_stock = st.number_input("In stock", min_value=0.0, value=0.0)
                    min_stock = st.number_input("Reorder point", min_value=0.0, value=0.0)
                    cost = st.number_input("Cost (€)", min_value=0.0, value=0.0)
                    selling_price = st.number_input("Selling price (€)", min_value=0.0, value=0.0)
                    
                    if st.form_submit_button("💾 Save"):
                        try:
                            cursor = conn.cursor()
                            cursor.execute(
                                "INSERT INTO items (code, name, type, unit_of_measure, storage_location, current_stock, min_stock, cost_price, selling_price) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                                (code, name, item_type, um, storage_loc, current_stock, min_stock, cost, selling_price)
                            )
                            cursor.execute("SELECT id FROM storage_locations WHERE name = ?", (storage_loc,))
                            if not cursor.fetchone():
                                auto_bc = generate_storage_barcode(conn, storage_loc)
                                cursor.execute("INSERT INTO storage_locations (name, site, barcode) VALUES (?, ?, ?)", (storage_loc, 'Main site', auto_bc))
                            conn.commit()
                            st.success(f"Articolul {code} salvat!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Eroare: {e}")

        with top_c3:
            st.button("↓ PDF", use_container_width=True)

        with top_c4:
            df_export = pd.read_sql_query("SELECT code as 'Part No.', name as 'Part description', selling_price as 'Selling price (€)', unit_of_measure as 'UoM', storage_location as 'Default storage location', cost_price as 'Cost (€)', current_stock as 'In stock' FROM items", conn)
            st.download_button("↓ CSV", data=df_export.to_csv(index=False), file_name="items_export.csv", mime="text/csv", use_container_width=True)

        with top_c5:
            with st.popover("↑ Import from CSV", use_container_width=True):
                st.subheader("Import Stocuri din MRPeasy")
                csv_file = st.file_uploader("Încarcă fișierul articles.csv", type=['csv'])
                if csv_file is not None:
                    try:
                        df_upload = pd.read_csv(csv_file)
                        st.write("Aperçu fișier:")
                        st.dataframe(df_upload.head(3))
                        
                        if st.button("🚀 Execută Importul"):
                            added, updated = process_mrpeasy_csv(df_upload)
                            st.success(f"Import finalizat! Adăugate: {added}, Actualizate: {updated}.")
                            st.rerun()
                    except Exception as e:
                        st.error(f"Eroare la procesare: {e}")

        st.write("")

        um_options = ["All"] + [r[0] for r in conn.cursor().execute("SELECT DISTINCT unit_of_measure FROM items WHERE unit_of_measure IS NOT NULL AND unit_of_measure != '' ORDER BY unit_of_measure").fetchall()]
        loc_options = ["All"] + [r[0] for r in conn.cursor().execute("SELECT DISTINCT storage_location FROM items WHERE storage_location IS NOT NULL AND storage_location != '' ORDER BY storage_location").fetchall()]

        col_part, col_desc, col_sell, col_uom, col_loc, col_cost, col_btn = st.columns([2, 3, 2, 1.2, 2.2, 2, 1.6])

        with col_part:
            f_part_no = st.text_input("Part No. ↓", "", placeholder="Search Part No.", key="f_part_no")

        with col_desc:
            f_description = st.text_input("Part description", "", placeholder="Search Description", key="f_desc")

        with col_sell:
            f_sell_min = st.number_input("Selling price Min (€)", value=0.0, step=1.0, key="f_s_min")
            f_sell_max = st.number_input("Selling price Max (€)", value=0.0, step=1.0, key="f_s_max")

        with col_uom:
            f_uom = st.selectbox("UoM", um_options, key="f_uom")

        with col_loc:
            f_location = st.selectbox("Default storage location (Client)", loc_options, key="f_loc")

        with col_cost:
            f_cost_min = st.number_input("Cost Min (€)", value=0.0, step=1.0, key="f_c_min")
            f_cost_max = st.number_input("Cost Max (€)", value=0.0, step=1.0, key="f_c_max")

        with col_btn:
            st.write("")
            st.write("")
            btn_search = st.button("Search", type="primary", use_container_width=True)

        query = """
            SELECT 
                id as ID, 
                code as 'Part No.', 
                name as 'Part description', 
                selling_price as 'Selling price (€)', 
                unit_of_measure as UoM, 
                storage_location as 'Default storage location', 
                cost_price as 'Cost (€)', 
                current_stock as 'In stock'
            FROM items WHERE 1=1
        """
        params = []

        if f_part_no:
            query += " AND code LIKE ?"
            params.append(f"%{f_part_no}%")

        if f_description:
            query += " AND name LIKE ?"
            params.append(f"%{f_description}%")

        if f_uom != "All":
            query += " AND unit_of_measure = ?"
            params.append(f_uom)

        if f_location != "All":
            query += " AND storage_location = ?"
            params.append(f_location)

        if f_sell_min > 0:
            query += " AND selling_price >= ?"
            params.append(f_sell_min)

        if f_sell_max > 0:
            query += " AND selling_price <= ?"
            params.append(f_sell_max)

        if f_cost_min > 0:
            query += " AND cost_price >= ?"
            params.append(f_cost_min)

        if f_cost_max > 0:
            query += " AND cost_price <= ?"
            params.append(f_cost_max)

        df_items = pd.read_sql_query(query, conn, params=params)
        st.dataframe(df_items, use_container_width=True, height=520, hide_index=True)

    # ------------------ SUBTAB: STOCK SETTINGS ------------------
    elif current_subtab == "Stock_settings":
        
        # EDITARE DETALII UOM
        if current_setting == "Units_of_measurement" and edit_uom_id is not None:
            
            uom_row = conn.cursor().execute("SELECT id, name FROM units_of_measurement WHERE id = ?", (edit_uom_id,)).fetchone()
            if uom_row:
                u_id, u_name = uom_row
                
                st.markdown(f"### Unit of measurement {u_name} details")
                
                b1, b2, b3, _ = st.columns([1, 1, 1, 7])
                with b1:
                    st.markdown(f'<a href="?page=Stock&subtab=Stock_settings&setting=Units_of_measurement" target="_self"><button style="height:36px; background-color:#e2e8f0; color:#1e293b; border:none; border-radius:4px; padding:0 20px; font-weight:bold; cursor:pointer;">Back</button></a>', unsafe_allow_html=True)
                with b2:
                    save_top = st.button("Save", type="primary", key="save_uom_top")
                with b3:
                    del_top = st.button("Delete", key="del_uom_top")

                st.write("")
                new_u_name = st.text_input("Name *", value=u_name)
                
                st.write("#### Unit conversions")
                st.markdown("""
                <div class="uom-tooltip">
                    Other units, which this unit can be converted to, for convenience. Can be used in bills of materials. E.g. if the unit is "kg", a conversion could be 1 gr = 0.001 kg.
                </div>
                """, unsafe_allow_html=True)

                df_convs = pd.read_sql_query("SELECT id, target_uom, rate FROM unit_conversions WHERE uom_id = ?", conn, params=[u_id])
                
                with st.form("uom_conversions_form"):
                    st.caption("Modifică sau adaugă conversii (Nume Unit & Rata de conversie):")
                    
                    edited_data = []
                    if not df_convs.empty:
                        for idx, r in df_convs.iterrows():
                            c_col1, c_col2, c_col3 = st.columns([3, 3, 1])
                            with c_col1:
                                t_uom = st.text_input(f"Target Name #{idx+1}", value=r['target_uom'], key=f"t_uom_{r['id']}")
                            with c_col2:
                                t_rate = st.number_input(f"Rate #{idx+1}", value=float(r['rate']), key=f"t_rate_{r['id']}")
                            with c_col3:
                                delete_row = st.checkbox("Delete", key=f"del_conv_{r['id']}")
                            
                            edited_data.append({'id': r['id'], 'target': t_uom, 'rate': t_rate, 'delete': delete_row})
                    
                    st.divider()
                    st.markdown("**➕ Adaugă o conversie nouă:**")
                    new_col1, new_col2 = st.columns([3, 3])
                    with new_col1:
                        new_target = st.text_input("Nume unitate nouă (ex: Min)", key="new_target_input")
                    with new_col2:
                        new_rate = st.number_input("Rată conversie", value=1.0, key="new_rate_input")

                    submit_conversions = st.form_submit_button("💾 Salvează modificările conversiilor")

                if submit_conversions:
                    cursor = conn.cursor()
                    for item in edited_data:
                        if item['delete']:
                            cursor.execute("DELETE FROM unit_conversions WHERE id = ?", (item['id'],))
                        else:
                            cursor.execute("UPDATE unit_conversions SET target_uom = ?, rate = ? WHERE id = ?", (item['target'], item['rate'], item['id']))
                    
                    if new_target and new_target.strip():
                        cursor.execute("INSERT INTO unit_conversions (uom_id, target_uom, rate) VALUES (?, ?, ?)", (u_id, new_target.strip(), new_rate))

                    conn.commit()
                    st.success("Conversiile au fost salvate cu succes!")
                    st.rerun()

                if save_top:
                    conn.cursor().execute("UPDATE units_of_measurement SET name = ? WHERE id = ?", (new_u_name, u_id))
                    conn.commit()
                    st.success("Numele unității a fost actualizat!")
                    st.rerun()

                if del_top:
                    conn.cursor().execute("DELETE FROM units_of_measurement WHERE id = ?", (u_id,))
                    conn.commit()
                    st.success("Unitatea de măsură a fost ștearsă!")
                    st.markdown('<meta http-equiv="refresh" content="0; url=?page=Stock&subtab=Stock_settings&setting=Units_of_measurement">', unsafe_allow_html=True)

        # MENIUL STANDARD SETTINGS
        else:
            col_set_nav, col_set_content = st.columns([2, 8])

            with col_set_nav:
                st.markdown("### Stock settings")
                
                p_class = "settings-item-active" if current_setting == "Product_groups" else "settings-item"
                u_class = "settings-item-active" if current_setting == "Units_of_measurement" else "settings-item"
                s_class = "settings-item-active" if current_setting == "Storage_locations" else "settings-item"

                st.markdown(f"""
                <div class="settings-sidebar">
                    <a href="?page=Stock&subtab=Stock_settings&setting=Product_groups" target="_self" class="{p_class}">Product groups</a>
                    <a href="?page=Stock&subtab=Stock_settings&setting=Units_of_measurement" target="_self" class="{u_class}">Units of measurement</a>
                    <a href="?page=Stock&subtab=Stock_settings&setting=Storage_locations" target="_self" class="{s_class}">Storage locations</a>
                </div>
                """, unsafe_allow_html=True)

            with col_set_content:
                
                # 1. PRODUCT GROUPS
                if current_setting == "Product_groups":
                    c_title, c_btn = st.columns([8, 2])
                    with c_title:
                        st.markdown("#### Product groups")
                    with c_btn:
                        with st.popover("➕ Create", use_container_width=True):
                            with st.form("add_group_form"):
                                g_num = st.text_input("Number")
                                g_name = st.text_input("Name")
                                if st.form_submit_button("Save"):
                                    conn.cursor().execute("INSERT INTO product_groups (number, name) VALUES (?, ?)", (g_num, g_name))
                                    conn.commit()
                                    st.rerun()

                    g_search = st.text_input("Search Number / Name", "", placeholder="Search...")
                    q_g = "SELECT number as Number, name as Name FROM product_groups WHERE 1=1"
                    p_g = []
                    if g_search:
                        q_g += " AND (number LIKE ? OR name LIKE ?)"
                        p_g.extend([f"%{g_search}%", f"%{g_search}%"])
                    
                    df_g = pd.read_sql_query(q_g, conn, params=p_g)
                    st.dataframe(df_g, use_container_width=True, hide_index=True)

                # 2. UNITS OF MEASUREMENT
                elif current_setting == "Units_of_measurement":
                    c_title, c_btn = st.columns([8, 2])
                    with c_title:
                        st.markdown("#### Units of measurement")
                    with c_btn:
                        with st.popover("➕ Create", use_container_width=True):
                            with st.form("add_uom_form"):
                                u_name = st.text_input("Unit of measurement")
                                if st.form_submit_button("Save"):
                                    conn.cursor().execute("INSERT OR IGNORE INTO units_of_measurement (name) VALUES (?)", (u_name,))
                                    conn.commit()
                                    st.rerun()

                    df_u = pd.read_sql_query("SELECT id, name FROM units_of_measurement ORDER BY name", conn)

                    rows_html = ""
                    for _, r in df_u.iterrows():
                        rows_html += f"""
                        <tr>
                            <td>{r['name']}</td>
                            <td style="text-align: right;">
                                <a href="?page=Stock&subtab=Stock_settings&setting=Units_of_measurement&uom_id={r['id']}" target="_top" style="color:#64748b; text-decoration:none; font-size:14px;" title="Edit">✏️</a>
                            </td>
                        </tr>
                        """

                    iframe_uom_html = f"""
                    <!DOCTYPE html>
                    <html>
                    <head>
                    <style>
                        * {{ box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }}
                        body {{ background-color: #ffffff; padding: 0; }}
                        .mrp-table {{ width: 100%; border-collapse: collapse; font-size: 13px; }}
                        .mrp-table th {{ background-color: #e2e8f0; color: #475569; font-weight: 600; padding: 8px 12px; text-align: left; border-bottom: 1px solid #cbd5e1; }}
                        .mrp-table td {{ padding: 8px 12px; border-bottom: 1px solid #f1f5f9; color: #1e293b; }}
                        .mrp-table tr:hover {{ background-color: #f8fafc; }}
                    </style>
                    </head>
                    <body>
                        <table class="mrp-table">
                            <thead>
                                <tr>
                                    <th>Unit of measurement ↑</th>
                                    <th style="text-align: right; width: 60px;">+</th>
                                </tr>
                            </thead>
                            <tbody>
                                {rows_html}
                            </tbody>
                        </table>
                    </body>
                    </html>
                    """
                    
                    calc_height = max(180, len(df_u) * 35 + 40)
                    components.html(iframe_uom_html, height=calc_height, scrolling=True)

                # 3. STORAGE LOCATIONS (CU CONFIRMARE DE ȘTERGERE)
                elif current_setting == "Storage_locations":
                    c_title, c_btn1, c_btn2, c_btn3 = st.columns([5, 2, 1.5, 2])
                    with c_title:
                        st.markdown("#### Storage locations")
                    
                    with c_btn1:
                        with st.popover("➕ Create Client/Location", use_container_width=True):
                            with st.form("add_loc_form"):
                                l_name = st.text_input("Storage location")
                                l_site = st.text_input("Site", "Main site")
                                custom_barcode = st.text_input("Barcode (Lăsați gol pentru generare automată)", "")
                                
                                if st.form_submit_button("Save"):
                                    final_bc = custom_barcode.strip() if custom_barcode.strip() else generate_storage_barcode(conn, l_name)
                                    conn.cursor().execute("INSERT OR IGNORE INTO storage_locations (name, site, barcode) VALUES (?, ?, ?)", (l_name, l_site, final_bc))
                                    conn.commit()
                                    st.success(f"Locația {l_name} creată cu Barcode: {final_bc}")
                                    st.rerun()

                    with c_btn2:
                        df_loc_exp = pd.read_sql_query("SELECT name as 'Storage location', site as Site, barcode as Barcode FROM storage_locations ORDER BY name", conn)
                        st.download_button("↓ CSV", data=df_loc_exp.to_csv(index=False), file_name="storage_locations.csv", mime="text/csv", use_container_width=True)

                    with c_btn3:
                        with st.popover("↑ Import from CSV", use_container_width=True):
                            st.subheader("Import Storage Locations")
                            loc_csv = st.file_uploader("Încarcă storage_locations.csv", type=['csv'], key="loc_csv_up")
                            if loc_csv is not None:
                                try:
                                    df_loc_up = pd.read_csv(loc_csv)
                                    st.write("Aperçu:")
                                    st.dataframe(df_loc_up.head(3))
                                    if st.button("🚀 Execută Importul Locații"):
                                        a, u = process_storage_locations_csv(df_loc_up)
                                        st.success(f"Import finalizat! Adăugate: {a}, Actualizate: {u}.")
                                        st.rerun()
                                except Exception as e:
                                    st.error(f"Eroare: {e}")

                    l_search = st.text_input("Search Storage location", "", placeholder="Search...")
                    q_l = "SELECT id as ID, name as 'Storage location', site as Site, barcode as Barcode FROM storage_locations WHERE 1=1"
                    p_l = []
                    if l_search:
                        q_l += " AND name LIKE ?"
                        p_l.append(f"%{l_search}%")

                    df_l = pd.read_sql_query(q_l, conn, params=p_l)

                    st.write("")
                    for _, row in df_l.iterrows():
                        loc_id = row['ID']
                        loc_name = row['Storage location']
                        loc_site = row['Site']
                        loc_bc = row['Barcode']

                        col1, col2, col3, col4 = st.columns([3, 2, 3, 1])
                        with col1:
                            st.write(f"**{loc_name}**")
                        with col2:
                            st.write(f"`{loc_site}`")
                        with col3:
                            st.write(f"`{loc_bc}`")
                        with col4:
                            with st.popover("🗑️", use_container_width=True):
                                st.write(f"**⚠️ Confirmare Ștergere**")
                                st.warning(f"Ești sigur că vrei să ștergi locația **{loc_name}**?")
                                col_confirm, col_cancel = st.columns(2)
                                with col_confirm:
                                    if st.button("DA, Șterge", key=f"del_loc_{loc_id}", type="primary", use_container_width=True):
                                        cursor = conn.cursor()
                                        cursor.execute("DELETE FROM storage_locations WHERE id = ?", (loc_id,))
                                        conn.commit()
                                        st.success(f"Locația {loc_name} a fost ștearsă!")
                                        st.rerun()
                                with col_cancel:
                                    st.write("")

                        st.divider()

    # ------------------ SUBTAB: CRITICAL ON-HAND ------------------
    elif current_subtab == "Critical_on_hand":
        st.subheader("🔴 Critical On-Hand Stock (Reorder Required)")
        df_critical = pd.read_sql_query("""
            SELECT 
                code as 'Part No.', 
                name as 'Part description', 
                current_stock as 'In stock', 
                min_stock as 'Reorder point', 
                (min_stock - current_stock) as 'Shortage Quantity',
                unit_of_measure as 'UoM', 
                storage_location as 'Default storage location'
            FROM items 
            WHERE current_stock <= min_stock AND min_stock > 0
            ORDER BY (min_stock - current_stock) DESC
        """, conn)
        
        if df_critical.empty:
            st.success("🟢 Toate produsele au stoc peste nivelul minim de reordonare!")
        else:
            st.warning(f"⚠️ Există {len(df_critical)} articole sub nivelul minim:")
            st.dataframe(df_critical, use_container_width=True, hide_index=True)

    # ------------------ SUBTAB: STATISTICS ------------------
    elif current_subtab == "Statistics":
        st.subheader("📊 Stock Statistics & Valuation")
        
        df_stat = pd.read_sql_query("SELECT type, current_stock, cost_price, selling_price FROM items", conn)
        
        col_s1, col_s2, col_s3 = st.columns(3)
        total_val_cost = (df_stat['current_stock'] * df_stat['cost_price']).sum()
        total_val_sell = (df_stat['current_stock'] * df_stat['selling_price']).sum()
        
        col_s1.metric("Valoare Totală Stoc (Cost)", f"{total_val_cost:,.2f} €")
        col_s2.metric("Valoare Estimat Vânzare", f"{total_val_sell:,.2f} €")
        col_s3.metric("Profit Potențial în Stoc", f"{(total_val_sell - total_val_cost):,.2f} €")
        
        st.divider()
        st.write("#### Distribuție Articole pe Categorii")
        type_counts = df_stat['type'].value_counts()
        st.bar_chart(type_counts)

    # ------------------ CELELALTE SUBTABS ------------------
    else:
        st.subheader(f"📦 {current_subtab.replace('_', ' ')}")
        st.info(f"Sub-modulul **{current_subtab.replace('_', ' ')}** este pregătit pentru conectare.")

# 9. ALTE MODULE
else:
    st.title(f"Modul: {current_page.replace('_', ' ')}")
    st.divider()
    st.info(f"Modulul **{current_page.replace('_', ' ')}** este pregătit.")

conn.close()
