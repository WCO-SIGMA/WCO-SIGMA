import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.express as px
from datetime import datetime
import uuid

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="WCO-SIGMA SIG+ACPM", layout="wide")

# --- CONFIGURACIÓN DE IDENTIFICADORES (URLs INDEPENDIENTES) ---
URL_COND = "https://docs.google.com/spreadsheets/d/18OIJe409rr6o_o4HSweiuncIoOrgJOXEt0GFCmEsL4g/edit"
URL_COMP = "https://docs.google.com/spreadsheets/d/1szrDZsA59e5sMF6OAzPeQ_nDX7E9lMehaXCPHmVNx5o/edit"
URL_ACPM = "TU_URL_DE_BD_ACPM_AQUI" # <--- REEMPLAZA CON LA URL DE TU BD ACPM

conn = st.connection("gsheets", type=GSheetsConnection)

# 2. ACCESO MULTIEMPRESA
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/1063/1063302.png", width=100)
nit_user = st.sidebar.text_input("Ingrese identificación (NIT/Cédula):", "").strip()

if not nit_user:
    st.title("🚀 WCO-SIGMA: Gestión Integral SIG+ACPM")
    st.success("✅ Conexión con Bases de Datos SST y PESV Establecida.")
    st.info("Por favor, ingrese el NIT para activar el tablero de control y reportes.")
