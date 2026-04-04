import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.express as px
from datetime import datetime
import uuid

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="WCO-SIGMA SIG+PESV", layout="wide")

# --- DIRECCIONES DE TUS ARCHIVOS ---
URL_COND = "https://docs.google.com/spreadsheets/d/18OIJe409rr6o_o4HSweiuncIoOrgJOXEt0GFCmEsL4g/edit"
URL_COMP = "https://docs.google.com/spreadsheets/d/1szrDZsA59e5sMF6OAzPeQ_nDX7E9lMehaXCPHmVNx5o/edit"

conn = st.connection("gsheets", type=GSheetsConnection)

# 2. ACCESO POR NIT
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/1063/1063302.png", width=100)
nit_input = st.sidebar.text_input("Ingrese identificación (NIT/Cédula):", "").strip()

if not nit_input:
    st.title("🚀 WCO-SIGMA: Gestión Integral")
    st.success("✅ Conexión con Google Cloud activa.")
    st.info("Ingrese el NIT para cargar los módulos técnicos.")
else:
    # --- MOTOR DE LECTURA INDEPENDIENTE ---
    # Leemos Condiciones
    try:
        df_cond_total = conn.read(spreadsheet=URL_COND, ttl=0)
        df_cond_total.columns = df_cond_total.columns.str.strip()
        df_cond_total['Nit'] = df_cond_total['Nit'].astype(str).str.replace('.0', '', regex=False).str.strip()
        df_cond_emp = df_cond_total[df_cond_total['Nit'] == nit_input]
    except:
        df_cond_total = pd.DataFrame()
        df_cond_emp = pd.DataFrame()

    # Leemos Comportamiento
    try:
        df_comp_total = conn.read(spreadsheet=URL_COMP, ttl=0)
        df_comp_total.columns = df_comp_total.columns.str.strip()
        df_comp_total['Nit'] = df_comp_total['Nit'].astype(str).str.replace('.0', '', regex=False).str.strip()
        df_comp_emp = df_comp_total[df_comp_total['Nit'] == nit_input]
    except:
        df_comp_total = pd.DataFrame()
        df_comp_emp = pd.DataFrame()

    menu = st.sidebar.radio("Navegación", ["📊 Dashboard Gerencial", "🛠️ Reporte Condiciones", "🧠 Reporte Comportamiento", "📂 Carpeta PHVA"])

    # --- PANTALLA 1: DASHBOARD GERENCIAL ---
    if menu == "📊 Dashboard Gerencial":
        st.title(f"📊 Dashboard Ejecutivo - NIT: {nit_input}")
        tab1, tab2 = st.tabs(["🔍 Gestión de Condiciones HSEQ", "🧠 Comportamiento & PESV"])
        
        with tab1:
            if not df_cond_emp.empty:
                col_a, col_b = st.columns(2)
                with col_a:
                    st.plotly_chart(px.pie(df_cond_emp, names='Estado', title="Estado de Hallazgos", hole=0.4), use_container_width=True)
                with col_b:
                    st.plotly_chart(px.bar(df_cond_emp['Condición Crítica'].value_counts().reset_index(), x='count', y='Condición Crítica', orientation='h', title="Tipología de Condiciones"), use_container_width=True)
                st.write("### 📋 Listado de Condiciones Encontradas")
                st.dataframe(df_cond_emp, use_container_width=True)
            else:
                st.warning("No hay datos en la base de Condiciones para este NIT.")

        with tab2:
            if not df_comp_emp.empty:
                st.plotly_chart(px.bar(df_comp_emp, x='Estado observado', color='Estado observado', title="Análisis de Observaciones"), use_container_width=True)
                st.write("### 📋 Histórico de Comportamientos y PESV")
                st.dataframe(df_comp_emp, use_container_width=True)
            else:
                st.warning("No hay datos en la base de Comportamiento para este NIT.")

    # --- PANTALLA 2: REPORTE CONDICIONES (VARIABLES RESTAURADAS) ---
    elif menu == "🛠️ Reporte Condiciones":
        st.title("🛠️ Inspección de Condiciones de Seguridad")
        with st.form("form_cond_full"):
            c1, c2 = st.columns(2)
            with c1:
                f_emp = st.text_input("Nombre de la Empresa")
                f_hall = st.text_area("Descripción del Hallazgo")
                f_cond = st.selectbox("Condición Crítica", ["Orden y aseo", "Herramientas/Equipos", "Daño locativo", "Sistemas eléctricos", "Alturas/Confinados", "Ambiental", "Vial", "Emergencias"])
                f_riesgo = st.selectbox("Clasificación GTC 45", ["Físico", "Químico", "Biológico", "Psicosocial", "Biomecánico", "Seguridad", "Natural"])
            with c2:
                f_comp = st.selectbox("Componente", ["SST", "Ambiente", "Vial", "Calidad"])
                f_resp = st.text_input("Responsable del cierre", "Líder HSEQ")
                f_prio = st.selectbox("Prioridad", ["Baja", "Media", "Alta"])
                f_est = st.selectbox("Estado inicial", ["Abierto", "En Proceso", "Cerrado"])
                f_obs = st.text_area("Plan de Acción / Observaciones")
            
            if st.form_submit_button("✅ GUARDAR EN BDI CONDICIONES"):
                nueva = pd.DataFrame([{
                    "Nit": str(nit_input), "Empresa": f_emp, "Fecha": str(datetime.now().date()), 
                    "Hallazgo": f_hall, "Condición Crítica": f_cond, "Clasificación del riesgo": f_riesgo, 
                    "Componente": f_comp, "Responsable del cierre": f_resp, 
                    "Fecha propuesta para el cierre": str(datetime.now().date()), 
                    "Prioridad": f_prio, "Estado": f_est, "Observación": f_obs
                }])
                df_final = pd.concat([df_cond_total, nueva], ignore_index=True)
                conn.update(spreadsheet=URL_COND, data=df_final)
                st.success("Inspección guardada exitosamente.")
                st.balloons()

    # --- PANTALLA 3: REPORTE COMPORTAMIENTO (VARIABLES RESTAURADAS) ---
    elif menu == "🧠 Reporte Comportamiento":
        st.title("🧠 Observación de Comportamiento y PESV")
        id_gen = str(uuid.uuid4())[:8].upper()
        with st.form("form_comp_full"):
            c1, c2 = st.columns(2)
            with c1:
                f_ins = st.text_input("Nombre del Inspector")
                f_tipo = st.selectbox("Tipo de Inspección", ["Conducta Humana", "Preoperacional Vehículo (PESV)", "Tareas Críticas", "Uso de EPP"])
                f_est_obs = st.selectbox("Estado Observado", ["✅ SEGURO", "⚠️ ATÍPICO", "🚫 PELIGROSO"])
            with c2:
                f_foto = st.text_input("Enlace Evidencia Fotográfica (Drive/Web)")
                f_humano = st.multiselect("Factores Humanos Detectados", ["Distracción", "Fatiga", "Exceso de confianza", "Omisión de norma", "Prisa/Afán"])
                f_detalles = st.text_area("Detalles y Compromisos del Trabajador")
            
            if st.form_submit_button("🚀 REGISTRAR EN BDI COMPORTAMIENTO"):
                nueva_c = pd.DataFrame([{
                    "Nit": str(nit_input), "ID_Inspección": id_gen, "Fecha/Hora Real": str(datetime.now()), 
                    "Inspector": f_ins, "Tipo de Inspección": f_tipo, "Estado observado": f_est_obs, 
                    "Evidencia Fotográfica": f_foto, "Observaciones Factor Humano": ", ".join(f_humano) + " | " + f_detalles
                }])
                df_final_c = pd.concat([df_comp_total, nueva_c], ignore_index=True)
                conn.update(spreadsheet=URL_COMP, data=df_final_c)
                st.success(f"Reporte {id_gen} registrado con éxito.")

    elif menu == "📂 Carpeta PHVA":
        st.link_button("📁 Abrir Drive", "https://drive.google.com/drive/u/0/folders/17o_kAZMRcGhDeI3vAd0dEk_UQJGYQWBZ")
