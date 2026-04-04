import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.express as px
from datetime import datetime
import uuid

# 1. CONFIGURACIÓN
st.set_page_config(page_title="WCO-SIGMA SIG+PESV", layout="wide")
conn = st.connection("gsheets", type=GSheetsConnection)

# 2. ACCESO POR NIT
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/1063/1063302.png", width=100)
nit_input = st.sidebar.text_input("Ingrese NIT o Cédula de la Empresa:", "").strip()

if not nit_input:
    st.title("🚀 WCO-SIGMA: Gestión Integral")
    st.info("Sincronización Multiempresa. Ingrese el NIT para iniciar.")
else:
    menu = st.sidebar.radio("Módulos de Gestión", [
        "📊 Dashboard Gerencial", 
        "🛠️ Inspección de Condiciones", 
        "🧠 Comportamiento & PESV",
        "📂 Carpeta PHVA"
    ])

    # --- LECTURA DE DATOS POR PESTAÑAS CON MANEJO DE ERRORES ---
    # Inicializamos variables vacías para evitar el NameError si falla la conexión
    df_cond_emp = pd.DataFrame()
    df_comp_emp = pd.DataFrame()
    df_cond_total = pd.DataFrame()
    df_comp_total = pd.DataFrame()

    try:
        # Intento de lectura de CONDICIONES
        df_cond_total = conn.read(worksheet="CONDICIONES", ttl=0)
        if not df_cond_total.empty:
            df_cond_total.columns = df_cond_total.columns.str.strip()
            df_cond_total['Nit'] = df_cond_total['Nit'].astype(str).str.replace('.0', '', regex=False).str.strip()
            df_cond_emp = df_cond_total[df_cond_total['Nit'] == nit_input]
    except Exception as e:
        st.sidebar.error("⚠️ No se encontró la pestaña 'CONDICIONES'")

    try:
        # Intento de lectura de COMPORTAMIENTO
        df_comp_total = conn.read(worksheet="COMPORTAMIENTO", ttl=0)
        if not df_comp_total.empty:
            df_comp_total.columns = df_comp_total.columns.str.strip()
            df_comp_total['Nit'] = df_comp_total['Nit'].astype(str).str.replace('.0', '', regex=False).str.strip()
            df_comp_emp = df_comp_total[df_comp_total['Nit'] == nit_input]
    except Exception as e:
        st.sidebar.error("⚠️ No se encontró la pestaña 'COMPORTAMIENTO'")

    # --- PANTALLA 1: DASHBOARD GERENCIAL ---
    if menu == "📊 Dashboard Gerencial":
        st.title(f"📊 Dashboard Ejecutivo - NIT: {nit_input}")
        
        # SECCIÓN CONDICIONES
        if not df_cond_emp.empty:
            st.subheader("🔍 Gestión de Condiciones (HSEQ)")
            c1, c2, c3 = st.columns(3)
            total_c = len(df_cond_emp)
            # Manejo de error si la columna Estado no existe o está vacía
            try:
                abiertos = len(df_cond_emp[df_cond_emp['Estado'].astype(str).str.upper() == 'ABIERTO'])
                c1.metric("Inspecciones Condiciones", total_c)
                c2.metric("Hallazgos Pendientes", abiertos, delta_color="inverse")
                c3.metric("% Eficacia", f"{int(((total_c-abiertos)/total_c)*100)}%" if total_c > 0 else "0%")
            except:
                st.write("Verifique la columna 'Estado' en la hoja CONDICIONES")

            g1, g2 = st.columns(2)
            with g1:
                if 'Condición Crítica' in df_cond_emp.columns:
                    fig_c = px.bar(df_cond_emp['Condición Crítica'].value_counts().reset_index(), 
                                 x='count', y='Condición Crítica', orientation='h', title="🎯 Top Condiciones Críticas")
                    st.plotly_chart(fig_c, use_container_width=True)
            with g2:
                if 'Clasificación del riesgo' in df_cond_emp.columns:
                    fig_r = px.pie(df_cond_emp, names='Clasificación del riesgo', title="☣️ Riesgos GTC 45", hole=0.4)
                    st.plotly_chart(fig_r, use_container_width=True)

            st.write("### 📑 Tabla de Seguimiento de Condiciones")
            st.dataframe(df_cond_emp, use_container_width=True)
        else:
            st.info("No hay datos registrados en la pestaña 'CONDICIONES' para este NIT.")
        
        # SECCIÓN COMPORTAMIENTO
        if not df_comp_emp.empty:
            st.divider()
            st.subheader("🧠 Gestión de Comportamiento & PESV")
            fig_comp = px.bar(df_comp_emp, x='Estado observado', color='Estado observado', 
                            title="📊 Resumen de Observaciones de Comportamiento")
            st.plotly_chart(fig_comp, use_container_width=True)
            st.dataframe(df_comp_emp, use_container_width=True)
        else:
            st.info("No hay datos registrados en la pestaña 'COMPORTAMIENTO' para este NIT.")

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
            
            if st.form_submit_button("✅ GUARDAR EN PESTAÑA CONDICIONES"):
                if df_cond_total is not None:
                    nueva_fila = pd.DataFrame([{
                        "Nit": str(nit_input), "Empresa": f_emp, "Fecha": str(f_fec), "Hallazgo": f_hall,
                        "Condición Crítica": f_cond, "Clasificación del riesgo": f_riesgo, "Componente": f_comp,
                        "Responsable del cierre": f_resp, "Fecha propuesta para el cierre": str(f_f_p),
                        "Prioridad": f_prio, "Estado": f_est, "Observación": f_obs
                    }])
                    df_upd = pd.concat([df_cond_total, nueva_fila], ignore_index=True)
                    conn.update(worksheet="CONDICIONES", data=df_upd)
                    st.success("Guardado en CONDICIONES. Refresque la página.")
                else:
                    st.error("Error: No se pudo conectar con la hoja de cálculo.")

    # --- PANTALLA 3: COMPORTAMIENTO ---
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
                f_humano = st.text_area("Observaciones Factor Humano")
            
            if st.form_submit_button("🚀 GUARDAR EN PESTAÑA COMPORTAMIENTO"):
                if df_comp_total is not None:
                    nueva_fila_c = pd.DataFrame([{
                        "Nit": str(nit_input), "ID_Inspección": id_auto, "Fecha/Hora Real": str(datetime.now()), 
                        "Inspector": f_inspector, "Tipo de Inspección": f_tipo, "Estado observado": f_estado_obs, 
                        "Evidencia Fotográfica": f_foto, "Observaciones Factor Humano": f_humano
                    }])
                    df_upd = pd.concat([df_comp_total, nueva_fila_c], ignore_index=True)
                    conn.update(worksheet="COMPORTAMIENTO", data=df_upd)
                    st.success(f"Guardado en COMPORTAMIENTO con ID {id_auto}.")
                else:
                    st.error("Error: No se pudo conectar con la hoja de cálculo.")

    elif menu == "📂 Carpeta PHVA":
        st.link_button("📁 Abrir Drive", "https://drive.google.com/drive/u/0/folders/17o_kAZMRcGhDeI3vAd0dEk_UQJGYQWBZ")
