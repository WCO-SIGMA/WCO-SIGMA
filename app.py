import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.express as px
from datetime import datetime
import uuid

# 1. CONFIGURACIÓN
st.set_page_config(page_title="WCO-SIGMA MULTIMODAL", layout="wide")

# 2. CONEXIONES INDEPENDIENTES
# URL del Libro de Condiciones
URL_COND = "https://docs.google.com/spreadsheets/d/TU_ID_AQUI_1" 
# URL del Nuevo Libro de Comportamiento
URL_COMP = "https://docs.google.com/spreadsheets/d/TU_ID_AQUI_2"

conn = st.connection("gsheets", type=GSheetsConnection)

# 3. ACCESO
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/1063/1063302.png", width=100)
nit_input = st.sidebar.text_input("Ingrese identificación (NIT/Cédula):", "").strip()

if not nit_input:
    st.title("🚀 WCO-SIGMA: Gestión Integral")
    st.info("Motores Sincronizados. Ingrese el NIT para iniciar.")
else:
    # --- LECTURA DE MOTORES ---
    try:
        df_cond_total = conn.read(spreadsheet=URL_COND, ttl=0)
        df_cond_total.columns = df_cond_total.columns.str.strip()
        df_cond_total['Nit'] = df_cond_total['Nit'].astype(str).str.replace('.0', '', regex=False).str.strip()
        df_cond_emp = df_cond_total[df_cond_total['Nit'] == nit_input]
    except:
        df_cond_emp = pd.DataFrame()

    try:
        df_comp_total = conn.read(spreadsheet=URL_COMP, ttl=0)
        df_comp_total.columns = df_comp_total.columns.str.strip()
        df_comp_total['Nit'] = df_comp_total['Nit'].astype(str).str.replace('.0', '', regex=False).str.strip()
        df_comp_emp = df_comp_total[df_comp_total['Nit'] == nit_input]
    except:
        df_comp_emp = pd.DataFrame()

    menu = st.sidebar.radio("Módulos", ["📊 Dashboard Gerencial", "🛠️ Condiciones", "🧠 Comportamiento", "📂 PHVA"])

    # --- PANTALLA 1: DASHBOARD ---
    if menu == "📊 Dashboard Gerencial":
        st.title(f"📊 Dashboard SIG - NIT: {nit_input}")
        t1, t2 = st.tabs(["🔍 Condiciones HSEQ", "🧠 Comportamiento & PESV"])
        
        with t1:
            if not df_cond_emp.empty:
                st.plotly_chart(px.pie(df_cond_emp, names='Estado', title="Avance Condiciones"), use_container_width=True)
                st.dataframe(df_cond_emp, use_container_width=True)
            else: st.warning("Sin datos en Condiciones.")
            
        with t2:
            if not df_comp_emp.empty:
                st.plotly_chart(px.bar(df_comp_emp, x='Estado observado', title="Estatus Comportamientos"), use_container_width=True)
                st.dataframe(df_comp_emp, use_container_width=True)
            else: st.warning("Sin datos en Comportamiento.")

    # --- PANTALLA 2: CONDICIONES ---
    elif menu == "🛠️ Condiciones":
        st.title("🛠️ Registro de Condiciones")
        with st.form("form_c"):
            f_emp = st.text_input("Empresa")
            f_hall = st.text_area("Hallazgo")
            if st.form_submit_button("✅ GUARDAR EN BDI CONDICIONES"):
                nueva = pd.DataFrame([{"Nit":nit_input, "Empresa":f_emp, "Fecha":str(datetime.now().date()), "Hallazgo":f_hall, "Condición Crítica":"General", "Clasificación del riesgo":"SST", "Componente":"SST", "Responsable del cierre":"N/A", "Fecha propuesta para el cierre":str(datetime.now().date()), "Prioridad":"Media", "Estado":"Abierto", "Observación":"N/A"}])
                conn.update(spreadsheet=URL_COND, data=pd.concat([df_cond_total, nueva], ignore_index=True))
                st.success("Guardado en Base de Condiciones")

    # --- PANTALLA 3: COMPORTAMIENTO ---
    elif menu == "🧠 Comportamiento":
        st.title("🧠 Registro de Comportamiento & PESV")
        with st.form("form_comp"):
            f_ins = st.text_input("Inspector")
            f_tipo = st.selectbox("Tipo", ["Comportamiento", "PESV Vehículo", "Tareas Críticas"])
            f_obs = st.text_area("Observación Factor Humano")
            if st.form_submit_button("🚀 REGISTRAR EN BDI COMPORTAMIENTO"):
                nueva_c = pd.DataFrame([{"Nit":nit_input, "ID_Inspección":str(uuid.uuid4())[:8], "Fecha/Hora Real":str(datetime.now()), "Inspector":f_ins, "Tipo de Inspección":f_tipo, "Estado observado":"Auditado", "Evidencia Fotográfica":"N/A", "Observaciones Factor Humano":f_obs}])
                conn.update(spreadsheet=URL_COMP, data=pd.concat([df_comp_total, nueva_c], ignore_index=True))
                st.success("Guardado en Base de Comportamiento")

    elif menu == "📂 PHVA":
        st.link_button("📁 Carpeta PHVA", "https://drive.google.com/drive/u/0/folders/17o_kAZMRcGhDeI3vAd0dEk_UQJGYQWBZ")
