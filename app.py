import streamlit as st
from streamlit_gsheets import GSheetsConnection

st.title("🔍 Diagnóstico de Pestañas WCO-SIGMA")
conn = st.connection("gsheets", type=GSheetsConnection)

try:
    # Intentamos leer el archivo completo para ver los nombres de las hojas
    df = conn.read()
    st.success("✅ Conexión exitosa con el archivo")
    
    # Este comando nos dirá cómo se llaman exactamente tus pestañas para la App
    # Nota: Si esto falla, intentaremos otra ruta
    st.write("### Nombres de pestañas detectadas:")
    # Intentamos forzar la lectura de metadatos si es posible
    st.info("Revisa en tu Google Sheets si los nombres tienen espacios o tildes.")
    
except Exception as e:
    st.error(f"Error de conexión: {e}")
