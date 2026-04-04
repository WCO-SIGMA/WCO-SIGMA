import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="WCO-SIGMA Pro", layout="wide", page_icon="🛡️")
conn = st.connection("gsheets", type=GSheetsConnection)

# --- LOGIN POR NIT ---
st.sidebar.title("🔐 Acceso Clientes")
nit_usuario = st.sidebar.text_input("Ingrese NIT (sin puntos)", "")

if not nit_usuario:
    st.title("🚀 WCO-SIGMA HSEQ")
    st.info("Ingrese su NIT para gestionar sus inspecciones.")
else:
    menu = st.sidebar.radio("Menú", ["📊 Panel de Control", "🔵 Reportar Inspección", "📂 Carpeta PHVA"])

    # LEER DATOS REALES
    # LEER DATOS REALES Y LIMPIAR TÍTULOS
    df_total = conn.read()
    
    # Esta línea borra espacios invisibles en los títulos
    df_total.columns = df_total.columns.str.strip() 
    
    # Filtramos usando el nombre exacto que pusiste
    # Si pusiste 'Nit' con N mayúscula, esto lo encontrará
    try:
        df_empresa = df_total[df_total['Nit'].astype(str) == str(nit_usuario)]
    except KeyError:
        st.error("⚠️ Error de Estructura: No encontré la columna 'Nit' en tu Excel.")
        st.write("Columnas detectadas en tu archivo:", list(df_total.columns))
        st.stop()
    df_empresa = df_total[df_total['Nit'].astype(str) == str(nit_usuario)]

    if menu == "📊 Panel de Control":
        st.title(f"📊 Gestión de Hallazgos - NIT {nit_usuario}")
        st.metric("Total Registros", len(df_empresa))
        st.dataframe(df_empresa, use_container_width=True)
    elif menu == "🔵 Reportar Inspección":
        st.title("🔵 Nuevo Reporte Técnico de Inspección")
    elif menu == "🔵 Reportar Inspección":
        st.title("🔵 Nuevo Reporte Técnico de Inspección")
        with st.form("registro_detallado"):  # <--- AQUÍ EMPIEZA EL FORMULARIO
            col1, col2 = st.columns(2)
            with col1:
                # MIRA AQUÍ: Asegúrate de que el nombre sea 'empresa_entrada'
                empresa_entrada = st.text_input("Nombre de la Empresa")
                with col2:
                prioridad = st.selectbox("Prioridad", ["Baja", "Media", "Alta"])
                responsable = st.text_input("Responsable del cierre")
                fecha_prop = st.date_input("Fecha propuesta para el cierre")
                estado = st.selectbox("Estado", ["Abierto", "En Proceso", "Cerrado"])
                observacion = st.text_area("Observación adicional")
            btn = st.form_submit_button("✅ GUARDAR EN BASE DE DATOS")
    if btn and hallazgo:
                # Crear la nueva fila con tu estructura exacta
                nueva_fila = pd.DataFrame([{
                    "Nit": str(nit_usuario),
                    "Empresa": empresa_login,
                    "Fecha": str(fecha_insp),
                    "Hallazgo": hallazgo,
                    "Componente": componente,
                    "Factor de riesgo asociado": f_riesgo,
                    "Clasificación": clasificacion,
                    "Responsable del cierre": responsable,
                    "Fecha propuesta para el cierre": str(fecha_prop),
                    "Prioridad": prioridad,
                    "Estado": estado,
                    "Observación": observacion
                }])
                
                # Sincronización con Google Sheets
                df_actualizado = pd.concat([df_total, nueva_fila], ignore_index=True)
                conn.update(data=df_actualizado)
                st.success("✅ ¡Registro guardado exitosamente en la BD Maestra!")
