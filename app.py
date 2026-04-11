import streamlit as st
import pandas as pd
import plotly.express as px

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="WCO-SIGMA HUB", layout="wide")

# --- CONEXIONES DE LECTURA (Pestañas de Formulario) ---
# Usamos el formato export?format=csv&gid=ID para leer la pestaña exacta de respuestas
URL_COND = "https://docs.google.com/spreadsheets/d/18OIJe409rr6o_o4HSweiuncIoOrgJOXEt0GFCmEsL4g/export?format=csv&gid=2138172721"
URL_COMP = "https://docs.google.com/spreadsheets/d/1szrDZsA59e5sMF6OAzPeQ_nDX7E9lMehaXCPHmVNx5o/export?format=csv&gid=980289568"
URL_ACPM = "https://docs.google.com/spreadsheets/d/1yXQNE3PiET-8VOHBWiReht7psRqjbAm5ZnY4P2XQQvg/export?format=csv&gid=1969292888"

# --- LINKS DE FORMULARIOS PARA EMBEBER ---
# Se cambia /edit por /viewform?embedded=true
FORM_COND = "https://docs.google.com/forms/d/e/1FAIpQLSc9V1N877n6v4W98XkM6n2k-3y1n3v-0x1u-r0-s0-t0-u0/viewform?embedded=true" # Nota: Reemplaza con el link de "Enviar" -> "< >"
FORM_COMP = "https://docs.google.com/forms/d/1zysW6ybFVJ3o83KfJRSsaRbLHXSciTF_Pf2vG1nTdtA/viewform?embedded=true"
FORM_ACPM = "https://docs.google.com/forms/d/1znB96CoZfnf72USGl83h6pGH-e7XFPnMtQCqfyX0I2g/viewform?embedded=true"

# --- MOTOR DE LECTURA ---
def cargar_datos(url, nit):
    try:
        # Limpieza de caché para ver datos nuevos
        df = pd.read_csv(url)
        df.columns = df.columns.str.strip()
        # Buscamos la columna NIT (Google Forms suele ponerla según la pregunta)
        col_nit = [c for c in df.columns if 'nit' in c.lower() or 'identificación' in c.lower()][0]
        df['Nit_M'] = df[col_nit].astype(str).apply(lambda x: x.split('.')[0].strip())
        return df[df['Nit_M'] == nit]
    except:
        return pd.DataFrame()

# 2. INTERFAZ LATERAL
st.sidebar.title("🛡️ WCO-SIGMA HUB")
nit_user = st.sidebar.text_input("Ingrese NIT para Consultar:", "").strip()

if not nit_user:
    st.title("🚀 WCO-SIGMA: Gestión HSEQ Pro")
    st.info("Bienvenido. Ingrese el NIT de la empresa para visualizar indicadores y realizar reportes.")
else:
    # Cargar datos filtrados
    df_cond = cargar_datos(URL_COND, nit_user)
    df_comp = cargar_datos(URL_COMP, nit_user)
    df_acpm = cargar_datos(URL_ACPM, nit_user)

    menu = st.sidebar.radio("Menú Principal", ["📊 Dashboard Gerencial", "📝 Realizar Nuevo Reporte"])

    if menu == "📊 Dashboard Gerencial":
        st.header(f"📊 Análisis de Indicadores - NIT: {nit_user}")
        tab1, tab2, tab3 = st.tabs(["🔍 BDI SIGMA", "🧠 COMPORTAMIENTO", "⚖️ ACPM"])
        
        with tab1:
            if not df_cond.empty:
                # Nota: Los nombres de columnas deben coincidir con las preguntas del formulario
                c1, c2 = st.columns(2)
                # Intentamos detectar columnas dinámicamente
                col_ct = [c for c in df_cond.columns if 'centro' in c.lower()][0]
                col_est = [c for c in df_cond.columns if 'estado' in c.lower()][0]
                
                c1.plotly_chart(px.bar(df_cond, x=col_ct, title="Hallazgos por Centro"), use_container_width=True)
                c2.plotly_chart(px.pie(df_cond, names=col_est, title="Estatus de Hallazgos"), use_container_width=True)
                st.dataframe(df_cond)
            else: st.warning("No se encontraron registros previos para este NIT en BDI SIGMA.")

        with tab2:
            if not df_comp.empty:
                col_obs = [c for c in df_comp.columns if 'observado' in c.lower()][0]
                st.plotly_chart(px.bar(df_comp, x=col_obs, color=col_obs, title="Cultura de Seguridad"), use_container_width=True)
                st.dataframe(df_comp)

        with tab3:
            if not df_acpm.empty:
                col_comp = [c for c in df_acpm.columns if 'componente' in c.lower()][0]
                st.plotly_chart(px.pie(df_acpm, names=col_comp, title="ACPM por Sistema"), use_container_width=True)
                st.dataframe(df_acpm)

    elif menu == "📝 Realizar Nuevo Reporte":
        st.header("📝 Centro de Reportes en Tiempo Real")
        opcion = st.selectbox("Seleccione el formulario:", 
                             ["Reporte BDI WCO SIGMA", "Reporte BDI COMPORTAMIENTO", "Reporte BD ACPM"])
        
        # Mapeo de URLs
        if opcion == "Reporte BDI WCO SIGMA": url_form = "https://docs.google.com/forms/d/e/1FAIpQLSdO7u00HovvK8vJ0zO0WvSgI7U_Xv9vP6Qp-U5yW1FwYy_zYw/viewform?embedded=true"
        elif opcion == "Reporte BDI COMPORTAMIENTO": url_form = "https://docs.google.com/forms/d/e/1FAIpQLSe-Xo5vB6pYv3FjR0C2y0iI_n9f3zYvL_n6pX6tY5w_zYw/viewform?embedded=true"
        else: url_form = "https://docs.google.com/forms/d/e/1FAIpQLSdX-vY4vP-m5vXzO0G6P9zV4t0v-vS_XzU-o6yS6tY5w_zYw/viewform?embedded=true"
        
        # Ajuste: Debes usar el link que sale en Google Forms -> ENVIAR -> icono "< >" (Insertar HTML)
        # Aquí pongo un ejemplo genérico, por favor reemplaza con tus links de "Insertar HTML"
        st.markdown(f'<iframe src="{url_form}" width="100%" height="1000" frameborder="0" marginheight="0" marginwidth="0">Cargando…</iframe>', unsafe_allow_html=True)
