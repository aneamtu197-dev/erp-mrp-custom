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
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        code VARCHAR(100) UNIQUE NOT NULL,
        name VARCHAR(255) NOT NULL,
        type VARCHAR(50) DEFAULT 'RAW_MATERIAL',
        unit_of_measure VARCHAR(20) DEFAULT 'pcs',
        current_stock REAL DEFAULT 0.0,
        min_stock REAL DEFAULT 0.0,
        cost_price REAL DEFAULT 0.0
    );
    """)
    conn.commit()
    conn.close()

init_and_repair_db()

def get_connection():
    return sqlite3.connect('erp_database.db')

# 3. Preluare Pagină din URL Query Parameters
query_params = st.query_params
current_page = query_params.get("page", "Home")

# 4. CSS CUSTOM PENTRU STILIZARE REPLICATĂ EXACT DIN POZA 10
st.markdown("""
<style>
    .stApp { background-color: #f8fafc; }
    [data-testid="stSidebar"] { display: none; }

    /* Top Bar */
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

    /* Meniu Rapid cu Iconițe (MRPeasy Top Bar) */
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
    .mrp-icon-item:hover {
        background-color: #1d4ed8;
    }

    /* Sub-meniu MRPeasy Sub-tabs */
    .mrp-subtabs {
        display: flex;
        gap: 20px;
        border-bottom: 2px solid #e2e8f0;
        padding-bottom: 8px;
        margin-bottom: 15px;
        font-size: 13px;
        font-weight: 600;
    }
    .mrp-subtab-active {
        color: #2563eb;
        border-bottom: 2px solid #2563eb;
        padding-bottom: 8px;
        text-decoration: none;
    }
    .mrp-subtab {
        color: #64748b;
        text-decoration: none;
    }
    .mrp-subtab:hover {
        color: #1e293b;
    }

    /* Grid Launchpad pentru Home (Poza 1) */
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
    .mrp-card:hover {
        background-color: #1d4ed8 !important;
        transform: translateY(-2px) !important;
    }
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
    .mrp-title {
        color: #ffffff !important;
        font-size: 12px !important;
        font-weight: 700 !important;
        text-align: center !important;
    }
</style>
""", unsafe_allow_html=True)

# Top Bar
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

# Bara de Iconițe MRPeasy
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
            val = row.get('cost', row.get('price', row.get('cost price', 0)))
            cost_price = float(val) if pd.notnull(val) else 0.0
        except:
            cost_price = 0.0

        cursor.execute("SELECT id FROM items WHERE code = ?", (code,))
        existing = cursor.fetchone()
        
        if existing:
            cursor.execute("""
                UPDATE items 
                SET name=?, type=?, unit_of_measure=?, current_stock=?, min_stock=?, cost_price=?
                WHERE code=?
            """, (name, item_type, um, current_stock, min_stock, cost_price, code))
            updated_count += 1
        else:
            cursor.execute("""
                INSERT INTO items (code, name, type, unit_of_measure, current_stock, min_stock, cost_price)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (code, name, item_type, um, current_stock, min_stock, cost_price))
            imported_count += 1

    conn.commit()
    return imported_count, updated_count


# 5. ECRAN PRINCIPAL (HOME LAUNCHPAD)
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

