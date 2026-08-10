import streamlit as st
import sqlite3
import pandas as pd
import os
from datetime import datetime

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

    # Unit Conversions (Pozele 16 & 17)
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

    # Populare implicită
    cursor.execute("SELECT COUNT(*) FROM units_of_measurement")
    if cursor.fetchone()[0] == 0:
        default_uoms = ['kg', 'l', 'm2', 'Ml', 'Ore', 'pcs', 'SET', 'BUC']
        for u in default_uoms:
            cursor.execute("INSERT OR IGNORE INTO units_of_measurement (name) VALUES (?)", (u,))

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

    conn.commit()
    conn.close()

init_and_repair_db()

def get_connection():
    return sqlite3.connect('erp_database.db')

# 3. Preluare Query Params
query_params = st.query_params
current_page = query_params.get("page", "Home")
current_subtab = query_params.get("subtab", "Items")
current_setting = query_params.get("setting", "Product_groups")
edit_uom_id = query_params.get("uom_id", None)

# 4. CSS STILIZARE REPLICATĂ DUPĂ POZELE 16 ŞI 17
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

    /* Stil Detalii UoM (Pozele 16/17) */
    .uom-tooltip {
        background-color: #1e293b;
        color: #ffffff;
        font-size: 11px;
        padding: 8px 12px;
        border-radius: 4px;
        margin-top: 10px;
        margin-bottom: 15px;
    }
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
    <a href="?page=CRM" target="_self" class="mrp-icon-item" title="CRM">📊</a>
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
            cursor.execute("INSERT OR IGNORE INTO storage_locations (name) VALUES (?)", (storage_loc,))
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
        barcode = str(row.get('barcode', '-')).strip()

        cursor.execute("SELECT id FROM storage_locations WHERE name = ?", (loc_name,))
        existing = cursor.fetchone()
        
        if existing:
            cursor.execute("""
                UPDATE storage_locations 
                SET site=?, barcode=?
                WHERE name=?
            """, (site, barcode, loc_name))
            updated_count += 1
        else:
            cursor.execute("""
                INSERT INTO storage_locations (name, site, barcode)
                VALUES (?, ?, ?)
            """, (loc_name, site, barcode))
            imported_count += 1

    conn.commit()
    return imported_count, updated_count


# 5. ECRAN PRINCIPAL
if current_page == 'Home':
    st.markdown("""
    <div class="mrp-launchpad">
        <a href="?page=Dashboard" target="_self" class="mrp-card"><div class="mrp-circle">⏱️</div><div class="mrp-title">Dashboard</div></a>
        <a href="?page=CRM" target="_self" class="mrp-card"><div class="mrp-circle">📊</div><div class="mrp-title">CRM</div></a>
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

# 6. ECRAN MODUL STOCK
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
                            cursor.execute("INSERT OR IGNORE INTO storage_locations (name) VALUES (?)", (storage_loc,))
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
        
        # DACA A FOST SELECTAT O UNITATE PENTRU EDITARE DETALII (POZELE 16 ŞI 17)
        if current_setting == "Units_of_measurement" and edit_uom_id is not None:
            
            uom_row = conn.cursor().execute("SELECT id, name FROM units_of_measurement WHERE id = ?", (edit_uom_id,)).fetchone()
            if uom_row:
                u_id, u_name = uom_row
                
                st.markdown(f"### Unit of measurement {u_name} details")
                
                # BARA BUTOANE SUS (Back, Save, Delete)
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

                # Conversii existente
                df_convs = pd.read_sql_query("SELECT id, target_uom, rate FROM unit_conversions WHERE uom_id = ?", conn, params=[u_id])
                
                # Formular adăugare conversie
                c_c1, c_c2, c_c3 = st.columns([2, 2, 2])
                with c_c1:
                    target_u = st.text_input("Target Unit Name", placeholder="ex: Min sau gr")
                with c_c2:
                    rate_val = st.number_input("Rate (ex: 1)", value=1.0)
                with c_c3:
                    st.write("")
                    st.write("")
                    add_conv = st.button("➕ Add Conversion")

                if add_conv and target_u:
                    conn.cursor().execute("INSERT INTO unit_conversions (uom_id, target_uom, rate) VALUES (?, ?, ?)", (u_id, target_u, rate_val))
                    conn.commit()
                    st.rerun()

                if not df_convs.empty:
                    st.dataframe(df_convs, use_container_width=True, hide_index=True)

                if save_top:
                    conn.cursor().execute("UPDATE units_of_measurement SET name = ? WHERE id = ?", (new_u_name, u_id))
                    conn.commit()
                    st.success("Salvat!")
                    st.rerun()

                if del_top:
                    conn.cursor().execute("DELETE FROM units_of_measurement WHERE id = ?", (u_id,))
                    conn.commit()
                    st.success("Șters!")
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
                    <a href="?page=Stock&subtab=Stock_settings&setting=Storage_locations" target="_self" class="{s_class}">Storage locations (Clients)</a>
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

                # 2. UNITS OF MEASUREMENT (POZELE 14, 16, 17)
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

                    df_u = pd.read_sql_query("SELECT id, name as 'Unit of measurement' FROM units_of_measurement ORDER BY name", conn)
                    
                    # Afișare interactivă cu link pentru editare detalii (Poza 16)
                    for _, r in df_u.iterrows():
                        c_name, c_act = st.columns([8, 2])
                        with c_name:
                            st.write(f"**{r['Unit of measurement']}**")
                        with c_act:
                            st.markdown(f'<a href="?page=Stock&subtab=Stock_settings&setting=Units_of_measurement&uom_id={r["id"]}" target="_self" style="text-decoration:none;">✏️ Edit Details</a>', unsafe_allow_html=True)
                        st.divider()

                # 3. STORAGE LOCATIONS / CLIENȚI
                elif current_setting == "Storage_locations":
                    c_title, c_btn1, c_btn2, c_btn3 = st.columns([5, 2, 1.5, 2])
                    with c_title:
                        st.markdown("#### Storage locations (Virtual Depozite Clienți)")
                    
                    with c_btn1:
                        with st.popover("➕ Create Client/Location", use_container_width=True):
                            with st.form("add_loc_form"):
                                l_name = st.text_input("Storage location")
                                l_site = st.text_input("Site", "Main site")
                                l_code = st.text_input("Barcode")
                                if st.form_submit_button("Save"):
                                    conn.cursor().execute("INSERT OR IGNORE INTO storage_locations (name, site, barcode) VALUES (?, ?, ?)", (l_name, l_site, l_code))
                                    conn.commit()
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
                    st.dataframe(df_l, use_container_width=True, hide_index=True)

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
                storage_location as 'Default storage location (Client)'
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

# 7. ALTE MODULE
else:
    st.title(f"Modul: {current_page.replace('_', ' ')}")
    st.divider()
    st.info(f"Modulul **{current_page.replace('_', ' ')}** este pregătit.")

conn.close()
