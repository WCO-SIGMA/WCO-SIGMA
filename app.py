import streamlit as st
import pandas as pd
import plotly.express as px

# 1. CONFIGURACIÓN
st.set_page_config(page_title="WCO-SIGMA HUB", layout="wide", page_icon="🛡️")

# --- ENLACES DE LECTURA ---
URL_COND = "https://docs.google.com/spreadsheets/d/18OIJe409rr6o_o4HSweiuncIoOrgJOXEt0GFCmEsL4g/export?format=csv&gid=2138172721"
URL_COMP = "https://docs.google.com/spreadsheets/d/1szrDZsA59e5sMF6OAzPeQ_nDX7E9lMehaXCPHmVNx5o/export?format=csv&gid=980289568"
URL_ACPM = "https://docs.google.com/spreadsheets/d/1yXQNE3PiET-8VOHBWiReht7psRqjbAm5ZnY4P2XQQvg/export?format=csv&gid=1969292888"

@st.cache_data(ttl=10)
def cargar_datos(url, nit):
    try:
        df = pd.read_csv(url)
        df.columns = df.columns.str.strip()
        # Buscar columna de NIT de forma flexible
        col_nit = [c for c in df.columns if 'nit' in c.lower() or 'identificación' in c.lower()]
        if not col_nit: return pd.DataFrame()
        
        df['Nit_M'] = df[col_nit[0]].astype(str).apply(lambda x: x.split('.')[0].strip())
        return df[df['Nit_M'] == nit]
    except: return pd.DataFrame()

# 2. INTERFAZ
nit_user = st.sidebar.text_input("Ingrese NIT Empresa:", "").strip()

if not nit_user:
    st.title("🚀 WCO-SIGMA PRO")
    st.info("Ingrese el NIT para visualizar sus tableros.")
else:
    df_cond = cargar_datos(URL_COND, nit_user)
    df_comp = cargar_datos(URL_COMP, nit_user)
    df_acpm = cargar_datos(URL_ACPM, nit_user)

    menu = st.sidebar.radio("Menú", ["📊 Dashboard", "📝 Reportes"])

    if menu == "📊 Dashboard":
        st.header(f"📊 Control Gerencial - NIT: {nit_user}")
        t1, t2, t3 = st.tabs(["🔍 BDI SIGMA", "🧠 COMPORTAMIENTO", "⚖️ ACPM"])
        
        with t1: # BDI SIGMA
            if not df_cond.empty:
                # Intentamos graficar solo lo que existe
                cols = df_cond.columns.tolist()
                c1, c2 = st.columns(2)
                
                # Gráfico 1: Centro de Trabajo
                ct = [c for c in cols if 'centro' in c.lower()]
                if ct: c1.plotly_chart(px.bar(df_cond, x=ct[0], title="Hallazgos por Centro", color=ct[0]), use_container_width=True)
                
                # Gráfico 2: Prioridad o Riesgo
                pr = [c for c in cols if 'prioridad' in c.lower() or 'riesgo' in c.lower()]
                if pr: c2.plotly_chart(px.pie(df_cond, names=pr[0], title="Distribución Crítica"), use_container_width=True)
                
                st.dataframe(df_cond)
            else: st.warning("No hay datos en BDI SIGMA.")

        with t2: # COMPORTAMIENTO
            if not df_comp.empty:
                eo = [c for c in df_comp.columns if 'observado' in c.lower() or 'estado' in c.lower()]
                if eo: st.plotly_chart(px.bar(df_comp, x=eo[0], color=eo[0], title="Cultura de Seguridad"), use_container_width=True)
                st.dataframe(df_comp)
            else: st.warning("No hay datos en Comportamiento.")

        with t3: # ACPM
            if not df_acpm.empty:
                cp = [c for c in df_acpm.columns if 'componente' in c.lower()]
                if cp: st.plotly_chart(px.pie(df_acpm, names=cp[0], title="ACPM por Componente"), use_container_width=True)
                st.dataframe(df_acpm)
            else: st.warning("No hay datos en ACPM.")

    elif menu == "📝 Reportes":
        st.header("📝 Registro de Inspección")
        # Aquí van tus enlaces reales de "Insertar HTML"
        st.info("Seleccione el módulo desde el formulario de Google abajo.")
        # Reemplaza con tu link de BDI SIGMA (el de < >)
        url_f = "https://docs.google.com/forms/d/e/15BeH-wHD4VJ63EARiHjTEZOUoStbk6o50zSrYmS5SQc/viewform?embedded=true"
        st.markdown(f'<iframe src="{url_f}" width="100%" height="800" frameborder="0">Cargando…</iframe>', unsafe_allow_html=True)
