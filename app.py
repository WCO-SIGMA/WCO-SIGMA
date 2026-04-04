import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.express as px
from datetime import datetime

# CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="WCO-SIGMA HSEQ", layout="wide")

# CONEXIÓN A GOOGLE SHEETS
conn = st.connection("gsheets", type=GSheetsConnection)

# LOGIN SIMPLE POR NIT
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/1063/1063302.png", width=100)
nit_usuario = st.sidebar.text_input("Ingrese el NIT de la Empresa:", "")

if not nit_usuario:
    st.title("🚀 Bienvenido a WCO-SIGMA")
    st.info("Por favor, ingrese el NIT en la barra lateral para acceder a su gestión HSEQ.")
else:
    # NAVEGACIÓN
    menu = st.sidebar.radio("Gestión HSEQ", ["📊 Panel de Control", "🔵 Reportar Inspección", "📂 Carpeta PHVA"])

    # LECTURA DE DATOS
    df_total = conn.read()
    df_total.columns = df_total.columns.str.strip()
    
    # FILTRO POR EMPRESA
    df_empresa = df_total[df_total['Nit'].astype(str) == str(nit_usuario)]

    # --- PANTALLA 1: PANEL DE CONTROL ---
    if menu == "📊 Panel de Control":
        st.title(f"📊 Dashboard Ejecutivo - NIT: {nit_usuario}")
        
        if not df_empresa.empty:
            # MÉTRICAS SUPERIORES
            c1, c2, c3 = st.columns(3)
            total = len(df_empresa)
            abiertos = len(df_empresa[df_empresa['Estado'] == 'Abierto'])
            cumplimiento = int(((total - abiertos) / total) * 100) if total > 0 else 0
            
            c1.metric("Inspecciones Totales", total)
            c2.metric("Pendientes (Abiertos)", abiertos, delta_color="inverse")
            c3.metric("Nivel de Cumplimiento", f"{cumplimiento}%")

            st.divider()

            # GRÁFICOS INTERACTIVOS
            g1, g2 = st.columns(2)
            with g1:
                fig_prio = px.pie(df_empresa, names='Prioridad', title="🔴 Gravedad de Hallazgos", hole=0.4)
                st.plotly_chart(fig_prio, use_container_width=True)
            with g2:
                fig_est = px.bar(df_empresa, x='Estado', color='Estado', title="🟢 Avance de Gestión")
                st.plotly_chart(fig_est, use_container_width=True)

            st.write("### 📑 Historial de Inspecciones")
            st.dataframe(df_empresa, use_container_width=True)
        else:
            st.warning("No se encontraron registros para este NIT. Inicie un reporte en el menú lateral.")

    # --- PANTALLA 2: REPORTAR INSPECCIÓN ---
    elif menu == "🔵 Reportar Inspección":
        st.title("🔵 Nuevo Reporte Técnico")
        with st.form("form_registro"):
            col1, col2 = st.columns(2)
            with col1:
                empresa = st.text_input("Nombre de la Empresa")
                fecha = st.date_input("Fecha", datetime.now())
                componente = st.text_input("Componente")
                hallazgo = st.text_area("Hallazgo detectado")
            with col2:
                prioridad = st.selectbox("Prioridad", ["Baja", "Media", "Alta"])
                estado = st.selectbox("Estado", ["Abierto", "En Proceso", "Cerrado"])
                responsable = st.text_input("Responsable")
                obs = st.text_area("Observaciones")
            
            submit = st.form_submit_button("✅ GUARDAR EN BASE DE DATOS")
            
            if submit and hallazgo:
                nueva_fila = pd.DataFrame([{
                    "Nit": str(nit_usuario), "Empresa": empresa, "Fecha": str(fecha),
                    "Hallazgo": hallazgo, "Componente": componente, "Prioridad": prioridad,
                    "Estado": estado, "Responsable del cierre": responsable, "Observación": obs
                }])
                try:
                    df_actualizado = pd.concat([df_total, nueva_fila], ignore_index=True)
                    conn.update(data=df_actualizado)
                    st.success("¡Registro guardado exitosamente!")
                    st.balloons()
                except Exception as e:
                    st.error("Error de permisos en Google Sheets. Verifique sus Secrets.")

    # --- PANTALLA 3: CARPETA PHVA ---
    elif menu == "📂 Carpeta PHVA":
        st.title("📂 Repositorio Documental")
        st.link_button("Abrir Carpeta en Google Drive", "https://drive.google.com/drive/u/0/folders/17o_kAZMRcGhDeI3vAd0dEk_UQJGYQWBZ")
