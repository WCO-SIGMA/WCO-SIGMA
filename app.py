import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.express as px
from datetime import datetime
import uuid

# 1. CONFIGURACIÓN
st.set_page_config(page_title="WCO-SIGMA SIG+PESV", layout="wide")

# --- CONEXIÓN A BASES DE DATOS ---
URL_COND = "https://docs.google.com/spreadsheets/d/18OIJe409rr6o_o4HSweiuncIoOrgJOXEt0GFCmEsL4g/edit"
URL_COMP = "https://docs.google.com/spreadsheets/d/1szrDZsA59e5sMF6OAzPeQ_nDX7E9lMehaXCPHmVNx5o/edit"

conn = st.connection("gsheets", type=GSheetsConnection)

# 2. ACCESO
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/1063/1063302.png", width=100)
nit_input = st.sidebar.text_input("Identificación Empresa (NIT):", "").strip()

if not nit_input:
    st.title("🚀 WCO-SIGMA: Sistema de Gestión PHVA")
    st.info("Ingrese el NIT para activar el análisis de datos y seguimiento de medidas.")
else:
    # --- CARGA DE DATOS ---
    try:
        df_cond = conn.read(spreadsheet=URL_COND, ttl=0)
        df_cond.columns = df_cond.columns.str.strip()
        df_cond['Nit'] = df_cond['Nit'].astype(str).str.replace('.0', '', regex=False).str.strip()
        df_cond_emp = df_cond[df_cond['Nit'] == nit_input]
    except: df_cond_emp = pd.DataFrame()

    try:
        df_comp = conn.read(spreadsheet=URL_COMP, ttl=0)
        df_comp.columns = df_comp.columns.str.strip()
        df_comp['Nit'] = df_comp['Nit'].astype(str).str.replace('.0', '', regex=False).str.strip()
        df_comp_emp = df_comp[df_comp['Nit'] == nit_input]
    except: df_comp_emp = pd.DataFrame()

    menu = st.sidebar.radio("Navegación", ["📊 Dashboard & Análisis", "📉 Seguimiento de Medidas", "🛠️ Registro Condiciones", "🧠 Registro Comportamiento"])

    # --- PANTALLA 1: DASHBOARD Y ANÁLISIS ---
    if menu == "📊 Dashboard & Análisis":
        st.title(f"📊 Análisis de Datos Gerenciales - NIT: {nit_input}")
        t1, t2 = st.tabs(["🔍 Análisis de Condiciones", "🧠 Análisis de Comportamiento"])

        with t1:
            if not df_cond_emp.empty:
                col1, col2 = st.columns([2, 1])
                with col1:
                    st.plotly_chart(px.bar(df_cond_emp, x='Condición Crítica', color='Estado', title="Distribución de Hallazgos"), use_container_width=True)
                with col2:
                    st.write("### 📝 Espacio de Análisis Técnico")
                    analisis_c = st.text_area("Diagnóstico de Condiciones HSEQ:", placeholder="Ej: Se observa un incremento en condiciones locativas...")
                    plan_c = st.text_area("Plan de Acción Propuesto:", placeholder="Ej: Realizar jornada de orden y aseo en semana 15...")
                
                st.markdown("---")
                st.write("### 📋 Base de Datos de Inspecciones")
                st.dataframe(df_cond_emp, use_container_width=True)
            else: st.warning("Sin datos para analizar en Condiciones.")

        with t2:
            if not df_comp_emp.empty:
                col3, col4 = st.columns([2, 1])
                with col3:
                    st.plotly_chart(px.pie(df_comp_emp, names='Estado observado', title="Cultura de Seguridad", hole=0.4), use_container_width=True)
                with col4:
                    st.write("### 🧠 Análisis de Factor Humano")
                    analisis_h = st.text_area("Diagnóstico de Comportamiento:", placeholder="Análisis de actos inseguros detectados...")
                    medida_h = st.text_area("Intervención PESV/SST:", placeholder="Medidas para corregir conductas...")
                
                st.markdown("---")
                st.write("### 📋 Histórico de Observaciones")
                st.dataframe(df_comp_emp, use_container_width=True)
            else: st.warning("Sin datos para analizar en Comportamiento.")

    # --- PANTALLA 2: SEGUIMIENTO DE MEDIDAS (PHVA) ---
    elif menu == "📉 Seguimiento de Medidas":
        st.title("📉 Seguimiento a Medidas de Intervención")
        st.info("Aquí puede visualizar y filtrar las tareas pendientes para asegurar el cierre de hallazgos.")
        
        if not df_cond_emp.empty:
            # Filtramos solo lo que no está cerrado
            pendientes = df_cond_emp[df_cond_emp['Estado'].str.upper() != 'CERRADO']
            
            c1, c2, c3 = st.columns(3)
            c1.metric("Tareas Pendientes", len(pendientes))
            c2.metric("Total Hallazgos", len(df_cond_emp))
            c3.metric("Nivel de Incumplimiento", f"{int((len(pendientes)/len(df_cond_emp))*100)}%" if len(df_cond_emp)>0 else "0%")

            st.write("### 🚩 Alerta de Medidas de Intervención Pendientes")
            st.table(pendientes[['Fecha', 'Condición Crítica', 'Hallazgo', 'Responsable del cierre', 'Estado']])
        else:
            st.success("🎉 No hay medidas de intervención pendientes para este NIT.")

    # --- MÓDULOS DE REGISTRO (SIN CAMBIOS) ---
    elif menu == "🛠️ Registro Condiciones":
        st.title("🛠️ Nuevo Reporte de Condiciones")
        with st.form("f_cond"):
            f_hall = st.text_area("Describa el Hallazgo")
            f_cond = st.selectbox("Categoría", ["Orden y aseo", "Vial", "Locativo", "Eléctrico", "Otros"])
            f_resp = st.text_input("Responsable Asignado")
            f_est = st.selectbox("Estado Actual", ["Abierto", "En Proceso"])
            if st.form_submit_button("✅ GUARDAR"):
                nueva = pd.DataFrame([{"Nit":str(nit_input), "Fecha":str(datetime.now().date()), "Hallazgo":f_hall, "Condición Crítica":f_cond, "Responsable del cierre":f_resp, "Estado":f_est}])
                conn.update(spreadsheet=URL_COND, data=pd.concat([df_cond, nueva], ignore_index=True))
                st.success("Guardado. Revise el Dashboard de Análisis.")

    elif menu == "🧠 Registro Comportamiento":
        st.title("🧠 Nueva Observación Conductual")
        with st.form("f_comp"):
            f_obs = st.text_area("Detalle del Comportamiento")
            f_tipo = st.selectbox("Tipo", ["Conducta", "PESV", "EPP"])
            f_est_obs = st.selectbox("Calificación", ["✅ SEGURO", "⚠️ ATÍPICO", "🚫 PELIGROSO"])
            if st.form_submit_button("🚀 REGISTRAR"):
                nueva_c = pd.DataFrame([{"Nit":str(nit_input), "ID_Inspección":str(uuid.uuid4())[:8], "Fecha/Hora Real":str(datetime.now()), "Tipo de Inspección":f_tipo, "Estado observado":f_est_obs, "Observaciones Factor Humano":f_obs}])
                conn.update(spreadsheet=URL_COMP, data=pd.concat([df_comp, nueva_c], ignore_index=True))
                st.success("Registrado.")

    elif menu == "📂 Carpeta PHVA":
        st.link_button("📁 Abrir Drive", "https://drive.google.com/drive/u/0/folders/17o_kAZMRcGhDeI3vAd0dEk_UQJGYQWBZ")