# 6. ECRAN MODUL STOCK (REPLICAT EXACT CA ÎN POZA 10)
elif current_page == 'Stock':
    
    # Calcul număr total de articole pentru titlu
    total_db_items = conn.cursor().execute("SELECT COUNT(*) FROM items").fetchone()[0]

    # Sub-meniul MRPeasy din Poza 10
    st.markdown(f"""
    <div class="mrp-subtabs">
        <a href="#" class="mrp-subtab-active">Items ({total_db_items})</a>
        <a href="#" class="mrp-subtab">Stock settings</a>
        <a href="#" class="mrp-subtab">Stock lots</a>
        <a href="#" class="mrp-subtab">Shipments</a>
        <a href="#" class="mrp-subtab">Inventory</a>
        <a href="#" class="mrp-subtab">Critical on-hand</a>
        <a href="#" class="mrp-subtab">Write-offs</a>
        <a href="#" class="mrp-subtab">Stock movement</a>
        <a href="#" class="mrp-subtab">Statistics</a>
    </div>
    """, unsafe_allow_html=True)

    # Bara de Titlu + Butoane Acțiuni Top (Poza 10)
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
                current_stock = st.number_input("In stock", min_value=0.0, value=0.0)
                min_stock = st.number_input("Reorder point", min_value=0.0, value=0.0)
                cost = st.number_input("Cost (€)", min_value=0.0, value=0.0)
                
                if st.form_submit_button("💾 Save"):
                    try:
                        cursor = conn.cursor()
                        cursor.execute(
                            "INSERT INTO items (code, name, type, unit_of_measure, current_stock, min_stock, cost_price) VALUES (?, ?, ?, ?, ?, ?, ?)",
                            (code, name, item_type, um, current_stock, min_stock, cost)
                        )
                        conn.commit()
                        st.success(f"Articolul {code} salvat!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Eroare: {e}")

    with top_c3:
        st.button("↓ PDF", use_container_width=True)

    with top_c4:
        # Preia datele filtrate pentru export CSV
        df_export = pd.read_sql_query("SELECT code as 'Part No.', name as 'Part description', unit_of_measure as 'UoM', cost_price as 'Cost (€)', current_stock as 'In stock' FROM items", conn)
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

    # FILTRELE DIN ANTETUL TABELULUI (REPLICARE EXACTĂ POZA 10)
    um_options = ["All"] + [r[0] for r in conn.cursor().execute("SELECT DISTINCT unit_of_measure FROM items WHERE unit_of_measure IS NOT NULL AND unit_of_measure != ''").fetchall()]

    f1, f2, f3, f4, f5, f6 = st.columns([2, 3, 2, 1.5, 2, 1.5])
    
    with f1:
        f_part_no = st.text_input("Part No. ↓", "", placeholder="Search Part No.", key="f_part_no")
        
    with f2:
        f_description = st.text_input("Part description", "", placeholder="Search Description", key="f_desc")
        
    with f3:
        f_cost_min = st.number_input("Cost Min (€)", value=0.0, step=1.0, key="f_c_min")
        f_cost_max = st.number_input("Cost Max (€)", value=0.0, step=1.0, key="f_c_max")

    with f4:
        f_uom = st.selectbox("UoM", um_options, key="f_uom")

    with f5:
        f_stock_status = st.selectbox("Stock Filter", ["All", "In Stock (>0)", "Critical (<=Min)", "Zero Stock (=0)"], key="f_st")

    with f6:
        st.write("")
        st.write("")
        btn_search = st.button("Search", type="primary", use_container_width=True)

    # CONSTRUIRE INTEROGARE SQL FILTRATĂ
    query = "SELECT id as ID, code as 'Part No.', name as 'Part description', unit_of_measure as UoM, cost_price as 'Cost (€)', current_stock as 'In stock', min_stock as 'Reorder point' FROM items WHERE 1=1"
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

    if f_cost_min > 0:
        query += " AND cost_price >= ?"
        params.append(f_cost_min)

    if f_cost_max > 0:
        query += " AND cost_price <= ?"
        params.append(f_cost_max)

    if f_stock_status == "In Stock (>0)":
        query += " AND current_stock > 0"
    elif f_stock_status == "Critical (<=Min)":
        query += " AND current_stock <= min_stock AND min_stock > 0"
    elif f_stock_status == "Zero Stock (=0)":
        query += " AND current_stock = 0"

    df_items = pd.read_sql_query(query, conn, params=params)

    # TABELUL PRINCIPAL DE DATE (MRPEASY)
    st.dataframe(df_items, use_container_width=True, height=520, hide_index=True)

# 7. ALTE MODULE
else:
    st.title(f"Modul: {current_page.replace('_', ' ')}")
    st.divider()
    st.info(f"Modulul **{current_page.replace('_', ' ')}** este pregătit.")

conn.close()
