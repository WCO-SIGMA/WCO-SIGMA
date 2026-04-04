import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.express as px
from datetime import datetime
import uuid

# 1. CONFIGURACIÓN
st.set_page_config(page_title="WCO-SIGMA SIG+PESV", layout="wide")
conn = st.connection("gsheets", type=GSheetsConnection)

# 2. ACCESO POR NIT
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/1063/1063302.png", width=100)
nit_input = st.sidebar.text_input("Ingrese NIT o Cédula:", "").strip()

if not nit_input:
    st.title("🚀 WCO-SIGMA: Gestión Integral")
    st.info("Conexión Establecida. Ingrese el NIT para cargar sus módulos.")
else:
    # --- DETECCIÓN AUTOMÁTICA DE PESTAÑAS ---
    # Intentamos leer las pestañas. Si fallan los nombres, usamos la posición (0 y 1)
    try:
        # Intentamos leer por nombre primero
        df_cond_total = conn.read(worksheet="CONDICIONES", ttl=0)
    except:
        # Si falla, leemos la primera pestaña que encuentre el Excel
        df_cond_total = conn.read(ttl=0)
        st.sidebar.warning("⚠️ Usando pestaña principal (Verifique nombre 'CONDICIONES')")

    try:
        df_comp_total = conn.read(worksheet="COMPORTAMIENTO", ttl=0)
    except:
        df_comp_total = pd.DataFrame()
        st.sidebar.error("❌ No se detecta pestaña 'COMPORTAMIENTO'")

    # Limpieza de datos cargados
    if not df_cond_total.empty:
        df_cond_total.columns = df_cond_total.columns.str.strip()
        df_cond_total['Nit'] = df_cond_total['Nit'].astype(str).str.replace('.0', '', regex=False).str.strip()
        df_cond_emp = df_cond_total[df_cond_total['Nit'] == nit_input]
    else:
        df_cond_emp = pd.DataFrame()

    if not df_comp_total.empty:
        df_comp_total.columns = df_comp_total.columns.str.strip()
        df_comp_total['Nit'] = df_comp_total['Nit'].astype(str).str.replace('.0', '', regex=False).str.strip()
        df_comp_emp = df_comp_total[df_comp_total['Nit'] == nit_input]
    else:
        df_comp_emp = pd.DataFrame()

    # --- MENÚ DE NAVEGACIÓN ---
    menu = st.sidebar.radio("Módulos de Gestión", [
        "📊 Dashboard Gerencial", 
        "🛠️ Inspección de Condiciones", 
        "🧠 Comportamiento & PESV",
        "📂 Carpeta PHVA"
    ])

    # --- PANTALLA 1: DASHBOARD ---
    if menu == "📊 Dashboard Gerencial":
        st.title(f"📊 Dashboard Ejecutivo - NIT: {nit_input}")
        
        tab1, tab2 = st.tabs(["🔍 Condiciones HSEQ", "🧠 Comportamiento & PESV"])
        
        with tab1:
            if not df_cond_emp.empty:
                c1, c2, c3 = st.columns(3)
                total_c = len(df_cond_emp)
                abiertos = len(df_cond_emp[df_cond_emp['Estado'].astype(str).str.upper() == 'ABIERTO'])
                c1.metric("Inspecciones", total_c)
                c2.metric("Pendientes", abiertos, delta_color="inverse")
                c3.metric("% Eficacia", f"{int(((total_c-abiertos)/total_c)*100)}%" if total_c > 0 else "0%")
                
                g1, g2 = st.columns(2)
                with g1:
                    st.plotly_chart(px.bar(df_cond_emp['Condición Crítica'].value_counts().reset_index(), x='count', y='Condición Crítica', orientation='h', title="Top Condiciones"), use_container_width=True)
                with g2:
                    st.plotly_chart(px.pie(df_cond_emp, names='Clasificación del riesgo', title="Riesgos GTC 45", hole=0.4), use_container_width=True)
                st.dataframe(df_cond_emp, use_container_width=True)
            else:
                st.info("Sin datos de condiciones para este NIT.")

        with tab2:
            if not df_comp_emp.empty:
                st.plotly_chart(px.bar(df_comp_emp, x='Estado observado', color='Estado observado', title="Resumen Comportamiento"), use_container_width=True)
                st.dataframe(df_comp_emp, use_container_width=True)
            else:
                st.info("Sin datos de comportamiento para este NIT.")

    # --- PANTALLA 2: FORMULARIO CONDICIONES ---
    elif menu == "🛠️ Inspección de Condiciones":
        st.title("🛠️ Registro de Condiciones")
        with st.form("f_cond"):
            col1, col2 = st.columns(2)
            with col1:
                f_emp = st.text_input("Empresa")
                f_fec = st.date_input("Fecha", datetime.now())
                f_hall = st.text_area("Hallazgo")
                f_cond = st.selectbox("Condición", ["Orden y aseo", "Herramientas", "Locativo", "Eléctrico", "Alturas", "Vial", "Otros"])
            with col2:
                f_riesgo = st.selectbox("GTC 45", ["Físico", "Químico", "Biológico", "Psicosocial", "Biomecánico", "Seguridad", "Natural"])
                f_est = st.selectbox("Estado", ["Abierto", "En Proceso", "Cerrado"])
                f_resp = st.text_input("Responsable")
                f_obs = st.text_area("Observación")
            
            if st.form_submit_button("✅ GUARDAR"):
                nueva = pd.DataFrame([{"Nit":str(nit_input), "Empresa":f_emp, "Fecha":str(f_fec), "Hallazgo":f_hall, "Condición Crítica":f_cond, "Clasificación del riesgo":f_riesgo, "Componente":"SST", "Responsable del cierre":f_resp, "Fecha propuesta para el cierre":str(f_fec), "Prioridad":"Media", "Estado":f_est, "Observación":f_obs}])
                conn.update(worksheet="CONDICIONES", data=pd.concat([df_cond_total, nueva], ignore_index=True))
                st.success("Guardado. Refresque.")

    # --- PANTALLA 3: FORMULARIO COMPORTAMIENTO ---
    elif menu == "🧠 Comportamiento & PESV":
        st.title("🧠 Registro de Comportamiento")
        id_a = str(uuid.uuid4())[:8].upper()
        with st.form("f_comp"):
            f_ins = st.text_input("Inspector")
            f_tipo = st.selectbox("Tipo", ["Comportamiento", "Preoperacional Vehículo", "Tareas Críticas"])
            f_est_obs = st.selectbox("Estado", ["✅ SEGURO", "⚠️ ATÍPICO", "🚫 PELIGROSO"])
            f_humano = st.text_area("Observación Factor Humano")
            if st.form_submit_button("🚀 REGISTRAR"):
                nueva_c = pd.DataFrame([{"Nit":str(nit_input), "ID_Inspección":id_a, "Fecha/Hora Real":str(datetime.now()), "Inspector":f_ins, "Tipo de Inspección":f_tipo, "Estado observado":f_est_obs, "Evidencia Fotográfica":"N/A", "Observaciones Factor Humano":f_humano}])
                conn.update(worksheet="COMPORTAMIENTO", data=pd.concat([df_comp_total, nueva_c], ignore_index=True))
                st.success("Comportamiento registrado.")

    elif menu == "📂 Carpeta PHVA":
        st.link_button("📁 Abrir Drive", "https://drive.google.com/drive/u/0/folders/17o_kAZMRcGhDeI3vAd0dEk_UQJGYQWBZ")
