import streamlit as st
import pandas as pd
import plotly.express as px

# 1. CONFIGURACIÓN
st.set_page_config(page_title="WCO-SIGMA HUB", layout="wide", page_icon="🛡️")

# --- ENLACES DE LECTURA ---
URL_COND = "https://docs.google.com/spreadsheets/d/18OIJe409rr6o_o4HSweiuncIoOrgJOXEt0GFCmEsL4g/export?format=csv&gid=2138172721"
URL_COMP = "https://docs.google.com/spreadsheets/d/1szrDZsA59e5sMF6OAzPeQ_nDX7E9lMehaXCPHmVNx5o/export?format=csv&gid=980289568"
URL_ACPM = "https://docs.google.com/spreadsheets/d/1yXQNE3PiET-8VOHBWiReht7psRqjbAm5ZnY4P2XQQvg/export?format=csv&gid=1969292888"

@st.cache_data(ttl=5) # Actualización casi instantánea
def cargar_datos(url, nit):
    try:
        df = pd.read_csv(url)
        df.columns = df.columns.str.strip()
        col_nit = [c for c in df.columns if 'nit' in c.lower() or 'identificación' in c.lower()]
        if not col_nit: return pd.DataFrame()
        df['Nit_M'] = df[col_nit[0]].astype(str).apply(lambda x: x.split('.')[0].strip())
        return df[df['Nit_M'] == nit]
    except: return pd.DataFrame()

# 2. INTERFAZ
st.sidebar.title("🛡️ Panel WCO-SIGMA")
nit_user = st.sidebar.text_input("Ingrese NIT Empresa:", "").strip()

if not nit_user:
    st.title("🚀 WCO-SIGMA PRO")
    st.info("Por favor ingrese el NIT para procesar los datos de las 3 secciones.")
else:
    df_cond = cargar_datos(URL_COND, nit_user)
    
    menu = st.sidebar.radio("Navegación", ["📊 Dashboard Gerencial", "📝 Nuevo Reporte"])

    if menu == "📊 Dashboard Gerencial":
        st.header(f"📊 Análisis Seccional - NIT: {nit_user}")
        
        if not df_cond.empty:
            # --- SECCIÓN 1: IDENTIFICACIÓN ---
            st.subheader("📍 Resumen de Inspecciones por Centro")
            col_ct = [c for c in df_cond.columns if 'centro' in c.lower()]
            if col_ct:
                fig_ct = px.bar(df_cond, x=col_ct[0], title="Frecuencia de Inspecciones", color=col_ct[0])
                st.plotly_chart(fig_ct, use_container_width=True)

            # --- SECCIÓN 2: CONDICIONES CRÍTICAS (ANÁLISIS MÚLTIPLE) ---
            st.subheader("⚠️ Análisis de Riesgos Específicos")
            # Buscamos todas las columnas que mencionaste en la sección 2
            riesgos = ["Mecánico", "Alturas", "Eléctrico", "Emergencias", "Ergonómicos", "Químico", "Vial", "Ambiente"]
            
            # Creamos columnas en Streamlit para mostrar pequeños gráficos de cada riesgo detectado
            cols_viz = st.columns(3)
            idx = 0
            for r in riesgos:
                col_found = [c for c in df_cond.columns if r.lower() in c.lower()]
                if col_found:
                    with cols_viz[idx % 3]:
                        fig_r = px.pie(df_cond, names=col_found[0], title=f"Estatus: {r}", hole=0.4)
                        st.plotly_chart(fig_r, use_container_width=True)
                    idx += 1

            # --- SECCIÓN 3: PRIORIDAD ---
            st.subheader("⚖️ Nivel de Urgencia Global")
            col_pri = [c for c in df_cond.columns if 'prioridad' in c.lower()]
            if col_pri:
                fig_pri = px.funnel(df_cond, x=col_pri[0], y=col_pri[0], title="Pirámide de Prioridad de Intervención")
                st.plotly_chart(fig_pri, use_container_width=True)

            st.write("### 📄 Base de Datos Completa")
            st.dataframe(df_cond)
            
        else:
            st.warning("No hay datos para este NIT. Asegúrese de haber enviado el formulario.")

    elif menu == "📝 Nuevo Reporte":
        st.header("📝 Formulario de Inspección BDI SIGMA")
        url_f = "https://docs.google.com/forms/d/e/1FAIpQLScy89n7_fUjNlqI6o8-R_9f7_fUjNlqI6o8-R_9f/viewform?embedded=true"
        st.markdown(f'<iframe src="{url_f}" width="100%" height="1000" frameborder="0">Cargando…</iframe>', unsafe_allow_html=True)
