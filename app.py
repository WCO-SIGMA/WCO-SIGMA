import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.express as px
from datetime import datetime
import uuid

# 1. CONFIGURACIÓN
st.set_page_config(page_title="WCO-SIGMA SIG+ACPM", layout="wide")

# --- CONFIGURACIÓN DE NOMBRES (DEBEN SER IDÉNTICOS A LOS DE TU DRIVE) ---
NOMBRE_COND = "BDI WCO SIGMA"
NOMBRE_COMP = "BDI COMPORTAMIENTO"
NOMBRE_ACPM = "BD ACPM" # <--- Aquí queda tu nombre corto

# URLs para lectura (Las que ya funcionan)
URL_COND = "https://docs.google.com/spreadsheets/d/18OIJe409rr6o_o4HSweiuncIoOrgJOXEt0GFCmEsL4g/edit"
URL_COMP = "https://docs.google.com/spreadsheets/d/1szrDZsA59e5sMF6OAzPeQ_nDX7E9lMehaXCPHmVNx5o/edit"
# ⚠️ PEGA AQUÍ LA URL DE TU BD ACPM PARA LA LECTURA
URL_ACPM = "TU_URL_DE_BD_ACPM_AQUI" 

conn = st.connection("gsheets", type=GSheetsConnection)

# 2. ACCESO POR NIT
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/1063/1063302.png", width=100)
nit_input = st.sidebar.text_input("Ingrese NIT de la Empresa:", "").strip()

if not nit_input:
    st.title("🚀 WCO-SIGMA: Sistema de Gestión Integrado")
    st.info("Ingrese su identificación para acceder a los tableros y reportes.")
else:
    # --- MOTOR DE LECTURA ---
    def cargar_datos(link):
        try:
            df = conn.read(spreadsheet=link, ttl=0)
            if df is not None and not df.empty:
                df.columns = df.columns.str.strip()
                df['Nit'] = df['Nit'].astype(str).str.replace('.0', '', regex=False).str.strip()
                return df, df[df['Nit'] == nit_input]
            return pd.DataFrame(), pd.DataFrame()
        except: return pd.DataFrame(), pd.DataFrame()

    df_cond_total, df_cond_emp = cargar_datos(URL_COND)
    df_comp_total, df_comp_emp = cargar_datos(URL_COMP)
    df_acpm_total, df_acpm_emp = cargar_datos(URL_ACPM)

    menu = st.sidebar.radio("Navegación", ["📊 Dashboard Gerencial", "⚖️ Gestión de ACPM", "🛠️ Reporte Condiciones", "🧠 Reporte Comportamiento"])

    # --- PANTALLA: DASHBOARD ---
    if menu == "📊 Dashboard Gerencial":
        st.title(f"📊 Tablero Ejecutivo - NIT: {nit_input}")
        t1, t2, t3 = st.tabs(["🔍 Condiciones", "🧠 Comportamiento", "⚖️ ACPM"])
        with t1:
            if not df_cond_emp.empty:
                st.plotly_chart(px.pie(df_cond_emp, names='Estado', title="Estatus Hallazgos"), use_container_width=True)
                st.dataframe(df_cond_emp, use_container_width=True)
        with t2:
            if not df_comp_emp.empty:
                st.plotly_chart(px.bar(df_comp_emp, x='Estado observado', color='Estado observado', title="Análisis de Conducta"), use_container_width=True)
                st.dataframe(df_comp_emp, use_container_width=True)
        with t3:
            if not df_acpm_emp.empty:
                st.plotly_chart(px.pie(df_acpm_emp, names='Componente', title="ACPM por Sistema SIG"), use_container_width=True)
                st.dataframe(df_acpm_emp, use_container_width=True)

    # --- PANTALLA: GESTIÓN DE ACPM (RESTAURADA) ---
    elif menu == "⚖️ Gestión de ACPM":
        st.title("⚖️ Módulo de Mejora Continua (ACPM)")
        with st.form("form_acpm_tecnico"):
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
                f_cambio = st.radio("¿Gestión del cambio? (IPVR/IAVI)", ["No", "Sí"])
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
                # GUARDADO USANDO EL NOMBRE CORTO
                conn.update(spreadsheet=NOMBRE_ACPM, data=pd.concat([df_acpm_total, nueva_acpm], ignore_index=True))
                st.success("ACPM centralizada con éxito.")
                st.balloons()

    # --- PANTALLA: REPORTES ---
    elif menu == "🛠️ Reporte Condiciones":
        st.title("🛠️ Registro de Condiciones HSEQ")
        with st.form("form_cond_full"):
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
                nueva_cond = pd.DataFrame([{"Nit": str(nit_input), "Empresa": f_emp_c, "Fecha": str(datetime.now().date()), "Hallazgo": f_hall_c, "Condición Crítica": f_cond_c, "Clasificación del riesgo": f_riesgo_c, "Componente": "SST", "Responsable del cierre": "Auditor", "Fecha propuesta para el cierre": str(datetime.now().date()), "Prioridad": f_prio_c, "Estado": f_est_c, "Observación": "Registro inicial"}])
                conn.update(spreadsheet=NOMBRE_COND, data=pd.concat([df_cond_total, nueva_cond], ignore_index=True))
                st.success("Condición guardada.")

    elif menu == "🧠 Reporte Comportamiento":
        st.title("🧠 Registro de Comportamiento y PESV")
        with st.form("form_comp_full"):
            c1, c2 = st.columns(2)
            with c1:
                f_ins_h = st.text_input("Inspector")
                f_tipo_h = st.selectbox("Tipo", ["Conducta Humana", "PESV", "Tareas Críticas"])
                f_est_h = st.selectbox("Estado Observado", ["✅ SEGURO", "⚠️ ATÍPICO", "🚫 PELIGROSO"])
            with c2:
                f_humano_h = st.multiselect("Factores Humanos", ["Distracción", "Fatiga", "Exceso de confianza", "Prisa"])
                f_detalles_h = st.text_area("Descripción")
            if st.form_submit_button("🚀 REGISTRAR COMPORTAMIENTO"):
                nueva_comp = pd.DataFrame([{"Nit": str(nit_input), "ID_Inspección": str(uuid.uuid4())[:8].upper(), "Fecha/Hora Real": str(datetime.now()), "Inspector": f_ins_h, "Tipo de Inspección": f_tipo_h, "Estado observado": f_est_h, "Evidencia Fotográfica": "N/A", "Observaciones Factor Humano": ", ".join(f_humano_h) + " | " + f_detalles_h}])
                conn.update(spreadsheet=NOMBRE_COMP, data=pd.concat([df_comp_total, nueva_comp], ignore_index=True))
                st.success("Comportamiento registrado.")
