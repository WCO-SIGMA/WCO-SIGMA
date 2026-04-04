import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.express as px
from datetime import datetime

# 1. CONFIGURACIÓN
st.set_page_config(page_title="WCO-SIGMA HSEQ", layout="wide")
conn = st.connection("gsheets", type=GSheetsConnection)

# 2. ACCESO (BARRA LATERAL)
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/1063/1063302.png", width=100)
nit_input = st.sidebar.text_input("Ingrese NIT o Cédula (sin puntos):", "").strip()

if not nit_input:
    st.title("🚀 Sistema de Gestión WCO-SIGMA")
    st.info("Ingrese su identificación en la barra lateral para comenzar.")
else:
    # MENÚ
    menu = st.sidebar.radio("Gestión HSEQ", ["📊 Panel de Control", "🔵 Reportar Inspección", "📂 Carpeta PHVA"])

    # LECTURA Y LIMPIEZA TOTAL
    df_total = conn.read()
    df_total.columns = df_total.columns.str.strip()
    
    # Convertimos la columna 'Nit' del Excel a texto limpio para comparar
    df_total['Nit'] = df_total['Nit'].astype(str).str.replace('.0', '', regex=False).str.strip()
    df_empresa = df_total[df_total['Nit'] == nit_input]

    # --- PANTALLA 1: PANEL DE CONTROL ---
    if menu == "📊 Panel de Control":
        st.title(f"📊 Dashboard - ID: {nit_input}")
        
        if not df_empresa.empty:
            c1, c2, c3 = st.columns(3)
            total = len(df_empresa)
            abiertos = len(df_empresa[df_empresa['Estado'].str.contains('Abierto', case=False, na=False)])
            
            c1.metric("Inspecciones", total)
            c2.metric("Pendientes", abiertos, delta_color="inverse")
            c3.metric("Cumplimiento", f"{int(((total-abiertos)/total)*100)}%" if total > 0 else "0%")

            st.divider()
            g1, g2 = st.columns(2)
            with g1:
                fig_prio = px.pie(df_empresa, names='Prioridad', title="🔴 Prioridad", hole=0.4)
                st.plotly_chart(fig_prio, use_container_width=True)
            with g2:
                fig_est = px.bar(df_empresa, x='Estado', color='Estado', title="🟢 Estados")
                st.plotly_chart(fig_est, use_container_width=True)

            st.write("### 📑 Historial de Reportes")
            st.dataframe(df_empresa, use_container_width=True)
        else:
            st.warning(f"No se encontraron datos para {nit_input}.")
            # Ayuda visual para el auditor (Walter)
            st.write("IDs encontrados en Excel para verificar:", df_total['Nit'].unique()[:5])

    # --- PANTALLA 2: REPORTAR INSPECCIÓN (CON LISTAS DESPLEGABLES) ---
    elif menu == "🔵 Reportar Inspección":
        st.title("🔵 Nuevo Reporte de Inspección")
        with st.form("form_bdi"):
            col1, col2 = st.columns(2)
            with col1:
                empresa = st.text_input("Nombre de la Empresa")
                fecha = st.date_input("Fecha", datetime.now())
                componente = st.text_input("Componente (Área/Proceso)")
                
                # LISTA DESPLEGABLE: FACTOR DE RIESGO
                f_riesgo = st.selectbox("Factor de Riesgo", [
                    "Físico", "Químico", "Biológico", "Biomecánico", 
                    "Psicosocial", "Condiciones de Seguridad", "Fenómenos Naturales"
                ])
                
                # LISTA DESPLEGABLE: CLASIFICACIÓN
                clasificacion = st.selectbox("Clasificación", [
                    "Ruido", "Iluminación", "Vibración", "Temperaturas", "Radiaciones",
                    "Polvos", "Líquidos", "Gases", "Virus/Bacterias", "Postura", 
                    "Esfuerzo", "Manipulación de cargas", "Mecánico", "Eléctrico",
                    "Locativo", "Tecnológico", "Accidentes de tránsito", "Público"
                ])
                
            with col2:
                hallazgo = st.text_area("Hallazgo Detectado")
                prioridad = st.selectbox("Prioridad", ["Baja", "Media", "Alta"])
                responsable = st.text_input("Responsable del cierre")
                fecha_prop = st.date_input("Fecha propuesta cierre", datetime.now())
                estado = st.selectbox("Estado", ["Abierto", "En Proceso", "Cerrado"])
                obs = st.text_area("Observaciones")
            
            if st.form_submit_button("✅ GUARDAR"):
                nueva_fila = pd.DataFrame([{
                    "Nit": str(nit_input), "Empresa": empresa, "Fecha": str(fecha),
                    "Hallazgo": hallazgo, "Componente": componente, 
                    "Factor de riesgo asociado": f_riesgo, "Clasificación": clasificacion,
                    "Responsable del cierre": responsable, "Fecha propuesta para el cierre": str(fecha_prop),
                    "Prioridad": prioridad, "Estado": estado, "Observación": obs
                }])
                try:
                    df_total = pd.concat([df_total, nueva_fila], ignore_index=True)
                    conn.update(data=df_total)
                    st.success("¡Registro guardado!")
                    st.balloons()
                except Exception as e:
                    st.error(f"Error al guardar: {e}")

    elif menu == "📂 Carpeta PHVA":
        st.link_button("📁 Abrir Drive", "https://drive.google.com/drive/u/0/folders/17o_kAZMRcGhDeI3vAd0dEk_UQJGYQWBZ")