else:
    # --- MOTOR DE LECTURA ROBUSTO ---
    def cargar_datos(url):
        try:
            df = conn.read(spreadsheet=url, ttl=0)
            if df is not None and not df.empty:
                df.columns = df.columns.str.strip()
                # Limpieza de NIT para evitar errores de formato decimal
                df['Nit'] = df['Nit'].astype(str).apply(lambda x: x.split('.')[0].strip())
                return df, df[df['Nit'] == nit_user]
            return pd.DataFrame(), pd.DataFrame()
        except: return pd.DataFrame(), pd.DataFrame()

    df_cond_total, df_cond_emp = cargar_datos(URL_COND)
    df_comp_total, df_comp_emp = cargar_datos(URL_COMP)
    df_acpm_total, df_acpm_emp = cargar_datos(URL_ACPM)

    menu = st.sidebar.radio("Navegación SIG", ["📊 Dashboard & Análisis", "⚖️ Gestión de ACPM", "🛠️ Reporte Condiciones", "🧠 Reporte Comportamiento"])

    # --- PANTALLA 1: DASHBOARD & ANÁLISIS ---
    if menu == "📊 Dashboard & Análisis":
        st.title(f"📊 Tablero de Control Gerencial - NIT: {nit_user}")
        tab1, tab2, tab3 = st.tabs(["🔍 Condiciones HSEQ", "🧠 Comportamiento/PESV", "⚖️ Mejora (ACPM)"])
        
        with tab1:
            if not df_cond_emp.empty:
                c1, c2 = st.columns(2)
                with c1: st.plotly_chart(px.pie(df_cond_emp, names='Estado', title="Estatus de Hallazgos", hole=0.4), use_container_width=True)
                with c2: st.plotly_chart(px.bar(df_cond_emp, x='Condición Crítica', color='Prioridad', title="Prioridad por Categoría"), use_container_width=True)
                st.subheader("📝 Análisis Técnico (Condiciones)")
                st.text_area("Diagnóstico Situacional:", key="an_c_vfinal")
                st.dataframe(df_cond_emp, use_container_width=True)
            else: st.warning("Sin datos en Condiciones.")

        with tab2:
            if not df_comp_emp.empty:
                g1, g2 = st.columns(2)
                with g1: st.plotly_chart(px.bar(df_comp_emp, x='Estado observado', color='Estado observado', title="Cultura de Seguridad"), use_container_width=True)
                with g2: st.plotly_chart(px.pie(df_comp_emp, names='Tipo de Inspección', title="Módulos PESV/SST"), use_container_width=True)
                st.subheader("🧠 Análisis Conductual")
                st.text_area("Diagnóstico de Factor Humano:", key="an_h_vfinal")
                st.dataframe(df_comp_emp, use_container_width=True)
            else: st.warning("Sin datos en Comportamiento.")

        with tab3:
            if not df_acpm_emp.empty:
                ca1, ca2 = st.columns(2)
                with ca1: st.plotly_chart(px.pie(df_acpm_emp, names='Componente', title="ACPM por Sistema SIG", hole=0.4), use_container_width=True)
                with ca2: st.plotly_chart(px.bar(df_acpm_emp, x='Estado', color='Fuente', title="Avance de Planes de Acción"), use_container_width=True)
                st.subheader("⚖️ Evaluación de la Mejora Continua")
                st.text_area("Análisis de Eficacia ACPM:", key="an_m_vfinal")
                st.dataframe(df_acpm_emp, use_container_width=True)
            else: st.warning("No hay registros en el módulo ACPM.")

    # --- PANTALLA 2: GESTIÓN DE ACPM (RESTAURADA COMPLETA) ---
    elif menu == "⚖️ Gestión de ACPM":
        st.title("⚖️ Registro Técnico de ACPM (5 Porqués)")
        with st.form("form_acpm_phva"):
            col1, col2 = st.columns(2)
            with col1:
                f_emp = st.text_input("Empresa/Sede")
                f_comp = st.selectbox("Componente", ["SST", "Ambiente", "Calidad", "Vial"])
                f_fuen = st.selectbox("Fuente", ["inspecciones", "auditorías", "incidentes", "revisión gerencial"])
                f_desc = st.text_area("Descripción Hallazgo")
                st.subheader("🧠 Análisis Causa Raíz")
                p1, p2, p3, p4, p5 = st.text_input("P1"), st.text_input("P2"), st.text_input("P3"), st.text_input("P4"), st.text_input("P5")
            with col2:
                f_raiz = st.text_input("Causa Raíz Final")
                f_acci = st.text_area("Plan de Acción (Tareas)")
                f_tipo = st.radio("Tipo Acción", ["Correctiva", "Preventiva", "Mejora"])
                f_resp = st.text_input("Responsable del Cierre")
                f_fec_c = st.date_input("Fecha Cierre Prevista")
                f_camb = st.radio("¿Activa Gestión del Cambio? (IPVR/IAVI)", ["No", "Sí"])
                f_esta = st.selectbox("Estado Actual", ["Abierta", "En Ejecución", "Cerrada"])

            if st.form_submit_button("💾 REGISTRAR ACPM"):
                nueva_a = pd.DataFrame([{
                    "Nit": str(nit_user), "Empresa": f_emp, "Fecha de reporte": str(datetime.now().date()),
                    "Componente": f_comp, "Fuente": f_fuen, "Descripción Hallazgo": f_desc,
                    "Análisis Causa ¿Porqué 1?": p1, "Análisis Causa ¿Porqué 2?": p2, "Análisis Causa ¿Porqué 3?": p3, 
                    "Análisis Causa ¿Porqué 4?": p4, "Análisis Causa ¿Porqué 5?": p5, "Causa raíz": f_raiz,
                    "Acción Propuesta": f_acci, "Tipo Acción": f_tipo, "Responsable": f_resp,
                    "Fecha Cierre Prevista": str(f_fec_c), "Eficacia de la acción tomada": "Pendiente",
                    "La acción tomada activa gestión del cambio (Si es afirmativo IPVR, IAVI y sus controles)": f_camb, "Estado": f_esta
                }])
                conn.update(spreadsheet=URL_ACPM, data=pd.concat([df_acpm_total, nueva_a], ignore_index=True))
                st.success("✅ ACPM Registrada.")
                st.balloons()

    # --- PANTALLA 3: REPORTE CONDICIONES (ESTRUCTURA EXACTA) ---
    elif menu == "🛠️ Reporte Condiciones":
        st.title("🛠️ Registro de Condiciones HSEQ")
        with st.form("form_cond_final"):
            c1, c2 = st.columns(2)
            with c1:
                f_emp_c = st.text_input("Empresa")
                f_hall_c = st.text_area("Descripción del Hallazgo")
                f_cond_c = st.selectbox("Condición Crítica", ["Orden y aseo", "Herramientas/Equipos", "Daño locativo", "Sistemas eléctricos", "Vial", "Otros"])
                f_ries_c = st.selectbox("Riesgo (GTC 45)", ["Físico", "Químico", "Biológico", "Psicosocial", "Biomecánico", "Seguridad", "Natural"])
            with c2:
                f_comp_c = st.selectbox("Componente", ["SST", "Ambiente", "Calidad", "Vial"])
                f_resp_c = st.text_input("Responsable del cierre")
                f_fec_p_c = st.date_input("Fecha propuesta para el cierre")
                f_prio_c = st.selectbox("Prioridad", ["Baja", "Media", "Alta"])
                f_est_c = st.selectbox("Estado", ["Abierto", "En Proceso", "Cerrado"])
                f_obs_c = st.text_area("Observación")
            
            if st.form_submit_button("✅ GUARDAR INSPECCIÓN"):
                nueva_c = pd.DataFrame([{
                    "Nit": str(nit_user), "Empresa": f_emp_c, "Fecha": str(datetime.now().date()), 
                    "Hallazgo": f_hall_c, "Condición Crítica": f_cond_c, "Clasificación del riesgo": f_ries_c, 
                    "Componente": f_comp_c, "Responsable del cierre": f_resp_c, 
                    "Fecha propuesta para el cierre": str(f_fec_p_c), "Prioridad": f_prio_c, 
                    "Estado": f_est_c, "Observación": f_obs_c
                }])
                conn.update(spreadsheet=URL_COND, data=pd.concat([df_cond_total, nueva_c], ignore_index=True))
                st.success("Inspección de condición guardada.")

    # --- PANTALLA 4: REPORTE COMPORTAMIENTO (ESTRUCTURA EXACTA) ---
    elif menu == "🧠 Reporte Comportamiento":
        st.title("🧠 Observación de Comportamiento y PESV")
        with st.form("form_comp_final"):
            col_h1, col_h2 = st.columns(2)
            with col_h1:
                f_ins_h = st.text_input("Nombre del Inspector")
                f_tipo_h = st.selectbox("Tipo de Inspección", ["Conducta Humana", "Preoperacional Vehículo", "Tareas Críticas"])
                f_est_obs_h = st.selectbox("Estado observado", ["✅ SEGURO", "⚠️ ATÍPICO", "🚫 PELIGROSO"])
            with col_h2:
                f_foto_h = st.text_input("Link Evidencia Fotográfica")
                f_obs_fact_h = st.text_area("Observaciones Factor Humano")
            
            if st.form_submit_button("🚀 REGISTRAR COMPORTAMIENTO"):
                nueva_h = pd.DataFrame([{
                    "Nit": str(nit_user), "ID_Inspección": str(uuid.uuid4())[:8].upper(), 
                    "Fecha/Hora Real": str(datetime.now()), "Inspector": f_ins_h, 
                    "Tipo de Inspección": f_tipo_h, "Estado observado": f_est_obs_h, 
                    "Evidencia Fotográfica": f_foto_h, "Observaciones Factor Humano": f_obs_fact_h
                }])
                conn.update(spreadsheet=URL_COMP, data=pd.concat([df_comp_total, nueva_h], ignore_index=True))
                st.success("Reporte de comportamiento guardado.")
