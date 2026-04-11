import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import uuid
import gspread # Nueva librería para escritura
from streamlit_canvas import st_canvas

# 1. CONFIGURACIÓN
st.set_page_config(page_title="WCO-SIGMA PRO", layout="wide")

# --- CONEXIONES (URLs de edición para lectura) ---
URL_COND = "https://docs.google.com/spreadsheets/d/18OIJe409rr6o_o4HSweiuncIoOrgJOXEt0GFCmEsL4g/edit"
URL_COMP = "https://docs.google.com/spreadsheets/d/1szrDZsA59e5sMF6OAzPeQ_nDX7E9lMehaXCPHmVNx5o/edit"
URL_ACPM = "https://docs.google.com/spreadsheets/d/1yXQNE3PiET-8VOHBWiReht7psRqjbAm5ZnY4P2XQQvg/edit" 

# --- FUNCIÓN PARA GUARDAR DATOS (Sustituye a conn.update) ---
def guardar_en_gsheet(url, nueva_fila_dict):
    try:
        # Extraer ID del spreadsheet de la URL
        ss_id = url.split("/d/")[1].split("/")[0]
        # Conexión simplificada (requiere que el link sea público editor)
        gc = gspread.public_browser_key() # Nota: En la nube requiere Service Account, 
        # pero para bypass usaremos este método:
        st.error("Para escribir datos, Google requiere autenticación oficial.")
        return False
    except: return False

# --- MOTOR DE LECTURA ---
def cargar_datos(url, nit):
    try:
        csv_url = url.replace('/edit', '/export?format=csv')
        df = pd.read_csv(csv_url)
        df.columns = df.columns.str.strip()
        col_nit = [c for c in df.columns if 'nit' in c.lower()][0]
        df['Nit_M'] = df[col_nit].astype(str).apply(lambda x: x.split('.')[0].strip())
        return df, df[df['Nit_M'] == nit]
    except: return pd.DataFrame(), pd.DataFrame()

# 2. LOGIN
nit_user = st.sidebar.text_input("Identificación Empresa (NIT):", "").strip()

if not nit_user:
    st.title("🚀 WCO-SIGMA PRO")
    st.info("Ingrese su NIT para activar la plataforma.")
else:
    df_cond_t, df_cond_e = cargar_datos(URL_COND, nit_user)
    df_comp_t, df_comp_e = cargar_datos(URL_COMP, nit_user)
    df_acpm_t, df_acpm_e = cargar_datos(URL_ACPM, nit_user)

    menu = st.sidebar.selectbox("Seleccione Módulo", ["📊 Dashboard", "🛠️ BDI SIGMA", "🧠 COMPORTAMIENTO", "⚖️ ACPM"])

    # --- REPORTE BDI SIGMA ---
    if menu == "🛠️ BDI SIGMA":
        st.subheader("🛠️ Reporte de Condiciones")
        with st.form("f_sigma"):
            f_ins = st.text_input("Inspector")
            f_ct = st.text_input("Centro de trabajo")
            f_tr = st.selectbox("Riesgo (GTC 45)", ["Físico", "Químico", "Seguridad", "Natural"])
            f_hal = st.text_area("Hallazgo")
            
            # Botón de Guardado con Instrucción Alternativa
            if st.form_submit_button("✅ REGISTRAR"):
                st.warning("⚠️ Streamlit Cloud requiere una Service Account para escribir en Google Sheets.")
                st.info(f"Datos preparados: {f_ct}, {f_tr}, {f_hal}. Para habilitar escritura automática, contacte a soporte para cargar el archivo secrets.toml.")

    # --- PANTALLA DASHBOARD (Visualización siempre activa) ---
    elif menu == "📊 Dashboard":
        st.header(f"📊 Control Gerencial - {nit_user}")
        if not df_cond_e.empty:
            st.plotly_chart(px.bar(df_cond_e, x='Centro de trabajo', color='Prioridad', title="Indicadores de Condiciones"), use_container_width=True)
        else:
            st.warning("No hay datos históricos para mostrar. El sistema está en modo lectura.")
