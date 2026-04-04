import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.express as px
from datetime import datetime
import uuid

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="WCO-SIGMA SIG+ACPM", layout="wide")

# --- CONEXIONES BASES DE DATOS (URLs COMPLETAS PARA EVITAR SpreadsheetNotFound) ---
URL_COND = "https://docs.google.com/spreadsheets/d/18OIJe409rr6o_o4HSweiuncIoOrgJOXEt0GFCmEsL4g/edit"
URL_COMP = "https://docs.google.com/spreadsheets/d/1szrDZsA59e5sMF6OAzPeQ_nDX7E9lMehaXCPHmVNx5o/edit"
# ⚠️ PEGA AQUÍ LA URL COMPLETA DE TU NUEVA HOJA "BD ACPM"
URL_ACPM = "TU_URL_COMPLETA_DE_LA_BD_ACPM_AQUI" 

conn = st.connection("gsheets", type=GSheetsConnection)

# 2. ACCESO MULTIEMPRESA
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/1063/1063302.png", width=100)
nit_input = st.sidebar.text_input("Ingrese NIT de la Empresa:", "").strip()

if not nit_input:
    st.title("🚀 WCO-SIGMA: Sistema de Gestión PHVA")
    st.info("Plataforma de Mejora Continua. Ingrese su identificación para acceder.")
