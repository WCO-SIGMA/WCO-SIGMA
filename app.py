import streamlit as st
import streamlit as st
import pandas as pd
from datetime import datetime

# --- CONFIGURACIÓN INICIAL ---
st.set_page_config(page_title="WCO-SIGMA HSEQ Pro", layout="wide", page_icon="🛡️")

# --- ESTILOS PERSONALIZADOS (Para que se vea profesional y puedas cobrar) ---
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 2px 2px 5px rgba(0,0,0,0.1); }
    </style>
    """, unsafe_allow_html=True)

# --- SISTEMA DE NAVEGACIÓN ---
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/1063/1063214.png", width=100)
st.sidebar.title("Sistema Integrado WCO-SIGMA")
empresa = st.sidebar.selectbox("🏢 Empresa Cliente", ["Demo SIGMA", "Cliente Alfa", "Cliente Beta"])

menu = st.sidebar.radio("📋 Ciclo PHVA (RUC / ISO)", [
    "🏠 Tablero de Control", 
    "🟢 PLANEAR (Estructura)", 
    "🔵 HACER (Ejecución)", 
    "🟡 VERIFICAR (Auditoría)", 
    "🔴 ACTUAR (Mejora)"
])

# --- BASE DE DATOS TEMPORAL (Luego conectamos Google Sheets) ---
if 'registros' not in st.session_state:
    st.session_state.registros = []

# --- 🟢 MÓDULO PLANEAR (DOCUMENTACIÓN) ---
if menu == "🟢 PLANEAR (Estructura)":
    st.title("🟢 Fase: PLANEAR")
    st.info("Aquí se encuentra la base documental del Sistema de Gestión.")
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("📁 Programas y Manuales")
        # Aquí es donde pondrás los links a tus archivos de GitHub o Drive
        st.write("- [📄 Política HSEQ](https://github.com/WCO-SIGMA/WCO-SIGMA)")
        st.write("- [📄 Matriz de Riesgos y Peligros](https://github.com/WCO-SIGMA/WCO-SIGMA)")
        st.write("- [📄 Programa de Capacitación](https://github.com/WCO-SIGMA/WCO-SIGMA)")
    with col2:
        st.subheader("🎯 Objetivos del Periodo")
        st.write("1. Cumplimiento del 100% del Plan de Trabajo.")
        st.write("2. Cero Accidentes Incapacitantes.")

# --- 🔵 MÓDULO HACER (REGISTROS) ---
elif menu == "🔵 HACER (Ejecución)":
    st.title("🔵 Fase: HACER")
    st.subheader("Registro de Inspecciones y Hallazgos")
    
    with st.form("registro_hseq"):
        fecha = st.date_input("Fecha de Inspección", datetime.now())
        hallazgo = st.text_area("Descripción de la condición encontrada")
        prioridad = st.select_slider("Nivel de Riesgo", options=["Bajo", "Medio", "Alto"])
        submit = st.form_submit_button("✅ Guardar y Desplegar Información")
        
        if submit and hallazgo:
            st.session_state.registros.append({
                "Empresa": empresa,
                "Fecha": fecha,
                "Hallazgo": hallazgo,
                "Prioridad": prioridad
            })
            st.success("¡Información registrada en el Sistema!")

# --- 🏠 TABLERO DE CONTROL (VERIFICACIÓN) ---
elif menu == "🏠 Tablero de Control":
    st.title(f"📊 Despliegue de Información: {empresa}")
    
    df = pd.DataFrame(st.session_state.registros)
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Inspecciones", len(df))
    c2.metric("Hallazgos Críticos", len(df[df['Prioridad'] == 'Alto']) if not df.empty else 0)
    c3.metric("Cumplimiento", "92%")

    if not df.empty:
        st.write("### 📝 Registro Histórico de la Empresa")
        st.dataframe(df[df['Empresa'] == empresa], use_container_width=True)
    else:
        st.warning("Aún no hay datos registrados para esta empresa.")

# --- EL RESTO DE MÓDULOS (VERIFICAR Y ACTUAR) ---
else:
    st.title(menu)
    st.write("Esta sección está lista para recibir sus informes de auditoría y planes de mejora.")
