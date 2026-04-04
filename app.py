import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.express as px
from datetime import datetime

# 1. CONFIGURACIÓN
st.set_page_config(page_title="WCO-SIGMA HSEQ", layout="wide")
conn = st.connection("gsheets", type=GSheetsConnection)

# 2. LOGIN Y LECTURA
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/1063/1063302.png", width=100)
nit_usuario = st.sidebar.text_input("Ingrese el NIT de la Empresa (sin espacios):", "")

if not nit_usuario:
    st.title("🚀 Bienvenido a WCO-SIGMA")
    st.info("Ingrese el NIT en la barra lateral para comenzar.")
else:
    menu = st.sidebar.radio("Gestión HSEQ", ["📊 Panel de Control", "🔵 Reportar Inspección", "📂 Carpeta PHVA"])
    
    # LEER DATOS Y LIMPIAR NOMBRES DE COLUMNAS
    df_total = conn.read()
    df_total.columns = df_total.columns.str.strip() # Quita espacios invisibles
    
    # FILTRO CRÍTICO: Convertimos ambos a String para que coincidan siempre
    df_empresa = df_total[df_total['Nit'].astype(str).str.strip() == str(nit_usuario).strip()]

    # --- PANTALLA 1: PANEL DE CONTROL ---
    if menu == "📊 Panel de Control":
        st.title(f"📊 Dashboard - NIT: {nit_usuario}")
        
        if not df_empresa.empty:
            c1, c2, c3 = st.columns(3)
            total = len(df_empresa)
            abiertos = len(df_empresa[df_empresa['Estado'] == 'Abierto'])
            cumplimiento = int(((total - abiertos) / total) * 100) if total > 0 else 0
            
            c1.metric("Inspecciones", total)
            c2.metric("Pendientes", abiertos, delta_color="inverse")
            c3.metric("Cumplimiento", f"{cumplimiento}%")

            st.divider()
            g1, g2 = st.columns(2)
            with g1:
                fig_prio = px.pie(df_empresa, names='Prioridad', title="🔴 Prioridad de Hallazgos", hole=0.4)
                st.plotly_chart(fig_prio, use_container_width=True)
            with g2:
                fig_est = px.bar(df_empresa, x='Estado', color='Estado', title="🟢 Estado de Gestión")
                st.plotly_chart(fig_est, use_container_width=True)

            st.write("### 📑 Historial Completo")
            st.dataframe(df_empresa, use_container_width=True)
        else:
            st.warning(f"No hay datos para el NIT {nit_usuario}. Verifique que coincida con el Excel.")
            st.write("Datos detectados en la base (Primeras filas):", df_total[['Nit', 'Empresa']].head())

    # --- PANTALLA 2: REPORTAR INSPECCIÓN (TODAS LAS VARIABLES) ---
    elif menu == "🔵 Reportar Inspección":
        st.title("🔵 Reporte Técnico Completo")
        with st.form("form_registro"):
            col1, col2 = st.columns(2)
            with col1:
                empresa_in = st.text_input("Nombre de la Empresa")
                fecha_in = st.date_input("Fecha de Inspección", datetime.now())
                componente = st.text_input("Componente")
                f_riesgo = st.text_input("Factor de riesgo asociado")
                clasificacion = st.text_input("Clasificación")
            with col2:
                hallazgo = st.text_area("Hallazgo")
                prioridad = st.selectbox("Prioridad", ["Baja", "Media", "Alta"])
                responsable = st.text_input("Responsable del cierre")
                fecha_prop = st.date_input("Fecha propuesta cierre", datetime.now())
                estado = st.selectbox("Estado", ["Abierto", "En Proceso", "Cerrado"])
                obs = st.text_area("Observaciones")
            
            if st.form_submit_button("✅ GUARDAR"):
                # IMPORTANTE: Los nombres aquí deben ser IGUALES a los encabezados de tu Excel
                nueva_fila = pd.DataFrame([{
                    "Nit": str(nit_usuario),
                    "Empresa": empresa_in,
                    "Fecha": str(fecha_in),
                    "Hallazgo": hallazgo,
                    "Componente": componente,
                    "Factor de riesgo asociado": f_riesgo,
                    "Clasificación": clasificacion,
                    "Responsable del cierre": responsable,
                    "Fecha propuesta para el cierre": str(fecha_prop),
                    "Prioridad": prioridad,
                    "Estado": estado,
                    "Observación": obs
                }])
                try:
                    df_act = pd.concat([df_total, nueva_fila], ignore_index=True)
                    conn.update(data=df_act)
                    st.success("¡Guardado! Refresque el Panel de Control.")
                    st.balloons()
                except Exception as e:
                    st.error("Error al guardar. Revise permisos.")

    elif menu == "📂 Carpeta PHVA":
        st.title("📂 Repositorio")
        st.link_button("Abrir Drive", "https://drive.google.com/drive/u/0/folders/17o_kAZMRcGhDeI3vAd0dEk_UQJGYQWBZ")
