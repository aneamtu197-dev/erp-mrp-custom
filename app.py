import streamlit as st
import sqlite3
import pandas as pd
import os
from datetime import datetime
import streamlit.components.v1 as components
from init_db import init_database

# Configurare Pagină
st.set_page_config(page_title="CAN Prod System", layout="wide", initial_sidebar_state="collapsed")

# Inițializare Bază de Date
if not os.path.exists('erp_database.db'):
    init_database()

def get_connection():
    return sqlite3.connect('erp_database.db')

# Preluare Pagină Curentă din URL
query_params = st.query_params
current_page = query_params.get("page", "Home")

# CSS Custom
st.markdown("""
<style>
    .stApp { background-color: #f8fafc; }
    [data-testid="stSidebar"] { display: none; }
    .top-bar {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 8px 25px;
        background-color: #ffffff;
        border-bottom: 1px solid #e2e8f0;
        margin-bottom: 20px;
        font-family: Arial, sans-serif;
    }
    .top-bar-left { display: flex; align-items: center; gap: 12px; }
    .logo-text { font-size: 20px; font-weight: 800; color: #2563eb; }
    .top-info { font-size: 11px; color: #94a3b8; }
    .top-bar-right { display: flex; align-items: center; gap: 18px; font-size: 13px; color: #475569; font-weight: 600; }
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

conn = get_connection()

# Functie de Mapare si Import MRPeasy CSV
def process_mrpeasy_csv(df):
    cursor = conn.cursor()
    imported_count = 0
    updated_count = 0
    
    # Normalizare nume coloane (lowercase)
    df.columns = [str(col).strip().lower() for col in df.columns]
    
    for _, row in df.iterrows():
        # Extragere Cod
        code = str(row.get('part number', row.get('code', row.get('cod', '')))).strip()
        if not code or code == 'nan':
            continue
            
        # Extragere Denumire
        name = str(row.get('description', row.get('name', row.get('denumire', code)))).strip()
        
        # Extragere Tip Articol
        type_val = str(row.get('group', row.get('type', row.get('tip', 'RAW_MATERIAL')))).upper()
        if 'RAW' in type_val or 'MATERIA' in type_val:
            item_type = 'RAW_MATERIAL'
        elif 'SUB' in type_val or 'ANSAMBLU' in type_val:
            item_type = 'SUBASSEMBLY'
        else:
            item_type = 'FINISHED_GOOD'
            
        # UM, Stoc, Stoc Min, Cost
        um = str(row.get('unit', row.get('unit of measure', row.get('um', 'BUC')))).strip()
        
        try:
            current_stock = float(row.get('in stock', row.get('available', row.get('stoc', 0))))
        except:
            current_stock = 0.0
            
        try:
            min_stock = float(row.get('reorder point', row.get('min stock', row.get('stoc min', 0))))
        except:
            min_stock = 0.0
            
        try:
            cost_price = float(row.get('cost', row.get('price', row.get('cost price', 0))))
        except:
            cost_price = 0.0

        # Verificare dacă codul există deja
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


# 1. ECRAN PRINCIPAL (LAUNCHPAD)
if current_page == 'Home':
    html_launchpad = """
    <!DOCTYPE html>
    <html>
    <head>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
        body { background-color: #f8fafc; padding: 10px 20px; }
        .grid-row { display: grid; grid-template-columns: repeat(8, 1fr); gap: 12px; margin-bottom: 12px; }
        .tile { background-color: #2563eb; height: 140px; border-radius: 4px; display: flex; flex-direction: column; align-items: center; justify-content: center; text-decoration: none; padding: 10px; transition: all 0.15s ease-in-out; cursor: pointer; }
        .tile-alt { background-color: #3b82f6; }
        .tile:hover { background-color: #1d4ed8; transform: translateY(-2px); box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3); }
        .icon-circle { width: 52px; height: 52px; background-color: #ffffff; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 24px; margin-bottom: 12px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .tile-title { color: #ffffff; font-size: 13px; font-weight: 700; text-align: center; line-height: 1.2; }
    </style>
    </head>
    <body>
    <div class="grid-row">
        <a href="?page=Dashboard" target="_top" class="tile"><div class="icon-circle">⏱️</div><div class="tile-title">Dashboard</div></a>
        <a href="?page=CRM" target="_top" class="tile"><div class="icon-circle">📊</div><div class="tile-title">CRM</div></a>
        <a href="?page=My_Production_Plan" target="_top" class="tile"><div class="icon-circle">📅</div><div class="tile-title">My Production Plan</div></a>
        <a href="?page=Production_Planning" target="_top" class="tile"><div class="icon-circle">📑</div><div class="tile-title">Production Planning</div></a>
        <a href="?page=Stock" target="_top" class="tile"><div class="icon-circle">📦</div><div class="tile-title">Stock</div></a>
        <a href="?page=Procurement" target="_top" class="tile"><div class="icon-circle">🛒</div><div class="tile-title">Procurement</div></a>
        <a href="?page=Accounting" target="_top" class="tile"><div class="icon-circle">📁</div><div class="tile-title">Accounting</div></a>
        <a href="?page=Settings" target="_top" class="tile tile-alt"><div class="icon-circle">⚙️</div><div class="tile-title">Settings</div></a>
    </div>
    <div class="grid-row">
        <a href="?page=Demo" target="_top" class="tile"><div class="icon-circle">🖥️</div><div class="tile-title">Demo Data and Videos</div></a>
        <a href="?page=Free_Use" target="_top" class="tile"><div class="icon-circle">🎁</div><div class="tile-title">Free Use</div></a>
        <a href="?page=Support" target="_top" class="tile"><div class="icon-circle">❓</div><div class="tile-title">Support</div></a>
    </div>
    </body>
    </html>
    """
    components.html(html_launchpad, height=340)

# 2. ECRAN MODUL STOCK
elif current_page == 'Stock':
    col_back, col_title = st.columns([1, 6])
    with col_back:
        st.markdown('<a href="?page=Home" target="_top" style="text-decoration:none;"><button style="height:38px; background-color:#475569; color:white; border:none; border-radius:4px; padding:0 15px; cursor:pointer; font-weight:bold;">⬅️ Main Menu</button></a>', unsafe_allow_html=True)
    with col_title:
        st.title("📦 Stock & Inventory Management (MRPeasy Sync)")

    st.divider()

    # BARA DE ACȚIUNI ȘI FILTRE
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
                code = st.text_input("Cod Articol (ex: MP-TEAVA-40x40)")
                name = st.text_input("Denumire Articol")
                item_type = st.selectbox("Tip Articol", ["RAW_MATERIAL", "SUBASSEMBLY", "FINISHED_GOOD"])
                um = st.text_input("Unitate de Măsură (UM)", "BUC")
                current_stock = st.number_input("Stoc Inițial", min_value=0.0, value=0.0)
                min_stock = st.number_input("Stoc Minim de Siguranță", min_value=0.0, value=0.0)
                cost = st.number_input("Cost Unitar Estimat (RON)", min_value=0.0, value=0.0)
                
                if st.form_submit_button("💾 Salvează Articolul"):
                    try:
                        cursor = conn.cursor()
                        cursor.execute(
                            "INSERT INTO items (code, name, type, unit_of_measure, current_stock, min_stock, cost_price) VALUES (?, ?, ?, ?, ?, ?, ?)",
                            (code, name, item_type, um, current_stock, min_stock, cost)
                        )
                        conn.commit()
                        st.success(f"Articolul {code} a fost salvat!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Eroare: {e}")

    with col_import:
        st.write("")
        st.write("")
        with st.popover("📥 Import CSV MRPeasy", use_container_width=True):
            st.subheader("Import Stocuri din MRPeasy")
            csv_file = st.file_uploader("Încarcă fișierul exportat din MRPeasy (Items.csv)", type=['csv'])
            if csv_file is not None:
                try:
                    df_upload = pd.read_csv(csv_file)
                    st.write("Aperçu fișier:")
                    st.dataframe(df_upload.head(3))
                    
                    if st.button("🚀 Execută Importul în Baza de Date"):
                        added, updated = process_mrpeasy_csv(df_upload)
                        st.success(f"Import finalizat! Adăugate: {added} repere noi, Actualizate: {updated} repere.")
                        st.rerun()
                except Exception as e:
                    st.error(f"Eroare la procesare CSV: {e}")

    # CONSTRUIRE INTEROGARE SQL
    query = "SELECT id as ID, code as Cod, name as Denumire, type as Tip, unit_of_measure as UM, current_stock as 'Stoc Actual', min_stock as 'Stoc Min', cost_price as 'Cost (RON)' FROM items WHERE 1=1"
    params = []
    
    if search_query:
        query += " AND (code LIKE ? OR name LIKE ?)"
        params.extend([f"%{search_query}%", f"%{search_query}%"])
        
    if type_filter != "TOATE":
        query += " AND type = ?"
        params.append(type_filter)
        
    df_items = pd.read_sql_query(query, conn, params=params)
    
    # AFISARE STATISTICI RAPIDE
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    total_repere = len(df_items)
    stoc_critic = len(df_items[df_items['Stoc Actual'] <= df_items['Stoc Min']]) if not df_items.empty else 0
    valoare_totala = (df_items['Stoc Actual'] * df_items['Cost (RON)']).sum() if not df_items.empty else 0
    
    kpi1.metric("Total Repere în Nomenclator", total_repere)
    kpi2.metric("Repere Sub Stocul Minim", stoc_critic, delta_color="inverse")
    kpi3.metric("Valoare Totală Stoc Estimat", f"{valoare_totala:,.2f} RON")
    kpi4.metric("Status Sincuronizare", "Live 🟢")

    st.write("### Lista Articolelor din Stoc")
    st.dataframe(df_items, use_container_width=True, height=450)

# CELELALTE MODULE
else:
    col_back, col_title = st.columns([1, 6])
    with col_back:
        st.markdown('<a href="?page=Home" target="_top" style="text-decoration:none;"><button style="height:38px; background-color:#475569; color:white; border:none; border-radius:4px; padding:0 15px; cursor:pointer; font-weight:bold;">⬅️ Main Menu</button></a>', unsafe_allow_html=True)
    with col_title:
        st.title(f"Modul: {current_page.replace('_', ' ')}")
    st.divider()
    st.info(f"Modulul **{current_page.replace('_', ' ')}** este pregătit.")

conn.close()
