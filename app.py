import streamlit as st
import pandas as pd
import plotly.express as px

# Configuración de la página
st.set_page_config(page_title="WCO-SIGMA HSEQ", layout="wide")

# Inicializar datos en la sesión si no existen
if 'inspecciones' not in st.session_state:
    st.session_state.inspecciones = []

# --- BARRA LATERAL (MENÚ) ---
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/1063/1063214.png", width=100)
st.sidebar.title("Navegación SIGMA")
menu = st.sidebar.radio("Ciclo PHVA", ["🏠 Panel WCO-SIGMA", "🟢 PLANEAR", "🔵 HACER", "🟡 VERIFICAR", "🔴 ACTUAR"])

# --- CONTENIDO PRINCIPAL ---
if menu == "🏠 Panel WCO-SIGMA":
    st.title("📊 Tablero de Control HSEQ")
    col1, col2 = st.columns(2)
    
    total = len(st.session_state.inspecciones)
    col1.metric("Total Inspecciones", total)
    col2.metric("Hallazgos Pendientes", total) # Simplificado para la prueba
    
    if total > 0:
        df = pd.DataFrame(st.session_state.inspecciones)
        st.write("### Últimos Registros")
        st.table(df)
    else:
        st.info("No hay datos desplegados aún. Ve a 'HACER' para registrar uno.")

elif menu == "🔵 HACER":
    st.title("🔵 Módulo: HACER")
    st.subheader("Inspecciones de Seguridad (RUC 4.4)")
    
    with st.form("form_inspeccion"):
        hallazgo = st.text_input("Descripción del Hallazgo/Condición")
        prioridad = st.selectbox("Prioridad", ["Alta", "Media", "Baja"])
        enviar = st.form_submit_button("Reportar Condición")
        
        if enviar and hallazgo:
            st.session_state.inspecciones.append({"Hallazgo": hallazgo, "Prioridad": prioridad})
            st.success("✅ ¡Información registrada y desplegada en el Panel!")

else:
    st.title(f"{menu}")
    st.write("Sección en desarrollo para el Sistema de Gestión.")
import streamlit as st
import pandas as pd
from datetime import datetime

# --- CONFIGURACIÓN DE SEGURIDAD ---
# Walter, aquí pones el ID de tu Google Sheets
ID_SHEET = "TU_ID_AQUI" 
URL_MAESTRA = f"https://docs.google.com/spreadsheets/d/{ID_SHEET}/export?format=csv"

st.set_page_config(page_title="WCO-SIGMA Multi-Cliente", layout="wide")

# --- SISTEMA DE ACCESO ---
st.sidebar.title("🔐 Acceso Clientes")
empresa_login = st.sidebar.selectbox("Seleccione su Empresa", ["Seleccionar...", "Empresa Alfa", "Empresa Beta", "Constructora Sigma"])

if empresa_login == "Seleccionar...":
    st.title("🚀 Bienvenido a WCO-SIGMA")
    st.info("Por favor, seleccione su empresa en el menú de la izquierda para acceder a su portal HSEQ.")
else:
    st.sidebar.success(f"Conectado a: {empresa_login}")
    menu = st.sidebar.radio("Menú de Gestión", ["🏠 Mi Panel Real-Time", "🔵 Reportar Hallazgo (HACER)"])

    # Simulación de Base de Datos (Para la prueba)
    if 'db' not in st.session_state:
        st.session_state.db = pd.DataFrame(columns=['Empresa', 'Fecha', 'Hallazgo', 'Prioridad'])

    df_total = st.session_state.db
    # FILTRO DE SEGURIDAD: La empresa solo ve lo que le pertenece
    df_empresa = df_total[df_total['Empresa'] == empresa_login]

    if menu == "🏠 Mi Panel Real-Time":
        st.title(f"📊 Panel de Control - {empresa_login}")
        col1, col2 = st.columns(2)
        col1.metric("Sus Reportes", len(df_empresa))
        col2.metric("Estado del Sistema", "Activo")
        
        st.write("### Sus registros almacenados")
        st.dataframe(df_empresa, use_container_width=True)

    elif menu == "🔵 Reportar Hallazgo (HACER)":
        st.title(f"📝 Nuevo Reporte para {empresa_login}")
        with st.form("form_cliente"):
            hallazgo = st.text_input("Descripción del hallazgo")
            prio = st.selectbox("Prioridad", ["Alta", "Media", "Baja"])
            btn = st.form_submit_button("Enviar Reporte Oficial")
            
            if btn and hallazgo:
                nuevo = {
                    "Empresa": empresa_login,
                    "Fecha": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "Hallazgo": hallazgo,
                    "Prioridad": prio
                }
                st.session_state.db = pd.concat([st.session_state.db, pd.DataFrame([nuevo])], ignore_index=True)
                st.success(f"✅ Reporte guardado. Se ha notificado al administrador de {empresa_login}")
