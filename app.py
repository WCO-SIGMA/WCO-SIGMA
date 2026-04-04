import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.express as px
from datetime import datetime
import uuid

# 1. CONFIGURACIÓN
st.set_page_config(page_title="WCO-SIGMA SIG+PESV", layout="wide")

# --- REEMPLAZA ESTAS URLS CON LAS TUYAS ---
URL_COND = "https://docs.google.com/spreadsheets/d/TU_ID_AQUI_1" 
URL_COMP = "https://docs.google.com/spreadsheets/d/TU_ID_AQUI_2"

conn = st.connection("gsheets", type=GSheetsConnection)

# 2. ACCESO POR NIT
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/1063/1063302.png", width=100)
nit_input = st.sidebar.text_input("Ingrese identificación (NIT/Cédula):", "").strip()

if not nit_input:
    st.title("🚀 WCO-SIGMA: Gestión Integral")
    st.info("Sistema Multimodal Activo. Ingrese el NIT para cargar su tablero.")
else:
    # --- MOTOR DE LECTURA ROBUSTO ---
    try:
        df_cond_total = conn.read(spreadsheet=URL_COND, ttl=0)
        df_cond_total.columns = df_cond_total.columns.str.strip()
        df_cond_total['Nit'] = df_cond_total['Nit'].astype(str).str.replace('.0', '', regex=False).str.strip()
        df_cond_emp = df_cond_total[df_cond_total['Nit'] == nit_input]
    except:
        df_cond_emp = pd.DataFrame()
        df_cond_total = pd.DataFrame()

    try:
        df_comp_total = conn.read(spreadsheet=URL_COMP, ttl=0)
        df_comp_total.columns = df_comp_total.columns.str.strip()
        df_comp_total['Nit'] = df_comp_total['Nit'].astype(str).str.replace('.0', '', regex=False).str.strip()
        df_comp_emp = df_comp_total[df_comp_total['Nit'] == nit_input]
    except:
        df_comp_emp = pd.DataFrame()
        df_comp_total = pd.DataFrame()

    menu = st.sidebar.radio("Menú Principal", ["📊 Dashboard Gerencial", "🛠️ Reporte Condiciones", "🧠 Reporte Comportamiento", "📂 Carpeta PHVA"])

    # --- PANTALLA 1: DASHBOARD GERENCIAL ---
    if menu == "📊 Dashboard Gerencial":
        st.title(f"📊 Dashboard Ejecutivo - NIT: {nit_input}")
        t1, t2 = st.tabs(["🔍 Condiciones HSEQ", "🧠 Comportamiento & PESV"])
        
        with t1:
            if not df_cond_emp.empty:
                c1, c2, c3 = st.columns(3)
                total_c = len(df_cond_emp)
                abiertos = len(df_cond_emp[df_cond_emp['Estado'].astype(str).str.upper() == 'ABIERTO'])
                c1.metric("Inspecciones", total_c)
                c2.metric("Pendientes", abiertos, delta_color="inverse")
                c3.metric("Eficacia", f"{int(((total_c-abiertos)/total_c)*100)}%" if total_c > 0 else "0%")
                
                col_a, col_b = st.columns(2)
                with col_a:
                    st.plotly_chart(px.bar(df_cond_emp['Condición Crítica'].value_counts().reset_index(), x='count', y='Condición Crítica', orientation='h', title="Hallazgos por Condición"), use_container_width=True)
                with col_b:
                    st.plotly_chart(px.pie(df_cond_emp, names='Clasificación del riesgo', title="Riesgos GTC 45", hole=0.4), use_container_width=True)
                st.dataframe(df_cond_emp, use_container_width=True)
            else:
                st.warning("No se encontraron datos en la Base de Condiciones para este NIT.")
            
        with t2:
            if not df_comp_emp.empty:
                st.plotly_chart(px.bar(df_comp_emp, x='Estado observado', color='Estado observado', title="Análisis de Comportamiento"), use_container_width=True)
                st.dataframe(df_comp_emp, use_container_width=True)
            else:
                st.warning("No se encontraron datos en la Base de Comportamiento para este NIT.")

    # --- PANTALLA 2: REPORTE CONDICIONES (CON TODAS LAS VARIABLES) ---
    elif menu == "🛠️ Reporte Condiciones":
        st.title("🛠️ Registro de Condiciones de Seguridad")
        with st.form("form_cond"):
            col1, col2 = st.columns(2)
            with col1:
                f_emp = st.text_input("Empresa")
                f_fec = st.date_input("Fecha", datetime.now())
                f_hall = st.text_area("Hallazgo Detallado")
                f_cond = st.selectbox("Condición Crítica", ["Orden y aseo", "Herramientas/Equipos", "Daño locativo", "Sistemas eléctricos", "Alturas/Confinados", "Ambiental", "Vial", "Otros"])
                f_riesgo = st.selectbox("Clasificación GTC 45", ["Físico", "Químico", "Biológico", "Psicosocial", "Biomecánico", "Seguridad", "Natural"])
            with col2:
                f_comp = st.selectbox("Componente SIG", ["SST", "Ambiente", "Vial", "Calidad"])
                f_resp = st.text_input("Responsable del cierre")
                f_f_p = st.date_input("Fecha propuesta para el cierre", datetime.now())
                f_prio = st.selectbox("Prioridad", ["Baja", "Media", "Alta"])
                f_est = st.selectbox("Estado", ["Abierto", "En Proceso", "Cerrado"])
                f_obs = st.text_area("Observación")
            
            if st.form_submit_button("✅ GUARDAR CONDICIÓN"):
                nueva = pd.DataFrame([{"Nit":str(nit_input), "Empresa":f_emp, "Fecha":str(f_fec), "Hallazgo":f_hall, "Condición Crítica":f_cond, "Clasificación del riesgo":f_riesgo, "Componente":f_comp, "Responsable del cierre":f_resp, "Fecha propuesta para el cierre":str(f_f_p), "Prioridad":f_prio, "Estado":f_est, "Observación":f_obs}])
                conn.update(spreadsheet=URL_COND, data=pd.concat([df_cond_total, nueva], ignore_index=True))
                st.success("Inspección de condición guardada.")

    # --- PANTALLA 3: REPORTE COMPORTAMIENTO (RECUPERANDO LISTAS DESPLEGABLES) ---
    elif menu == "🧠 Reporte Comportamiento":
        st.title("🧠 Inspección de Comportamiento y PESV")
        id_auto = str(uuid.uuid4())[:8].upper()
        with st.form("form_comp"):
            col1, col2 = st.columns(2)
            with col1:
                f_inspector = st.text_input("Nombre del Inspector")
                f_tipo = st.selectbox("Tipo de Inspección", [
                    "Observación de Comportamiento Seguro",
                    "Preoperacional Vehículo (PESV)",
                    "Preoperacional Herramientas/Equipos",
                    "Auditoría Tareas Críticas"
                ])
                f_est_obs = st.selectbox("Estado Observado", ["✅ SEGURO", "⚠️ ATÍPICO", "🚫 PELIGROSO"])
            with col2:
                f_foto = st.text_input("Enlace de Evidencia Fotográfica")
                # RECUPERAMOS EL FACTOR HUMANO MULTIPLE
                f_humano = st.multiselect("Factores Humanos Detectados:", [
                    "Distracción / Falta de atención", "Fatiga / Cansancio", 
                    "Falta de EPP / Uso incorrecto", "Exceso de confianza", 
                    "Omisión de procedimiento", "Prisa / Afán excesivo"
                ])
                f_detalles = st.text_area("Detalles y Compromisos")
            
            if st.form_submit_button("🚀 REGISTRAR COMPORTAMIENTO"):
                nueva_c = pd.DataFrame([{
                    "Nit":str(nit_input), "ID_Inspección":id_auto, "Fecha/Hora Real":str(datetime.now()), 
                    "Inspector":f_inspector, "Tipo de Inspección":f_tipo, "Estado observado":f_est_obs, 
                    "Evidencia Fotográfica":f_foto, "Observaciones Factor Humano": ", ".join(f_humano) + " | " + f_detalles
                }])
                conn.update(spreadsheet=URL_COMP, data=pd.concat([df_comp_total, nueva_c], ignore_index=True))
                st.success(f"Reporte {id_auto} guardado con éxito.")

    elif menu == "📂 Carpeta PHVA":
        st.link_button("📁 Abrir Drive", "https://drive.google.com/drive/u/0/folders/17o_kAZMRcGhDeI3vAd0dEk_UQJGYQWBZ")
