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
        unit_of_measure VARCHAR(20) DEFAULT 'BUC',
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

# 3. Navigare prin Query Params (Funcționează 100% instant la click)
query_params = st.query_params
current_page = query_params.get("page", "Home")

# Top Bar
now_str = datetime.now().strftime("%d/%m/%Y %H:%M")
st.markdown(f"""
<style>
    .stApp {{ background-color: #f8fafc; }}
    [data-testid="stSidebar"] {{ display: none; }}
    .top-bar {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 8px 25px;
        background-color: #ffffff;
        border-bottom: 1px solid #e2e8f0;
        margin-bottom: 20px;
        font-family: Arial, sans-serif;
    }}
    .top-bar-left {{ display: flex; align-items: center; gap: 12px; }}
    .logo-text {{ font-size: 20px; font-weight: 800; color: #2563eb; }}
    .top-info {{ font-size: 11px; color: #94a3b8; }}
    .top-bar-right {{ display: flex; align-items: center; gap: 18px; font-size: 13px; color: #475569; font-weight: 600; }}
</style>
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

conn = get_connection()

# Funcție Import MRPeasy CSV
def process_mrpeasy_csv(df):
    cursor = conn.cursor()
    imported_count = 0
    updated_count = 0
    df.columns = [str(col).strip().lower() for col in df.columns]
    
    for _, row in df.iterrows():
        code = str(row.get('part number', row.get('code', row.get('cod', '')))).strip()
        if not code or code == 'nan':
            continue
            
        name = str(row.get('description', row.get('name', row.get('denumire', code)))).strip()
        
        type_val = str(row.get('group', row.get('type', row.get('tip', 'RAW_MATERIAL')))).upper()
        if 'RAW' in type_val or 'MATERIA' in type_val:
            item_type = 'RAW_MATERIAL'
        elif 'SUB' in type_val or 'ANSAMBLU' in type_val:
            item_type = 'SUBASSEMBLY'
        else:
            item_type = 'FINISHED_GOOD'
            
        um = str(row.get('unit', row.get('unit of measure', row.get('um', 'BUC')))).strip()
        
        try: current_stock = float(row.get('in stock', row.get('available', row.get('stoc', 0))))
        except: current_stock = 0.0
            
        try: min_stock = float(row.get('reorder point', row.get('min stock', row.get('stoc min', 0))))
        except: min_stock = 0.0
            
        try: cost_price = float(row.get('cost', row.get('price', row.get('cost price', 0))))
        except: cost_price = 0.0

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


# 4. ECRAN PRINCIPAL (NATIVE BUTTONS CU DESIGN PERFECT MRPEASY)
if current_page == 'Home':
    
    # CSS de forțare cercuri albe și pătrate albastre pe st.link_button
    st.markdown("""
    <style>
        /* Grila cu 8 coloane de dimensiuni identice */
        div[data-testid="stHorizontalBlock"] {
            gap: 12px !important;
        }
        div[data-testid="stHorizontalBlock"] > div {
            flex: 1 1 0% !important;
            min-width: 0px !important;
        }

        /* Cardul Albastru */
        a[data-testid="stHeaderActionElements"], .mrp-tile {
            display: flex !important;
            flex-direction: column !important;
            align-items: center !important;
            justify-content: center !important;
            background-color: #2563eb !important;
            height: 140px !important;
            border-radius: 4px !important;
            text-decoration: none !important;
            padding: 10px !important;
            transition: all 0.15s ease-in-out !important;
            box-shadow: 0 2px 4px rgba(0,0,0,0.08) !important;
        }

        .mrp-tile-alt {
            background-color: #3b82f6 !important;
        }

        .mrp-tile:hover {
            background-color: #1d4ed8 !important;
            transform: translateY(-2px);
            box-shadow: 0 6px 12px rgba(37, 99, 235, 0.25) !important;
        }

        /* Cercul Alb din Mijloc */
        .mrp-circle {
            width: 50px;
            height: 50px;
            background-color: #ffffff;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 22px;
            margin-bottom: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }

        /* Titlul Alb Sub Cerc */
        .mrp-label {
            color: #ffffff;
            font-size: 12px;
            font-weight: 700;
            text-align: center;
            line-height: 1.2;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        }
    </style>
    """, unsafe_allow_html=True)

    # Rândul 1 (8 Card-uri)
    col1, col2, col3, col4, col5, col6, col7, col8 = st.columns(8)
    
    with col1:
        st.markdown('<a href="?page=Dashboard" target="_self" class="mrp-tile"><div class="mrp-circle">⏱️</div><div class="mrp-label">Dashboard</div></a>', unsafe_allow_html=True)
    with col2:
        st.markdown('<a href="?page=CRM" target="_self" class="mrp-tile"><div class="mrp-circle">📊</div><div class="mrp-label">CRM</div></a>', unsafe_allow_html=True)
    with col3:
        st.markdown('<a href="?page=My_Production_Plan" target="_self" class="mrp-tile"><div class="mrp-circle">📅</div><div class="mrp-label">My Production Plan</div></a>', unsafe_allow_html=True)
    with col4:
        st.markdown('<a href="?page=Production_Planning" target="_self" class="mrp-tile"><div class="mrp-circle">📑</div><div class="mrp-label">Production Planning</div></a>', unsafe_allow_html=True)
    with col5:
        st.markdown('<a href="?page=Stock" target="_self" class="mrp-tile"><div class="mrp-circle">📦</div><div class="mrp-label">Stock</div></a>', unsafe_allow_html=True)
    with col6:
        st.markdown('<a href="?page=Procurement" target="_self" class="mrp-tile"><div class="mrp-circle">🛒</div><div class="mrp-label">Procurement</div></a>', unsafe_allow_html=True)
    with col7:
        st.markdown('<a href="?page=Accounting" target="_self" class="mrp-tile"><div class="mrp-circle">📁</div><div class="mrp-label">Accounting</div></a>', unsafe_allow_html=True)
    with col8:
        st.markdown('<a href="?page=Settings" target="_self" class="mrp-tile mrp-tile-alt"><div class="mrp-circle">⚙️</div><div class="mrp-label">Settings</div></a>', unsafe_allow_html=True)

    st.write("") # Spațiu
    
    # Rândul 2 (3 Card-uri)
    col_a, col_b, col_c, col_d, col_e, col_f, col_g, col_h = st.columns(8)
    
    with col_a:
        st.markdown('<a href="?page=Demo" target="_self" class="mrp-tile"><div class="mrp-circle">🖥️</div><div class="mrp-label">Demo Data and Videos</div></a>', unsafe_allow_html=True)
    with col_b:
        st.markdown('<a href="?page=Free_Use" target="_self" class="mrp-tile"><div class="mrp-circle">🎁</div><div class="mrp-label">Free Use</div></a>', unsafe_allow_html=True)
    with col_c:
        st.markdown('<a href="?page=Support" target="_self" class="mrp-tile"><div class="mrp-circle">❓</div><div class="mrp-label">Support</div></a>', unsafe_allow_html=True)

# 5. ECRAN MODUL STOCK
elif current_page == 'Stock':
    col_back, col_title = st.columns([1, 6])
    with col_back:
        st.markdown('<a href="?page=Home" target="_self" style="text-decoration:none;"><button style="height:38px; background-color:#475569; color:white; border:none; border-radius:4px; padding:0 15px; cursor:pointer; font-weight:bold;">⬅️ Main Menu</button></a>', unsafe_allow_html=True)
    with col_title:
        st.title("📦 Stock & Inventory Management")

    st.divider()

    col_search, col_filter, col_add, col_import = st.columns([3, 2, 2, 2])
    
    with col_search:
        search_query = st.text_input("🔍 Căutare după Cod sau Denumire", "")
        
    with col_filter:
        type_filter = st.selectbox("Filtrează Tip Articol", ["TOATE", "RAW_MATERIAL", "SUBASSEMBLY", "FINISHED_GOOD"])
        
    with col_add:
        st.write("")
        st.write("")
        with st.popover("➕ Articol Nou", use_container_width=True):
            with st.form("add_item_form"):
                st.subheader("Adăugare Repere în Stoc")
                code = st.text_input("Cod Articol")
                name = st.text_input("Denumire Articol")
                item_type = st.selectbox("Tip Articol", ["RAW_MATERIAL", "SUBASSEMBLY", "FINISHED_GOOD"])
                um = st.text_input("UM", "BUC")
                current_stock = st.number_input("Stoc Inițial", min_value=0.0, value=0.0)
                min_stock = st.number_input("Stoc Minim", min_value=0.0, value=0.0)
                cost = st.number_input("Cost (RON)", min_value=0.0, value=0.0)
                
                if st.form_submit_button("💾 Salvează"):
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

    with col_import:
        st.write("")
        st.write("")
        with st.popover("📥 Import CSV MRPeasy", use_container_width=True):
            st.subheader("Import Stocuri din MRPeasy")
            csv_file = st.file_uploader("Încarcă fișierul Items.csv", type=['csv'])
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

    query = "SELECT id as ID, code as Cod, name as Denumire, type as Tip, unit_of_measure as UM, current_stock as 'Stoc Actual', min_stock as 'Stoc Min', cost_price as 'Cost (RON)' FROM items WHERE 1=1"
    params = []
    
    if search_query:
        query += " AND (code LIKE ? OR name LIKE ?)"
        params.extend([f"%{search_query}%", f"%{search_query}%"])
        
    if type_filter != "TOATE":
        query += " AND type = ?"
        params.append(type_filter)
        
    df_items = pd.read_sql_query(query, conn, params=params)
    
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    total_repere = len(df_items)
    stoc_critic = len(df_items[df_items['Stoc Actual'] <= df_items['Stoc Min']]) if not df_items.empty else 0
    valoare_totala = (df_items['Stoc Actual'] * df_items['Cost (RON)']).sum() if not df_items.empty else 0
    
    kpi1.metric("Total Repere", total_repere)
    kpi2.metric("Stoc Critic", stoc_critic, delta_color="inverse")
    kpi3.metric("Valoare Totală", f"{valoare_totala:,.2f} RON")
    kpi4.metric("Status Sincronizare", "Live 🟢")

    st.write("### Lista Articolelor din Stoc")
    st.dataframe(df_items, use_container_width=True, height=450)

# 6. ALTE MODULE
else:
    col_back, col_title = st.columns([1, 6])
    with col_back:
        st.markdown('<a href="?page=Home" target="_self" style="text-decoration:none;"><button style="height:38px; background-color:#475569; color:white; border:none; border-radius:4px; padding:0 15px; cursor:pointer; font-weight:bold;">⬅️ Main Menu</button></a>', unsafe_allow_html=True)
    with col_title:
        st.title(f"Modul: {current_page.replace('_', ' ')}")
    st.divider()
    st.info(f"Modulul **{current_page.replace('_', ' ')}** este pregătit.")

conn.close()
