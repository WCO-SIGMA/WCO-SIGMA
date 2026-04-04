import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.express as px
from datetime import datetime

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="WCO-SIGMA SIG+PESV", layout="wide")

# 2. CONEXIÓN Y LIMPIEZA DE CACHÉ FORZADA
conn = st.connection("gsheets", type=GSheetsConnection)

# 3. ACCESO (BARRA LATERAL)
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/1063/1063302.png", width=100)
nit_input = st.sidebar.text_input("Ingrese NIT o Cédula:", "").strip()

if not nit_input:
    st.title("🚀 WCO-SIGMA: Gestión Integral")
    st.info("Ingrese su identificación para sincronizar los datos del SIG.")
else:
    menu = st.sidebar.radio("Menú Principal", ["📊 Dashboard Gerencial", "🔵 Reportar Hallazgo SIG/PESV", "📂 Carpeta PHVA"])

    # LECTURA DE DATOS (ttl=0 para evitar que muestre datos viejos)
    df_total = conn.read(ttl=0) 
    df_total.columns = df_total.columns.str.strip()
    
    # Aseguramos que el NIT sea comparado como texto limpio
    df_total['Nit'] = df_total['Nit'].astype(str).str.replace('.0', '', regex=False).str.strip()
    df_empresa = df_total[df_total['Nit'] == nit_input]

    # --- PANTALLA 1: DASHBOARD (PANEL DE CONTROL) ---
    if menu == "📊 Dashboard Gerencial":
        st.title(f"📊 Informe Gerencial SIG - ID: {nit_input}")
        
        if not df_empresa.empty:
            c1, c2, c3 = st.columns(3)
            total = len(df_empresa)
            # Contamos abiertos ignorando mayúsculas/minúsculas
            abiertos = len(df_empresa[df_empresa['Estado'].astype(str).str.contains('Abierto', case=False, na=False)])
            
            c1.metric("Hallazgos Totales", total)
            c2.metric("Pendientes", abiertos, delta_color="inverse")
            c3.metric("% Eficacia", f"{int(((total-abiertos)/total)*100)}%" if total > 0 else "0%")

            st.divider()

            g1, g2 = st.columns(2)
            with g1:
                if 'Condición Crítica' in df_empresa.columns:
                    fig_cond = px.bar(df_empresa['Condición Crítica'].value_counts().reset_index(), 
                                    x='count', y='Condición Crítica', orientation='h',
                                    title="🎯 Hallazgos por Condición", color='count')
                    st.plotly_chart(fig_cond, use_container_width=True)
            with g2:
                if 'Componente' in df_empresa.columns:
                    fig_comp = px.pie(df_empresa, names='Componente', title="📂 Distribución SIG", hole=0.4)
                    st.plotly_chart(fig_comp, use_container_width=True)

            st.subheader("📝 Análisis de Resultados")
            st.text_area("Causa Raíz y Plan de Acción:", placeholder="Escriba aquí el análisis del auditor...")

            st.write("### 📑 Tabla Actualizada de Registros")
            st.dataframe(df_empresa, use_container_width=True)
        else:
            st.warning("No se encontraron registros actualizados para este ID.")

    # --- PANTALLA 2: REPORTE (ORDEN QUIRÚRGICO DE COLUMNAS) ---
    elif menu == "🔵 Reportar Hallazgo SIG/PESV":
        st.title("🔵 Registro Técnico SIG")
        with st.form("form_sig"):
            col1, col2 = st.columns(2)
            with col1:
                f_empresa = st.text_input("Empresa")
                f_fecha = st.date_input("Fecha", datetime.now())
                f_hallazgo = st.text_area("Hallazgo Detallado")
                f_condicion = st.selectbox("Condición Crítica", [
                    "Orden y aseo", "Herramientas/Equipos en mal estado", "Daño locativo", 
                    "Sistemas eléctricos", "Alturas/Confinados", "Ambiental (Residuos/Fugas)", 
                    "Vial (PESV)", "Otros"])
                
            with col2:
                f_riesgo = st.text_input("Clasificación del riesgo")
                f_componente = st.selectbox("Componente", ["SST", "Ambiente", "Vial", "Calidad"])
                f_responsable = st.text_input("Responsable del cierre")
                f_fecha_p = st.date_input("Fecha propuesta para el cierre", datetime.now())
                f_prioridad = st.selectbox("Prioridad", ["Baja", "Media", "Alta"])
                f_estado = st.selectbox("Estado", ["Abierto", "En Proceso", "Cerrado"])
                f_obs = st.text_area("Observación")
            
            if st.form_submit_button("✅ GUARDAR Y SINCRONIZAR"):
                # ESTE MAPEO DEBE SER IDÉNTICO AL ORDEN DE TU EXCEL
                nueva_fila = pd.DataFrame([{
                    "Nit": str(nit_input),
                    "Empresa": f_empresa,
                    "Fecha": str(f_fecha),
                    "Hallazgo": f_hallazgo,
                    "Condición Crítica": f_condicion,
                    "Clasificación del riesgo": f_riesgo,
                    "Componente": f_componente,
                    "Responsable del cierre": f_responsable,
                    "Fecha propuesta para el cierre": str(f_fecha_p),
                    "Prioridad": f_prioridad,
                    "Estado": f_estado,
                    "Observación": f_obs
                }])
                
                try:
                    # Forzamos que las columnas sigan el orden del Excel antes de subir
                    columnas_excel = ["Nit", "Empresa", "Fecha", "Hallazgo", "Condición Crítica", 
                                     "Clasificación del riesgo", "Componente", "Responsable del cierre", 
                                     "Fecha propuesta para el cierre", "Prioridad", "Estado", "Observación"]
                    nueva_fila = nueva_fila[columnas_excel]
                    
                    df_actualizado = pd.concat([df_total, nueva_fila], ignore_index=True)
                    conn.update(data=df_actualizado)
                    st.success("¡Sincronización exitosa! Refresque el Dashboard.")
                    st.balloons()
                except Exception as e:
                    st.error(f"Error de mapeo: {e}")

    elif menu == "📂 Carpeta PHVA":
        st.link_button("📁 Abrir Drive", "https://drive.google.com/drive/u/0/folders/17o_kAZMRcGhDeI3vAd0dEk_UQJGYQWBZ")
