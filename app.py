import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.express as px
from datetime import datetime
import uuid

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="WCO-SIGMA SIG+ACPM", layout="wide")

# --- IDs Y URLs DE TUS ARCHIVOS (CONFIGURACIÓN CRÍTICA) ---
# Extrae el ID de tu URL: https://docs.google.com/spreadsheets/d/ESTE_ES_EL_ID/edit
URL_COND = "https://docs.google.com/spreadsheets/d/18OIJe409rr6o_o4HSweiuncIoOrgJOXEt0GFCmEsL4g/edit"
URL_COMP = "https://docs.google.com/spreadsheets/d/1szrDZsA59e5sMF6OAzPeQ_nDX7E9lMehaXCPHmVNx5o/edit"

# ⚠️ PEGA AQUÍ SOLO EL ID DE TU NUEVA HOJA "BD ACPM"
ID_ACPM = "1szrDZsA59e5sMF6OAzPeQ_nDX7E9lMehaXCPHmVNx5o" # Reemplaza con el ID real de tu ACPM

conn = st.connection("gsheets", type=GSheetsConnection)

# 2. ACCESO POR NIT
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/1063/1063302.png", width=100)
nit_input = st.sidebar.text_input("Ingrese NIT de la Empresa:", "").strip()

if not nit_input:
    st.title("🚀 WCO-SIGMA: Sistema de Gestión Integrado")
    st.success("✅ Motores BDI vinculados.")
    st.info("Ingrese su identificación para acceder a los módulos PHVA.")
