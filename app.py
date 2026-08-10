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

# Preluare Pagină Curentă din URL (Query Params)
query_params = st.query_params
current_page = query_params.get("page", "Home")

# Stiluri globale pentru paginile interioare
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

# 2. ECRANUL PRINCIPAL (REPLICARE EXACTĂ IMAGINE)
if current_page == 'Home':
    
    html_launchpad = """
    <!DOCTYPE html>
    <html>
    <head>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
        body { background-color: #f8fafc; padding: 10px 20px; }
        
        .grid-row {
            display: grid;
            grid-template-columns: repeat(8, 1fr);
            gap: 12px;
            margin-bottom: 12px;
        }

        .tile {
            background-color: #2563eb;
            height: 140px;
            border-radius: 4px;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            text-decoration: none;
            padding: 10px;
            transition: all 0.15s ease-in-out;
            cursor: pointer;
        }

        .tile-alt {
            background-color: #3b82f6; /* Nuanță ușor mai deschisă pentru ultimul card */
        }

        .tile:hover {
            background-color: #1d4ed8;
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3);
        }

        .icon-circle {
            width: 52px;
            height: 52px;
            background-color: #ffffff;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 24px;
            margin-bottom: 12px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }

        .tile-title {
            color: #ffffff;
            font-size: 13px;
            font-weight: 700;
            text-align: center;
            line-height: 1.2;
        }
    </style>
    </head>
    <body>

    <!-- Rândul 1 (8 Card-uri) -->
    <div class="grid-row">
        <a href="?page=Dashboard" target="_top" class="tile">
            <div class="icon-circle">⏱️</div>
            <div class="tile-title">Dashboard</div>
        </a>
        <a href="?page=CRM" target="_top" class="tile">
            <div class="icon-circle">📊</div>
            <div class="tile-title">CRM</div>
        </a>
        <a href="?page=My_Production_Plan" target="_top" class="tile">
            <div class="icon-circle">📅</div>
            <div class="tile-title">My Production Plan</div>
        </a>
        <a href="?page=Production_Planning" target="_top" class="tile">
            <div class="icon-circle">📑</div>
            <div class="tile-title">Production Planning</div>
        </a>
        <a href="?page=Stock" target="_top" class="tile">
            <div class="icon-circle">📦</div>
            <div class="tile-title">Stock</div>
        </a>
        <a href="?page=Procurement" target="_top" class="tile">
            <div class="icon-circle">🛒</div>
            <div class="tile-title">Procurement</div>
        </a>
        <a href="?page=Accounting" target="_top" class="tile">
            <div class="icon-circle">📁</div>
            <div class="tile-title">Accounting</div>
        </a>
        <a href="?page=Settings" target="_top" class="tile tile-alt">
            <div class="icon-circle">⚙️</div>
            <div class="tile-title">Settings</div>
        </a>
    </div>

    <!-- Rândul 2 (3 Card-uri) -->
    <div class="grid-row">
        <a href="?page=Demo" target="_top" class="tile">
            <div class="icon-circle">🖥️</div>
            <div class="tile-title">Demo Data and Videos</div>
        </a>
        <a href="?page=Free_Use" target="_top" class="tile">
            <div class="icon-circle">🎁</div>
            <div class="tile-title">Free Use</div>
        </a>
        <a href="?page=Support" target="_top" class="tile">
            <div class="icon-circle">❓</div>
            <div class="tile-title">Support</div>
        </a>
    </div>

    </body>
    </html>
    """
    components.html(html_launchpad, height=340)

# 3. INTERFEȚELE PENTRU MODULE
else:
    col_back, col_title = st.columns([1, 6])
    with col_back:
        st.markdown('<a href="?page=Home" target="_top" style="text-decoration:none;"><button style="height:38px; background-color:#475569; color:white; border:none; border-radius:4px; padding:0 15px; cursor:pointer; font-weight:bold;">⬅️ Main Menu</button></a>', unsafe_allow_html=True)
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
