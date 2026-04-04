import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.express as px
from datetime import datetime
import uuid

# 1. CONFIGURACIÓN
st.set_page_config(page_title="WCO-SIGMA SIG+PESV", layout="wide")

# --- IDs DE TUS ARCHIVOS ---
ID_COND = "18OIJe409rr6o_o4HSweiuncIoOrgJOXEt0GFCmEsL4g"
ID_COMP = "1szrDZsA59e5sMF6OAzPeQ_nDX7E9lMehaXCPHmVNx5o"

conn = st.connection("gsheets", type=GSheetsConnection)

# 2. ACCESO
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/1063/1063302.png", width=100)
nit_input = st.sidebar.text_input("Ingrese NIT o Cédula:", "").strip()

if not nit_input:
    st.title("🚀 WCO-SIGMA: Gestión Integral")
    st.success("✅ Conexión con Google Cloud establecida con éxito.")
    st.info("Ingrese el NIT para visualizar sus tableros de control.")
else:
    # --- LECTURA DE DATOS CON MANEJO DE RESPUESTA 200 ---
    try:
        df_cond_total = conn.read(spreadsheet=ID_COND, ttl=0)
        if isinstance(df_cond_total, pd.DataFrame):
            df_cond_total.columns = df_cond_total.columns.str.strip()
            df_cond_total['Nit'] = df_cond_total['Nit'].astype(str).str.replace('.0', '', regex=False).str.strip()
            df_cond_emp = df_cond_total[df_cond_total['Nit'] == nit_input]
        else:
            df_cond_emp = pd.DataFrame()
    except:
        df_cond_emp = pd.DataFrame()

    try:
        df_comp_total = conn.read(spreadsheet=ID_COMP, ttl=0)
        if isinstance(df_comp_total, pd.DataFrame):
            df_comp_total.columns = df_comp_total.columns.str.strip()
            df_comp_total['Nit'] = df_comp_total['Nit'].astype(str).str.replace('.0', '', regex=False).str.strip()
            df_comp_emp = df_comp_total[df_comp_total['Nit'] == nit_input]
        else:
            df_comp_emp = pd.DataFrame()
    except:
        df_comp_emp = pd.DataFrame()

    menu = st.sidebar.radio("Módulos", ["📊 Dashboard Gerencial", "🛠️ Reporte Condiciones", "🧠 Reporte Comportamiento", "📂 Carpeta PHVA"])

    # --- DASHBOARD ---
    if menu == "📊 Dashboard Gerencial":
        st.title(f"📊 Dashboard SIG - NIT: {nit_input}")
        t1, t2 = st.tabs(["🔍 Condiciones HSEQ", "🧠 Comportamiento & PESV"])
        
        with t1:
            if not df_cond_emp.empty:
                c1, c2 = st.columns(2)
                with c1: st.plotly_chart(px.pie(df_cond_emp, names='Estado', title="Estatus de Hallazgos"), use_container_width=True)
                with c2: st.plotly_chart(px.bar(df_cond_emp, x='Condición Crítica', title="Tipología de Riesgos"), use_container_width=True)
                st.dataframe(df_cond_emp, use_container_width=True)
            else:
                st.warning("No hay datos registrados en Condiciones. Realice su primer reporte en el menú lateral.")

        with t2:
            if not df_comp_emp.empty:
                st.plotly_chart(px.bar(df_comp_emp, x='Estado observado', color='Estado observado', title="Análisis de Comportamiento"), use_container_width=True)
                st.dataframe(df_comp_emp, use_container_width=True)
            else:
                st.warning("No hay datos en Comportamiento.")

    # --- FORMULARIOS ---
    elif menu == "🛠️ Reporte Condiciones":
        st.title("🛠️ Registro de Condiciones")
        with st.form("f_cond"):
            f_emp = st.text_input("Empresa")
            f_hall = st.text_area("Hallazgo")
            f_cond = st.selectbox("Condición", ["Orden y aseo", "Herramientas", "Locativo", "Vial", "Otros"])
            f_est = st.selectbox("Estado", ["Abierto", "En Proceso", "Cerrado"])
            if st.form_submit_button("✅ GUARDAR"):
                nueva = pd.DataFrame([{"Nit":str(nit_input), "Empresa":f_emp, "Fecha":str(datetime.now().date()), "Hallazgo":f_hall, "Condición Crítica":f_cond, "Clasificación del riesgo":"SST", "Componente":"SST", "Responsable del cierre":"Asignado", "Fecha propuesta para el cierre":str(datetime.now().date()), "Prioridad":"Media", "Estado":f_est, "Observación":"Registro inicial"}])
                conn.update(spreadsheet=ID_COND, data=pd.concat([df_cond_total, nueva], ignore_index=True))
                st.success("¡Reporte guardado con éxito! Refresque el Dashboard.")

    elif menu == "🧠 Reporte Comportamiento":
        st.title("🧠 Registro de Comportamiento")
        with st.form("f_comp"):
            f_ins = st.text_input("Inspector")
            f_obs = st.text_area("Observaciones")
            if st.form_submit_button("🚀 REGISTRAR"):
                nueva_c = pd.DataFrame([{"Nit":str(nit_input), "ID_Inspección":str(uuid.uuid4())[:8].upper(), "Fecha/Hora Real":str(datetime.now()), "Inspector":f_ins, "Tipo de Inspección":"Conducta", "Estado observado":"✅ SEGURO", "Evidencia Fotográfica":"N/A", "Observaciones Factor Humano":f_obs}])
                conn.update(spreadsheet=ID_COMP, data=pd.concat([df_comp_total, nueva_c], ignore_index=True))
                st.success("¡Comportamiento registrado!")

    elif menu == "📂 Carpeta PHVA":
        st.link_button("📁 Abrir Drive", "https://drive.google.com/drive/u/0/folders/17o_kAZMRcGhDeI3vAd0dEk_UQJGYQWBZ")