else:
    # --- MOTOR DE LECTURA ---
    def cargar_datos(url_sheet):
        try:
            df = conn.read(spreadsheet=url_sheet, ttl=0)
            if df is not None and not df.empty:
                df.columns = df.columns.str.strip()
                df['Nit'] = df['Nit'].astype(str).str.replace('.0', '', regex=False).str.strip()
                return df, df[df['Nit'] == nit_input]
            return pd.DataFrame(), pd.DataFrame()
        except:
            return pd.DataFrame(), pd.DataFrame()

    df_cond_total, df_cond_emp = cargar_datos(URL_COND)
    df_comp_total, df_comp_emp = cargar_datos(URL_COMP)
    df_acpm_total, df_acpm_emp = cargar_datos(URL_ACPM)

    menu = st.sidebar.radio("Navegación", ["📊 Dashboard Gerencial", "⚖️ Gestión de ACPM", "🛠️ Reporte Condiciones", "🧠 Reporte Comportamiento"])

    # --- PANTALLA: GESTIÓN DE ACPM ---
    if menu == "⚖️ Gestión de ACPM":
        st.title("⚖️ Módulo de Acciones Correctivas, Preventivas y de Mejora")
        
        with st.expander("➕ REGISTRAR NUEVA ACPM (Análisis de Causa Raíz)"):
            with st.form("form_acpm_vfinal"):
                col1, col2 = st.columns(2)
                with col1:
                    f_empresa = st.text_input("Empresa / Unidad")
                    f_componente = st.selectbox("Componente", ["SST", "Ambiente", "Calidad", "Vial"])
                    f_fuente = st.selectbox("Fuente", [
                        "inspecciones", "investigación de incidentes", 
                        "auditorías internas y externas", "observación de tareas", 
                        "reportes de actos y condiciones", "Legislación o normatividad", 
                        "Revisión gerencial"
                    ])
                    f_desc = st.text_area("Descripción Hallazgo")
                    st.subheader("🧠 Análisis 5 Porqués")
                    p1 = st.text_input("¿Por qué 1?")
                    p2 = st.text_input("¿Por qué 2?")
                    p3 = st.text_input("¿Por qué 3?")
                    p4 = st.text_input("¿Por qué 4?")
                    p5 = st.text_input("¿Por qué 5?")
                    f_raiz = st.text_input("Causa raíz")
                with col2:
                    f_accion = st.text_area("Acción Propuesta")
                    f_tipo = st.radio("Tipo Acción", ["Correctiva", "Preventiva", "Mejora"])
                    f_resp = st.text_input("Responsable")
                    f_fec_c = st.date_input("Fecha Cierre Prevista")
                    f_eficacia = st.selectbox("Eficacia", ["Pendiente", "Eficaz", "No Eficaz"])
                    # VARIABLE DE GESTIÓN DEL CAMBIO
                    f_cambio = st.radio("¿La acción tomada activa gestión del cambio? (IPVR, IAVI y controles)", ["No", "Sí"])
                    f_estado = st.selectbox("Estado", ["Abierta", "En Ejecución", "Cerrada"])

                if st.form_submit_button("💾 CENTRALIZAR ACPM"):
                    nueva_acpm = pd.DataFrame([{
                        "Nit": str(nit_input), 
                        "Empresa": f_empresa, 
                        "Fecha de reporte": str(datetime.now().date()),
                        "Componente": f_componente, 
                        "Fuente": f_fuente, 
                        "Descripción Hallazgo": f_desc,
                        "Análisis Causa ¿Porqué 1?": p1, 
                        "Análisis Causa ¿Porqué 2?": p2,
                        "Análisis Causa ¿Porqué 3?": p3, 
                        "Análisis Causa ¿Porqué 4?": p4,
                        "Análisis Causa ¿Porqué 5?": p5, 
                        "Causa raíz": f_raiz,
                        "Acción Propuesta": f_accion, 
                        "Tipo Acción": f_tipo, 
                        "Responsable": f_resp,
                        "Fecha Cierre Prevista": str(f_fec_c), 
                        "Eficacia de la acción tomada": f_eficacia,
                        "La acción tomada activa gestión del cambio (Si es afirmativo IPVR, IAVI y sus controles)": f_cambio, 
                        "Estado": f_estado
                    }])
                    
                    # ACTUALIZACIÓN USANDO URL COMPLETA
                    df_upd = pd.concat([df_acpm_total, nueva_acpm], ignore_index=True)
                    conn.update(spreadsheet=URL_ACPM, data=df_upd)
                    st.success("ACPM guardada con éxito en la base de datos.")
                    st.balloons()

        st.write("### 📋 Registro Histórico de ACPM")
        st.dataframe(df_acpm_emp, use_container_width=True)

    # --- RESTO DEL CÓDIGO (Dashboard y Reportes) SE MANTIENE IGUAL ---
    elif menu == "📊 Dashboard Gerencial":
        st.title(f"📊 Dashboard Ejecutivo - NIT: {nit_input}")
        tab1, tab2, tab3 = st.tabs(["🔍 Condiciones", "🧠 Comportamiento", "⚖️ ACPM"])
        with tab1:
            if not df_cond_emp.empty: st.plotly_chart(px.pie(df_cond_emp, names='Estado', title="Estado Condiciones"), use_container_width=True)
        with tab2:
            if not df_comp_emp.empty: st.plotly_chart(px.bar(df_comp_emp, x='Estado observado', title="Riesgo Conductual"), use_container_width=True)
        with tab3:
            if not df_acpm_emp.empty:
                c_a1, c_a2 = st.columns(2)
                with c_a1: st.plotly_chart(px.pie(df_acpm_emp, names='Componente', title="ACPM por Componente"), use_container_width=True)
                with c_a2: st.plotly_chart(px.bar(df_acpm_emp, x='Fuente', title="Fuentes de Hallazgos"), use_container_width=True)

    elif menu == "🛠️ Reporte Condiciones":
        st.title("🛠️ Registro de Condiciones")
        with st.form("f_cond"):
            f_hall = st.text_area("Hallazgo")
            if st.form_submit_button("✅ GUARDAR"):
                nueva_cond = pd.DataFrame([{"Nit":str(nit_input), "Empresa":"Sede Principal", "Fecha":str(datetime.now().date()), "Hallazgo":f_hall, "Condición Crítica":"General", "Clasificación del riesgo":"Seguridad", "Componente":"SST", "Responsable del cierre":"Líder HSEQ", "Fecha propuesta para el cierre":str(datetime.now().date()), "Prioridad":"Media", "Estado":"Abierto", "Observación":"Registro inicial"}])
                conn.update(spreadsheet=URL_COND, data=pd.concat([df_cond_total, nueva_cond], ignore_index=True))
                st.success("Condición guardada.")

    elif menu == "🧠 Reporte Comportamiento":
        st.title("🧠 Registro de Comportamiento")
        with st.form("f_comp"):
            f_obs = st.text_area("Observación")
            if st.form_submit_button("🚀 REGISTRAR"):
                nueva_comp = pd.DataFrame([{"Nit":str(nit_input), "ID_Inspección":str(uuid.uuid4())[:8], "Fecha/Hora Real":str(datetime.now()), "Inspector":"Auditor", "Tipo de Inspección":"Conducta", "Estado observado":"✅ SEGURO", "Evidencia Fotográfica":"N/A", "Observaciones Factor Humano":f_obs}])
                conn.update(spreadsheet=URL_COMP, data=pd.concat([df_comp_total, nueva_comp], ignore_index=True))
                st.success("Comportamiento registrado.")
