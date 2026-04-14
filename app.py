import streamlit as st
import pandas as pd
import plotly.express as px

# 1. CONFIGURACIÓN
st.set_page_config(page_title="WCO-SIGMA HUB", layout="wide", page_icon="🛡️")

# --- ENLACES DE LECTURA ---
URL_COND = "https://docs.google.com/spreadsheets/d/18OIJe409rr6o_o4HSweiuncIoOrgJOXEt0GFCmEsL4g/export?format=csv&gid=2138172721"
URL_COMP = "https://docs.google.com/spreadsheets/d/1szrDZsA59e5sMF6OAzPeQ_nDX7E9lMehaXCPHmVNx5o/export?format=csv&gid=980289568"
URL_ACPM = "https://docs.google.com/spreadsheets/d/1yXQNE3PiET-8VOHBWiReht7psRqjbAm5ZnY4P2XQQvg/export?format=csv&gid=1969292888"

# --- MOTOR DE LECTURA ROBUSTO ---
@st.cache_data(ttl=10) # Actualización rápida para pruebas
def cargar_datos(url, nit):
    try:
        df = pd.read_csv(url)
        df.columns = df.columns.str.strip()
        # Buscamos la columna de NIT/Identificación
        col_nit = [c for c in df.columns if 'nit' in c.lower() or 'identificación' in c.lower()]
        if not col_nit:
            return pd.DataFrame(), df.columns.tolist() # Retorna columnas para debug
        
        df['Nit_M'] = df[col_nit[0]].astype(str).apply(lambda x: x.split('.')[0].strip())
        return df[df['Nit_M'] == nit], df.columns.tolist()
    except Exception as e:
        return pd.DataFrame(), []

# 2. INTERFAZ
st.sidebar.title("🛡️ WCO-SIGMA HUB")
nit_user = st.sidebar.text_input("Ingrese NIT Empresa:", "").strip()

if not nit_user:
    st.title("🚀 WCO-SIGMA PRO")
    st.info("Ingrese el NIT para activar los indicadores.")
else:
    # Cargar datos
    df_cond, cols_cond = cargar_datos(URL_COND, nit_user)
    df_comp, cols_comp = cargar_datos(URL_COMP, nit_user)
    df_acpm, cols_acpm = cargar_datos(URL_ACPM, nit_user)

    menu = st.sidebar.radio("Navegación", ["📊 Dashboard Gerencial", "📝 Nuevo Reporte"])

    if menu == "📊 Dashboard Gerencial":
        st.header(f"📊 Análisis de Gestión - NIT: {nit_user}")
        t1, t2, t3 = st.tabs(["🔍 BDI SIGMA", "🧠 COMPORTAMIENTO", "⚖️ ACPM"])
        
        with t1:
            if not df_cond.empty:
                # Búsqueda segura de columnas
                c_ct = [c for c in df_cond.columns if 'centro' in c.lower()]
                c_es = [c for c in df_cond.columns if 'estado' in c.lower()]
                
                col1, col2 = st.columns(2)
                if c_ct:
                    col1.plotly_chart(px.bar(df_cond, x=c_ct[0], title="Hallazgos por Centro", color=c_ct[0]), use_container_width=True)
                if c_es:
                    col2.plotly_chart(px.pie(df_cond, names=c_es[0], title="Estatus General"), use_container_width=True)
                
                st.write("### Tabla de Datos (BDI SIGMA)")
                st.dataframe(df_cond)
            else:
                st.warning("No se encontraron registros de Condiciones para este NIT.")
                if st.checkbox("Ver nombres de columnas detectadas (BDI SIGMA)"):
                    st.write(cols_cond)

        with t2:
            if not df_comp.empty:
                c_eo = [c for c in df_comp.columns if 'observado' in c.lower() or 'estado' in c.lower()]
                if c_eo:
                    st.plotly_chart(px.bar(df_comp, x=c_eo[0], color=c_eo[0], title="Cultura de Seguridad"), use_container_width=True)
                st.dataframe(df_comp)
            else:
                st.warning("Sin datos en Comportamiento.")

        with t3:
            if not df_acpm.empty:
                c_co = [c for c in df_acpm.columns if 'componente' in c.lower()]
                if c_co:
                    st.plotly_chart(px.pie(df_acpm, names=c_co[0], title="ACPM por Sistema"), use_container_width=True)
                st.dataframe(df_acpm)
            else:
                st.warning("Sin datos en ACPM.")

    elif menu == "📝 Nuevo Reporte":
        st.header("📝 Centro de Reportes Digitales")
        opcion = st.selectbox("Seleccione reporte:", ["BDI SIGMA", "COMPORTAMIENTO", "ACPM"])
        
        # Mapeo de URLs
        urls = {
            "BDI SIGMA": "https://docs.google.com/forms/d/e/1FAIpQLSc_Tu_ID_Sigma/viewform?embedded=true",
            "COMPORTAMIENTO": "https://docs.google.com/forms/d/e/1FAIpQLSc_Tu_ID_Comp/viewform?embedded=true",
            "ACPM": "https://docs.google.com/forms/d/e/1FAIpQLSc_Tu_ID_ACPM/viewform?embedded=true"
        }
        # NOTA: Reemplaza estos links con tus links de "Insertar HTML" (< >)
        url_f = urls[opcion]
        st.markdown(f'<iframe src="{url_f}" width="100%" height="900" frameborder="0">Cargando…</iframe>', unsafe_allow_html=True)
