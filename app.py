import streamlit as st
import sqlite3
import pandas as pd
import os
from datetime import datetime
from init_db import init_database

# Configurare Pagină
st.set_page_config(page_title="CAN Prod System", layout="wide", initial_sidebar_state="collapsed")

# Inițializare Bază de Date
if not os.path.exists('erp_database.db'):
    init_database()

def get_connection():
    return sqlite3.connect('erp_database.db')

# Navigare prin Session State (Funcționează garantat la click)
if 'current_page' not in st.session_state:
    st.session_state['current_page'] = 'Home'

def navigate_to(page_name):
    st.session_state['current_page'] = page_name

# CSS Custom pentru Replicare Exactă a Interfeței MRPeasy
st.markdown("""
<style>
    /* Fundal general gri deschis */
    .stApp {
        background-color: #f8fafc;
    }
    
    /* Ascundere Meniu Lateral Streamlit */
    [data-testid="stSidebar"] { display: none; }
    
    /* Top Bar Styling */
    .top-bar {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 8px 20px;
        background-color: #ffffff;
        border-bottom: 1px solid #e1e6eb;
        margin-bottom: 20px;
        font-family: Arial, sans-serif;
    }
    .top-bar-left { display: flex; align-items: center; gap: 12px; }
    .logo-text { font-size: 20px; font-weight: 800; color: #1e62d0; }
    .top-info { font-size: 11px; color: #94a3b8; }
    .top-bar-right { display: flex; align-items: center; gap: 18px; font-size: 13px; color: #475569; font-weight: 600; }

    /* Egalizare strictă lățime coloane */
    [data-testid="column"] {
        flex: 1 1 0% !important;
        min-width: 0px !important;
    }

    /* Stilizare Card-uri Albastre */
    div.stButton > button {
        width: 100% !important;
        height: 135px !important;
        background-color: #2563eb !important;
        color: #ffffff !important;
        border-radius: 6px !important;
        border: none !important;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.08) !important;
        transition: all 0.15s ease-in-out !important;
        padding: 8px 2px !important;
    }

    /* Text & Iconițe centrate în carduri */
    div.stButton > button p {
        font-size: 12px !important;
        font-weight: 700 !important;
        color: #ffffff !important;
        white-space: pre-line !important;
        line-height: 1.3 !important;
        text-align: center !important;
    }

    /* Hover pe Card-uri */
    div.stButton > button:hover {
        background-color: #1d4ed8 !important;
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(37, 99, 235, 0.25) !important;
    }

    /* Buton Înapoi */
    .back-btn button {
        height: 38px !important;
        background-color: #475569 !important;
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

conn = get_connection()

# Funcție Procesare Import CSV MRPeasy
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


# 1. ECRAN PRINCIPAL (LAUNCHPAD - BUTOANE NATIVE STREAMLIT)
if st.session_state['current_page'] == 'Home':
    
    # Rândul 1 (8 Card-uri)
    col1, col2, col3, col4, col5, col6, col7, col8 = st.columns(8)
    
    with col1:
        if st.button("⏱️\n\nDashboard", key="btn_dash", on_click=navigate_to, args=("Dashboard",)): pass
    with col2:
        if st.button("📊\n\nCRM", key="btn_crm", on_click=navigate_to, args=("CRM",)): pass
    with col3:
        if st.button("📅\n\nMy Production Plan", key="btn_my_plan", on_click=navigate_to, args=("My Production Plan",)): pass
    with col4:
        if st.button("📑\n\nProduction Planning", key="btn_prod_plan", on_click=navigate_to, args=("Production Planning",)): pass
    with col5:
        if st.button("📦\n\nStock", key="btn_stock", on_click=navigate_to, args=("Stock",)): pass
    with col6:
        if st.button("🛒\n\nProcurement", key="btn_proc", on_click=navigate_to, args=("Procurement",)): pass
    with col7:
        if st.button("📁\n\nAccounting", key="btn_acc", on_click=navigate_to, args=("Accounting",)): pass
    with col8:
        if st.button("⚙️\n\nSettings", key="btn_sett", on_click=navigate_to, args=("Settings",)): pass

    st.write("") # Spațiu
    
    # Rândul 2 (3 Card-uri)
    col_a, col_b, col_c, col_d, col_e, col_f, col_g, col_h = st.columns(8)
    
    with col_a:
        if st.button("🖥️\n\nDemo Data", key="btn_demo", on_click=navigate_to, args=("Demo",)): pass
    with col_b:
        if st.button("🎁\n\nFree Use", key="btn_free", on_click=navigate_to, args=("Free Use",)): pass
    with col_c:
        if st.button("❓\n\nSupport", key="btn_supp", on_click=navigate_to, args=("Support",)): pass

# 2. ECRAN MODUL STOCK
elif st.session_state['current_page'] == 'Stock':
    col_back, col_title = st.columns([1, 6])
    with col_back:
        st.markdown('<div class="back-btn">', unsafe_allow_html=True)
        if st.button("⬅️ Main Menu", on_click=navigate_to, args=("Home",)): pass
        st.markdown('</div>', unsafe_allow_html=True)
    with col_title:
        st.title("📦 Stock & Inventory Management")

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

    # INTEROGARE SQL SI FILTRARE
    query = "SELECT id as ID, code as Cod, name as Denumire, type as Tip, unit_of_measure as UM, current_stock as 'Stoc Actual', min_stock as 'Stoc Min', cost_price as 'Cost (RON)' FROM items WHERE 1=1"
    params = []
    
    if search_query:
        query += " AND (code LIKE ? OR name LIKE ?)"
        params.extend([f"%{search_query}%", f"%{search_query}%"])
        
    if type_filter != "TOATE":
        query += " AND type = ?"
        params.append(type_filter)
        
    df_items = pd.read_sql_query(query, conn, params=params)
    
    # KPI METRICS
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    total_repere = len(df_items)
    stoc_critic = len(df_items[df_items['Stoc Actual'] <= df_items['Stoc Min']]) if not df_items.empty else 0
    valoare_totala = (df_items['Stoc Actual'] * df_items['Cost (RON)']).sum() if not df_items.empty else 0
    
    kpi1.metric("Total Repere în Nomenclator", total_repere)
    kpi2.metric("Repere Sub Stocul Minim", stoc_critic, delta_color="inverse")
    kpi3.metric("Valoare Totală Stoc Estimat", f"{valoare_totala:,.2f} RON")
    kpi4.metric("Status Sincronizare", "Live 🟢")

    st.write("### Lista Articolelor din Stoc")
    st.dataframe(df_items, use_container_width=True, height=450)

# ALTE MODULE
else:
    col_back, col_title = st.columns([1, 6])
    with col_back:
        st.markdown('<div class="back-btn">', unsafe_allow_html=True)
        if st.button("⬅️ Main Menu", on_click=navigate_to, args=("Home",)): pass
        st.markdown('</div>', unsafe_allow_html=True)
    with col_title:
        st.title(f"Modul: {st.session_state['current_page']}")
    st.divider()
    st.info(f"Modulul **{st.session_state['current_page']}** este pregătit.")

conn.close()
