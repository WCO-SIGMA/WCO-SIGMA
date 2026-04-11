import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.express as px
from datetime import datetime
import uuid

# Intento de importación protegida para evitar que la App se caiga
try:
    from streamlit_canvas import st_canvas
    CANVAS_AVAILABLE = True
except ImportError:
    CANVAS_AVAILABLE = False

# 1. CONFIGURACIÓN
st.set_page_config(page_title="WCO-SIGMA PRO", layout="wide")

# --- CONEXIONES ---
URL_COND = "https://docs.google.com/spreadsheets/d/18OIJe409rr6o_o4HSweiuncIoOrgJOXEt0GFCmEsL4g/edit"
URL_COMP = "https://docs.google.com/spreadsheets/d/1szrDZsA59e5sMF6OAzPeQ_nDX7E9lMehaXCPHmVNx5o/edit"
URL_ACPM = "https://docs.google.com/spreadsheets/d/1yXQNE3PiET-8VOHBWiReht7psRqjbAm5ZnY4P2XQQvg/edit" 

conn = st.connection("gsheets", type=GSheetsConnection)

# --- CARGA DE DATOS ---
def cargar_datos(url, nit):
    try:
        df = conn.read(spreadsheet=url, ttl=0)
        df.columns = df.columns.str.strip()
        col_nit = [c for c in df.columns if 'nit' in c.lower()][0]
        df['Nit_M'] = df[col_nit].astype(str).apply(lambda x: x.split('.')[0].strip())
        return df, df[df['Nit_M'] == nit]
    except: return pd.DataFrame(), pd.DataFrame()

# 2. LOGIN
nit_user = st.sidebar.text_input("NIT Empresa:", "").strip()

if not nit_user:
    st.title("🚀 WCO-SIGMA PRO")
    if not CANVAS_AVAILABLE:
        st.warning("⚠️ Nota: La librería de firmas no se ha detectado. Revisa el archivo requirements.txt")
    st.info("Ingrese su NIT para comenzar.")
else:
    df_cond_t, df_cond_e = cargar_datos(URL_COND, nit_user)
    df_comp_t, df_comp_e = cargar_datos(URL_COMP, nit_user)
    df_acpm_t, df_acpm_e = cargar_datos(URL_ACPM, nit_user)

    menu = st.sidebar.selectbox("Módulo", ["📊 Dashboard", "🛠️ BDI SIGMA", "🧠 COMPORTAMIENTO", "⚖️ ACPM"])

    # --- PANTALLA DASHBOARD ---
    if menu == "📊 Dashboard":
        st.header(f"📊 Control Gerencial - {nit_user}")
        if not df_cond_e.empty:
            st.plotly_chart(px.bar(df_cond_e, x='Centro de trabajo', color='Prioridad'), use_container_width=True)
        else: st.info("Sin datos para mostrar.")

    # --- PANTALLA REPORTE (CON FIRMA PROTEGIDA) ---
    elif menu == "🛠️ BDI SIGMA":
        st.subheader("🛠️ Reporte de Condiciones")
        with st.form("form_sigma"):
            f_ins = st.text_input("Inspector")
            f_ct = st.text_input("Centro de trabajo")
            f_tr = st.selectbox("Riesgo (GTC 45)", ["Físico", "Químico", "Seguridad", "Otros"])
            f_hal = st.text_area("Hallazgo")
            
            if CANVAS_AVAILABLE:
                st.write("✒️ Firma Electrónica")
                st_canvas(stroke_width=2, stroke_color="#000", background_color="#eee", height=100, key="canvas_sig")
            else:
                st.error("Módulo de firma no disponible.")

            if st.form_submit_button("💾 GUARDAR"):
                id_i = str(uuid.uuid4())[:8].upper()
                nueva = pd.DataFrame([{"Nit":nit_user, "ID_Inspección":id_i, "Fecha/Hora Real":str(datetime.now()), "Inspector":f_ins, "Centro de trabajo":f_ct, "Hallazgo":f_hal}])
                conn.update(spreadsheet=URL_COND, data=pd.concat([df_cond_t, nueva], ignore_index=True))
                st.success("Guardado exitosamente.")
