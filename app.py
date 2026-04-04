import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.express as px
from datetime import datetime
import uuid

# 1. CONFIGURACIÓN
st.set_page_config(page_title="WCO-SIGMA SIG+PESV", layout="wide")

# --- ⚠️ PEGA TUS ENLACES REALES AQUÍ ⚠️ ---
URL_COND = "AQUÍ_VA_TU_URL_DE_CONDICIONES" 
URL_COMP = "AQUÍ_VA_TU_URL_DE_COMPORTAMIENTO"

conn = st.connection("gsheets", type=GSheetsConnection)

# 2. ACCESO POR NIT
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/1063/1063302.png", width=100)
nit_input = st.sidebar.text_input("Ingrese identificación (NIT/Cédula):", "").strip()

if not nit_input:
    st.title("🚀 WCO-SIGMA: Gestión Integral")
    st.info("Sincronización Multi-Motor. Ingrese el NIT para iniciar.")
else:
    # --- LECTURA DE DATOS ---
    try:
        df_cond_total = conn.read(spreadsheet=URL_COND, ttl=0)
        df_cond_total.columns = df_cond_total.columns.str.strip()
        df_cond_total['Nit'] = df_cond_total['Nit'].astype(str).str.replace('.0', '', regex=False).str.strip()
        df_cond_emp = df_cond_total[df_cond_total['Nit'] == nit_input]
    except:
        df_cond_emp = pd.DataFrame()
        df_cond_total = pd.DataFrame()

    try:
        df_comp_total = conn.read(spreadsheet=URL_COMP, ttl=0)
        df_comp_total.columns = df_comp_total.columns.str.strip()
        df_comp_total['Nit'] = df_comp_total['Nit'].astype(str).str.replace('.0', '', regex=False).str.strip()
        df_comp_emp = df_comp_total[df_comp_total['Nit'] == nit_input]
    except:
        df_comp_emp = pd.DataFrame()
        df_comp_total = pd.DataFrame()

    menu = st.sidebar.radio("Módulos", ["📊 Dashboard Gerencial", "🛠️ Reporte Condiciones", "🧠 Reporte Comportamiento", "📂 Carpeta PHVA"])

    # --- PANTALLA 1: DASHBOARD ---
    if menu == "📊 Dashboard Gerencial":
        st.title(f"📊 Dashboard SIG - NIT: {nit_input}")
        t1, t2 = st.tabs(["🔍 Condiciones HSEQ", "🧠 Comportamiento & PESV"])
        
        with t1:
            if not df_cond_emp.empty:
                c1, c2, c3 = st.columns(3)
                total_c = len(df_cond_emp)
                abiertos = len(df_cond_emp[df_cond_emp['Estado'].astype(str).str.upper() == 'ABIERTO'])
                c1.metric("Inspecciones", total_c)
                c2.metric("Pendientes", abiertos, delta_color="inverse")
                c3.metric("Eficacia", f"{int(((total_c-abiertos)/total_c)*100)}%" if total_c > 0 else "0%")
                st.plotly_chart(px.bar(df_cond_emp['Condición Crítica'].value_counts().reset_index(), x='count', y='Condición Crítica', orientation='h', title="Hallazgos por Condición"), use_container_width=True)
                st.dataframe(df_cond_emp, use_container_width=True)
            else:
                st.warning("Sin datos en Condiciones.")

        with t2:
            if not df_comp_emp.empty:
                st.plotly_chart(px.bar(df_comp_emp, x='Estado observado', color='Estado observado', title="Análisis Comportamiento"), use_container_width=True)
                st.dataframe(df_comp_emp, use_container_width=True)
            else:
                st.warning("Sin datos en Comportamiento.")

    # --- PANTALLA 2: CONDICIONES ---
    elif menu == "🛠️ Reporte Condiciones":
        st.title("🛠️ Registro de Condiciones HSEQ")
        with st.form("form_cond"):
            col1, col2 = st.columns(2)
            with col1:
                f_emp = st.text_input("Empresa")
                f_hall = st.text_area("Hallazgo Detallado")
                f_cond = st.selectbox("Condición Crítica", ["Orden y aseo", "Herramientas/Equipos", "Daño locativo", "Sistemas eléctricos", "Ambiental", "Vial", "Otros"])
                f_riesgo = st.selectbox("GTC 45", ["Físico", "Químico", "Biológico", "Psicosocial", "Biomecánico", "Seguridad", "Natural"])
            with col2:
                f_comp = st.selectbox("Componente", ["SST", "Ambiente", "Vial", "Calidad"])
                f_prio = st.selectbox("Prioridad", ["Baja", "Media", "Alta"])
                f_est = st.selectbox("Estado", ["Abierto", "En Proceso", "Cerrado"])
                f_obs = st.text_area("Observación / Plan de Acción")
            
            if st.form_submit_button("✅ GUARDAR CONDICIÓN"):
                nueva = pd.DataFrame([{"Nit":str(nit_input), "Empresa":f_emp, "Fecha":str(datetime.now().date()), "Hallazgo":f_hall, "Condición Crítica":f_cond, "Clasificación del riesgo":f_riesgo, "Componente":f_comp, "Responsable del cierre":"Auditor", "Fecha propuesta para el cierre":str(datetime.now().date()), "Prioridad":f_prio, "Estado":f_est, "Observación":f_obs}])
                conn.update(spreadsheet=URL_COND, data=pd.concat([df_cond_total, nueva], ignore_index=True))
                st.success("Guardado en Condiciones.")

    # --- PANTALLA 3: COMPORTAMIENTO ---
    elif menu == "🧠 Reporte Comportamiento":
        st.title("🧠 Registro de Comportamiento & PESV")
        id_auto = str(uuid.uuid4())[:8].upper()
        with st.form("form_comp"):
            f_ins = st.text_input("Inspector")
            f_tipo = st.selectbox("Tipo de Inspección", ["Observación de Comportamiento", "Preoperacional Vehículo (PESV)", "Auditoría Tareas Críticas"])
            f_est_obs = st.selectbox("Estado Observado", ["✅ SEGURO", "⚠️ ATÍPICO", "🚫 PELIGROSO"])
            f_humano = st.multiselect("Factores Humanos:", ["Distracción", "Fatiga", "Falta de EPP", "Exceso de confianza", "Prisa"])
            f_detalles = st.text_area("Descripción detallada")
            
            if st.form_submit_button("🚀 REGISTRAR COMPORTAMIENTO"):
                nueva_c = pd.DataFrame([{"Nit":str(nit_input), "ID_Inspección":id_auto, "Fecha/Hora Real":str(datetime.now()), "Inspector":f_ins, "Tipo de Inspección":f_tipo, "Estado observado":f_est_obs, "Evidencia Fotográfica":"N/A", "Observaciones Factor Humano": ", ".join(f_humano) + " | " + f_detalles}])
                conn.update(spreadsheet=URL_COMP, data=pd.concat([df_comp_total, nueva_c], ignore_index=True))
                st.success(f"Registrado con ID {id_auto}.")

    elif menu == "📂 Carpeta PHVA":
        st.link_button("📁 Abrir Drive", "https://drive.google.com/drive/u/0/folders/17o_kAZMRcGhDeI3vAd0dEk_UQJGYQWBZ")
