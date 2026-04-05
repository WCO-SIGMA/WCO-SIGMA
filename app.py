import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.express as px
from datetime import datetime
import uuid
from fpdf import FPDF

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="WCO-SIGMA SIG+ACPM", layout="wide")

# --- CONFIGURACIÓN DE CONEXIONES (ACTUALIZA AQUÍ TUS URL) ---
URL_COND = "https://docs.google.com/spreadsheets/d/18OIJe409rr6o_o4HSweiuncIoOrgJOXEt0GFCmEsL4g/edit"
URL_COMP = "https://docs.google.com/spreadsheets/d/1szrDZsA59e5sMF6OAzPeQ_nDX7E9lMehaXCPHmVNx5o/edit"
URL_ACPM = "https://docs.google.com/spreadsheets/d/PONER_AQUI_TU_ID_REAL/edit" 

conn = st.connection("gsheets", type=GSheetsConnection)

# 2. ACCESO POR NIT
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/1063/1063302.png", width=100)
nit_user = st.sidebar.text_input("Ingrese NIT de la Empresa:", "").strip()

if not nit_user:
    st.title("🚀 WCO-SIGMA: Suite de Gestión PHVA")
    st.info("Motores Sincronizados. Ingrese el NIT para activar el Dashboard Gerencial.")
else:
    # --- MOTOR DE LECTURA ROBUSTO ---
    def cargar(url, nombre_debug):
        try:
            df = conn.read(spreadsheet=url, ttl=0)
            if df is not None and not df.empty:
                df.columns = df.columns.str.strip()
                df['Nit'] = df['Nit'].astype(str).apply(lambda x: x.split('.')[0].strip())
                return df, df[df['Nit'] == nit_user]
            return pd.DataFrame(), pd.DataFrame()
        except:
            st.sidebar.error(f"Error en: {nombre_debug}")
            return pd.DataFrame(), pd.DataFrame()

    df_cond_t, df_cond_e = cargar(URL_COND, "BDI SIGMA")
    df_comp_t, df_comp_e = cargar(URL_COMP, "BDI COMPORTAMIENTO")
    df_acpm_t, df_acpm_e = cargar(URL_ACPM, "BD ACPM")

    menu = st.sidebar.radio("Navegación", ["📊 Dashboard Gerencial", "⚖️ Gestión de ACPM", "🛠️ Reporte Condiciones", "🧠 Reporte Comportamiento"])

    # --- PANTALLA 1: DASHBOARD GERENCIAL (RECUPERANDO TODOS LOS GRÁFICOS) ---
    if menu == "📊 Dashboard Gerencial":
        st.title(f"📊 Tablero de Control - NIT: {nit_user}")
        tab1, tab2, tab3 = st.tabs(["🔍 BDI WCO SIGMA", "🧠 BDI COMPORTAMIENTO", "⚖️ BD ACPM"])
        
        with tab1:
            if not df_cond_e.empty:
                st.subheader("Visualización de Condiciones HSEQ")
                col1, col2 = st.columns(2)
                with col1:
                    st.plotly_chart(px.bar(df_cond_e, x='Centro de trabajo', color='Prioridad', title="Hallazgos por Centro"), use_container_width=True)
                    st.plotly_chart(px.pie(df_cond_e, names='Condición Crítica', title="Condiciones Críticas", hole=0.3), use_container_width=True)
                with col2:
                    st.plotly_chart(px.bar(df_cond_e, x='Lugar', color='Estado', title="Hallazgos por Lugar"), use_container_width=True)
                    st.plotly_chart(px.pie(df_cond_e, names='Estado', title="Avance de Cierres"), use_container_width=True)
                
                # Espacios de Análisis
                st.markdown("---")
                a1, a2 = st.columns(2)
                txt_an_cond = a1.text_area("Análisis Técnico (Condiciones):", key="an1")
                txt_pl_cond = a2.text_area("Plan de Acción (Condiciones):", key="pl1")
            else: st.warning("Sin datos en BDI WCO SIGMA")

        with tab2:
            if not df_comp_e.empty:
                st.subheader("Análisis de Comportamiento y PESV")
                g1, g2 = st.columns(2)
                with g1:
                    st.plotly_chart(px.bar(df_comp_e, x='Centro de trabajo', color='Estado observado', title="Cultura por Centro"), use_container_width=True)
                with g2:
                    st.plotly_chart(px.pie(df_comp_e, names='Lugar', title="Observaciones por Lugar"), use_container_width=True)
                st.plotly_chart(px.bar(df_comp_e, x='Estado observado', title="Estatus de Comportamientos"), use_container_width=True)
                
                st.markdown("---")
                a3, a4 = st.columns(2)
                txt_an_comp = a3.text_area("Análisis de Riesgo Conductual:", key="an2")
                txt_pl_comp = a4.text_area("Plan de Intervención Humana:", key="pl2")
            else: st.warning("Sin datos en BDI COMPORTAMIENTO")

        with tab3:
            if not df_acpm_e.empty:
                st.subheader("Gestión de Mejora Continua (ACPM)")
                ca1, ca2 = st.columns(2)
                with ca1:
                    st.plotly_chart(px.pie(df_acpm_e, names='Componente', title="ACPM por Sistema", hole=0.4), use_container_width=True)
                    st.plotly_chart(px.bar(df_acpm_e, x='Causa raíz', color='Estado', title="Análisis de Causa Raíz"), use_container_width=True)
                with ca2:
                    st.plotly_chart(px.bar(df_acpm_e, x='Fuente', color='Tipo Acción', title="Fuente vs Tipo de Acción"), use_container_width=True)
                    st.plotly_chart(px.pie(df_acpm_e, names='Estado', title="Estatus de ACPM"), use_container_width=True)
                
                st.markdown("---")
                txt_an_acpm = st.text_area("Evaluación de la Mejora Continua:", key="an3")
            else: st.error("Sin datos en BD ACPM. Verifique el NIT o la URL.")

    # --- LOS FORMULARIOS SE MANTIENEN IGUAL QUE EN LA VERSIÓN ANTERIOR ---
    # ... (Aquí iría el resto de tu código de formularios)
