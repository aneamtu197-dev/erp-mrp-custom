import streamlit as st
import sqlite3
import pandas as pd
import os
from init_db import init_database

st.set_page_config(page_title="ERP Custom", layout="wide")

# Inițializare bază de date dacă nu există
if not os.path.exists('erp_database.db'):
    init_database()

def get_connection():
    return sqlite3.connect('erp_database.db')

st.title("⚙️ ERP/MRP Custom - Core Systems")

menu = st.sidebar.radio("Navigare", ["Dashboard", "Nomenclator Articole (Items)", "Adaugă Articol Nou"])

conn = get_connection()

if menu == "Dashboard":
    st.header("Panou de Control Producție")
    col1, col2, col3 = st.columns(3)
    
    total_items = pd.read_sql_query("SELECT COUNT(*) as count FROM items", conn)['count'][0]
    total_partners = pd.read_sql_query("SELECT COUNT(*) as count FROM partners", conn)['count'][0]
    
    col1.metric("Total Articole (Items)", total_items)
    col2.metric("Parteneri (Clienți/Furnizori)", total_partners)
    col3.metric("Status Sistem Online", "Activ ✅")

elif menu == "Nomenclator Articole (Items)":
    st.header("📋 Lista Articole din Nomenclator")
    df_items = pd.read_sql_query("SELECT * FROM items", conn)
    st.dataframe(df_items, use_container_width=True)

elif menu == "Adaugă Articol Nou":
    st.header("➕ Adaugă Articol Nou")
    with st.form("add_item_form"):
        code = st.text_input("Cod Articol (ex: MP-001 sau PF-100)")
        name = st.text_input("Denumire Articol")
        item_type = st.selectbox("Tip Articol", ["RAW_MATERIAL", "SUBASSEMBLY", "FINISHED_GOOD"])
        um = st.text_input("Unitate de Măsură", "BUC")
        min_stock = st.number_input("Stoc Minim", min_value=0.0, value=0.0)
        cost_price = st.number_input("Cost Estimat (RON)", min_value=0.0, value=0.0)
        
        submitted = st.form_submit_button("Salvează Articol")
        if submitted:
            try:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO items (code, name, type, unit_of_measure, min_stock, cost_price) VALUES (?, ?, ?, ?, ?, ?)",
                    (code, name, item_type, um, min_stock, cost_price)
                )
                conn.commit()
                st.success(f"Articolul '{name}' a fost adăugat cu succes!")
            except Exception as e:
                st.error(f"Eroare la salvare (Codul există deja?): {e}")

conn.close()
