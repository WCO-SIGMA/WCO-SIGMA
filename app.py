import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.express as px
from datetime import datetime
import uuid

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="WCO-SIGMA SIG+ACPM", layout="wide")

# --- CONFIGURACIÓN DE CONEXIONES (NOMBRES PARA GUARDAR / URLs PARA LEER) ---
TITULO_COND = "BDI WCO SIGMA"
TITULO_COMP = "BDI COMPORTAMIENTO"
TITULO_ACPM = "BD ACPM" 

URL_COND = "https://docs.google.com/spreadsheets/d/18OIJe409rr6o_o4HSweiuncIoOrgJOXEt0GFCmEsL4g/edit"
URL_COMP = "https://docs.google.com/spreadsheets/d/1szrDZsA59e5sMF6OAzPeQ_nDX7E9lMehaXCPHmVNx5o/edit"
URL_ACPM = "TU_URL_DE_BD_ACPM_AQUI" # <--- REEMPLAZA ESTA URL

conn = st.connection("gsheets", type=GSheetsConnection)

# 2. ACCESO POR NIT
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/1063/1063302.png", width=100)
nit_user = st.sidebar.text_input("Ingrese identificación (NIT/Cédula):", "").strip()

if not nit_user:
    st.title("🚀 WCO-SIGMA: Sistema de Gestión PHVA")
    st.info("Ingrese su NIT para desplegar los tableros de análisis y módulos de reporte.")
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

    menu = st.sidebar.radio("Navegación", ["📊 Dashboard SIG & Análisis", "⚖️ Gestión de ACPM", "🛠️ Reporte Condiciones", "🧠 Reporte Comportamiento"])

    # --- PANTALLA 1: DASHBOARD SIG CON ESPACIOS DE ANÁLISIS ---
    if menu == "📊 Dashboard SIG & Análisis":
        st.title(f"📊 Panel Gerencial de Análisis - NIT: {nit_user}")
        tab1, tab2, tab3 = st.tabs(["🔍 Análisis de Condiciones", "🧠 Análisis de Comportamiento", "⚖️ Análisis de ACPM"])
        
        with tab1:
            if not df_cond_emp.empty:
                c1, c2 = st.columns(2)
                with c1: st.plotly_chart(px.pie(df_cond_emp, names='Estado', title="Estatus de Hallazgos", hole=0.4), use_container_width=True)
                with c2: st.plotly_chart(px.bar(df_cond_emp, x='Condición Crítica', color='Prioridad', title="Prioridad por Categoría"), use_container_width=True)
                
                st.subheader("📝 Diagnóstico y Plan de Acción (Condiciones)")
                col_c1, col_c2 = st.columns(2)
                with col_c1: st.text_area("Análisis Situacional - Condiciones:", key="an_cond", placeholder="Análisis de tendencias encontradas...")
                with col_c2: st.text_area("Medidas de Intervención Propuestas:", key="pl_cond", placeholder="Acciones inmediatas para mitigar riesgos...")
                st.dataframe(df_cond_emp, use_container_width=True)
            else: st.warning("Sin datos de condiciones.")

        with tab2:
            if not df_comp_emp.empty:
                g1, g2 = st.columns(2)
                with g1: st.plotly_chart(px.bar(df_comp_emp, x='Estado observado', color='Estado observado', title="Cultura de Seguridad"), use_container_width=True)
                with g2: st.plotly_chart(px.pie(df_comp_emp, names='Tipo de Inspección', title="Tipos de Auditoría Realizadas"), use_container_width=True)
                
                st.subheader("🧠 Análisis de Factor Humano & PESV")
                col_h1, col_h2 = st.columns(2)
                with col_h1: st.text_area("Análisis de Riesgo Conductual:", key="an_comp", placeholder="Análisis de actos inseguros y fatiga...")
                with col_h2: st.text_area("Plan de Refuerzo y Cultura:", key="pl_comp", placeholder="Estrategias pedagógicas y de control...")
                st.dataframe(df_comp_emp, use_container_width=True)
            else: st.warning("Sin datos de comportamiento.")

        with tab3:
            if not df_acpm_emp.empty:
                ga1, ga2 = st.columns(2)
                with ga1: st.plotly_chart(px.pie(df_acpm_emp, names='Componente', title="ACPM por Sistema SIG"), use_container_width=True)
                with ga2: st.plotly_chart(px.bar(df_acpm_emp, x='Estado', color='Fuente', title="Avance de la Mejora Continua"), use_container_width=True)
                
                st.subheader("⚖️ Análisis de Eficacia ACPM")
                col_m1, col_m2 = st.columns(2)
                with col_m1: st.text_area("Análisis de Causa Raíz Sistémico:", key="an_acpm", placeholder="Evaluación consolidada de fallas del sistema...")
                with col_m2: st.text_area("Plan de Seguimiento Gerencial:", key="pl_acpm", placeholder="Determinación de eficacia y mejora continua...")
                st.dataframe(df_acpm_emp, use_container_width=True)
            else: st.warning("Sin registros en el módulo ACPM.")

    # --- PANTALLA 2: GESTIÓN DE ACPM (RESTAURADA CON TODAS LAS VARIABLES) ---
    elif menu == "⚖️ Gestión de ACPM":
        st.title("⚖️ Reporte de Acciones Correctivas (ACPM)")
        with st.form("form_acpm_full"):
            col1, col2 = st.columns(2)
            with col1:
                f_emp = st.text_input("Empresa/Unidad")
                f_comp = st.selectbox("Componente", ["SST", "Ambiente", "Calidad", "Vial"])
                f_fuen = st.selectbox("Fuente", ["inspecciones", "investigación de incidentes", "auditorías internas y externas", "observación de tareas", "reportes de actos y condiciones", "Legislación o normatividad", "Revisión gerencial"])
                f_desc = st.text_area("Descripción Hallazgo")
                st.subheader("Análisis 5 Porqués")
                p1, p2, p3, p4, p5 = st.text_input("¿P1?"), st.text_input("¿P2?"), st.text_input("¿P3?"), st.text_input("¿P4?"), st.text_input("¿P5?")
            with col2:
                f_raiz = st.text_input("Causa Raíz Final")
                f_acci = st.text_area("Acción Propuesta")
                f_tipo = st.radio("Tipo Acción", ["Correctiva", "Preventiva", "Mejora"])
                f_resp = st.text_input("Responsable")
                f_fec_c = st.date_input("Fecha Cierre Prevista")
                f_cambio = st.radio("¿Activa gestión del cambio? (IPVR/IAVI)", ["No", "Sí"])
                f_estado = st.selectbox("Estado", ["Abierta", "En Ejecución", "Cerrada"])

            if st.form_submit_button("💾 CENTRALIZAR ACPM"):
                nueva_acpm = pd.DataFrame([{
                    "Nit": str(nit_user), "Empresa": f_emp, "Fecha de reporte": str(datetime.now().date()),
                    "Componente": f_comp, "Fuente": f_fuen, "Descripción Hallazgo": f_desc,
                    "Análisis Causa ¿Porqué 1?": p1, "Análisis Causa ¿Porqué 2?": p2, "Análisis Causa ¿Porqué 3?": p3, 
                    "Análisis Causa ¿Porqué 4?": p4, "Análisis Causa ¿Porqué 5?": p5, "Causa raíz": f_raiz,
                    "Acción Propuesta": f_acci, "Tipo Acción": f_tipo, "Responsable": f_resp,
                    "Fecha Cierre Prevista": str(f_fec_c), "Eficacia de la acción tomada": "Pendiente",
                    "La acción tomada activa gestión del cambio (Si es afirmativo IPVR, IAVI y sus controles)": f_cambio, 
                    "Estado": f_estado
                }])
                df_upd = pd.concat([df_acpm_total, nueva_acpm], ignore_index=True)
                conn.update(spreadsheet=TITULO_ACPM, data=df_upd)
                st.success("✅ ACPM Guardada.")
                st.balloons()

    # --- PANTALLA 3: REPORTE CONDICIONES (RESTAURADA CON TODAS LAS VARIABLES) ---
    elif menu == "🛠️ Reporte Condiciones":
        st.title("🛠️ Inspección de Condiciones HSEQ")
        with st.form("form_cond_vfull"):
            c1, c2 = st.columns(2)
            with c1:
                f_emp_c = st.text_input("Empresa")
                f_hall_c = st.text_area("Descripción del Hallazgo")
                f_cat_c = st.selectbox("Categoría Crítica", ["Orden y aseo", "Herramientas/Equipos", "Daño locativo", "Sistemas eléctricos", "Vial", "Otros"])
            with c2:
                f_gtc = st.selectbox("Riesgo (GTC 45)", ["Físico", "Químico", "Biológico", "Psicosocial", "Biomecánico", "Seguridad", "Natural"])
                f_prio = st.selectbox("Prioridad", ["Baja", "Media", "Alta"])
                f_est_c = st.selectbox("Estado Actual", ["Abierto", "En Proceso", "Cerrado"])
            
            if st.form_submit_button("✅ GUARDAR CONDICIÓN"):
                nueva_cond = pd.DataFrame([{
                    "Nit": str(nit_user), "Empresa": f_emp_c, "Fecha": str(datetime.now().date()), 
                    "Hallazgo": f_hall_c, "Condición Crítica": f_cat_c, "Clasificación del riesgo": f_gtc, 
                    "Componente": "SST", "Responsable del cierre": "Auditor", 
                    "Fecha propuesta para el cierre": str(datetime.now().date()), 
                    "Prioridad": f_prio, "Estado": f_est_c, "Observación": "Registro vía App"
                }])
                conn.update(spreadsheet=TITULO_COND, data=pd.concat([df_cond_total, nueva_cond], ignore_index=True))
                st.success("Guardado en BDI Condiciones.")

    # --- PANTALLA 4: REPORTE COMPORTAMIENTO (RESTAURADA CON TODAS LAS VARIABLES) ---
    elif menu == "🧠 Reporte Comportamiento":
        st.title("🧠 Observación de Comportamiento y PESV")
        with st.form("form_comp_vfull"):
            col1, col2 = st.columns(2)
            with col1:
                f_ins = st.text_input("Nombre del Inspector")
                f_tipo = st.selectbox("Módulo", ["Conducta Humana", "Preoperacional PESV", "Tareas Críticas"])
                f_res = st.selectbox("Calificación", ["✅ SEGURO", "⚠️ ATÍPICO", "🚫 PELIGROSO"])
            with col2:
                f_fac = st.multiselect("Factores Humanos", ["Distracción", "Fatiga", "Exceso de confianza", "Prisa"])
                f_det = st.text_area("Detalles de la conducta")
            
            if st.form_submit_button("🚀 REGISTRAR COMPORTAMIENTO"):
                nueva_comp = pd.DataFrame([{
                    "Nit": str(nit_user), "ID_Inspección": str(uuid.uuid4())[:8].upper(), 
                    "Fecha/Hora Real": str(datetime.now()), "Inspector": f_ins, 
                    "Tipo de Inspección": f_tipo, "Estado observado": f_res, 
                    "Evidencia Fotográfica": "N/A", "Observaciones Factor Humano": ", ".join(f_fac) + " | " + f_det
                }])
                conn.update(spreadsheet=TITULO_COMP, data=pd.concat([df_comp_total, nueva_comp], ignore_index=True))
                st.success("Guardado en BDI Comportamiento.")
