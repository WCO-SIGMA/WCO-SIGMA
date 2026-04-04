import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.express as px
from datetime import datetime
import uuid

# 1. CONFIGURACIÓN
st.set_page_config(page_title="WCO-SIGMA SIG+PESV", layout="wide")

# --- DIRECCIONES EXACTAS (BASADAS EN TUS ENLACES) ---
URL_COND = "https://docs.google.com/spreadsheets/d/18OIJe409rr6o_o4HSweiuncIoOrgJOXEt0GFCmEsL4g/edit"
URL_COMP = "https://docs.google.com/spreadsheets/d/1szrDZsA59e5sMF6OAzPeQ_nDX7E9lMehaXCPHmVNx5o/edit"

conn = st.connection("gsheets", type=GSheetsConnection)

# 2. ACCESO
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/1063/1063302.png", width=100)
nit_input = st.sidebar.text_input("Ingrese identificación (NIT/Cédula):", "").strip()

if not nit_input:
    st.title("🚀 WCO-SIGMA: Gestión Integral")
    st.success("✅ Conexión con Google Cloud activa.")
    st.info("Ingrese el NIT para cargar sus bases de datos.")
else:
    # --- MOTOR DE LECTURA (USANDO URL DIRECTA) ---
    try:
        df_cond_total = conn.read(spreadsheet=URL_COND, ttl=0)
        df_cond_total.columns = df_cond_total.columns.str.strip()
        df_cond_total['Nit'] = df_cond_total['Nit'].astype(str).str.replace('.0', '', regex=False).str.strip()
        df_cond_emp = df_cond_total[df_cond_total['Nit'] == nit_input]
    except:
        df_cond_total = pd.DataFrame()
        df_cond_emp = pd.DataFrame()

    try:
        df_comp_total = conn.read(spreadsheet=URL_COMP, ttl=0)
        df_comp_total.columns = df_comp_total.columns.str.strip()
        df_comp_total['Nit'] = df_comp_total['Nit'].astype(str).str.replace('.0', '', regex=False).str.strip()
        df_comp_emp = df_comp_total[df_comp_total['Nit'] == nit_input]
    except:
        df_comp_total = pd.DataFrame()
        df_comp_emp = pd.DataFrame()

    menu = st.sidebar.radio("Módulos", ["📊 Dashboard Gerencial", "🛠️ Reporte Condiciones", "🧠 Reporte Comportamiento", "📂 Carpeta PHVA"])

    # --- PANTALLA 1: DASHBOARD ---
    if menu == "📊 Dashboard Gerencial":
        st.title(f"📊 Dashboard Ejecutivo - NIT: {nit_input}")
        t1, t2 = st.tabs(["🔍 Condiciones HSEQ", "🧠 Comportamiento & PESV"])
        
        with t1:
            if not df_cond_emp.empty:
                c1, c2 = st.columns(2)
                with c1: st.plotly_chart(px.pie(df_cond_emp, names='Estado', title="Estatus Hallazgos"), use_container_width=True)
                with c2: st.plotly_chart(px.bar(df_cond_emp, x='Condición Crítica', title="Resumen Riesgos"), use_container_width=True)
                st.dataframe(df_cond_emp, use_container_width=True)
            else: st.warning("No hay datos en Condiciones.")

        with t2:
            if not df_comp_emp.empty:
                st.plotly_chart(px.bar(df_comp_emp, x='Estado observado', title="Análisis Conducta"), use_container_width=True)
                st.dataframe(df_comp_emp, use_container_width=True)
            else: st.warning("No hay datos en Comportamiento.")

    # --- PANTALLA 2: FORMULARIO CONDICIONES ---
    elif menu == "🛠️ Reporte Condiciones":
        st.title("🛠️ Registro de Condiciones HSEQ")
        with st.form("form_final_cond"):
            col1, col2 = st.columns(2)
            with col1:
                f_emp = st.text_input("Empresa")
                f_hall = st.text_area("Hallazgo")
                f_cond = st.selectbox("Condición", ["Orden y aseo", "Herramientas", "Locativo", "Vial", "SST"])
            with col2:
                f_riesgo = st.selectbox("GTC 45", ["Físico", "Químico", "Biológico", "Psicosocial", "Biomecánico", "Seguridad"])
                f_est = st.selectbox("Estado", ["Abierto", "En Proceso", "Cerrado"])
            
            if st.form_submit_button("✅ GUARDAR"):
                nueva = pd.DataFrame([{
                    "Nit": str(nit_input), "Empresa": f_emp, "Fecha": str(datetime.now().date()), 
                    "Hallazgo": f_hall, "Condición Crítica": f_cond, "Clasificación del riesgo": f_riesgo, 
                    "Componente": "SST", "Responsable del cierre": "Auditor", 
                    "Fecha propuesta para el cierre": str(datetime.now().date()), 
                    "Prioridad": "Media", "Estado": f_est, "Observación": "Registro Inicial"
                }])
                
                # UNIÓN Y GUARDADO USANDO URL
                df_final = pd.concat([df_cond_total, nueva], ignore_index=True) if not df_cond_total.empty else nueva
                conn.update(spreadsheet=URL_COND, data=df_final)
                st.success("¡Datos sincronizados con BDI WCO SIGMA!")
                st.balloons()

    # --- PANTALLA 3: FORMULARIO COMPORTAMIENTO ---
    elif menu == "🧠 Reporte Comportamiento":
        st.title("🧠 Registro de Comportamiento")
        id_a = str(uuid.uuid4())[:8].upper()
        with st.form("form_final_comp"):
            f_ins = st.text_input("Nombre Inspector")
            f_obs = st.text_area("Observación")
            if st.form_submit_button("🚀 REGISTRAR"):
                nueva_c = pd.DataFrame([{
                    "Nit": str(nit_input), "ID_Inspección": id_a, "Fecha/Hora Real": str(datetime.now()), 
                    "Inspector": f_ins, "Tipo de Inspección": "Conducta", "Estado observado": "Seguro", 
                    "Evidencia Fotográfica": "N/A", "Observaciones Factor Humano": f_obs
                }])
                
                df_final_c = pd.concat([df_comp_total, nueva_c], ignore_index=True) if not df_comp_total.empty else nueva_c
                conn.update(spreadsheet=URL_COMP, data=df_final_c)
                st.success(f"¡Reporte {id_a} guardado en BDI COMPORTAMIENTO!")

    elif menu == "📂 Carpeta PHVA":
        st.link_button("📁 Abrir Drive", "https://drive.google.com/drive/u/0/folders/17o_kAZMRcGhDeI3vAd0dEk_UQJGYQWBZ")
