import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.express as px
from datetime import datetime
import uuid

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="WCO-SIGMA SIG+ACPM", layout="wide")

# --- CONFIGURACIÓN DE URLs (USA LAS URLs COMPLETAS AQUÍ) ---
URL_COND = "https://docs.google.com/spreadsheets/d/18OIJe409rr6o_o4HSweiuncIoOrgJOXEt0GFCmEsL4g/edit"
URL_COMP = "https://docs.google.com/spreadsheets/d/1szrDZsA59e5sMF6OAzPeQ_nDX7E9lMehaXCPHmVNx5o/edit"
# ⚠️ PEGA AQUÍ LA URL COMPLETA DE TU BD ACPM
URL_ACPM = "TU_URL_COMPLETA_DE_LA_BD_ACPM_AQUI" 

conn = st.connection("gsheets", type=GSheetsConnection)

# 2. ACCESO
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/1063/1063302.png", width=100)
nit_user = st.sidebar.text_input("Ingrese NIT de la Empresa:", "").strip()

if not nit_user:
    st.title("🚀 WCO-SIGMA: Sistema de Gestión PHVA")
    st.info("Por favor, ingrese el NIT para activar el sistema.")
else:
    # --- MOTOR DE LECTURA CON LIMPIEZA DE NIT ---
    def cargar_datos(url):
        try:
            df = conn.read(spreadsheet=url, ttl=0)
            if df is not None and not df.empty:
                df.columns = df.columns.str.strip()
                # Limpiamos el NIT de cualquier decimal o espacio para que coincida con el input
                df['Nit'] = df['Nit'].astype(str).apply(lambda x: x.split('.')[0].strip())
                return df, df[df['Nit'] == nit_user]
            return pd.DataFrame(), pd.DataFrame()
        except:
            return pd.DataFrame(), pd.DataFrame()

    df_cond_total, df_cond_emp = cargar_datos(URL_COND)
    df_comp_total, df_comp_emp = cargar_datos(URL_COMP)
    df_acpm_total, df_acpm_emp = cargar_datos(URL_ACPM)

    menu = st.sidebar.radio("Navegación", ["📊 Dashboard SIG", "⚖️ Gestión de ACPM", "🛠️ Reporte Condiciones", "🧠 Reporte Comportamiento"])

    # --- DASHBOARD ---
    if menu == "📊 Dashboard SIG":
        st.title(f"📊 Tablero SIG - NIT: {nit_user}")
        t1, t2, t3 = st.tabs(["🔍 Condiciones", "🧠 Comportamiento", "⚖️ ACPM"])
        
        with t1:
            if not df_cond_emp.empty:
                c1, c2 = st.columns(2)
                with c1: st.plotly_chart(px.pie(df_cond_emp, names='Estado', title="Estatus Condiciones"), use_container_width=True)
                with c2: st.plotly_chart(px.bar(df_cond_emp, x='Prioridad', title="Prioridad"), use_container_width=True)
                st.dataframe(df_cond_emp)
            else: st.warning("No hay datos de condiciones para este NIT.")

        with t2:
            if not df_comp_emp.empty:
                st.plotly_chart(px.bar(df_comp_emp, x='Estado observado', title="Análisis Conductual"), use_container_width=True)
                st.dataframe(df_comp_emp)
            else: st.warning("No hay datos de comportamiento.")

        with t3:
            if not df_acpm_emp.empty:
                ca1, ca2 = st.columns(2)
                with ca1: st.plotly_chart(px.pie(df_acpm_emp, names='Componente', title="ACPM por SIG"), use_container_width=True)
                with ca2: st.plotly_chart(px.bar(df_acpm_emp, x='Estado', title="Estado ACPM"), use_container_width=True)
                st.dataframe(df_acpm_emp)
            else: st.warning("No hay ACPM registradas.")

    # --- FORMULARIO ACPM ---
    elif menu == "⚖️ Gestión de ACPM":
        st.title("⚖️ Registro de Acciones ACPM")
        with st.form("form_acpm"):
            col1, col2 = st.columns(2)
            with col1:
                f_emp = st.text_input("Empresa")
                f_comp = st.selectbox("Componente", ["SST", "Ambiente", "Calidad", "Vial"])
                f_fuen = st.selectbox("Fuente", ["inspecciones", "auditorías", "incidentes", "otros"])
                f_desc = st.text_area("Descripción")
                st.write("**Análisis 5 Porqués**")
                p1, p2, p3, p4, p5 = st.text_input("P1"), st.text_input("P2"), st.text_input("P3"), st.text_input("P4"), st.text_input("P5")
            with col2:
                f_raiz = st.text_input("Causa Raíz")
                f_acci = st.text_area("Plan de Acción")
                f_tipo = st.radio("Tipo", ["Correctiva", "Preventiva", "Mejora"])
                f_resp = st.text_input("Responsable")
                f_fec_c = st.date_input("Fecha Cierre")
                f_camb = st.radio("¿Gestión del cambio?", ["No", "Sí"])
                f_esta = st.selectbox("Estado", ["Abierta", "En Ejecución"])

            if st.form_submit_button("💾 GUARDAR ACPM"):
                nueva = pd.DataFrame([{
                    "Nit": str(nit_user), "Empresa": f_emp, "Fecha de reporte": str(datetime.now().date()),
                    "Componente": f_comp, "Fuente": f_fuen, "Descripción Hallazgo": f_desc,
                    "Análisis Causa ¿Porqué 1?": p1, "Análisis Causa ¿Porqué 2?": p2,
                    "Análisis Causa ¿Porqué 3?": p3, "Análisis Causa ¿Porqué 4?": p4,
                    "Análisis Causa ¿Porqué 5?": p5, "Causa raíz": f_raiz,
                    "Acción Propuesta": f_acci, "Tipo Acción": f_tipo, "Responsable": f_resp,
                    "Fecha Cierre Prevista": str(f_fec_c), "Eficacia de la acción tomada": "Pendiente",
                    "La acción tomada activa gestión del cambio (Si es afirmativo IPVR, IAVI y sus controles)": f_camb, 
                    "Estado": f_esta
                }])
                df_upd = pd.concat([df_acpm_total, nueva], ignore_index=True)
                conn.update(spreadsheet=URL_ACPM, data=df_upd)
                st.success("¡ACPM Guardada!")
                st.balloons()

    # --- OTROS REPORTES (VERSIONES SIMPLES PARA ASEGURAR GUARDADO) ---
    elif menu == "🛠️ Reporte Condiciones":
        st.title("🛠️ Registro de Condiciones")
        with st.form("f_cond"):
            f_h = st.text_area("Hallazgo")
            if st.form_submit_button("✅ GUARDAR"):
                nueva_c = pd.DataFrame([{"Nit": str(nit_user), "Empresa": "Sede", "Fecha": str(datetime.now().date()), "Hallazgo": f_h, "Condición Crítica": "General", "Clasificación del riesgo": "Seguridad", "Componente": "SST", "Responsable del cierre": "Auditor", "Fecha propuesta para el cierre": str(datetime.now().date()), "Prioridad": "Media", "Estado": "Abierto", "Observación": "Registro inicial"}])
                conn.update(spreadsheet=URL_COND, data=pd.concat([df_cond_total, nueva_c], ignore_index=True))
                st.success("Guardado.")

    elif menu == "🧠 Reporte Comportamiento":
        st.title("🧠 Registro de Comportamiento")
        with st.form("f_comp"):
            f_o = st.text_area("Observación")
            if st.form_submit_button("🚀 REGISTRAR"):
                nueva_comp = pd.DataFrame([{"Nit": str(nit_user), "ID_Inspección": str(uuid.uuid4())[:8], "Fecha/Hora Real": str(datetime.now()), "Inspector": "Auditor", "Tipo de Inspección": "Conducta", "Estado observado": "✅ SEGURO", "Evidencia Fotográfica": "N/A", "Observaciones Factor Humano": f_o}])
                conn.update(spreadsheet=URL_COMP, data=pd.concat([df_comp_total, nueva_comp], ignore_index=True))
                st.success("Registrado.")
