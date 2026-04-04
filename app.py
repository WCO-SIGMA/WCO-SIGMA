import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.express as px
from datetime import datetime
import uuid

# 1. CONFIGURACIÓN
st.set_page_config(page_title="WCO-SIGMA SIG+PESV", layout="wide")

# --- ⚠️ ATENCIÓN: PEGA AQUÍ TUS URLS REALES ⚠️ ---
URL_COND = "PON_AQUI_LA_URL_DE_CONDICIONES" 
URL_COMP = "PON_AQUI_LA_URL_DE_COMPORTAMIENTO"

conn = st.connection("gsheets", type=GSheetsConnection)

# 2. ACCESO POR NIT
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/1063/1063302.png", width=100)
nit_input = st.sidebar.text_input("Ingrese NIT o Cédula:", "").strip()

if not nit_input:
    st.title("🚀 WCO-SIGMA: Gestión Integral")
    st.info("Sincronización Multi-Motor. Ingrese el NIT para iniciar sesión.")
else:
    # --- MOTOR DE LECTURA CON VALIDACIÓN ---
    try:
        df_cond_total = conn.read(spreadsheet=URL_COND, ttl=0)
        df_cond_total.columns = df_cond_total.columns.str.strip()
        df_cond_total['Nit'] = df_cond_total['Nit'].astype(str).str.replace('.0', '', regex=False).str.strip()
        df_cond_emp = df_cond_total[df_cond_total['Nit'] == nit_input]
    except Exception as e:
        st.sidebar.error("❌ Error conectando a Condiciones. Revise URL y Permisos.")
        df_cond_total = pd.DataFrame()
        df_cond_emp = pd.DataFrame()

    try:
        df_comp_total = conn.read(spreadsheet=URL_COMP, ttl=0)
        df_comp_total.columns = df_comp_total.columns.str.strip()
        df_comp_total['Nit'] = df_comp_total['Nit'].astype(str).str.replace('.0', '', regex=False).str.strip()
        df_comp_emp = df_comp_total[df_comp_total['Nit'] == nit_input]
    except Exception as e:
        st.sidebar.error("❌ Error conectando a Comportamiento. Revise URL y Permisos.")
        df_comp_total = pd.DataFrame()
        df_comp_emp = pd.DataFrame()

    menu = st.sidebar.radio("Menú Principal", ["📊 Dashboard Gerencial", "🛠️ Reporte Condiciones", "🧠 Reporte Comportamiento", "📂 Carpeta PHVA"])

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
                st.dataframe(df_cond_emp, use_container_width=True)
            else:
                st.warning("No hay datos en la Base de Condiciones.")

        with t2:
            if not df_comp_emp.empty:
                st.plotly_chart(px.bar(df_comp_emp, x='Estado observado', title="Análisis Comportamiento"), use_container_width=True)
                st.dataframe(df_comp_emp, use_container_width=True)
            else:
                st.warning("No hay datos en la Base de Comportamiento.")

    # --- PANTALLA 2: CONDICIONES ---
    elif menu == "🛠️ Reporte Condiciones":
        st.title("🛠️ Registro de Condiciones HSEQ")
        with st.form("form_cond"):
            col1, col2 = st.columns(2)
            with col1:
                f_emp = st.text_input("Empresa")
                f_hall = st.text_area("Hallazgo Detallado")
                f_cond = st.selectbox("Condición Crítica", ["Orden y aseo", "Herramientas/Equipos", "Daño locativo", "Ambiental", "Vial", "Otros"])
            with col2:
                f_riesgo = st.selectbox("GTC 45", ["Físico", "Químico", "Biológico", "Psicosocial", "Biomecánico", "Seguridad", "Natural"])
                f_est = st.selectbox("Estado", ["Abierto", "En Proceso", "Cerrado"])
            
            if st.form_submit_button("✅ GUARDAR"):
                if URL_COND != "PON_AQUI_LA_URL_DE_CONDICIONES":
                    nueva = pd.DataFrame([{"Nit":str(nit_input), "Empresa":f_emp, "Fecha":str(datetime.now().date()), "Hallazgo":f_hall, "Condición Crítica":f_cond, "Clasificación del riesgo":f_riesgo, "Componente":"SST", "Responsable del cierre":"Pendiente", "Fecha propuesta para el cierre":str(datetime.now().date()), "Prioridad":"Media", "Estado":f_est, "Observación":"Registro inicial"}])
                    conn.update(spreadsheet=URL_COND, data=pd.concat([df_cond_total, nueva], ignore_index=True))
                    st.success("Guardado en Condiciones.")
                else:
                    st.error("Error: Configure la URL de Condiciones en el código.")

    # --- PANTALLA 3: COMPORTAMIENTO ---
    elif menu == "🧠 Reporte Comportamiento":
        st.title("🧠 Registro de Comportamiento & PESV")
        id_auto = str(uuid.uuid4())[:8].upper()
        with st.form("form_comp"):
            f_ins = st.text_input("Nombre del Inspector")
            f_tipo = st.selectbox("Tipo", ["Observación de Comportamiento", "Preoperacional Vehículo", "Auditoría Tareas Críticas"])
            f_humano = st.text_area("Observaciones Factor Humano")
            
            if st.form_submit_button("🚀 REGISTRAR"):
                if URL_COMP != "PON_AQUI_LA_URL_DE_COMPORTAMIENTO":
                    nueva_c = pd.DataFrame([{"Nit":str(nit_input), "ID_Inspección":id_auto, "Fecha/Hora Real":str(datetime.now()), "Inspector":f_ins, "Tipo de Inspección":f_tipo, "Estado observado":"Auditado", "Evidencia Fotográfica":"N/A", "Observaciones Factor Humano":f_humano}])
                    conn.update(spreadsheet=URL_COMP, data=pd.concat([df_comp_total, nueva_c], ignore_index=True))
                    st.success(f"Registrado con ID {id_auto}.")
                else:
                    st.error("Error: Configure la URL de Comportamiento en el código.")

    elif menu == "📂 Carpeta PHVA":
        st.link_button("📁 Abrir Drive", "https://drive.google.com/drive/u/0/folders/17o_kAZMRcGhDeI3vAd0dEk_UQJGYQWBZ")
