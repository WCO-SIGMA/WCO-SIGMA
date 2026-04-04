import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.express as px
from datetime import datetime
import uuid

# 1. CONFIGURACIÓN
st.set_page_config(page_title="WCO-SIGMA SIG+ACPM", layout="wide")

# --- IDENTIFICADORES DE ARCHIVO ---
TITULO_COND = "BDI WCO SIGMA"
TITULO_COMP = "BDI COMPORTAMIENTO"
TITULO_ACPM = "BD ACPM" 

URL_COND = "https://docs.google.com/spreadsheets/d/18OIJe409rr6o_o4HSweiuncIoOrgJOXEt0GFCmEsL4g/edit"
URL_COMP = "https://docs.google.com/spreadsheets/d/1szrDZsA59e5sMF6OAzPeQ_nDX7E9lMehaXCPHmVNx5o/edit"
# ⚠️ ASEGÚRATE DE QUE ESTA URL SEA LA DE TU BD ACPM
URL_ACPM = "TU_URL_DE_BD_ACPM_AQUI" 

conn = st.connection("gsheets", type=GSheetsConnection)

# 2. ACCESO
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/1063/1063302.png", width=100)
nit_user = st.sidebar.text_input("Ingrese NIT de la Empresa:", "").strip()

if not nit_user:
    st.title("🚀 WCO-SIGMA: Sistema de Gestión PHVA")
    st.info("Sistemas Vinculados. Ingrese el NIT para activar el análisis.")
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

    # --- PANTALLA 1: DASHBOARD & ANÁLISIS ---
    if menu == "📊 Dashboard & Análisis":
        st.title(f"📊 Panel Gerencial - NIT: {nit_user}")
        tab1, tab2, tab3 = st.tabs(["🔍 Condiciones HSEQ", "🧠 Comportamiento/PESV", "⚖️ Mejora (ACPM)"])
        
        with tab1:
            if not df_cond_emp.empty:
                c1, c2 = st.columns(2)
                with c1: st.plotly_chart(px.pie(df_cond_emp, names='Estado', title="Estatus Hallazgos", hole=0.4), use_container_width=True)
                with c2: st.plotly_chart(px.bar(df_cond_emp, x='Condición Crítica', color='Prioridad', title="Prioridad por Categoría"), use_container_width=True)
                st.subheader("📝 Análisis de Condiciones")
                st.text_area("Análisis Técnico:", key="an_c")
                st.dataframe(df_cond_emp, use_container_width=True)
            else: st.warning("Sin datos en Condiciones.")

        with tab2:
            if not df_comp_emp.empty:
                g1, g2 = st.columns(2)
                with g1: st.plotly_chart(px.bar(df_comp_emp, x='Estado observado', color='Estado observado', title="Cultura de Seguridad"), use_container_width=True)
                with g2: st.plotly_chart(px.pie(df_comp_emp, names='Tipo de Inspección', title="Módulos de Observación"), use_container_width=True)
                st.subheader("🧠 Análisis Conductual")
                st.text_area("Diagnóstico de Factor Humano:", key="an_h")
                st.dataframe(df_comp_emp, use_container_width=True)
            else: st.warning("Sin datos en Comportamiento.")

        with tab3:
            st.subheader("⚖️ Indicadores de Mejora Continua (ACPM)")
            if not df_acpm_emp.empty:
                # GRÁFICOS DE ACPM
                col_acpm1, col_acpm2 = st.columns(2)
                with col_acpm1:
                    # Gráfico por Componente (SST, Vial, etc)
                    if 'Componente' in df_acpm_emp.columns:
                        st.plotly_chart(px.pie(df_acpm_emp, names='Componente', title="ACPM por Sistema SIG", hole=0.4), use_container_width=True)
                with col_acpm2:
                    # Gráfico por Estado
                    if 'Estado' in df_acpm_emp.columns:
                        st.plotly_chart(px.bar(df_acpm_emp, x='Estado', color='Fuente', title="Avance de Tareas"), use_container_width=True)
                
                # ESPACIOS DE ANÁLISIS Y PLAN DE ACCIÓN ACPM
                st.markdown("---")
                st.subheader("📝 Evaluación y Determinación de Plan de Acción (ACPM)")
                col_an1, col_an2 = st.columns(2)
                with col_an1:
                    st.text_area("Análisis de Eficacia de las Acciones:", key="an_acpm_v", placeholder="Analice si las acciones están cerrando las brechas...")
                with col_an2:
                    st.text_area("Determinación de Nuevas Medidas SIG:", key="pl_acpm_v", placeholder="Defina nuevos compromisos gerenciales...")
                
                st.dataframe(df_acpm_emp, use_container_width=True)
            else:
                st.warning("⚠️ No hay datos registrados en el módulo ACPM para este NIT. Realice un reporte para activar los gráficos.")

    # --- PANTALLA 2: GESTIÓN DE ACPM (REPORTE) ---
    elif menu == "⚖️ Gestión de ACPM":
        st.title("⚖️ Registro de Acciones ACPM")
        with st.form("form_acpm"):
            c1, c2 = st.columns(2)
            with c1:
                f_emp = st.text_input("Empresa")
                f_comp = st.selectbox("Componente", ["SST", "Ambiente", "Calidad", "Vial"])
                f_fuen = st.selectbox("Fuente", ["inspecciones", "auditorías", "incidentes", "revisión gerencial"])
                f_desc = st.text_area("Descripción Hallazgo")
            with c2:
                f_raiz = st.text_input("Causa Raíz Final")
                f_acci = st.text_area("Acción Propuesta")
                f_tipo = st.radio("Tipo Acción", ["Correctiva", "Preventiva", "Mejora"])
                f_fec_c = st.date_input("Fecha Cierre Prevista")
                f_cambio = st.radio("¿Activa gestión del cambio?", ["No", "Sí"])
                f_estado = st.selectbox("Estado", ["Abierta", "En Ejecución"])

            if st.form_submit_button("💾 GUARDAR ACPM"):
                nueva = pd.DataFrame([{
                    "Nit": str(nit_user), "Empresa": f_emp, "Fecha de reporte": str(datetime.now().date()),
                    "Componente": f_comp, "Fuente": f_fuen, "Descripción Hallazgo": f_desc,
                    "Análisis Causa ¿Porqué 1?": "N/A", "Análisis Causa ¿Porqué 2?": "N/A", 
                    "Análisis Causa ¿Porqué 3?": "N/A", "Análisis Causa ¿Porqué 4?": "N/A", 
                    "Análisis Causa ¿Porqué 5?": "N/A", "Causa raíz": f_raiz,
                    "Acción Propuesta": f_acci, "Tipo Acción": f_tipo, "Responsable": "SIG",
                    "Fecha Cierre Prevista": str(f_fec_c), "Eficacia de la acción tomada": "Pendiente",
                    "La acción tomada activa gestión del cambio (Si es afirmativo IPVR, IAVI y sus controles)": f_cambio, 
                    "Estado": f_estado
                }])
                df_upd = pd.concat([df_acpm_total, nueva], ignore_index=True)
                conn.update(spreadsheet=TITULO_ACPM, data=df_upd)
                st.success("ACPM Guardada.")

    # --- REPORTES DE INSPECCIÓN (MANTENER VARIABLES ACTIVAS) ---
    elif menu == "🛠️ Reporte Condiciones":
        st.title("🛠️ Registro de Condiciones")
        with st.form("f_cond"):
            f_hall = st.text_area("Hallazgo")
            f_cat = st.selectbox("Categoría", ["Orden y aseo", "Herramientas", "Vial", "Otros"])
            if st.form_submit_button("✅ GUARDAR"):
                nueva_c = pd.DataFrame([{"Nit": str(nit_user), "Empresa": "Sede", "Fecha": str(datetime.now().date()), "Hallazgo": f_hall, "Condición Crítica": f_cat, "Clasificación del riesgo": "Seguridad", "Componente": "SST", "Responsable del cierre": "Auditor", "Fecha propuesta para el cierre": str(datetime.now().date()), "Prioridad": "Media", "Estado": "Abierto", "Observación": "Registro inicial"}])
                conn.update(spreadsheet=TITULO_COND, data=pd.concat([df_cond_total, nueva_c], ignore_index=True))
                st.success("Condición guardada.")

    elif menu == "🧠 Reporte Comportamiento":
        st.title("🧠 Registro de Comportamiento")
        with st.form("f_comp"):
            f_obs = st.text_area("Observación")
            if st.form_submit_button("🚀 REGISTRAR"):
                nueva_comp = pd.DataFrame([{"Nit": str(nit_user), "ID_Inspección": str(uuid.uuid4())[:8], "Fecha/Hora Real": str(datetime.now()), "Inspector": "Auditor", "Tipo de Inspección": "Conducta", "Estado observado": "✅ SEGURO", "Evidencia Fotográfica": "N/A", "Observaciones Factor Humano": f_obs}])
                conn.update(spreadsheet=TITULO_COMP, data=pd.concat([df_comp_total, nueva_comp], ignore_index=True))
                st.success("Comportamiento registrado.")
