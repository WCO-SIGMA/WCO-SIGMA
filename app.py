import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.express as px
from datetime import datetime
import uuid
from fpdf import FPDF

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="WCO-SIGMA SIG+ACPM", layout="wide")

# --- CONFIGURACIÓN DE CONEXIONES (URLs REALES) ---
URL_COND = "https://docs.google.com/spreadsheets/d/18OIJe409rr6o_o4HSweiuncIoOrgJOXEt0GFCmEsL4g/edit"
URL_COMP = "https://docs.google.com/spreadsheets/d/1szrDZsA59e5sMF6OAzPeQ_nDX7E9lMehaXCPHmVNx5o/edit"
URL_ACPM = "TU_URL_DE_ACPM_AQUI" # <--- ASEGÚRATE DE QUE ESTA SEA LA CORRECTA

conn = st.connection("gsheets", type=GSheetsConnection)

# 2. ACCESO POR NIT
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/1063/1063302.png", width=100)
nit_user = st.sidebar.text_input("Ingrese NIT de la Empresa:", "").strip()

if not nit_user:
    st.title("🚀 WCO-SIGMA: Suite de Gestión PHVA")
    st.info("Sistemas BDI Sincronizados. Ingrese el NIT para visualizar indicadores.")
else:
    # --- MOTOR DE LECTURA ORIGINAL (EL QUE FUNCIONABA) ---
    def cargar(url):
        try:
            df = conn.read(spreadsheet=url, ttl=0)
            if df is not None and not df.empty:
                df.columns = df.columns.str.strip()
                df['Nit'] = df['Nit'].astype(str).apply(lambda x: x.split('.')[0].strip())
                return df, df[df['Nit'] == nit_user]
            return pd.DataFrame(), pd.DataFrame()
        except: return pd.DataFrame(), pd.DataFrame()

    df_cond_t, df_cond_e = cargar(URL_COND)
    df_comp_t, df_comp_e = cargar(URL_COMP)
    df_acpm_t, df_acpm_e = cargar(URL_ACPM)

    menu = st.sidebar.radio("Navegación", ["📊 Dashboard Gerencial", "⚖️ Gestión de ACPM", "🛠️ Reporte Condiciones", "🧠 Reporte Comportamiento"])

    # --- PANTALLA 1: DASHBOARD GERENCIAL ---
    if menu == "📊 Dashboard Gerencial":
        st.title(f"📊 Tablero de Control - NIT: {nit_user}")
        tab1, tab2, tab3 = st.tabs(["🔍 BDI WCO SIGMA", "🧠 BDI COMPORTAMIENTO", "⚖️ BD ACPM"])
        
        with tab1:
            if not df_cond_e.empty:
                c1, c2 = st.columns(2)
                with c1:
                    st.plotly_chart(px.bar(df_cond_e, x='Centro de trabajo', color='Prioridad', title="Hallazgos por Centro"), use_container_width=True)
                    st.plotly_chart(px.pie(df_cond_e, names='Condición Crítica', title="Condiciones Críticas", hole=0.3), use_container_width=True)
                with c2:
                    st.plotly_chart(px.bar(df_cond_e, x='Lugar', color='Estado', title="Hallazgos por Lugar"), use_container_width=True)
                    st.plotly_chart(px.pie(df_cond_e, names='Estado', title="Avance de Cierres"), use_container_width=True)
                
                st.markdown("---")
                a1, a2 = st.columns(2)
                txt_an_cond = a1.text_area("Análisis Técnico (Condiciones):", key="an_c")
                txt_pl_cond = a2.text_area("Plan de Acción (Condiciones):", key="pl_c")
            else: st.warning("Sin datos en BDI WCO SIGMA")

        with tab2:
            if not df_comp_e.empty:
                g1, g2 = st.columns(2)
                with g1: st.plotly_chart(px.bar(df_comp_e, x='Centro de trabajo', color='Estado observado', title="Cultura por Centro"), use_container_width=True)
                with g2: st.plotly_chart(px.pie(df_comp_e, names='Lugar', title="Observaciones por Lugar"), use_container_width=True)
                st.plotly_chart(px.bar(df_comp_e, x='Estado observado', title="Estatus de Comportamientos"), use_container_width=True)
                
                st.markdown("---")
                a3, a4 = st.columns(2)
                txt_an_comp = a3.text_area("Análisis de Riesgo Conductual:", key="an_h")
                txt_pl_comp = a4.text_area("Plan de Intervención Humana:", key="pl_h")
            else: st.warning("Sin datos en BDI COMPORTAMIENTO")

       with tab3:
            st.subheader("⚖️ Gestión de Mejora Continua (ACPM)")
            
            # --- BLOQUE DE DIAGNÓSTICO PARA WALTER ---
            if df_acpm_t.empty:
                st.error("❌ El sistema no logra leer el archivo. Verifica que la URL_ACPM sea correcta y que el archivo sea público o compartido con la cuenta de servicio.")
            else:
                if df_acpm_e.empty:
                    st.warning(f"⚠️ El archivo se lee, pero no hay datos para el NIT: {nit_user}")
                    with st.expander("🔍 CLIC AQUÍ PARA VER POR QUÉ NO HAY DATOS"):
                        st.write("1. Columnas detectadas en tu Excel:", list(df_acpm_t.columns))
                        st.write("2. ¿Existe la columna 'Nit'?:", "SÍ" if 'Nit' in df_acpm_t.columns else "NO (Revisa si escribiste NIT, nit, o N.I.T)")
                        if 'Nit' in df_acpm_t.columns:
                            st.write("3. Primeros 5 NITs encontrados en tu Excel:", df_acpm_t['Nit'].unique()[:5])
                else:
                    # --- SI HAY DATOS, GRAFICA NORMALMENTE ---
                    ca1, ca2 = st.columns(2)
                    with ca1:
                        st.plotly_chart(px.pie(df_acpm_e, names='Componente', title="ACPM por Sistema", hole=0.4), use_container_width=True)
                        st.plotly_chart(px.bar(df_acpm_e, x='Causa raíz', color='Estado', title="Análisis de Causa Raíz"), use_container_width=True)
                    with ca2:
                        st.plotly_chart(px.bar(df_acpm_e, x='Fuente', color='Tipo Acción', title="Fuente vs Tipo de Acción"), use_container_width=True)
                        st.plotly_chart(px.pie(df_acpm_e, names='Estado', title="Estatus de ACPM"), use_container_width=True)
                    
                    st.markdown("---")
                    txt_an_acpm = st.text_area("Evaluación de la Mejora Continua / Plan de Acción ACPM:", key="an_m_vfinal")
                    st.dataframe(df_acpm_e, use_container_width=True)

    # --- LÓGICA DE FORMULARIOS (RESTANTE) ---
    # ... (Mantenemos los formularios de ayer que funcionan perfectamente)
