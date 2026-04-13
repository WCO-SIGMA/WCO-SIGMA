import streamlit as st
import pandas as pd
import plotly.express as px

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="WCO-SIGMA HUB", layout="wide", page_icon="🛡️")

# --- ENLACES DE LECTURA (Hojas de Respuestas) ---
URL_COND = "https://docs.google.com/spreadsheets/d/18OIJe409rr6o_o4HSweiuncIoOrgJOXEt0GFCmEsL4g/export?format=csv&gid=2138172721"
URL_COMP = "https://docs.google.com/spreadsheets/d/1szrDZsA59e5sMF6OAzPeQ_nDX7E9lMehaXCPHmVNx5o/export?format=csv&gid=980289568"
URL_ACPM = "https://docs.google.com/spreadsheets/d/1yXQNE3PiET-8VOHBWiReht7psRqjbAm5ZnY4P2XQQvg/export?format=csv&gid=1969292888"

# --- MOTOR DE LECTURA ---
@st.cache_data(ttl=30) # Se actualiza cada 30 segundos
def cargar_datos(url, nit):
    try:
        df = pd.read_csv(url)
        df.columns = df.columns.str.strip()
        # Identifica la columna de NIT/Identificación dinámicamente
        col_nit = [c for c in df.columns if 'nit' in c.lower() or 'identificación' in c.lower()][0]
        df['Nit_M'] = df[col_nit].astype(str).apply(lambda x: x.split('.')[0].strip())
        return df[df['Nit_M'] == nit]
    except:
        return pd.DataFrame()

# 2. INTERFAZ LATERAL
st.sidebar.title("🛡️ WCO-SIGMA HUB")
nit_user = st.sidebar.text_input("Ingrese NIT Empresa:", "").strip()

if not nit_user:
    st.title("🚀 WCO-SIGMA: Sistema de Gestión HSEQ")
    st.markdown("""
    ### Bienvenido.
    Ingrese el **NIT de su empresa** para acceder a:
    * 📊 Tableros de control en tiempo real.
    * 📝 Formularios de inspección y reporte.
    """)
else:
    # Carga de datos para los gráficos
    df_cond = cargar_datos(URL_COND, nit_user)
    df_comp = cargar_datos(URL_COMP, nit_user)
    df_acpm = cargar_datos(URL_ACPM, nit_user)

    menu = st.sidebar.radio("Navegación", ["📊 Dashboard Gerencial", "📝 Nuevo Reporte"])

    # --- PANTALLA DASHBOARD ---
    if menu == "📊 Dashboard Gerencial":
        st.header(f"📊 Análisis de Gestión - NIT: {nit_user}")
        tab1, tab2, tab3 = st.tabs(["🔍 BDI SIGMA", "🧠 COMPORTAMIENTO", "⚖️ ACPM"])
        
        with tab1:
            if not df_cond.empty:
                c1, c2 = st.columns(2)
                col_ct = [c for c in df_cond.columns if 'centro' in c.lower() or 'trabajo' in c.lower()][0]
                col_est = [c for c in df_cond.columns if 'estado' in c.lower()][0]
                
                c1.plotly_chart(px.bar(df_cond, x=col_ct, title="Reportes por Centro", color=col_ct), use_container_width=True)
                c2.plotly_chart(px.pie(df_cond, names=col_est, title="Estatus de Hallazgos"), use_container_width=True)
                st.dataframe(df_cond)
            else: st.warning("Sin datos históricos en BDI SIGMA.")

        with tab2:
            if not df_comp.empty:
                col_obs = [c for c in df_comp.columns if 'observado' in c.lower() or 'estado' in c.lower()][0]
                st.plotly_chart(px.bar(df_comp, x=col_obs, color=col_obs, title="Cultura de Seguridad"), use_container_width=True)
                st.dataframe(df_comp)
            else: st.warning("Sin datos en Comportamiento.")

        with tab3:
            if not df_acpm.empty:
                col_comp = [c for c in df_acpm.columns if 'componente' in c.lower()][0]
                st.plotly_chart(px.pie(df_acpm, names=col_comp, title="ACPM por Sistema"), use_container_width=True)
                st.dataframe(df_acpm)
            else: st.warning("Sin datos en Gestión ACPM.")

    # --- PANTALLA REPORTES (Usando tus links de formulario) ---
    elif menu == "📝 Nuevo Reporte":
        st.header("📝 Registro de Información en Campo")
        opcion = st.selectbox("Seleccione el reporte a realizar:", 
                             ["BDI WCO SIGMA", "BDI COMPORTAMIENTO", "BD ACPM"])
        
        # Mapeo de URLs transformadas para visualización embebida
        if opcion == "BDI WCO SIGMA":
            url_f = "https://docs.google.com/forms/d/e/1FAIpQLScy89n7_fUjNlqI6o8-R_9f7_fUjNlqI6o8-R_9f/viewform?embedded=true"
            # Como no tengo el ID público exacto, usaremos el link directo que generó tu formulario
            url_f = "https://docs.google.com/forms/d/15BeH-wHD4VJ63EARiHjTEZOUoStbk6o50zSrYmS5SQc/viewform?embedded=true"
        elif opcion == "BDI COMPORTAMIENTO":
            url_f = "https://docs.google.com/forms/d/1zysW6ybFVJ3o83KfJRSsaRbLHXSciTF_Pf2vG1nTdtA/viewform?embedded=true"
        else:
            url_f = "https://docs.google.com/forms/d/1znB96CoZfnf72USGl83h6pGH-e7XFPnMtQCqfyX0I2g/viewform?embedded=true"
        
        st.markdown(f'<iframe src="{url_f}" width="100%" height="900" frameborder="0" marginheight="0" marginwidth="0">Cargando…</iframe>', unsafe_allow_html=True)
