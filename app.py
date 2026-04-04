import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.express as px
from datetime import datetime

# 1. CONFIGURACIÓN DE LA PÁGINA
st.set_page_config(page_title="WCO-SIGMA HSEQ", layout="wide")

# 2. CONEXIÓN A GOOGLE SHEETS
conn = st.connection("gsheets", type=GSheetsConnection)

# 3. BARRA LATERAL (LOGIN Y MENÚ)
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/1063/1063302.png", width=100)
st.sidebar.title("Configuración")
nit_usuario = st.sidebar.text_input("Ingrese el NIT de la Empresa:", "")

if not nit_usuario:
    st.title("🚀 Bienvenido a WCO-SIGMA")
    st.info("Por favor, ingrese el NIT en la barra lateral para acceder al sistema.")
else:
    # MENÚ DE NAVEGACIÓN
    menu = st.sidebar.radio("Gestión HSEQ", ["📊 Panel de Control", "🔵 Reportar Inspección", "📂 Carpeta PHVA"])

    # LECTURA DE DATOS DESDE EXCEL
    df_total = conn.read()
    # Limpiamos nombres de columnas (quita espacios invisibles)
    df_total.columns = df_total.columns.str.strip()
    
    # FILTRO POR NIT (Asegura que coincidan como texto)
    df_empresa = df_total[df_total['Nit'].astype(str).str.strip() == str(nit_usuario).strip()]

    # --- PANTALLA 1: PANEL DE CONTROL ---
    if menu == "📊 Panel de Control":
        st.title(f"📊 Dashboard Ejecutivo - NIT: {nit_usuario}")
        
        if not df_empresa.empty:
            # MÉTRICAS CLAVE
            c1, c2, c3 = st.columns(3)
            total = len(df_empresa)
            abiertos = len(df_empresa[df_empresa['Estado'] == 'Abierto'])
            cumplimiento = int(((total - abiertos) / total) * 100) if total > 0 else 0
            
            c1.metric("Inspecciones Realizadas", total)
            c2.metric("Hallazgos Pendientes", abiertos, delta_color="inverse")
            c3.metric("Cumplimiento General", f"{cumplimiento}%")

            st.divider()

            # GRÁFICOS
            col_g1, col_g2 = st.columns(2)
            with col_g1:
                fig_prio = px.pie(df_empresa, names='Prioridad', title="🔴 Prioridad de Riesgos", hole=0.4,
                                 color_discrete_sequence=px.colors.qualitative.Pastel)
                st.plotly_chart(fig_prio, use_container_width=True)
            
            with col_g2:
                fig_est = px.bar(df_empresa, x='Estado', color='Estado', title="🟢 Estado de la Gestión",
                                color_discrete_map={'Abierto':'#EF553B', 'En Proceso':'#FECB52', 'Cerrado':'#00CC96'})
                st.plotly_chart(fig_est, use_container_width=True)

            st.write("### 📑 Tabla de Datos Completa")
            # Mostramos la tabla filtrada con todas las columnas
            st.dataframe(df_empresa, use_container_width=True)
        else:
            st.warning(f"No se encontraron datos para el NIT {nit_usuario}.")
            st.info("Asegúrese de que el NIT en el Excel coincida exactamente con el que ingresó.")

    # --- PANTALLA 2: REPORTAR INSPECCIÓN ---
    elif menu == "🔵 Reportar Inspección":
        st.title("🔵 Nuevo Reporte de Inspección")
        with st.form("form_inspeccion"):
            c_a, c_b = st.columns(2)
            with c_a:
                f_empresa = st.text_input("Empresa")
                f_fecha = st.date_input("Fecha de Inspección", datetime.now())
                f_componente = st.text_input("Componente")
                f_hallazgo = st.text_area("Hallazgo")
                f_riesgo = st.text_input("Factor de riesgo asociado")
                f_clasifica = st.text_input("Clasificación")
            with c_b:
                f_responsable = st.text_input("Responsable del cierre")
                f_fecha_p = st.date_input("Fecha propuesta para el cierre", datetime.now())
                f_prioridad = st.selectbox("Prioridad", ["Baja", "Media", "Alta"])
                f_estado = st.selectbox("Estado", ["Abierto", "En Proceso", "Cerrado"])
                f_obs = st.text_area("Observación")
            
            enviar = st.form_submit_button("✅ GUARDAR REGISTRO")
            
            if enviar and f_hallazgo:
                # CREAR NUEVA FILA (Nombres exactos del Excel)
                nueva_data = pd.DataFrame([{
                    "Nit": str(nit_usuario),
                    "Empresa": f_empresa,
                    "Fecha": str(f_fecha),
                    "Hallazgo": f_hallazgo,
                    "Componente": f_componente,
                    "Factor de riesgo asociado": f_riesgo,
                    "Clasificación": f_clasifica,
                    "Responsable del cierre": f_responsable,
                    "Fecha propuesta para el cierre": str(f_fecha_p),
                    "Prioridad": f_prioridad,
                    "Estado": f_estado,
                    "Observación": f_obs
                }])
                
                try:
                    df_update = pd.concat([df_total, nueva_data], ignore_index=True)
                    conn.update(data=df_update)
                    st.success("¡Registro guardado exitosamente!")
                    st.balloons()
                except Exception as e:
                    st.error(f"Error al guardar: {e}")

    # --- PANTALLA 3: CARPETA PHVA ---
    elif menu == "📂 Carpeta PHVA":
        st.title("📂 Repositorio Documental")
        st.write("Acceda a la documentación del Sistema de Gestión:")
        st.link_button("📁 Abrir Carpeta PHVA en Drive", "https://drive.google.com/drive/u/0/folders/17o_kAZMRcGhDeI3vAd0dEk_UQJGYQWBZ")
