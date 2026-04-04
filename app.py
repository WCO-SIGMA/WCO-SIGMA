import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.express as px
from datetime import datetime
import uuid

# 1. CONFIGURACIÓN
st.set_page_config(page_title="WCO-SIGMA SIG+PESV", layout="wide")
conn = st.connection("gsheets", type=GSheetsConnection)

# 2. ACCESO POR NIT (SOPORTE MULTIEMPRESA)
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/1063/1063302.png", width=100)
nit_input = st.sidebar.text_input("Ingrese NIT o Cédula de la Empresa:", "").strip()

if not nit_input:
    st.title("🚀 WCO-SIGMA: Sistema Integrado de Gestión")
    st.info("Sincronización Multiempresa. Ingrese el NIT para visualizar su información.")
else:
    menu = st.sidebar.radio("Módulos de Gestión", [
        "📊 Dashboard Gerencial", 
        "🛠️ Inspección de Condiciones", 
        "🧠 Comportamiento & PESV",
        "📂 Carpeta PHVA"
    ])

    # LECTURA DE DATOS
    df_total = conn.read(ttl=0)
    df_total.columns = df_total.columns.str.strip()
    df_total['Nit'] = df_total['Nit'].astype(str).str.replace('.0', '', regex=False).str.strip()
    
    # Filtro principal por NIT (Garantiza que cada cliente solo vea lo suyo)
    df_empresa = df_total[df_total['Nit'] == nit_input]

    # --- PANTALLA 1: DASHBOARD GERENCIAL RECOMPUESTO ---
    if menu == "📊 Dashboard Gerencial":
        st.title(f"📊 Dashboard Ejecutivo - NIT: {nit_input}")
        
        # Separamos los datos para que los gráficos no se mezclen
        df_condiciones = df_empresa[df_empresa['Componente'].isin(['SST', 'Ambiente', 'Vial', 'Calidad'])]
        df_comportamiento = df_empresa[df_empresa['Componente'] == 'COMPORTAMIENTO']

        if not df_condiciones.empty:
            st.subheader("🔍 Análisis de Condiciones (HSEQ)")
            c1, c2, c3 = st.columns(3)
            total_c = len(df_condiciones)
            abiertos = len(df_condiciones[df_condiciones['Estado'].astype(str).str.upper() == 'ABIERTO'])
            c1.metric("Inspecciones Condiciones", total_c)
            c2.metric("Hallazgos Pendientes", abiertos, delta_color="inverse")
            c3.metric("% Eficacia", f"{int(((total_c-abiertos)/total_c)*100)}%" if total_c > 0 else "0%")

            st.divider()
            g1, g2 = st.columns(2)
            with g1:
                fig_c = px.bar(df_condiciones['Condición Crítica'].value_counts().reset_index(), 
                             x='count', y='Condición Crítica', orientation='h', title="🎯 Top Condiciones Críticas")
                st.plotly_chart(fig_c, use_container_width=True)
            with g2:
                fig_r = px.pie(df_condiciones, names='Clasificación del riesgo', title="☣️ Riesgos GTC 45", hole=0.4)
                st.plotly_chart(fig_r, use_container_width=True)

            st.subheader("📝 Conclusiones y Plan de Acción (Auditoría)")
            st.text_area("Análisis de resultados para el Informe Gerencial:", placeholder="Escriba aquí sus observaciones...")
            st.write("### 📑 Tabla de Seguimiento de Condiciones")
            st.dataframe(df_condiciones, use_container_width=True)
        
        if not df_comportamiento.empty:
            st.divider()
            st.subheader("🧠 Análisis de Comportamiento & PESV")
            fig_comp = px.bar(df_comportamiento, x='Estado observado', color='Estado observado', title="📊 Resumen Comportamientos")
            st.plotly_chart(fig_comp, use_container_width=True)
            st.dataframe(df_comportamiento, use_container_width=True)

    # --- PANTALLA 2: INSPECCIÓN DE CONDICIONES ---
    elif menu == "🛠️ Inspección de Condiciones":
        st.title("🛠️ Registro de Condiciones HSEQ")
        with st.form("form_cond"):
            col1, col2 = st.columns(2)
            with col1:
                f_emp = st.text_input("Empresa")
                f_fec = st.date_input("Fecha", datetime.now())
                f_hall = st.text_area("Hallazgo Detallado")
                f_cond = st.selectbox("Condición Crítica", ["Orden y aseo", "Herramientas/Equipos", "Daño locativo", "Sistemas eléctricos", "Alturas/Confinados", "Ambiental", "Vial", "Otros"])
                f_riesgo = st.selectbox("Clasificación GTC 45", ["Físico", "Químico", "Biológico", "Psicosocial", "Biomecánico", "Seguridad", "Natural"])
            with col2:
                f_comp = st.selectbox("Componente SIG", ["SST", "Ambiente", "Vial", "Calidad"])
                f_resp = st.text_input("Responsable del cierre")
                f_f_p = st.date_input("Fecha propuesta cierre", datetime.now())
                f_prio = st.selectbox("Prioridad", ["Baja", "Media", "Alta"])
                f_est = st.selectbox("Estado", ["Abierto", "En Proceso", "Cerrado"])
                f_obs = st.text_area("Observación")
            
            if st.form_submit_button("✅ GUARDAR CONDICIÓN"):
                nueva_fila = pd.DataFrame([{
                    "Nit": str(nit_input), "Empresa": f_emp, "Fecha": str(f_fec), "Hallazgo": f_hall,
                    "Condición Crítica": f_cond, "Clasificación del riesgo": f_riesgo, "Componente": f_comp,
                    "Responsable del cierre": f_resp, "Fecha propuesta para el cierre": str(f_f_p),
                    "Prioridad": f_prio, "Estado": f_est, "Observación": f_obs,
                    "ID_Inspección": "N/A", "Fecha/Hora Real": str(datetime.now()), "Inspector": "N/A", "Tipo de Inspección": "N/A", "Estado observado": "N/A", "Evidencia Fotográfica": "N/A", "Observaciones Factor Humano": "N/A"
                }])
                df_upd = pd.concat([df_total, nueva_fila], ignore_index=True)
                conn.update(data=df_upd)
                st.success("Condición guardada exitosamente.")

    # --- PANTALLA 3: COMPORTAMIENTO (CAMPOS ESPECIALES) ---
    elif menu == "🧠 Comportamiento & PESV":
        st.title("🧠 Reporte de Comportamiento y Preoperacionales")
        id_auto = str(uuid.uuid4())[:8].upper()
        with st.form("form_comp"):
            col1, col2 = st.columns(2)
            with col1:
                f_inspector = st.text_input("Nombre del Inspector")
                f_tipo = st.selectbox("Tipo de Inspección", ["Comportamiento Seguro", "Preoperacional Vehículo", "Preoperacional Herramientas", "Tareas Críticas"])
                f_estado_obs = st.selectbox("Estado Observado", ["✅ SEGURO", "⚠️ ATÍPICO", "🚫 PELIGROSO"])
            with col2:
                f_foto = st.text_input("Enlace Evidencia Fotográfica")
                f_humano = st.text_area("Observaciones Factor Humano (Distracción, fatiga, EPP, confianza)")
            
            if st.form_submit_button("🚀 REGISTRAR COMPORTAMIENTO"):
                nueva_fila_c = pd.DataFrame([{
                    "Nit": str(nit_input), "Empresa": "REGISTRO COMPORTAMIENTO", "Fecha": str(datetime.now().date()), 
                    "Hallazgo": f_humano, "Condición Crítica": f_tipo, "Clasificación del riesgo": "Factor Humano",
                    "Componente": "COMPORTAMIENTO", "Responsable del cierre": "N/A", "Fecha propuesta para el cierre": "N/A",
                    "Prioridad": "N/A", "Estado": "N/A", "Observación": "N/A",
                    "ID_Inspección": id_auto, "Fecha/Hora Real": str(datetime.now()), "Inspector": f_inspector, "Tipo de Inspección": f_tipo, "Estado observado": f_estado_obs, "Evidencia Fotográfica": f_foto, "Observaciones Factor Humano": f_humano
                }])
                df_upd = pd.concat([df_total, nueva_fila_c], ignore_index=True)
                conn.update(data=df_upd)
                st.success(f"Comportamiento {id_auto} registrado con éxito.")

    elif menu == "📂 Carpeta PHVA":
        st.link_button("📁 Abrir Drive", "https://drive.google.com/drive/u/0/folders/17o_kAZMRcGhDeI3vAd0dEk_UQJGYQWBZ")
