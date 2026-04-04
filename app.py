import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.express as px
from datetime import datetime
import uuid

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="WCO-SIGMA SIG+PESV", layout="wide")

# --- IDs EXTRAÍDOS DE TUS ENLACES ---
ID_COND = "18OIJe409rr6o_o4HSweiuncIoOrgJOXEt0GFCmEsL4g"
ID_COMP = "1szrDZsA59e5sMF6OAzPeQ_nDX7E9lMehaXCPHmVNx5o"

conn = st.connection("gsheets", type=GSheetsConnection)

# 2. ACCESO POR NIT
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/1063/1063302.png", width=100)
nit_input = st.sidebar.text_input("Ingrese NIT o Cédula de la Empresa:", "").strip()

if not nit_input:
    st.title("🚀 WCO-SIGMA: Sistema de Gestión Integrado")
    st.info("Conexión Establecida con BDI. Ingrese el NIT para cargar sus datos.")
else:
    # --- MOTOR DE LECTURA DE DATOS ---
    try:
        # Lectura de Condiciones
        df_cond_total = conn.read(spreadsheet=ID_COND, ttl=0)
        df_cond_total.columns = df_cond_total.columns.str.strip()
        df_cond_total['Nit'] = df_cond_total['Nit'].astype(str).str.replace('.0', '', regex=False).str.strip()
        df_cond_emp = df_cond_total[df_cond_total['Nit'] == nit_input]
    except Exception as e:
        st.sidebar.error(f"Error en BDI Condiciones: {e}")
        df_cond_total = pd.DataFrame()
        df_cond_emp = pd.DataFrame()

    try:
        # Lectura de Comportamiento
        df_comp_total = conn.read(spreadsheet=ID_COMP, ttl=0)
        df_comp_total.columns = df_comp_total.columns.str.strip()
        df_comp_total['Nit'] = df_comp_total['Nit'].astype(str).str.replace('.0', '', regex=False).str.strip()
        df_comp_emp = df_comp_total[df_comp_total['Nit'] == nit_input]
    except Exception as e:
        st.sidebar.error(f"Error en BDI Comportamiento: {e}")
        df_comp_total = pd.DataFrame()
        df_comp_emp = pd.DataFrame()

    # --- MENÚ DE NAVEGACIÓN ---
    menu = st.sidebar.radio("Módulos de Gestión", [
        "📊 Dashboard Gerencial", 
        "🛠️ Inspección de Condiciones", 
        "🧠 Comportamiento & PESV",
        "📂 Carpeta PHVA"
    ])

    # --- PANTALLA 1: DASHBOARD GERENCIAL ---
    if menu == "📊 Dashboard Gerencial":
        st.title(f"📊 Dashboard Ejecutivo - NIT: {nit_input}")
        
        tab1, tab2 = st.tabs(["🔍 Gestión de Condiciones", "🧠 Gestión de Comportamiento"])
        
        with tab1:
            if not df_cond_emp.empty:
                c1, c2, c3 = st.columns(3)
                total_c = len(df_cond_emp)
                abiertos = len(df_cond_emp[df_cond_emp['Estado'].astype(str).str.upper() == 'ABIERTO'])
                c1.metric("Total Inspecciones", total_c)
                c2.metric("Hallazgos Abiertos", abiertos, delta_color="inverse")
                c3.metric("% Eficacia Cierre", f"{int(((total_c-abiertos)/total_c)*100)}%" if total_c > 0 else "0%")
                
                g1, g2 = st.columns(2)
                with g1:
                    fig_c = px.bar(df_cond_emp['Condición Crítica'].value_counts().reset_index(), 
                                 x='count', y='Condición Crítica', orientation='h', title="🎯 Top Condiciones Críticas")
                    st.plotly_chart(fig_c, use_container_width=True)
                with g2:
                    fig_r = px.pie(df_cond_emp, names='Clasificación del riesgo', title="☣️ Riesgos GTC 45", hole=0.4)
                    st.plotly_chart(fig_r, use_container_width=True)
                st.write("### 📑 Histórico de Condiciones")
                st.dataframe(df_cond_emp, use_container_width=True)
            else:
                st.warning("No hay registros de condiciones para este NIT.")

        with tab2:
            if not df_comp_emp.empty:
                st.plotly_chart(px.bar(df_comp_emp, x='Estado observado', color='Estado observado', title="📊 Resumen de Comportamientos"), use_container_width=True)
                st.write("### 📑 Histórico de Comportamiento")
                st.dataframe(df_comp_emp, use_container_width=True)
            else:
                st.warning("No hay registros de comportamiento para este NIT.")

    # --- PANTALLA 2: FORMULARIO CONDICIONES ---
    elif menu == "🛠️ Inspección de Condiciones":
        st.title("🛠️ Registro de Condiciones HSEQ")
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
                f_prio = st.selectbox("Prioridad", ["Baja", "Media", "Alta"])
                f_est = st.selectbox("Estado", ["Abierto", "En Proceso", "Cerrado"])
                f_obs = st.text_area("Observación / Plan de Acción")
            
            if st.form_submit_button("✅ GUARDAR EN BDI CONDICIONES"):
                nueva_fila = pd.DataFrame([{
                    "Nit": str(nit_input), "Empresa": f_emp, "Fecha": str(f_fec), "Hallazgo": f_hall,
                    "Condición Crítica": f_cond, "Clasificación del riesgo": f_riesgo, "Componente": f_comp,
                    "Responsable del cierre": "Asignado", "Fecha propuesta para el cierre": str(f_fec),
                    "Prioridad": f_prio, "Estado": f_est, "Observación": f_obs
                }])
                df_upd = pd.concat([df_cond_total, nueva_fila], ignore_index=True)
                conn.update(spreadsheet=ID_COND, data=df_upd)
                st.success("Inspección guardada exitosamente en BDI WCO SIGMA.")

    # --- PANTALLA 3: FORMULARIO COMPORTAMIENTO ---
    elif menu == "🧠 Comportamiento & PESV":
        st.title("🧠 Registro de Comportamiento y PESV")
        id_auto = str(uuid.uuid4())[:8].upper()
        with st.form("form_comp"):
            col1, col2 = st.columns(2)
            with col1:
                f_inspector = st.text_input("Nombre del Inspector")
                f_tipo = st.selectbox("Tipo de Inspección", ["Observación de Comportamiento", "Preoperacional Vehículo (PESV)", "Tareas Críticas"])
                f_est_obs = st.selectbox("Estado Observado", ["✅ SEGURO", "⚠️ ATÍPICO", "🚫 PELIGROSO"])
            with col2:
                f_foto = st.text_input("Enlace Evidencia Fotográfica")
                f_humano = st.multiselect("Factores Humanos Detectados:", ["Distracción", "Fatiga", "Falta de EPP", "Exceso de confianza", "Prisa"])
                f_detalles = st.text_area("Detalles de la observación")
            
            if st.form_submit_button("🚀 REGISTRAR EN BDI COMPORTAMIENTO"):
                nueva_fila_c = pd.DataFrame([{
                    "Nit": str(nit_input), "ID_Inspección": id_auto, "Fecha/Hora Real": str(datetime.now()), 
                    "Inspector": f_inspector, "Tipo de Inspección": f_tipo, "Estado observado": f_est_obs, 
                    "Evidencia Fotográfica": f_foto, "Observaciones Factor Humano": ", ".join(f_humano) + " | " + f_detalles
                }])
                df_upd_c = pd.concat([df_comp_total, nueva_fila_c], ignore_index=True)
                conn.update(spreadsheet=ID_COMP, data=df_upd_c)
                st.success(f"Reporte {id_auto} guardado en BDI COMPORTAMIENTO.")

    elif menu == "📂 Carpeta PHVA":
        st.link_button("📁 Abrir Drive", "https://drive.google.com/drive/u/0/folders/17o_kAZMRcGhDeI3vAd0dEk_UQJGYQWBZ")
