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

# Gestionare Navigare prin Parametri URL (Query Params)
query_params = st.query_params
current_page = query_params.get("page", "Home")

# CSS Custom pentru Replicare Exactă Poza 1 (Grilă Flexibilă HTML cu Carduri Albastre Egale)
st.markdown("""
    <style>
    /* Ascundere Meniu Lateral Streamlit */
    [data-testid="stSidebar"] { display: none; }
    
    /* Top Bar MRPeasy Styling */
    .top-bar {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 10px 25px;
        background-color: #ffffff;
        border-bottom: 1px solid #e1e6eb;
        margin-bottom: 25px;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }
    .top-bar-left {
        display: flex;
        align-items: center;
        gap: 12px;
    }
    .logo-text {
        font-size: 20px;
        font-weight: 800;
        color: #2563EB;
    }
    .top-info {
        font-size: 11px;
        color: #8c9ba5;
    }
    .top-bar-right {
        display: flex;
        align-items: center;
        gap: 18px;
        font-size: 13px;
        color: #4a5568;
        font-weight: 500;
    }

    /* Container Grilă HTML cu carduri egale (Tiles) */
    .tiles-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(130px, 1fr));
        gap: 12px;
        padding: 0 10px;
    }

    /* Stilizare Card-uri Albastre ca în Poza 1 */
    .tile-card {
        background-color: #2563eb;
        color: #ffffff !important;
        height: 130px;
        border-radius: 6px;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        text-decoration: none !important;
        padding: 10px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.08);
        transition: all 0.2s ease-in-out;
        text-align: center;
    }

    .tile-card:hover {
        background-color: #1d4ed8;
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(37, 99, 235, 0.25);
    }

    /* Cerc Alb pentru Iconiță */
    .icon-circle {
        width: 42px;
        height: 42px;
        background-color: #ffffff;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 20px;
        margin-bottom: 10px;
    }

    .tile-title {
        font-size: 12px;
        font-weight: 700;
        color: #ffffff;
        line-height: 1.2;
    }

    /* Buton Înapoi la Meniu */
    .back-btn button {
        height: 38px !important;
        background-color: #4a5568 !important;
        color: #ffffff !important;
    }
    </style>
""", unsafe_allow_html=True)

# 1. BARA SUPERIOARĂ (TOP BAR)
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

# 2. ECRANUL PRINCIPAL (HTML TILES PERFECT EGALE)
if current_page == 'Home':
    
    # Definire Module (Iconiță + Titlu + Pagină)
    modules = [
        {"icon": "⏱️", "title": "Dashboard", "page": "Dashboard"},
        {"icon": "📈", "title": "CRM", "page": "CRM"},
        {"icon": "📅", "title": "My Production Plan", "page": "My_Production_Plan"},
        {"icon": "📊", "title": "Production Planning", "page": "Production_Planning"},
        {"icon": "📦", "title": "Stock", "page": "Stock"},
        {"icon": "🛒", "title": "Procurement", "page": "Procurement"},
        {"icon": "📁", "title": "Accounting", "page": "Accounting"},
        {"icon": "⚙️", "title": "Settings", "page": "Settings"},
        {"icon": "🖥️", "title": "Demo Data and Videos", "page": "Demo"},
        {"icon": "🎁", "title": "Free Use", "page": "Free_Use"},
        {"icon": "❓", "title": "Support", "page": "Support"}
    ]

    # Generare Grilă HTML
    grid_html = '<div class="tiles-grid">'
    for m in modules:
        grid_html += f'''
            <a href="?page={m['page']}" target="_self" class="tile-card">
                <div class="icon-circle">{m['icon']}</div>
                <div class="tile-title">{m['title']}</div>
            </a>
        '''
    grid_html += '</div>'
    
    st.markdown(grid_html, unsafe_allow_html=True)

# 3. INTERFEȚELE MODULELOR
else:
    col_back, col_title = st.columns([1, 6])
    with col_back:
        st.markdown(f'<a href="?page=Home" target="_self" style="text-decoration:none;"><button style="height:38px; background-color:#4a5568; color:white; border:none; border-radius:4px; padding:0 15px; cursor:pointer;">⬅️ Main Menu</button></a>', unsafe_allow_html=True)
    with col_title:
        st.title(f"Modul: {current_page.replace('_', ' ')}")

    st.divider()

    if current_page == 'Stock':
        st.subheader("📦 Nomenclator Articole (Items & Inventory)")
        
        c1, c2 = st.columns([3, 1])
        with c2:
            with st.popover("➕ Adaugă Articol Nou"):
                with st.form("add_item"):
                    code = st.text_input("Cod Articol")
                    name = st.text_input("Denumire Articol")
                    item_type = st.selectbox("Tip Articol", ["RAW_MATERIAL", "SUBASSEMBLY", "FINISHED_GOOD"])
                    um = st.text_input("UM", "BUC")
                    min_stock = st.number_input("Stoc Min", value=0.0)
                    cost = st.number_input("Cost (RON)", value=0.0)
                    if st.form_submit_button("Salvează"):
                        cursor = conn.cursor()
                        cursor.execute("INSERT INTO items (code, name, type, unit_of_measure, min_stock, cost_price) VALUES (?, ?, ?, ?, ?, ?)",
                                       (code, name, item_type, um, min_stock, cost))
                        conn.commit()
                        st.success("Salvat!")
                        st.rerun()

        df_items = pd.read_sql_query("SELECT id as ID, code as Cod, name as Denumire, type as Tip, unit_of_measure as UM, min_stock as 'Stoc Min', cost_price as Cost FROM items", conn)
        st.dataframe(df_items, use_container_width=True)

    elif current_page == 'Dashboard':
        st.subheader("📊 Starea Producției și KPIs")
        kpi1, kpi2, kpi3 = st.columns(3)
        total_items = pd.read_sql_query("SELECT COUNT(*) as c FROM items", conn)['c'][0]
        kpi1.metric("Total Articole în Stoc", total_items)
        kpi2.metric("Comenzi Active", "0")
        kpi3.metric("Status Sistem", "ONLINE 🟢")

    elif current_page == 'Settings':
        st.subheader("⚙️ Setări & Import CSV MRPeasy / SAGA")
        file = st.file_uploader("Încarcă fișier CSV MRPeasy", type=['csv'])
        if file:
            df = pd.read_csv(file)
            st.dataframe(df.head())

    else:
        st.info(f"Modulul **{current_page.replace('_', ' ')}** este pregătit pentru conectarea datelor.")

conn.close()
