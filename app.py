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
