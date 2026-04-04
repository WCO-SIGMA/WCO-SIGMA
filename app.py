import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.express as px
from datetime import datetime
import uuid

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="WCO-SIGMA SIG+PESV", layout="wide")
conn = st.connection("gsheets", type=GSheetsConnection)

# 2. ACCESO POR NIT
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/1063/1063302.png", width=100)
nit_input = st.sidebar.text_input("Ingrese NIT o Cédula:", "").strip()

if not nit_input:
    st.title("🚀 WCO-SIGMA: Gestión Integral")
    st.info("Conexión Establecida. Ingrese el NIT para cargar sus módulos.")
else:
    # --- MOTOR DE CARGA INDEPENDIENTE ---
    # Cargamos CONDICIONES
    try:
        df_cond_total = conn.read(worksheet="CONDICIONES", ttl=0)
        df_cond_total.columns = df_cond_total.columns.str.strip()
        df_cond_total['Nit'] = df_cond_total['Nit'].astype(str).str.replace('.0', '', regex=False).str.strip()
        df_cond_emp = df_cond_total[df_cond_total['Nit'] == nit_input]
    except:
        df_cond_emp = pd.DataFrame()
        st.sidebar.error("❌ Pestaña 'CONDICIONES' no encontrada")

    # Cargamos COMPORTAMIENTO
    try:
        df_comp_total = conn.read(worksheet="COMPORTAMIENTO", ttl=0)
        df_comp_total.columns = df_comp_total.columns.str.strip()
        df_comp_total['Nit'] = df_comp_total['Nit'].astype(str).str.replace('.0', '', regex=False).str.strip()
        df_comp_emp = df_comp_total[df_comp_total['Nit'] == nit_input]
    except:
        df_comp_emp = pd.DataFrame()
        st.sidebar.error("❌ Pestaña 'COMPORTAMIENTO' no encontrada")

    # --- MENÚ DE NAVEGACIÓN ---
    menu = st.sidebar.radio("Módulos de Gestión", [
        "📊 Dashboard Gerencial", 
        "🛠️ Inspección de Condiciones", 
        "🧠 Comportamiento & PESV",
        "📂 Carpeta PHVA"
    ])

    # --- PANTALLA 1: DASHBOARD (SEPARACIÓN TOTAL) ---
    if menu == "📊 Dashboard Gerencial":
        st.title(f"📊 Dashboard Ejecutivo - NIT: {nit_input}")
        
        # Usamos TABS para asegurar que las tablas NO se mezclen visualmente
        tab_cond, tab_comp = st.tabs(["🔍 REPORTE DE CONDICIONES", "🧠 REPORTE DE COMPORTAMIENTO"])
        
        with tab_cond:
            if not df_cond_emp.empty:
                # Solo mostramos columnas de condiciones
                cols_cond = ["Nit", "Empresa", "Fecha", "Hallazgo", "Condición Crítica", "Clasificación del riesgo", "Estado"]
                existing_cols = [c for c in cols_cond if c in df_cond_emp.columns]
                
                c1, c2 = st.columns(2)
                with c1:
                    st.plotly_chart(px.bar(df_cond_emp['Condición Crítica'].value_counts().reset_index(), 
                                         x='count', y='Condición Crítica', orientation='h', title="Top Condiciones"), use_container_width=True)
                with c2:
                    st.plotly_chart(px.pie(df_cond_emp, names='Estado', title="Estado de Hallazgos", hole=0.4), use_container_width=True)
                
                st.write("### 📑 Tabla de Inspecciones de Condiciones")
                st.dataframe(df_cond_emp[existing_cols], use_container_width=True)
            else:
                st.warning("No hay datos en la pestaña CONDICIONES para este NIT.")

        with tab_comp:
            if not df_comp_emp.empty:
                # Solo mostramos columnas de comportamiento
                cols_comp = ["Nit", "ID_Inspección", "Fecha/Hora Real", "Inspector", "Tipo de Inspección", "Estado observado"]
                existing_cols_comp = [c for c in cols_comp if c in df_comp_emp.columns]

                st.plotly_chart(px.bar(df_comp_emp, x='Estado observado', color='Estado observado', title="Análisis de Comportamiento"), use_container_width=True)
                
                st.write("### 📑 Tabla de Observaciones de Comportamiento")
                st.dataframe(df_comp_emp[existing_cols_comp], use_container_width=True)
            else:
                st.warning("No hay datos en la pestaña COMPORTAMIENTO para este NIT.")

    # --- PANTALLA 2: FORMULARIO CONDICIONES ---
    elif menu == "🛠️ Inspección de Condiciones":
        st.title("🛠️ Registro de Condiciones HSEQ")
        with st.form("f_cond"):
            col1, col2 = st.columns(2)
            with col1:
                f_emp = st.text_input("Empresa")
                f_fec = st.date_input("Fecha", datetime.now())
                f_hall = st.text_area("Hallazgo")
                f_cond = st.selectbox("Condición", ["Orden y aseo", "Herramientas", "Locativo", "Eléctrico", "Vial"])
            with col2:
                f_riesgo = st.selectbox("GTC 45", ["Físico", "Químico", "Biológico", "Psicosocial", "Biomecánico", "Seguridad"])
                f_est = st.selectbox("Estado", ["Abierto", "En Proceso", "Cerrado"])
                f_resp = st.text_input("Responsable")
                f_obs = st.text_area("Observación")
            
            if st.form_submit_button("✅ GUARDAR EN CONDICIONES"):
                nueva = pd.DataFrame([{"Nit":str(nit_input), "Empresa":f_emp, "Fecha":str(f_fec), "Hallazgo":f_hall, "Condición Crítica":f_cond, "Clasificación del riesgo":f_riesgo, "Componente":"SST", "Responsable del cierre":f_resp, "Fecha propuesta para el cierre":str(f_fec), "Prioridad":"Media", "Estado":f_est, "Observación":f_obs}])
                conn.update(worksheet="CONDICIONES", data=pd.concat([df_cond_total, nueva], ignore_index=True))
                st.success("Guardado en pestaña CONDICIONES.")

    # --- PANTALLA 3: FORMULARIO COMPORTAMIENTO ---
    elif menu == "🧠 Comportamiento & PESV":
        st.title("🧠 Registro de Comportamiento")
        id_a = str(uuid.uuid4())[:8].upper()
        with st.form("f_comp"):
            f_ins = st.text_input("Inspector")
            f_tipo = st.selectbox("Tipo", ["Comportamiento", "Preoperacional Vehículo", "Tareas Críticas"])
            f_est_obs = st.selectbox("Estado", ["✅ SEGURO", "⚠️ ATÍPICO", "🚫 PELIGROSO"])
            f_humano = st.text_area("Observación Factor Humano")
            
            if st.form_submit_button("🚀 REGISTRAR EN COMPORTAMIENTO"):
                nueva_c = pd.DataFrame([{"Nit":str(nit_input), "ID_Inspección":id_a, "Fecha/Hora Real":str(datetime.now()), "Inspector":f_ins, "Tipo de Inspección":f_tipo, "Estado observado":f_est_obs, "Evidencia Fotográfica":"N/A", "Observaciones Factor Humano":f_humano}])
                conn.update(worksheet="COMPORTAMIENTO", data=pd.concat([df_comp_total, nueva_c], ignore_index=True))
                st.success(f"Registrado en pestaña COMPORTAMIENTO con ID {id_a}.")

    elif menu == "📂 Carpeta PHVA":
        st.link_button("📁 Abrir Drive", "https://drive.google.com/drive/u/0/folders/17o_kAZMRcGhDeI3vAd0dEk_UQJGYQWBZ")
