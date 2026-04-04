import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.express as px
from datetime import datetime
import uuid

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="WCO-SIGMA SIG+ACPM", layout="wide")

# --- CONFIGURACIÓN DE IDENTIFICADORES (NOMBRES DE ARCHIVO EN DRIVE) ---
TITULO_COND = "BDI WCO SIGMA"
TITULO_COMP = "BDI COMPORTAMIENTO"
TITULO_ACPM = "BD ACPM" 

# URLs PARA LECTURA (DASHBOARD)
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

    # --- PANTALLA 1: DASHBOARD & ANÁLISIS ---
    if menu == "📊 Dashboard & Análisis":
        st.title(f"📊 Panel Gerencial de Análisis - NIT: {nit_user}")
        tab1, tab2, tab3 = st.tabs(["🔍 Condiciones HSEQ", "🧠 Comportamiento/PESV", "⚖️ Mejora (ACPM)"])
        
        with tab1:
            if not df_cond_emp.empty:
                c1, c2 = st.columns(2)
                with c1: st.plotly_chart(px.pie(df_cond_emp, names='Estado', title="Estatus de Hallazgos", hole=0.4), use_container_width=True)
                with c2: st.plotly_chart(px.bar(df_cond_emp, x='Condición Crítica', color='Prioridad', title="Prioridad por Tipo de Condición"), use_container_width=True)
                st.subheader("📝 Análisis y Plan de Acción (Condiciones)")
                st.text_area("Análisis Técnico de Condiciones:", key="an_c_v")
                st.text_area("Propuesta de Medidas de Intervención:", key="pl_c_v")
                st.dataframe(df_cond_emp, use_container_width=True)
            else: st.warning("Sin datos en BDI WCO SIGMA.")

        with tab2:
            if not df_comp_emp.empty:
                g1, g2 = st.columns(2)
                with g1: st.plotly_chart(px.bar(df_comp_emp, x='Estado observado', color='Estado observado', title="Cultura de Seguridad"), use_container_width=True)
                with g2: st.plotly_chart(px.pie(df_comp_emp, names='Tipo de Inspección', title="Módulos de Observación"), use_container_width=True)
                st.subheader("🧠 Análisis de Factor Humano")
                st.text_area("Diagnóstico de Riesgo Conductual:", key="an_h_v")
                st.text_area("Plan de Refuerzo PESV/SST:", key="pl_h_v")
                st.dataframe(df_comp_emp, use_container_width=True)
            else: st.warning("Sin datos en BDI COMPORTAMIENTO.")

        with tab3:
            if not df_acpm_emp.empty:
                ga1, ga2 = st.columns(2)
                with ga1: st.plotly_chart(px.pie(df_acpm_emp, names='Componente', title="ACPM por SIG"), use_container_width=True)
                with ga2: st.plotly_chart(px.bar(df_acpm_emp, x='Estado', color='Tipo Acción', title="Avance Mejora Continua"), use_container_width=True)
                st.subheader("⚖️ Evaluación de Mejora")
                st.text_area("Análisis de Eficacia ACPM:", key="an_m_v")
                st.dataframe(df_acpm_emp, use_container_width=True)
            else: st.warning("Sin datos en BD ACPM.")

    # --- PANTALLA 2: GESTIÓN DE ACPM (RESTAURADA) ---
    elif menu == "⚖️ Gestión de ACPM":
        st.title("⚖️ Registro Técnico de ACPM")
        with st.form("form_acpm_final"):
            col1, col2 = st.columns(2)
            with col1:
                f_emp_a = st.text_input("Empresa")
                f_comp_a = st.selectbox("Componente", ["SST", "Ambiente", "Calidad", "Vial"])
                f_fuen_a = st.selectbox("Fuente", ["inspecciones", "investigación de incidentes", "auditorías internas y externas", "observación de tareas", "reportes de actos y condiciones", "Legislación o normatividad", "Revisión gerencial"])
                f_desc_a = st.text_area("Descripción Hallazgo")
                st.subheader("Análisis 5 Porqués")
                p1, p2, p3, p4, p5 = st.text_input("¿P1?"), st.text_input("¿P2?"), st.text_input("¿P3?"), st.text_input("¿P4?"), st.text_input("¿P5?")
            with col2:
                f_raiz_a = st.text_input("Causa Raíz Final")
                f_acci_a = st.text_area("Acción Propuesta")
                f_tipo_a = st.radio("Tipo Acción", ["Correctiva", "Preventiva", "Mejora"])
                f_resp_a = st.text_input("Responsable")
                f_fec_c_a = st.date_input("Fecha Cierre Prevista")
                f_camb_a = st.radio("¿Activa gestión del cambio? (IPVR/IAVI)", ["No", "Sí"])
                f_esta_a = st.selectbox("Estado", ["Abierta", "En Ejecución", "Cerrada"])

            if st.form_submit_button("💾 GUARDAR ACPM"):
                nueva_acpm = pd.DataFrame([{
                    "Nit": str(nit_user), "Empresa": f_emp_a, "Fecha de reporte": str(datetime.now().date()),
                    "Componente": f_comp_a, "Fuente": f_fuen_a, "Descripción Hallazgo": f_desc_a,
                    "Análisis Causa ¿Porqué 1?": p1, "Análisis Causa ¿Porqué 2?": p2, "Análisis Causa ¿Porqué 3?": p3, 
                    "Análisis Causa ¿Porqué 4?": p4, "Análisis Causa ¿Porqué 5?": p5, "Causa raíz": f_raiz_a,
                    "Acción Propuesta": f_acci_a, "Tipo Acción": f_tipo_a, "Responsable": f_resp_a,
                    "Fecha Cierre Prevista": str(f_fec_c_a), "Eficacia de la acción tomada": "Pendiente",
                    "La acción tomada activa gestión del cambio (Si es afirmativo IPVR, IAVI y sus controles)": f_camb_a, "Estado": f_esta_a
                }])
                conn.update(spreadsheet=TITULO_ACPM, data=pd.concat([df_acpm_total, nueva_acpm], ignore_index=True))
                st.success("✅ ACPM Guardada.")

    # --- PANTALLA 3: REPORTE CONDICIONES (ESTRUCTURA BDI WCO SIGMA) ---
    elif menu == "🛠️ Reporte Condiciones":
        st.title("🛠️ Inspección de Condiciones de Seguridad")
        with st.form("form_cond_v7"):
            c1, c2 = st.columns(2)
            with c1:
                f_emp_c = st.text_input("Empresa")
                f_hall_c = st.text_area("Hallazgo")
                f_cond_c = st.selectbox("Condición Crítica", ["Orden y aseo", "Herramientas/Equipos", "Daño locativo", "Sistemas eléctricos", "Vial", "Otros"])
                f_ries_c = st.selectbox("Clasificación del riesgo", ["Físico", "Químico", "Biológico", "Psicosocial", "Biomecánico", "Seguridad", "Natural"])
            with c2:
                f_comp_c = st.selectbox("Componente", ["SST", "Ambiente", "Calidad", "Vial"])
                f_resp_c = st.text_input("Responsable del cierre")
                f_fec_p_c = st.date_input("Fecha propuesta para el cierre")
                f_prio_c = st.selectbox("Prioridad", ["Baja", "Media", "Alta"])
                f_est_c = st.selectbox("Estado", ["Abierto", "En Proceso", "Cerrado"])
                f_obs_c = st.text_area("Observación")
            
            if st.form_submit_button("✅ GUARDAR EN BDI WCO SIGMA"):
                nueva_fila_c = pd.DataFrame([{
                    "Nit": str(nit_user), "Empresa": f_emp_c, "Fecha": str(datetime.now().date()), 
                    "Hallazgo": f_hall_c, "Condición Crítica": f_cond_c, "Clasificación del riesgo": f_ries_c, 
                    "Componente": f_comp_c, "Responsable del cierre": f_resp_c, 
                    "Fecha propuesta para el cierre": str(f_fec_p_c), "Prioridad": f_prio_c, 
                    "Estado": f_est_c, "Observación": f_obs_c
                }])
                conn.update(spreadsheet=TITULO_COND, data=pd.concat([df_cond_total, nueva_fila_c], ignore_index=True))
                st.success("Inspección de condición guardada.")

    # --- PANTALLA 4: REPORTE COMPORTAMIENTO (ESTRUCTURA BDI COMPORTAMIENTO) ---
    elif menu == "🧠 Reporte Comportamiento":
        st.title("🧠 Observación de Comportamiento y PESV")
        with st.form("form_comp_v7"):
            col_h1, col_h2 = st.columns(2)
            with col_h1:
                f_ins_h = st.text_input("Inspector")
                f_tipo_h = st.selectbox("Tipo de Inspección", ["Conducta Humana", "Preoperacional Vehículo", "Tareas Críticas"])
                f_est_obs_h = st.selectbox("Estado observado", ["✅ SEGURO", "⚠️ ATÍPICO", "🚫 PELIGROSO"])
            with col_h2:
                f_foto_h = st.text_input("Evidencia Fotográfica (Link)")
                f_obs_fact_h = st.text_area("Observaciones Factor Humano")
            
            if st.form_submit_button("🚀 REGISTRAR EN BDI COMPORTAMIENTO"):
                nueva_fila_h = pd.DataFrame([{
                    "Nit": str(nit_user), "ID_Inspección": str(uuid.uuid4())[:8].upper(), 
                    "Fecha/Hora Real": str(datetime.now()), "Inspector": f_ins_h, 
                    "Tipo de Inspección": f_tipo_h, "Estado observado": f_est_obs_h, 
                    "Evidencia Fotográfica": f_foto_h, "Observaciones Factor Humano": f_obs_fact_h
                }])
                conn.update(spreadsheet=TITULO_COMP, data=pd.concat([df_comp_total, nueva_fila_h], ignore_index=True))
                st.success("Reporte de comportamiento guardado.")
