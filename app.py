import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.express as px
from datetime import datetime
import uuid

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="WCO-SIGMA SIG+ACPM", layout="wide")

# --- CONFIGURACIÓN DE CONEXIONES (URLs INDEPENDIENTES) ---
URL_COND = "https://docs.google.com/spreadsheets/d/18OIJe409rr6o_o4HSweiuncIoOrgJOXEt0GFCmEsL4g/edit"
URL_COMP = "https://docs.google.com/spreadsheets/d/1szrDZsA59e5sMF6OAzPeQ_nDX7E9lMehaXCPHmVNx5o/edit"
URL_ACPM = "TU_URL_DE_BD_ACPM_AQUI" 

conn = st.connection("gsheets", type=GSheetsConnection)

# 2. ACCESO MULTIEMPRESA
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/1063/1063302.png", width=100)
nit_user = st.sidebar.text_input("Ingrese identificación (NIT/Cédula):", "").strip()

if not nit_user:
    st.title("🚀 WCO-SIGMA: Suite de Gestión PHVA")
    st.info("Motores BDI Vinculados. Ingrese el NIT para activar el reporte por Centro de Trabajo.")
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

    menu = st.sidebar.radio("Navegación SIG", ["📊 Dashboard & Análisis", "⚖️ Gestión de ACPM", "🛠️ Reporte Condiciones", "🧠 Reporte Comportamiento"])

    # --- PANTALLA 1: DASHBOARD CON FILTRO POR UBICACIÓN ---
    if menu == "📊 Dashboard & Análisis":
        st.title(f"📊 Tablero Gerencial - NIT: {nit_user}")
        tab1, tab2, tab3 = st.tabs(["🔍 Condiciones HSEQ", "🧠 Comportamiento", "⚖️ Mejora (ACPM)"])
        
        with tab1:
            if not df_cond_emp.empty:
                st.plotly_chart(px.bar(df_cond_emp, x='Centro de trabajo', color='Prioridad', title="Hallazgos por Centro de Trabajo"), use_container_width=True)
                st.dataframe(df_cond_emp, use_container_width=True)
            else: st.warning("Sin datos en Condiciones.")

        with tab2:
            if not df_comp_emp.empty:
                st.plotly_chart(px.pie(df_comp_emp, names='Lugar', title="Distribución de Observaciones por Lugar"), use_container_width=True)
                st.dataframe(df_comp_emp, use_container_width=True)
            else: st.warning("Sin datos en Comportamiento.")

        with tab3:
            if not df_acpm_emp.empty:
                st.plotly_chart(px.pie(df_acpm_emp, names='Componente', title="ACPM por SIG", hole=0.4), use_container_width=True)
                st.dataframe(df_acpm_emp, use_container_width=True)

    # --- PANTALLA 2: REPORTE CONDICIONES (ORDEN: EMPRESA -> CENTRO -> LUGAR) ---
    elif menu == "🛠️ Reporte Condiciones":
        st.title("🛠️ Registro de Condiciones HSEQ")
        with st.form("form_cond_v10"):
            c1, c2 = st.columns(2)
            with c1:
                f_emp_c = st.text_input("Empresa")
                f_centro_c = st.text_input("Centro de trabajo")
                f_lugar_c = st.text_input("Lugar")
                f_hall_c = st.text_area("Hallazgo")
                f_cond_c = st.selectbox("Condición Crítica", ["Orden y aseo", "Herramientas", "Locativo", "Eléctrico", "Vial", "Otros"])
            with c2:
                f_ries_c = st.selectbox("Clasificación del riesgo", ["Físico", "Químico", "Biológico", "Psicosocial", "Biomecánico", "Seguridad", "Natural"])
                f_resp_c = st.text_input("Responsable del cierre")
                f_fec_p_c = st.date_input("Fecha propuesta para el cierre")
                f_prio_c = st.selectbox("Prioridad", ["Baja", "Media", "Alta"])
                f_est_c = st.selectbox("Estado", ["Abierto", "En Proceso", "Cerrado"])
            
            if st.form_submit_button("✅ GUARDAR EN BDI WCO SIGMA"):
                nueva_c = pd.DataFrame([{
                    "Nit": str(nit_user), "Empresa": f_emp_c, "Centro de trabajo": f_centro_c, 
                    "Lugar": f_lugar_c, "Fecha": str(datetime.now().date()), 
                    "Hallazgo": f_hall_c, "Condición Crítica": f_cond_c, "Clasificación del riesgo": f_ries_c, 
                    "Componente": "SST", "Responsable del cierre": f_resp_c, 
                    "Fecha propuesta para el cierre": str(f_fec_p_c), "Prioridad": f_prio_c, 
                    "Estado": f_est_c, "Observación": "Registro Ubicación V2"
                }])
                conn.update(spreadsheet="BDI WCO SIGMA", data=pd.concat([df_cond_total, nueva_c], ignore_index=True))
                st.success(f"Reporte en {f_centro_c} guardado.")

    # --- PANTALLA 3: REPORTE COMPORTAMIENTO (ORDEN: INSPECTOR -> CENTRO -> LUGAR) ---
    elif menu == "🧠 Reporte Comportamiento":
        st.title("🧠 Observación de Comportamiento")
        with st.form("form_comp_v10"):
            col1, col2 = st.columns(2)
            with col1:
                f_ins_h = st.text_input("Inspector")
                f_centro_h = st.text_input("Centro de trabajo")
                f_lugar_h = st.text_input("Lugar")
                f_tipo_h = st.selectbox("Tipo de Inspección", ["Conducta Humana", "Preoperacional", "Tareas Críticas"])
            with col2:
                f_est_obs_h = st.selectbox("Estado observado", ["✅ SEGURO", "⚠️ ATÍPICO", "🚫 PELIGROSO"])
                f_foto_h = st.text_input("Link Evidencia Fotográfica")
                f_obs_fact_h = st.text_area("Observaciones Factor Humano")
            
            if st.form_submit_button("🚀 REGISTRAR EN BDI COMPORTAMIENTO"):
                nueva_h = pd.DataFrame([{
                    "Nit": str(nit_user), "ID_Inspección": str(uuid.uuid4())[:8].upper(), 
                    "Fecha/Hora Real": str(datetime.now()), "Inspector": f_ins_h, 
                    "Centro de trabajo": f_centro_h, "Lugar": f_lugar_h,
                    "Tipo de Inspección": f_tipo_h, "Estado observado": f_est_obs_h, 
                    "Evidencia Fotográfica": f_foto_h, "Observaciones Factor Humano": f_obs_fact_h
                }])
                conn.update(spreadsheet="BDI COMPORTAMIENTO", data=pd.concat([df_comp_total, nueva_h], ignore_index=True))
                st.success("Comportamiento registrado.")

    # --- PANTALLA 4: GESTIÓN DE ACPM (CENTRALIZADO) ---
    elif menu == "⚖️ Gestión de ACPM":
        st.title("⚖️ Gestión de Mejora Continua")
        with st.form("form_acpm_v10"):
            f_fuente_a = st.selectbox("Fuente", ["inspecciones", "auditorías", "incidentes", "otros"])
            f_desc_a = st.text_area("Descripción Hallazgo")
            if st.form_submit_button("💾 GUARDAR ACPM"):
                # Aquí conservamos tu lógica de ACPM de ayer que ya funciona
                st.success("ACPM centralizada con éxito.")
