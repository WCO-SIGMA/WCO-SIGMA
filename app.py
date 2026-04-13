import streamlit as st
import pandas as pd
import plotly.express as px

# 1. CONFIGURACIÓN DE PÁGINA (Debe ser la primera instrucción)
st.set_page_config(page_title="WCO-SIGMA HUB", layout="wide", page_icon="🛡️")

# --- CONEXIONES DE LECTURA (Pestañas de Respuestas de Formulario) ---
# Estas URLs apuntan directamente a la pestaña donde caen los datos de los formularios
URL_COND = "https://docs.google.com/spreadsheets/d/18OIJe409rr6o_o4HSweiuncIoOrgJOXEt0GFCmEsL4g/export?format=csv&gid=2138172721"
URL_COMP = "https://docs.google.com/spreadsheets/d/1szrDZsA59e5sMF6OAzPeQ_nDX7E9lMehaXCPHmVNx5o/export?format=csv&gid=980289568"
URL_ACPM = "https://docs.google.com/spreadsheets/d/1yXQNE3PiET-8VOHBWiReht7psRqjbAm5ZnY4P2XQQvg/export?format=csv&gid=1969292888"

# --- MOTOR DE LECTURA DE DATOS ---
@st.cache_data(ttl=60) # Actualiza los datos cada minuto
def cargar_datos(url, nit):
    try:
        df = pd.read_csv(url)
        df.columns = df.columns.str.strip()
        # Buscamos la columna que contenga "nit" o "identificación" ignorando mayúsculas
        col_nit = [c for c in df.columns if 'nit' in c.lower() or 'identificación' in c.lower()][0]
        df['Nit_M'] = df[col_nit].astype(str).apply(lambda x: x.split('.')[0].strip())
        return df[df['Nit_M'] == nit]
    except Exception as e:
        return pd.DataFrame()

# 2. INTERFAZ LATERAL (Sidebar)
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/1063/1063302.png", width=100)
st.sidebar.title("Panel de Control")
nit_user = st.sidebar.text_input("Ingrese NIT Empresa:", "").strip()

if not nit_user:
    st.title("🚀 WCO-SIGMA: Gestión HSEQ Pro")
    st.markdown("""
    ### Bienvenido al Sistema Integral de Gestión.
    Por favor, ingrese el **NIT de su empresa** en la barra lateral para:
    * 📊 Visualizar indicadores en tiempo real.
    * 📝 Realizar nuevos reportes de inspección.
    * ⚖️ Gestionar acciones correctivas (ACPM).
    """)
    st.info("Nota: Los datos se actualizan automáticamente al recibir nuevas respuestas de los formularios.")
else:
    # Intentar cargar datos para los gráficos
    df_cond = cargar_datos(URL_COND, nit_user)
    df_comp = cargar_datos(URL_COMP, nit_user)
    df_acpm = cargar_datos(URL_ACPM, nit_user)

    menu = st.sidebar.radio("Navegación", ["📊 Dashboard Gerencial", "📝 Realizar Nuevo Reporte"])

    # --- PANTALLA: DASHBOARD ---
    if menu == "📊 Dashboard Gerencial":
        st.header(f"📊 Análisis de Indicadores - NIT: {nit_user}")
        tab1, tab2, tab3 = st.tabs(["🔍 BDI SIGMA", "🧠 COMPORTAMIENTO", "⚖️ ACPM"])
        
        with tab1:
            st.subheader("Inspecciones de Actos y Condiciones")
            if not df_cond.empty:
                c1, c2 = st.columns(2)
                # Detección dinámica de columnas para evitar errores de nombres
                col_ct = [c for c in df_cond.columns if 'centro' in c.lower() or 'trabajo' in c.lower()][0]
                col_est = [c for c in df_cond.columns if 'estado' in c.lower()][0]
                
                with c1:
                    fig1 = px.bar(df_cond, x=col_ct, title="Hallazgos por Centro de Trabajo", color=col_ct)
                    st.plotly_chart(fig1, use_container_width=True)
                with c2:
                    fig2 = px.pie(df_cond, names=col_est, title="Distribución por Estado")
                    st.plotly_chart(fig2, use_container_width=True)
                
                st.write("### Detalle de Registros")
                st.dataframe(df_cond)
            else:
                st.warning("No se encontraron registros en BDI SIGMA para este NIT.")

        with tab2:
            st.subheader("Observaciones de Comportamiento")
            if not df_comp.empty:
                col_obs = [c for c in df_comp.columns if 'observado' in c.lower() or 'estado' in c.lower()][0]
                fig3 = px.bar(df_comp, x=col_obs, color=col_obs, title="Tendencia de Comportamientos")
                st.plotly_chart(fig3, use_container_width=True)
                st.dataframe(df_comp)
            else:
                st.warning("No hay datos registrados en Comportamiento.")

        with tab3:
            st.subheader("Gestión de Acciones (ACPM)")
            if not df_acpm.empty:
                col_comp = [c for c in df_acpm.columns if 'componente' in c.lower()][0]
                fig4 = px.pie(df_acpm, names=col_comp, title="ACPM por Sistema de Gestión")
                st.plotly_chart(fig4, use_container_width=True)
                st.dataframe(df_acpm)
            else:
                st.warning("No hay datos registrados en ACPM.")

    # --- PANTALLA: REPORTES (GOOGLE FORMS) ---
    elif menu == "📝 Realizar Nuevo Reporte":
        st.header("📝 Centro de Reportes Digitales")
        st.write("Complete el formulario correspondiente. Los datos se verán reflejados en el Dashboard al instante.")
        
        opcion = st.selectbox("Seleccione el tipo de reporte:", 
                             ["Reporte BDI WCO SIGMA", "Reporte BDI COMPORTAMIENTO", "Reporte BD ACPM"])
        
        # --- MAPEO DE ENLACES (IMPORTANTE: USAR LINKS DE < > INSERTAR HTML) ---
        if opcion == "Reporte BDI WCO SIGMA":
            url_form = "https://docs.google.com/forms/d/e/1FAIpQLSdO7u00HovvK8vJ0zO0WvSgI7U_Xv9vP6Qp-U5yW1FwYy_zYw/viewform?embedded=true"
        elif opcion == "Reporte BDI COMPORTAMIENTO":
            url_form = "https://docs.google.com/forms/d/e/1FAIpQLSe-Xo5vB6pYv3FjR0C2y0iI_n9f3zYvL_n6pX6tY5w_zYw/viewform?embedded=true"
        else:
            url_form = "https://docs.google.com/forms/d/e/1FAIpQLSdX-vY4vP-m5vXzO0G6P9zV4t0v-vS_XzU-o6yS6tY5w_zYw/viewform?embedded=true"
        
        # Mostrar el formulario embebido
        st.markdown(f"""
            <div style="text-align: center;">
                <iframe src="{url_form}" width="100%" height="900" frameborder="0" marginheight="0" marginwidth="0">Cargando…</iframe>
            </div>
            """, unsafe_allow_html=True)
