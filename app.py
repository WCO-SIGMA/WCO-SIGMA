import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.express as px
from datetime import datetime
import uuid

# 1. CONFIGURACIÓN
st.set_page_config(page_title="WCO-SIGMA SIG+ACPM", layout="wide")

# --- CONFIGURACIÓN DE IDENTIFICADORES (NOMBRES DE ARCHIVO EN DRIVE) ---
TITULO_COND = "BDI WCO SIGMA"
TITULO_COMP = "BDI COMPORTAMIENTO"
TITULO_ACPM = "BD ACPM" 

# URLs PARA LECTURA (Dashboard)
URL_COND = "https://docs.google.com/spreadsheets/d/18OIJe409rr6o_o4HSweiuncIoOrgJOXEt0GFCmEsL4g/edit"
URL_COMP = "https://docs.google.com/spreadsheets/d/1szrDZsA59e5sMF6OAzPeQ_nDX7E9lMehaXCPHmVNx5o/edit"
URL_ACPM = "TU_URL_DE_BD_ACPM_AQUI" 

conn = st.connection("gsheets", type=GSheetsConnection)

# 2. ACCESO POR NIT
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/1063/1063302.png", width=100)
nit_user = st.sidebar.text_input("Ingrese identificación (NIT/Cédula):", "").strip()

if not nit_user:
    st.title("🚀 WCO-SIGMA: Gestión Integral PHVA")
    st.info("Sistemas BDI Vinculados. Ingrese el NIT para activar el análisis y reportes.")
else:
    # --- MOTOR DE LECTURA ---
    def cargar_datos(url):
        try:
            df = conn.read(spreadsheet=url, ttl=0)
            if df is not None and not df.empty:
                df.columns = df.columns.str.strip()
                df['Nit'] = df['Nit'].astype(str).apply(lambda x: x.split('.')[0].strip())
                return df, df[df['Nit'] == nit_user]
            return pd.DataFrame(), pd.DataFrame()
        except: return pd.DataFrame(), pd.DataFrame()

    df_cond_total, df_cond_emp = cargar_datos(URL_COND)
    df_comp_total, df_comp_emp = cargar_datos(URL_COMP)
    df_acpm_total, df_acpm_emp = cargar_datos(URL_ACPM)

    menu = st.sidebar.radio("Navegación", ["📊 Dashboard & Análisis", "⚖️ Gestión de ACPM", "🛠️ Reporte Condiciones", "🧠 Reporte Comportamiento"])

    # --- PANTALLA 1: DASHBOARD & ANÁLISIS (ESTRUCTURAS RECUPERADAS) ---
    if menu == "📊 Dashboard & Análisis":
        st.title(f"📊 Panel Gerencial de Análisis - NIT: {nit_user}")
        tab1, tab2, tab3 = st.tabs(["🔍 Condiciones HSEQ", "🧠 Comportamiento/PESV", "⚖️ Mejora (ACPM)"])
        
        with tab1:
            if not df_cond_emp.empty:
                c1, c2 = st.columns(2)
                with c1: st.plotly_chart(px.pie(df_cond_emp, names='Estado', title="Estatus de Hallazgos", hole=0.4), use_container_width=True)
                with c2: st.plotly_chart(px.bar(df_cond_emp, x='Condición Crítica', color='Prioridad', title="Prioridad por Tipo de Condición"), use_container_width=True)
                st.subheader("📝 Análisis y Plan de Acción")
                st.text_area("Análisis Técnico de Condiciones:", key="an_c")
                st.text_area("Propuesta de Medidas de Intervención:", key="pl_c")
                st.dataframe(df_cond_emp, use_container_width=True)
            else: st.warning("Sin datos en BDI WCO SIGMA.")

        with tab2:
            if not df_comp_emp.empty:
                g1, g2 = st.columns(2)
                with g1: st.plotly_chart(px.bar(df_comp_emp, x='Estado observado', color='Estado observado', title="Cultura de Seguridad"), use_container_width=True)
                with g2: st.plotly_chart(px.pie(df_comp_emp, names='Tipo de Inspección', title="Módulos de Observación"), use_container_width=True)
                st.subheader("🧠 Análisis de Factor Humano")
                st.text_area("Diagnóstico de Riesgo Conductual:", key="an_h")
                st.text_area("Plan de Refuerzo PESV/SST:", key="pl_h")
                st.dataframe(df_comp_emp, use_container_width=True)
            else: st.warning("Sin datos en BDI COMPORTAMIENTO.")

        with tab3:
            if not df_acpm_emp.empty:
                st.plotly_chart(px.pie(df_acpm_emp, names='Componente', title="ACPM por Sistema SIG"), use_container_width=True)
                st.subheader("⚖️ Evaluación de Mejora")
                st.text_area("Análisis de Eficacia ACPM:", key="an_m")
                st.dataframe(df_acpm_emp, use_container_width=True)

    # --- PANTALLA 2: REPORTE CONDICIONES (ESTRUCTURA FIEL A BDI WCO SIGMA) ---
    elif menu == "🛠️ Reporte Condiciones":
        st.title("🛠️ Inspección de Condiciones de Seguridad")
        with st.form("form_cond_final"):
            col1, col2 = st.columns(2)
            with col1:
                f_emp = st.text_input("Empresa")
                f_hall = st.text_area("Hallazgo")
                f_cond = st.selectbox("Condición Crítica", ["Orden y aseo", "Herramientas/Equipos", "Daño locativo", "Sistemas eléctricos", "Vial", "Otros"])
                f_riesgo = st.selectbox("Clasificación del riesgo", ["Físico", "Químico", "Biológico", "Psicosocial", "Biomecánico", "Seguridad", "Natural"])
            with col2:
                f_comp = st.selectbox("Componente", ["SST", "Ambiente", "Calidad", "Vial"])
                f_resp = st.text_input("Responsable del cierre")
                f_fec_p = st.date_input("Fecha propuesta para el cierre")
                f_prio = st.selectbox("Prioridad", ["Baja", "Media", "Alta"])
                f_est = st.selectbox("Estado", ["Abierto", "En Proceso", "Cerrado"])
                f_obs = st.text_area("Observación")
            
            if st.form_submit_button("✅ GUARDAR EN BDI WCO SIGMA"):
                nueva_fila = pd.DataFrame([{
                    "Nit": str(nit_user), "Empresa": f_emp, "Fecha": str(datetime.now().date()), 
                    "Hallazgo": f_hall, "Condición Crítica": f_cond, "Clasificación del riesgo": f_riesgo, 
                    "Componente": f_comp, "Responsable del cierre": f_resp, 
                    "Fecha propuesta para el cierre": str(f_fec_p), "Prioridad": f_prio, 
                    "Estado": f_est, "Observación": f_obs
                }])
                conn.update(spreadsheet=TITULO_COND, data=pd.concat([df_cond_total, nueva_fila], ignore_index=True))
                st.success("Inspección registrada con éxito.")

    # --- PANTALLA 3: REPORTE COMPORTAMIENTO (ESTRUCTURA FIEL A BDI COMPORTAMIENTO) ---
    elif menu == "🧠 Reporte Comportamiento":
        st.title("🧠 Observación de Comportamiento y PESV")
        with
