import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.express as px
from datetime import datetime

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="WCO-SIGMA HSEQ", layout="wide")

# 2. CONEXIÓN A GOOGLE SHEETS
conn = st.connection("gsheets", type=GSheetsConnection)

# 3. ACCESO POR NIT (BARRA LATERAL)
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/1063/1063302.png", width=100)
st.sidebar.title("Acceso Clientes")
nit_usuario = st.sidebar.text_input("Ingrese NIT o Cédula:", "")

if not nit_usuario:
    st.title("🚀 Sistema de Gestión WCO-SIGMA")
    st.info("Por favor, ingrese su identificación en el panel izquierdo para visualizar sus indicadores y reportes.")
else:
    # MENÚ DE NAVEGACIÓN
    menu = st.sidebar.radio("Gestión HSEQ", ["📊 Panel de Control", "🔵 Reportar Inspección", "📂 Carpeta PHVA"])

    # LECTURA DE DATOS (Forzamos limpieza de encabezados)
    try:
        df_total = conn.read()
        df_total.columns = df_total.columns.str.strip() # Limpia espacios en los nombres de columnas
        
        # FILTRO DE SEGURIDAD (Convertimos a texto para comparar)
        df_empresa = df_total[df_total['Nit'].astype(str).str.strip() == str(nit_usuario).strip()]
    except Exception as e:
        st.error(f"Error leyendo la base de datos: {e}")
        df_empresa = pd.DataFrame()

    # --- PANTALLA 1: PANEL DE CONTROL ---
    if menu == "📊 Panel de Control":
        st.title(f"📊 Dashboard Ejecutivo - ID: {nit_usuario}")
        
        if not df_empresa.empty:
            # MÉTRICAS PRINCIPALES
            c1, c2, c3 = st.columns(3)
            total_insp = len(df_empresa)
            # Buscamos la columna 'Estado' sin importar si está en mayúscula o minúscula
            abiertos = len(df_empresa[df_empresa['Estado'].str.contains('Abierto', case=False, na=False)])
            cumplimiento = int(((total_insp - abiertos) / total_insp) * 100) if total_insp > 0 else 0
            
            c1.metric("Inspecciones Totales", total_insp)
            c2.metric("Hallazgos Pendientes", abiertos, delta_color="inverse")
            c3.metric("Nivel de Cumplimiento", f"{cumplimiento}%")

            st.divider()

            # GRÁFICOS INTERACTIVOS
            g1, g2 = st.columns(2)
            with g1:
                if 'Prioridad' in df_empresa.columns:
                    fig_prio = px.pie(df_empresa, names='Prioridad', title="🔴 Gravedad de Hallazgos", hole=0.4)
                    st.plotly_chart(fig_prio, use_container_width=True)
            with g2:
                if 'Estado' in df_empresa.columns:
                    fig_est = px.bar(df_empresa, x='Estado', color='Estado', title="🟢 Avance de Gestión",
                                   color_discrete_map={'Abierto':'#EF553B', 'Cerrado':'#00CC96'})
                    st.plotly_chart(fig_est, use_container_width=True)

            st.write("### 📑 Historial de Inspecciones Registradas")
            st.dataframe(df_empresa, use_container_width=True)
        else:
            st.warning(f"No se encontraron registros para el NIT/Cédula: {nit_usuario}")
            st.info("Asegúrese de que el número ingresado coincida exactamente con el registrado en el Excel.")

    # --- PANTALLA 2: REPORTAR INSPECCIÓN ---
    elif menu == "🔵 Reportar Inspección":
        st.title("🔵 Registro de Inspección Técnica")
        with st.form("form_bdi"):
            col1, col2 = st.columns(2)
            with col1:
                empresa = st.text_input("Nombre de la Empresa")
                fecha = st.date_input("Fecha de Inspección", datetime.now())
                componente = st.text_input("Componente")
                f_riesgo = st.text_input("Factor de riesgo asociado")
                clasificacion = st.text_input("Clasificación")
                hallazgo = st.text_area("Hallazgo Detectado")
            with col2:
                prioridad = st.selectbox("Prioridad", ["Baja", "Media", "Alta"])
                responsable = st.text_input("Responsable del cierre")
                fecha_prop = st.date_input("Fecha propuesta cierre", datetime.now())
                estado = st.selectbox("Estado", ["Abierto", "En Proceso", "Cerrado"])
                obs = st.text_area("Observaciones Adicionales")
            
            if st.form_submit_button("✅ GUARDAR EN BASE DE DATOS"):
                nueva_fila = pd.DataFrame([{
                    "Nit": str(nit_usuario), "Empresa": empresa, "Fecha": str(fecha),
                    "Hallazgo": hallazgo, "Componente": componente, 
                    "Factor de riesgo asociado": f_riesgo, "Clasificación": clasificacion,
                    "Responsable del cierre": responsable, "Fecha propuesta para el cierre": str(fecha_prop),
                    "Prioridad": prioridad, "Estado": estado, "Observación": obs
                }])
                try:
                    df_actualizado = pd.concat([df_total, nueva_fila], ignore_index=True)
                    conn.update(data=df_actualizado)
                    st.success("¡Registro guardado exitosamente en BDI WCO SIGMA!")
                    st.balloons()
                except Exception as e:
                    st.error("Error al conectar con Google Sheets. Verifique permisos.")

    # --- PANTALLA 3: CARPETA PHVA ---
    elif menu == "📂 Carpeta PHVA":
        st.title("📂 Repositorio Documental PHVA")
        st.write("Seleccione el botón para acceder a las carpetas de gestión en la nube:")
        st.link_button("📁 Abrir Google Drive", "https://drive.google.com/drive/u/0/folders/17o_kAZMRcGhDeI3vAd0dEk_UQJGYQWBZ")
