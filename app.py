import streamlit as st
import sqlite3
import pandas as pd
import os
from datetime import datetime

# 1. Configurare Pagină
st.set_page_config(page_title="CAN Prod System", layout="wide", initial_sidebar_state="collapsed")

# 2. Reparare și Inițializare Bază de Date
def init_and_repair_db():
    conn = sqlite3.connect('erp_database.db')
    cursor = conn.cursor()
    
    # Tabela principală Items
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

    # Tabela pentru Stock Movements (Istoric mișcări stoc)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS stock_movements (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        item_code VARCHAR(100) NOT NULL,
        movement_type VARCHAR(50) NOT NULL,
        quantity REAL NOT NULL,
        source_location VARCHAR(100),
        destination_location VARCHAR(100),
        user VARCHAR(100),
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        notes TEXT
    );
    """)

    # Tabela pentru Write-offs (Casări)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS write_offs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        item_code VARCHAR(100) NOT NULL,
        quantity REAL NOT NULL,
        reason TEXT,
        user VARCHAR(100),
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    """)
    
    conn.commit()
    conn.close()

init_and_repair_db()

def get_connection():
    return sqlite3.connect('erp_database.db')

# 3. Preluare Pagină și Sub-tab din URL Query Parameters
query_params = st.query_params
current_page = query_params.get("page", "Home")
current_subtab = query_params.get("subtab", "Items")

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

# Funcție Import MRPeasy CSV
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

# 6. ECRAN MODUL STOCK (CU SUB-MENIURI DINAMICE ŞI INTERACTIVE)
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
                    storage_loc = st.text_input("Default storage location", "General")
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
            f_location = st.selectbox("Default storage location", loc_options, key="f_loc")

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
            st.success("🟢 Toate produsele au stoc peste limita minimă de siguranță!")
        else:
            st.warning(f"⚠️ Există {len(df_critical)} articole sub nivelul minim de reordonare:")
            st.dataframe(df_critical, use_container_width=True, hide_index=True)

    # ------------------ SUBTAB: STOCK SETTINGS ------------------
    elif current_subtab == "Stock_settings":
        st.subheader("⚙️ Stock Settings & Storage Locations")
        df_locations = pd.read_sql_query("""
            SELECT storage_location as 'Location Name', COUNT(*) as 'Total Items Stored', SUM(current_stock) as 'Total Units'
            FROM items 
            GROUP BY storage_location
        """, conn)
        st.dataframe(df_locations, use_container_width=True, hide_index=True)

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
