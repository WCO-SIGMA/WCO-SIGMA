import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.express as px
from datetime import datetime
import uuid

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="WCO-SIGMA SIG+ACPM", layout="wide")

# --- IDENTIFICADORES DE ARCHIVO (NOMBRES EN GOOGLE DRIVE) ---
TITULO_COND = "BDI WCO SIGMA"
TITULO_COMP = "BDI COMPORTAMIENTO"
TITULO_ACPM = "BD ACPM" 

# --- URLs DE LECTURA ---
URL_COND = "https://docs.google.com/spreadsheets/d/18OIJe409rr6o_o4HSweiuncIoOrgJOXEt0GFCmEsL4g/edit"
URL_COMP = "https://docs.google.com/spreadsheets/d/1szrDZsA59e5sMF6OAzPeQ_nDX7E9lMehaXCPHmVNx5o/edit"
URL_ACPM = "PEGA_AQUÍ_TU_URL_DE_ACPM" # <--- IMPORTANTE: VERIFICA ESTA URL

conn = st.connection("gsheets", type=GSheetsConnection)

# 2. ACCESO POR NIT
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/1063/1063302.png", width=100)
nit_user = st.sidebar.text_input("Ingrese identificación (NIT/Cédula):", "").strip()

if not nit_user:
    st.title("🚀 WCO-SIGMA: Suite de Gestión PHVA")
    st.success("✅ Conexión con Google Sheets Establecida.")
    st.info("Ingrese su identificación para activar el panel de control.")
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

    menu = st.sidebar.radio("Navegación", ["📊 Dashboard & Análisis SIG", "⚖️ Gestión de ACPM", "🛠️ Reporte Condiciones", "🧠 Reporte Comportamiento"])

    # --- PANTALLA 1: DASHBOARD & ANÁLISIS (GRÁFICOS ACTIVOS) ---
    if menu == "📊 Dashboard & Análisis SIG":
        st.title(f"📊 Panel de Control SIG - NIT: {nit_user}")
        tab1, tab2, tab3 = st.tabs(["🔍 Inspecciones (Condiciones)", "🧠 Comportamiento", "⚖️ Mejora (ACPM)"])
        
        with tab1:
            if not df_cond_emp.empty:
                c1, c2 = st.columns(2)
                with c1: st.plotly_chart(px.pie(df_cond_emp, names='Estado', title="Estatus de Hallazgos", hole=0.4), use_container_width=True)
                with c2: st.plotly_chart(px.bar(df_cond_emp, x='Condición Crítica', color='Prioridad', title="Prioridad por Categoría"), use_container_width=True)
                st.subheader("📝 Análisis Técnico (Condiciones)")
                st.text_area("Diagnóstico Situacional:", key="txt_an_cond")
                st.dataframe(df_cond_emp, use_container_width=True)
            else: st.warning("Sin datos de condiciones.")

        with tab2:
            if not df_comp_emp.empty:
                g1, g2 = st.columns(2)
                with g1: st.plotly_chart(px.bar(df_comp_emp, x='Estado observado', color='Estado observado', title="Cultura de Seguridad"), use_container_width=True)
                with g2: st.plotly_chart(px.pie(df_comp_emp, names='Tipo de Inspección', title="Módulos Evaluados"), use_container_width=True)
                st.subheader("🧠 Análisis de Factor Humano")
                st.text_area("Diagnóstico Conductual:", key="txt_an_comp")
                st.dataframe(df_comp_emp, use_container_width=True)
            else: st.warning("Sin datos de comportamiento.")

        with tab3:
            st.subheader("⚖️ Indicadores de Gestión de Mejora (ACPM)")
            if not df_acpm_emp.empty:
                ca1, ca2 = st.columns(2)
                # Gráfico 1: Por Componente
                if 'Componente' in df_acpm_emp.columns:
                    with ca1: st.plotly_chart(px.pie(df_acpm_emp, names='Componente', title="ACPM por Sistema SIG", hole=0.4), use_container_width=True)
                # Gráfico 2: Por Estado y Fuente
                if 'Estado' in df_acpm_emp.columns:
                    with ca2: st.plotly_chart(px.bar(df_acpm_emp, x='Estado', color='Fuente', title="Estado de Implementación"), use_container_width=True)
                
                st.subheader("📝 Evaluación de Eficacia y Plan de Acción (ACPM)")
                col_an1, col_an2 = st.columns(2)
                with col_an1: st.text_area("Análisis de Resultados ACPM:", key="txt_an_acpm")
                with col_an2: st.text_area("Nuevos Compromisos SIG:", key="txt_pl_acpm")
                st.dataframe(df_acpm_emp, use_container_width=True)
            else:
                st.info("No hay datos de ACPM para graficar aún.")

    # --- PANTALLA 2: GESTIÓN DE ACPM (RECUPERADOS 5 PORQUÉS) ---
    elif menu == "⚖️ Gestión de ACPM":
        st.title("⚖️ Registro Técnico de ACPM (PHVA)")
        with st.form("form_acpm_v9"):
            col1, col2 = st.columns(2)
            with col1:
                f_emp = st.text_input("Empresa/Sede")
                f_comp = st.selectbox("Componente", ["SST", "Ambiente", "Calidad", "Vial"])
                f_fuen = st.selectbox("Fuente", ["inspecciones", "auditorías", "incidentes", "revisión gerencial", "otros"])
                f_desc = st.text_area("Descripción del Hallazgo")
                st.subheader("🧠 Análisis de Causa (5 Porqués)")
                p1 = st.text_input("¿Por qué 1?")
                p2 = st.text_input("¿Por qué 2?")
                p3 = st.text_input("¿Por qué 3?")
                p4 = st.text_input("¿Por qué 4?")
                p5 = st.text_input("¿Por qué 5?")
            with col2:
                f_raiz = st.text_input("Causa Raíz Final")
                f_acci = st.text_area("Plan de Acción (Tareas)")
                f_tipo = st.radio("Tipo de Acción", ["Correctiva", "Preventiva", "Mejora"])
                f_resp = st.text_input("Responsable")
                f_fec_c = st.date_input("Fecha Cierre Prevista")
                f_camb = st.radio("¿Activa Gestión del Cambio? (IPVR/IAVI)", ["No", "Sí"])
                f_esta = st.selectbox("Estado Inicial", ["Abierta", "En Ejecución"])

            if st.form_submit_button("💾 REGISTRAR ACPM"):
                nueva_acpm = pd.DataFrame([{
                    "Nit": str(nit_user), "Empresa": f_emp, "Fecha de reporte": str(datetime.now().date()),
                    "Componente": f_comp, "Fuente": f_fuen, "Descripción Hallazgo": f_desc,
                    "Análisis Causa ¿Porqué 1?": p1, "Análisis Causa ¿Porqué 2?": p2, 
                    "Análisis Causa ¿Porqué 3?": p3, "Análisis Causa ¿Porqué 4?": p4, 
                    "Análisis Causa ¿Porqué 5?": p5, "Causa raíz": f_raiz,
                    "Acción Propuesta": f_acci, "Tipo Acción": f_tipo, "Responsable": f_resp,
                    "Fecha Cierre Prevista": str(f_fec_c), "Eficacia de la acción tomada": "Pendiente",
                    "La acción tomada activa gestión del cambio (Si es afirmativo IPVR, IAVI y sus controles)": f_camb, 
                    "Estado": f_esta
                }])
                conn.update(spreadsheet=TITULO_ACPM, data=pd.concat([df_acpm_total, nueva_acpm], ignore_index=True))
                st.success("✅ ACPM Registrada exitosamente con análisis de causa.")

    # --- PANTALLA 3: REPORTE CONDICIONES (ESTRUCTURA BDI WCO SIGMA) ---
    elif menu == "🛠️ Reporte Condiciones":
        st.title("🛠️ Inspección de Condiciones HSEQ")
        with st.form("form_cond_v9"):
            c1, c2 = st.columns(2)
            with c1:
                f_emp_c = st.text_input("Empresa")
                f_hall_c = st.text_area("Hallazgo Detectado")
                f_cond_c = st.selectbox("Condición Crítica", ["Orden y aseo", "Equipos", "Locativo", "Eléctrico", "Vial", "Otros"])
                f_ries_c = st.selectbox("Clasificación del riesgo (GTC 45)", ["Físico", "Químico", "Biológico", "Psicosocial", "Biomecánico", "Seguridad", "Natural"])
            with c2:
                f_comp_c = st.selectbox("Componente", ["SST", "Ambiente", "Calidad", "Vial"])
                f_resp_c = st.text_input("Responsable del cierre")
                f_fec_p_c = st.date_input("Fecha cierre propuesta")
                f_prio_c = st.selectbox("Prioridad", ["Baja", "Media", "Alta"])
                f_est_c = st.selectbox("Estado", ["Abierto", "En Proceso", "Cerrado"])
                f_obs_c = st.text_area("Observaciones adicionales")
            
            if st.form_submit_button("✅ GUARDAR INSPECCIÓN"):
                nueva_c = pd.DataFrame([{
                    "Nit": str(nit_user), "Empresa": f_emp_c, "Fecha": str(datetime.now().date()), 
                    "Hallazgo": f_hall_c, "Condición Crítica": f_cond_c, "Clasificación del riesgo": f_ries_c, 
                    "Componente": f_comp_c, "Responsable del cierre": f_resp_c, 
                    "Fecha propuesta para el cierre": str(f_fec_p_c), "Prioridad": f_prio_c, 
                    "Estado": f_est_c, "Observación": f_obs_c
                }])
                conn.update(spreadsheet=TITULO_COND, data=pd.concat([df_cond_total, nueva_c], ignore_index=True))
                st.success("Inspección guardada en BDI WCO SIGMA.")

    # --- PANTALLA 4: REPORTE COMPORTAMIENTO (ESTRUCTURA BDI COMPORTAMIENTO) ---
    elif menu == "🧠 Reporte Comportamiento":
        st.title("🧠 Observación de Comportamiento")
        with st.form("form_comp_v9"):
            col_h1, col_h2 = st.columns(2)
            with col_h1:
                f_ins_h = st.text_input("Nombre Inspector")
                f_tipo_h = st.selectbox("Tipo de Inspección", ["Conducta Humana", "Preoperacional", "Tarea Crítica"])
                f_est_h = st.selectbox("Estado observado", ["✅ SEGURO", "⚠️ ATÍPICO", "🚫 PELIGROSO"])
            with col_h2:
                f_foto_h = st.text_input("URL Evidencia Fotográfica")
                f_obs_h = st.text_area("Observaciones Factor Humano")
            
            if st.form_submit_button("🚀 REGISTRAR COMPORTAMIENTO"):
                nueva_h = pd.DataFrame([{
                    "Nit": str(nit_user), "ID_Inspección": str(uuid.uuid4())[:8].upper(), 
                    "Fecha/Hora Real": str(datetime.now()), "Inspector": f_ins_h, 
                    "Tipo de Inspección": f_tipo_h, "Estado observado": f_est_h, 
                    "Evidencia Fotográfica": f_foto_h, "Observaciones Factor Humano": f_obs_h
                }])
                conn.update(spreadsheet=TITULO_COMP, data=pd.concat([df_comp_total, nueva_h], ignore_index=True))
                st.success("Comportamiento guardado en BDI COMPORTAMIENTO.")