else:
    # --- MOTOR DE LECTURA ---
    def cargar_datos(link_or_id):
        try:
            df = conn.read(spreadsheet=link_or_id, ttl=0)
            if df is not None and not df.empty:
                df.columns = df.columns.str.strip()
                df['Nit'] = df['Nit'].astype(str).str.replace('.0', '', regex=False).str.strip()
                return df, df[df['Nit'] == nit_input]
            return pd.DataFrame(), pd.DataFrame()
        except:
            return pd.DataFrame(), pd.DataFrame()

    df_cond_total, df_cond_emp = cargar_datos(URL_COND)
    df_comp_total, df_comp_emp = cargar_datos(URL_COMP)
    df_acpm_total, df_acpm_emp = cargar_datos(ID_ACPM)

    menu = st.sidebar.radio("Navegación", ["📊 Dashboard Gerencial", "⚖️ Gestión de ACPM", "🛠️ Reporte Condiciones", "🧠 Reporte Comportamiento"])

    # --- PANTALLA 1: DASHBOARD ---
    if menu == "📊 Dashboard Gerencial":
        st.title(f"📊 Tablero de Control - NIT: {nit_input}")
        tab1, tab2, tab3 = st.tabs(["🔍 Condiciones", "🧠 Comportamiento", "⚖️ ACPM"])
        
        with tab1:
            if not df_cond_emp.empty:
                st.plotly_chart(px.pie(df_cond_emp, names='Estado', title="Estatus de Hallazgos"), use_container_width=True)
                st.dataframe(df_cond_emp, use_container_width=True)
            else: st.warning("Sin datos en Condiciones.")
        
        with tab2:
            if not df_comp_emp.empty:
                st.plotly_chart(px.bar(df_comp_emp, x='Estado observado', color='Estado observado', title="Análisis Conductual"), use_container_width=True)
                st.dataframe(df_comp_emp, use_container_width=True)
            else: st.warning("Sin datos en Comportamiento.")
            
        with tab3:
            if not df_acpm_emp.empty:
                st.plotly_chart(px.pie(df_acpm_emp, names='Componente', title="ACPM por SIG"), use_container_width=True)
                st.dataframe(df_acpm_emp, use_container_width=True)
            else: st.warning("Sin datos de ACPM registrados.")

    # --- PANTALLA 2: GESTIÓN DE ACPM (RESTAURADA) ---
    elif menu == "⚖️ Gestión de ACPM":
        st.title("⚖️ Módulo de Mejora Continua (ACPM)")
        with st.form("form_acpm_final"):
            c1, c2 = st.columns(2)
            with c1:
                f_emp = st.text_input("Empresa")
                f_comp = st.selectbox("Componente", ["SST", "Ambiente", "Calidad", "Vial"])
                f_fuente = st.selectbox("Fuente", ["inspecciones", "investigación de incidentes", "auditorías internas y externas", "observación de tareas", "reportes de actos y condiciones", "Legislación o normatividad", "Revisión gerencial"])
                f_desc = st.text_area("Descripción Hallazgo")
                st.subheader("Análisis 5 Porqués")
                p1, p2, p3, p4, p5 = st.text_input("¿P1?"), st.text_input("¿P2?"), st.text_input("¿P3?"), st.text_input("¿P4?"), st.text_input("¿P5?")
                f_raiz = st.text_input("Causa Raíz")
            with c2:
                f_accion = st.text_area("Acción Propuesta")
                f_tipo = st.radio("Tipo Acción", ["Correctiva", "Preventiva", "Mejora"])
                f_resp = st.text_input("Responsable")
                f_fec_c = st.date_input("Fecha Cierre Prevista")
                f_eficacia = st.selectbox("Eficacia", ["Pendiente", "Eficaz", "No Eficaz"])
                f_cambio = st.radio("¿Activa gestión del cambio?", ["No", "Sí"])
                f_estado = st.selectbox("Estado", ["Abierta", "En Ejecución", "Cerrada"])

            if st.form_submit_button("💾 GUARDAR ACPM"):
                nueva_acpm = pd.DataFrame([{
                    "Nit": str(nit_input), "Empresa": f_emp, "Fecha de reporte": str(datetime.now().date()),
                    "Componente": f_comp, "Fuente": f_fuente, "Descripción Hallazgo": f_desc,
                    "Análisis Causa ¿Porqué 1?": p1, "Análisis Causa ¿Porqué 2?": p2,
                    "Análisis Causa ¿Porqué 3?": p3, "Análisis Causa ¿Porqué 4?": p4,
                    "Análisis Causa ¿Porqué 5?": p5, "Causa raíz": f_raiz,
                    "Acción Propuesta": f_accion, "Tipo Acción": f_tipo, "Responsable": f_resp,
                    "Fecha Cierre Prevista": str(f_fec_c), "Eficacia de la acción tomada": f_eficacia,
                    "La acción tomada activa gestión del cambio (Si es afirmativo IPVR, IAVI y sus controles)": f_cambio, 
                    "Estado": f_estado
                }])
                # USAMOS EL ID DIRECTAMENTE PARA EVITAR SpreadsheetNotFound
                df_upd = pd.concat([df_acpm_total, nueva_acpm], ignore_index=True)
                conn.update(spreadsheet=ID_ACPM, data=df_upd)
                st.success("ACPM centralizada con éxito.")
                st.balloons()

    # --- PANTALLA 3: REPORTES (RESTAURADOS) ---
    elif menu == "🛠️ Reporte Condiciones":
        st.title("🛠️ Registro de Condiciones HSEQ")
        with st.form("form_cond_vfull"):
            col1, col2 = st.columns(2)
            with col1:
                f_emp_c = st.text_input("Empresa")
                f_hall_c = st.text_area("Hallazgo")
                f_cond_c = st.selectbox("Categoría", ["Orden y aseo", "Herramientas", "Locativo", "Eléctrico", "Vial", "Otros"])
            with col2:
                f_riesgo_c = st.selectbox("GTC 45", ["Físico", "Químico", "Biológico", "Psicosocial", "Biomecánico", "Seguridad", "Natural"])
                f_prio_c = st.selectbox("Prioridad", ["Baja", "Media", "Alta"])
                f_est_c = st.selectbox("Estado", ["Abierto", "En Proceso", "Cerrado"])
            
            if st.form_submit_button("✅ GUARDAR CONDICIÓN"):
                nueva_cond = pd.DataFrame([{
                    "Nit": str(nit_input), "Empresa": f_emp_c, "Fecha": str(datetime.now().date()), 
                    "Hallazgo": f_hall_c, "Condición Crítica": f_cond_c, "Clasificación del riesgo": f_riesgo_c, 
                    "Componente": "SST", "Responsable del cierre": "Auditor", 
                    "Fecha propuesta para el cierre": str(datetime.now().date()), 
                    "Prioridad": f_prio_c, "Estado": f_est_c, "Observación": "Registro inicial"
                }])
                conn.update(spreadsheet=URL_COND, data=pd.concat([df_cond_total, nueva_cond], ignore_index=True))
                st.success("Condición guardada.")

    elif menu == "🧠 Reporte Comportamiento":
        st.title("🧠 Registro de Comportamiento y PESV")
        with st.form("form_comp_vfull"):
            c1, c2 = st.columns(2)
            with c1:
                f_ins_h = st.text_input("Inspector")
                f_tipo_h = st.selectbox("Tipo", ["Conducta Humana", "PESV", "Tareas Críticas"])
                f_est_h = st.selectbox("Estado Observado", ["✅ SEGURO", "⚠️ ATÍPICO", "🚫 PELIGROSO"])
            with c2:
                f_humano_h = st.multiselect("Factores", ["Distracción", "Fatiga", "Exceso de confianza", "Prisa"])
                f_detalles_h = st.text_area("Descripción")
            
            if st.form_submit_button("🚀 REGISTRAR COMPORTAMIENTO"):
                nueva_comp = pd.DataFrame([{
                    "Nit": str(nit_input), "ID_Inspección": str(uuid.uuid4())[:8].upper(), 
                    "Fecha/Hora Real": str(datetime.now()), "Inspector": f_ins_h, 
                    "Tipo de Inspección": f_tipo_h, "Estado observado": f_est_h, 
                    "Evidencia Fotográfica": "N/A", "Observaciones Factor Humano": ", ".join(f_humano_h) + " | " + f_detalles_h
                }])
                conn.update(spreadsheet=URL_COMP, data=pd.concat([df_comp_total, nueva_comp], ignore_index=True))
                st.success("Comportamiento registrado.")
