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

# Session State pentru Navigare
if 'current_page' not in st.session_state:
    st.session_state['current_page'] = 'Home'

def set_page(page_name):
    st.session_state['current_page'] = page_name

# CSS Custom - Replicare Fidela Interfață MRPeasy Launchpad
st.markdown("""
    <style>
    /* Fundalul general gri deschis ca în MRPeasy */
    .stApp {
        background-color: #f4f6f8;
    }
    
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
        margin-bottom: 30px;
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
        color: #1e62d0;
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

    /* Grid layout pentru Card-uri */
    [data-testid="column"] {
        flex: 1 1 0% !important;
        min-width: 0px !important;
    }

    /* Card-uri / Butoane stil MRPeasy (Alb albastru/gri) */
    div.stButton > button {
        width: 100% !important;
        height: 140px !important;
        background-color: #ffffff !important;
        color: #2d3748 !important;
        border-radius: 8px !important;
        border: 1px solid #e2e8f0 !important;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.02) !important;
        transition: all 0.2s ease !important;
        padding: 15px 5px !important;
    }
    
    /* Text și Iconițe în interiorul card-urilor */
    div.stButton > button p {
        font-size: 13px !important;
        font-weight: 600 !important;
        color: #2d3748 !important;
        white-space: pre-line !important;
        line-height: 1.5 !important;
        text-align: center !important;
    }

    /* Cardul selectat / Hover */
    div.stButton > button:hover {
        border-color: #1e62d0 !important;
        box-shadow: 0 6px 12px rgba(30, 98, 208, 0.1) !important;
        transform: translateY(-2px);
    }

    /* Back Button */
    .back-btn button {
        height: 38px !important;
        background-color: #4a5568 !important;
        color: #ffffff !important;
    }
    .back-btn button p {
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

# 2. INTERFAȚA LAUNCHPAD (TILES MRPEASY)
if st.session_state['current_page'] == 'Home':
    
    # Rândul 1 (8 Card-uri)
    col1, col2, col3, col4, col5, col6, col7, col8 = st.columns(8)
    
    with col1:
        if st.button("⏱️\n\nDashboard", key="btn_dash"):
            set_page("Dashboard")
            st.rerun()
            
    with col2:
        if st.button("📈\n\nCRM", key="btn_crm"):
            set_page("CRM")
            st.rerun()
            
    with col3:
        if st.button("📅\n\nMy Production Plan", key="btn_my_plan"):
            set_page("My Production Plan")
            st.rerun()
            
    with col4:
        if st.button("📊\n\nProduction Planning", key="btn_prod_plan"):
            set_page("Production Planning")
            st.rerun()
            
    with col5:
        if st.button("📦\n\nStock", key="btn_stock"):
            set_page("Stock")
            st.rerun()
            
    with col6:
        if st.button("🛒\n\nProcurement", key="btn_proc"):
            set_page("Procurement")
            st.rerun()
            
    with col7:
        if st.button("📁\n\nAccounting", key="btn_acc"):
            set_page("Accounting")
            st.rerun()
            
    with col8:
        if st.button("⚙️\n\nSettings", key="btn_sett"):
            set_page("Settings")
            st.rerun()

    st.write("")
    
    # Rândul 2 (3 Card-uri)
    col_a, col_b, col_c, col_d, col_e, col_f, col_g, col_h = st.columns(8)
    
    with col_a:
        if st.button("🖥️\n\nDemo Data and Videos", key="btn_demo"):
            st.info("Secțiune Demo")
            
    with col_b:
        if st.button("🎁\n\nFree Use", key="btn_free"):
            st.info("Aplicație Liberă")
            
    with col_c:
        if st.button("❓\n\nSupport", key="btn_supp"):
            st.info("Suport Tehnic")

# 3. INTERFEȚELE MODULELOR
else:
    col_back, col_title = st.columns([1, 6])
    with col_back:
        st.markdown('<div class="back-btn">', unsafe_allow_html=True)
        if st.button("⬅️ Main Menu"):
            set_page("Home")
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    with col_title:
        st.title(f"Modul: {st.session_state['current_page']}")

    st.divider()

    if st.session_state['current_page'] == 'Stock':
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

    elif st.session_state['current_page'] == 'Dashboard':
        st.subheader("📊 Starea Producției și KPIs")
        kpi1, kpi2, kpi3 = st.columns(3)
        total_items = pd.read_sql_query("SELECT COUNT(*) as c FROM items", conn)['c'][0]
        kpi1.metric("Total Articole în Stoc", total_items)
        kpi2.metric("Comenzi Active", "0")
        kpi3.metric("Status Sistem", "ONLINE 🟢")

    elif st.session_state['current_page'] == 'Settings':
        st.subheader("⚙️ Setări & Import CSV MRPeasy / SAGA")
        file = st.file_uploader("Încarcă fișier CSV MRPeasy", type=['csv'])
        if file:
            df = pd.read_csv(file)
            st.dataframe(df.head())

    else:
        st.info(f"Modulul **{st.session_state['current_page']}** este pregătit pentru conectarea datelor.")

conn.close()
