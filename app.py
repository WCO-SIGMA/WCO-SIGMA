import streamlit as st
import pandas as pd
from datetime import datetime

# --- CONFIGURACIÓN DE IDs ---
SHEET_ID = "18OIJe409rr6o_o4HSweiuncIoOrgJOXEt0GFCmEsL4g"
DRIVE_MOTHER_FOLDER = "17o_kAZMRcGhDeI3vAd0dEk_UQJGYQWBZ"

# URL para lectura de datos (CSV export)
URL_DATOS = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

st.set_page_config(page_title="WCO-SIGMA HSEQ Pro", layout="wide", page_icon="🛡️")

# --- LOGIN POR NIT ---
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/1063/1063214.png", width=100)
st.sidebar.title("Acceso al Sistema")
nit_usuario = st.sidebar.text_input("Ingrese el NIT de su Empresa (sin puntos)", "")

if not nit_usuario:
    st.title("🚀 Bienvenido a WCO-SIGMA")
    st.warning("Por favor, ingrese su NIT en la barra lateral para acceder a su información.")
    st.info("Este sistema permite la gestión autónoma de su SG-SST bajo el ciclo PHVA.")
else:
    st.sidebar.success(f"Sesión Activa: NIT {nit_usuario}")
    menu = st.sidebar.radio("Gestión HSEQ", ["📊 Tablero de Control", "🟢 PLANEAR", "🔵 HACER (Inspecciones)", "🟡 VERIFICAR", "🔴 ACTUAR"])

    # Intentar leer datos de Google Sheets
    try:
        df_total = pd.read_csv(URL_DATOS)
        # Filtramos por NIT (Asegúrate que en tu Excel la primera columna se llame 'NIT')
        df_empresa = df_total[df_total['NIT'].astype(str) == str(nit_usuario)]
    except:
        df_empresa = pd.DataFrame(columns=['NIT', 'Fecha', 'Hallazgo', 'Prioridad'])

    # --- 📊 TABLERO DE CONTROL ---
    if menu == "📊 Tablero de Control":
        st.title(f"📊 Panel de Gestión - NIT: {nit_usuario}")
        c1, c2 = st.columns(2)
        c1.metric("Inspecciones Realizadas", len(df_empresa))
        c2.metric("Estado del SIG", "En Ejecución")
        
        st.write("### Historial de Hallazgos")
        st.dataframe(df_empresa, use_container_width=True)

    # --- 🟢 PLANEAR (Conexión a Drive) ---
    elif menu == "🟢 PLANEAR":
        st.title("🟢 Módulo PLANEAR")
        st.write("Acceda a su documentación estratégica:")
        url_p = "https://drive.google.com/drive/u/0/folders/17o_kAZMRcGhDeI3vAd0dEk_UQJGYQWBZ" # Tu carpeta madre
        st.link_button("📂 Abrir Carpeta de Documentación (P)", url_p)
        st.info("Aquí podrá consultar: Política, Matriz de Riesgos y Objetivos.")

    # --- 🔵 HACER (Registro de Inspecciones) ---
    elif menu == "🔵 HACER (Inspecciones)":
        st.title("🔵 Registro de Inspección In-Situ")
        with st.form("form_registro"):
            hallazgo = st.text_area("Describa la condición o hallazgo encontrado:")
            prioridad = st.selectbox("Prioridad", ["Baja", "Media", "Alta"])
            btn_guardar = st.form_submit_button("Guardar Reporte")
            
            if btn_guardar and hallazgo:
                # Nota: Para guardar de forma automática en Sheets desde Streamlit Community Cloud, 
                # se requiere configurar 'Secrets'. Por ahora, te genera el link para que lo veas.
                st.success(f"✅ Hallazgo registrado para el NIT {nit_usuario}.")
                st.write("**Datos a sincronizar:**")
                st.write(f"- NIT: {nit_usuario} | Fecha: {datetime.now().date()} | Hallazgo: {hallazgo}")
                st.info("Para activar el guardado automático permanente, debemos configurar los 'Secrets' en tu panel de Streamlit.")

# --- FOOTER ---
st.sidebar.markdown("---")
st.sidebar.write("Desarrollado por Walter - WCO-SIGMA")
