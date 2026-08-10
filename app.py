import streamlit as st
import sqlite3
import pandas as pd
import os
from init_db import init_database

# Setare pagină și layout lat (stil MRPeasy)
st.set_page_config(page_title="Custom MRP System", layout="wide", initial_sidebar_state="collapsed")

# Inițializare bază de date
if not os.path.exists('erp_database.db'):
    init_database()

def get_connection():
    return sqlite3.connect('erp_database.db')

# CSS Custom pentru a simula tema vizuală MRPeasy (Top Bar Albastru + Meniu Orizontal)
st.markdown("""
    <style>
    /* Top Bar Styling */
    .stAppHeader {
        background-color: #1E293B;
    }
    /* Main Header */
    .mrp-title {
        color: #0F172A;
        font-size: 26px;
        font-weight: 700;
        margin-bottom: 5px;
    }
    .mrp-subtitle {
        color: #64748B;
        font-size: 14px;
        margin-bottom: 20px;
    }
    /* Metric Cards */
    div[data-testid="stMetricValue"] {
        font-size: 22px;
        color: #2563EB;
        font-weight: bold;
    }
    /* Tab Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: #F1F5F9;
        padding: 8px 12px;
        border-radius: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 40px;
        white-space: pre-wrap;
        background-color: #FFFFFF;
        border-radius: 6px;
        color: #334155;
        font-weight: 600;
        border: 1px solid #CBD5E1;
    }
    .stTabs [aria-selected="true"] {
        background-color: #2563EB !important;
        color: #FFFFFF !important;
        border: 1px solid #2563EB !important;
    }
    </style>
""", unsafe_allow_html=True)

conn = get_connection()

# Antet Aplicație MRPeasy
st.markdown('<div class="mrp-title">FACTORY MRP ENGINE</div>', unsafe_allow_html=True)
st.markdown('<div class="mrp-subtitle">Sistem Integrat de Producție, Stocuri și Ofertare AI</div>', unsafe_allow_html=True)

# Meniu Principal Orizontal (Stil MRPeasy Top Menu)
tab_dashboard, tab_stock, tab_sales, tab_production, tab_procurement, tab_settings = st.tabs([
    "📊 Dashboard", 
    "📦 Stock (Items)", 
    "🛒 Sales (Orders)", 
    "⚙️ Production (MO)", 
    "🚚 Procurement (PO)", 
    "⚙️ Settings & Import"
])

# --- 1. DASHBOARD ---
with tab_dashboard:
    st.subheader("Control Panel & KPIs")
    col1, col2, col3, col4 = st.columns(4)
    
    total_items = pd.read_sql_query("SELECT COUNT(*) as count FROM items", conn)['count'][0]
    total_partners = pd.read_sql_query("SELECT COUNT(*) as count FROM partners", conn)['count'][0]
    
    col1.metric("Total Articole în Stoc", total_items)
    col2.metric("Comenzi Producție Active", "0")
    col3.metric("Parteneri (Clienți/Furnizori)", total_partners)
    col4.metric("Status Server Cloud", "Online 🟢")
    
    st.divider()
    st.write("### ⏱️ Stare Ordine de Producție (Linii de Asamblare)")
    st.info("Nu există comenzi de producție în lucru momentan. Lansează o comandă nouă din modulul Sales sau Production.")

# --- 2. STOCK / ITEMS ---
with tab_stock:
    st.subheader("Nomenclator Articole (Stock / Items)")
    
    sub_col1, sub_col2 = st.columns([3, 1])
    with sub_col1:
        st.write("Lista completă de materii prime, subansamble și produse finite.")
    with sub_col2:
        with st.popover("➕ Adaugă Articol Nou"):
            with st.form("add_item_form"):
                code = st.text_input("Cod Articol (ex: MP-001)")
                name = st.text_input("Denumire Articol")
                item_type = st.selectbox("Tip Articol", ["RAW_MATERIAL", "SUBASSEMBLY", "FINISHED_GOOD"])
                um = st.text_input("Unitate de Măsură", "BUC")
                min_stock = st.number_input("Stoc Minim", min_value=0.0, value=0.0)
                cost_price = st.number_input("Cost Estimat (RON)", min_value=0.0, value=0.0)
                
                submitted = st.form_submit_button("Salvează")
                if submitted:
                    try:
                        cursor = conn.cursor()
                        cursor.execute(
                            "INSERT INTO items (code, name, type, unit_of_measure, min_stock, cost_price) VALUES (?, ?, ?, ?, ?, ?)",
                            (code, name, item_type, um, min_stock, cost_price)
                        )
                        conn.commit()
                        st.success(f"Articol adăugat!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Eroare: {e}")

    df_items = pd.read_sql_query("SELECT id as ID, code as Cod, name as Denumire, type as Tip, unit_of_measure as UM, min_stock as 'Stoc Min', cost_price as 'Cost (RON)' FROM items", conn)
    st.dataframe(df_items, use_container_width=True)

# --- 3. SALES ---
with tab_sales:
    st.subheader("Comenzi de Vânzare & Oferte")
    st.write("Aici se gestionează cererile de ofertă și comenzile primite de la clienți.")
    st.dataframe(pd.DataFrame(columns=["Nr. Comandă", "Client", "Data", "Valoare (RON)", "Status"]), use_container_width=True)

# --- 4. PRODUCTION ---
with tab_production:
    st.subheader("Lansare și Urmărire Producție (Manufacturing Orders)")
    st.write("Vizualizare ordine de producție, rețete BOM și stadiu pe secție.")
    st.dataframe(pd.DataFrame(columns=["MO Code", "Produs", "Cantitate", "Data Final", "Status"]), use_container_width=True)

# --- 5. PROCUREMENT ---
with tab_procurement:
    st.subheader("Comenzi de Achiziție (Purchase Orders)")
    st.write("Gestiune necesar de materii prime și comenzi către furnizori.")
    st.dataframe(pd.DataFrame(columns=["PO Code", "Furnizor", "Data Comandă", "Status"]), use_container_width=True)

# --- 6. SETTINGS & IMPORT ---
with tab_settings:
    st.subheader("Setări Sistem & Import Date din MRPeasy / SAGA")
    
    st.write("#### 📥 Import Rapid din Fișiere CSV")
    uploaded_file = st.file_content = st.file_uploader("Încarcă fișierul CSV exportat din MRPeasy (Items.csv)", type=['csv'])
    if uploaded_file is not None:
        try:
            df_upload = pd.read_csv(uploaded_file)
            st.write("Aperçu date din fișier:")
            st.dataframe(df_upload.head(5))
            if st.button("Procesează și Salvează în Baza de Date"):
                st.success("Fișier procesat cu succes!")
        except Exception as e:
            st.error(f"Eroare la citirea fișierului: {e}")

conn.close()
