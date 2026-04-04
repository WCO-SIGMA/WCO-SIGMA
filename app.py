import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.express as px
from datetime import datetime
import uuid

# 1. CONFIGURACIÓN
st.set_page_config(page_title="WCO-SIGMA SIG+PESV", layout="wide")
conn = st.connection("gsheets", type=GSheetsConnection)

# --- CONFIGURACIÓN DE URLS (REEMPLAZA CON TU URL BASE) ---
# Copia la URL de tu Excel hasta antes del /edit
url_base = "https://docs.google.com/spreadsheets/d/17o_kAZMRcGhDeI3vAd0dEk_UQJGYQWBZ"

# 2. ACCESO POR NIT
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/1063/1063302.png", width=100)
nit_input = st.sidebar.text_input("Ingrese NIT o Cédula:", "").strip()

if not nit_input:
    st.title("🚀 WCO-SIGMA: Gestión Integral")
    st.info("Conexión por GID Activada. Ingrese el NIT para cargar módulos.")
else:
    # --- LECTURA FORZADA POR GID ---
    try:
        # Lee CONDICIONES (Normalmente gid=0)
        df_cond_total = conn.read(spreadsheet=url_base, worksheet="0", ttl=0)
        df_cond_total.columns = df_cond_total.columns.str.strip()
        df_cond_total['Nit'] = df_cond_total['Nit'].astype(str).str.replace('.0', '', regex=False).str.strip()
        df_cond_emp = df_cond_total[df_cond_total['Nit'] == nit_input]
    except:
        df_cond_emp = pd.DataFrame()
        st.sidebar.error("⚠️ Error en Hoja Condiciones")

    try:
        # AQUÍ DEBES PONER EL GID DE TU PESTAÑA COMPORTAMIENTO
        # Reemplaza "PON_AQUI_TU_GID" por el número que viste en la URL de esa pestaña
        df_comp_total = conn.read(spreadsheet=url_base, worksheet="COMPORTAMIENTO", ttl=0)
        df_comp_total.columns = df_comp_total.columns.str.strip()
        df_comp_total['Nit'] = df_comp_total['Nit'].astype(str).str.replace('.0', '', regex=False).str.strip()
        df_comp_emp = df_comp_total[df_comp_total['Nit'] == nit_input]
    except:
        df_comp_emp = pd.DataFrame()
        st.sidebar.error("⚠️ Error en Hoja Comportamiento")

    # --- MENÚ ---
    menu = st.sidebar.radio("Módulos", ["📊 Dashboard", "🛠️ Condiciones", "🧠 Comportamiento", "📂 PHVA"])

    if menu == "📊 Dashboard":
        st.title(f"📊 Dashboard - NIT: {nit_input}")
        t1, t2 = st.tabs(["🔍 Condiciones", "🧠 Comportamiento"])
        with t1:
            if not df_cond_emp.empty:
                st.plotly_chart(px.pie(df_cond_emp, names='Estado', title="Estado Condiciones"), use_container_width=True)
                st.dataframe(df_cond_emp, use_container_width=True)
        with t2:
            if not df_comp_emp.empty:
                st.plotly_chart(px.bar(df_comp_emp, x='Estado observado', title="Comportamiento"), use_container_width=True)
                st.dataframe(df_comp_emp, use_container_width=True)

    elif menu == "🛠️ Condiciones":
        st.title("🛠️ Registro de Condiciones")
        with st.form("f1"):
            f_emp = st.text_input("Empresa")
            f_hall = st.text_area("Hallazgo")
            if st.form_submit_button("✅ GUARDAR"):
                # Lógica de guardado simplificada para asegurar el tiro
                nueva = pd.DataFrame([{"Nit":str(nit_input), "Empresa":f_emp, "Fecha":str(datetime.now().date()), "Hallazgo":f_hall, "Condición Crítica":"Varios", "Clasificación del riesgo":"SST", "Componente":"SST", "Responsable del cierre":"N/A", "Fecha propuesta para el cierre":str(datetime.now().date()), "Prioridad":"Media", "Estado":"Abierto", "Observación":"N/A"}])
                conn.update(worksheet="0", data=pd.concat([df_cond_total, nueva], ignore_index=True))
                st.success("Guardado en Condiciones")

    elif menu == "🧠 Comportamiento":
        st.title("🧠 Registro de Comportamiento")
        with st.form("f2"):
            f_ins = st.text_input("Inspector")
            f_obs = st.text_area("Observación")
            if st.form_submit_button("🚀 REGISTRAR"):
                nueva_c = pd.DataFrame([{"Nit":str(nit_input), "ID_Inspección":str(uuid.uuid4())[:8], "Fecha/Hora Real":str(datetime.now()), "Inspector":f_ins, "Tipo de Inspección":"Conducta", "Estado observado":"Seguro", "Evidencia Fotográfica":"N/A", "Observaciones Factor Humano":f_obs}])
                conn.update(worksheet="COMPORTAMIENTO", data=pd.concat([df_comp_total, nueva_c], ignore_index=True))
                st.success("Guardado en Comportamiento")

    elif menu == "📂 PHVA":
        st.link_button("📁 Drive", "https://drive.google.com/drive/u/0/folders/17o_kAZMRcGhDeI3vAd0dEk_UQJGYQWBZ")
