import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.express as px
from datetime import datetime
import uuid

# 1. CONFIGURACIÓN DE LA PLATAFORMA
st.set_page_config(page_title="WCO-SIGMA SIG+ACPM", layout="wide")

# --- CONFIGURACIÓN DE IDs (VERIFICA QUE SEAN LOS CORRECTOS) ---
ID_COND = "18OIJe409rr6o_o4HSweiuncIoOrgJOXEt0GFCmEsL4g"
ID_COMP = "1szrDZsA59e5sMF6OAzPeQ_nDX7E9lMehaXCPHmVNx5o"
ID_ACPM = "TU_ID_DE_BD_ACPM_AQUI" 

conn = st.connection("gsheets", type=GSheetsConnection)

# 2. ACCESO MULTIEMPRESA POR NIT
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/1063/1063302.png", width=100)
nit_input = st.sidebar.text_input("Ingrese identificación (NIT/Cédula):", "").strip()

if not nit_input:
    st.title("🚀 WCO-SIGMA: Sistema de Gestión Integrado")
    st.success("✅ Conexión con Bases de Datos Establecida.")
    st.info("Por favor, ingrese el NIT de la empresa para desplegar su información exclusiva.")
else:
    # --- MOTOR DE LECTURA ---
    def cargar_datos(sheet_id):
        try:
            df = conn.read(spreadsheet=sheet_id, ttl=0)
            if df is not None and not df.empty:
                df.columns = df.columns.str.strip()
                df['Nit'] = df['Nit'].astype(str).str.replace('.0', '', regex=False).str.strip()
                return df, df[df['Nit'] == nit_input]
            return pd.DataFrame(), pd.DataFrame()
        except: return pd.DataFrame(), pd.DataFrame()

    # Carga de datos filtrados por NIT
    df_cond_total, df_cond_emp = cargar_datos(ID_COND)
    df_comp_total, df_comp_emp = cargar_datos(ID_COMP)
    df_acpm_total, df_acpm_emp = cargar_datos(ID_ACPM)

    menu = st.sidebar.radio("Menú Principal", ["📊 Dashboard SIG", "⚖️ Gestión de ACPM", "🛠️ Reporte Condiciones", "🧠 Reporte Comportamiento"])

    # --- MÓDULO 1: DASHBOARD ---
    if menu == "📊 Dashboard SIG":
        st.title(f"📊 Tablero de Control Gerencial - NIT: {nit_input}")
        tab1, tab2, tab3 = st.tabs(["🔍 Hallazgos de Condiciones", "🧠 Análisis Conductual", "⚖️ Mejora Continua (ACPM)"])
        
        with tab1:
            if not df_cond_emp.empty:
                col_c1, col_c2 = st.columns(2)
                with col_c1: st.plotly_chart(px.pie(df_cond_emp, names='Estado', title="Estatus de Condiciones"), use_container_width=True)
                with col_c2: st.plotly_chart(px.bar(df_cond_emp, x='Prioridad', color='Prioridad', title="Prioridad de Cierre"), use_container_width=True)
                st.dataframe(df_cond_emp, use_container_width=True)
            else: st.warning("No hay datos de condiciones para este NIT.")

        with tab2:
            if not df_comp_emp.empty:
                st.plotly_chart(px.bar(df_comp_emp, x='Estado observado', color='Estado observado', title="Riesgo por Comportamiento"), use_container_width=True)
                st.dataframe(df_comp_emp, use_container_width=True)
            else: st.warning("No hay datos de comportamiento para este NIT.")

        with tab3:
            if not df_acpm_emp.empty:
                col_a1, col_a2 = st.columns(2)
                with col_a1: st.plotly_chart(px.pie(df_acpm_emp, names='Componente', title="ACPM por Componente (SST/Vial/etc)"), use_container_width=True)
                with col_a2: st.plotly_chart(px.bar(df_acpm_emp, x='Estado', color='Estado', title="Estado de Planes de Acción"), use_container_width=True)
                st.dataframe(df_acpm_emp, use_container_width=True)
            else: st.warning("No hay acciones (ACPM) registradas aún.")

    # --- MÓDULO 2: GESTIÓN DE ACPM (REFORZADO) ---
    elif menu == "⚖️ Gestión de ACPM":
        st.title("⚖️ Reporte de Acciones Correctivas, Preventivas y de Mejora")
        with st.form("form_acpm_completo"):
            st.subheader("1. Identificación del Hallazgo")
            c1, c2 = st.columns(2)
            with c1:
                f_emp = st.text_input("Nombre de la Empresa / Sede")
                f_comp = st.selectbox("Componente Relacionado", ["SST", "Ambiente", "Calidad", "Vial"])
                f_fuente = st.selectbox("Fuente del Hallazgo", ["inspecciones", "investigación de incidentes", "auditorías internas y externas", "observación de tareas", "reportes de actos y condiciones", "Legislación o normatividad", "Revisión gerencial"])
            with c2:
                f_fec_r = st.date_input("Fecha de reporte", datetime.now())
                f_desc = st.text_area("Descripción detallada del Hallazgo")

            st.markdown("---")
            st.subheader("2. Análisis de Causa Raíz (Metodología 5 Porqués)")
            p1 = st.text_input("¿Por qué 1? (Causa inmediata)")
            p2 = st.text_input("¿Por qué 2?")
            p3 = st.text_input("¿Por qué 3?")
            p4 = st.text_input("¿Por qué 4?")
            p5 = st.text_input("¿Por qué 5? (Causa Raíz)")
            f_raiz = st.text_area("Conclusión de Causa Raíz")

            st.markdown("---")
            st.subheader("3. Plan de Acción y Gestión del Cambio")
            c3, c4 = st.columns(2)
            with c3:
                f_accion = st.text_area("Acción Propuesta (¿Qué se va a hacer?)")
                f_tipo = st.radio("Tipo de Acción", ["Correctiva", "Preventiva", "Mejora"])
                f_resp = st.text_input("Responsable del Cierre")
            with c4:
                f_fec_p = st.date_input("Fecha Cierre Prevista")
                f_cambio = st.radio("¿La acción tomada activa gestión del cambio? (Si es afirmativo IPVR, IAVI y sus controles)", ["No", "Sí"])
                f_estado = st.selectbox("Estado Inicial", ["Abierta", "En Ejecución"])

            if st.form_submit_button("💾 REGISTRAR Y CENTRALIZAR ACPM"):
                nueva_acpm = pd.DataFrame([{
                    "Nit": str(nit_input), "Empresa": f_emp, "Fecha de reporte": str(f_fec_r),
                    "Componente": f_comp, "Fuente": f_fuente, "Descripción Hallazgo": f_desc,
                    "Análisis Causa ¿Porqué 1?": p1, "Análisis Causa ¿Porqué 2?": p2,
                    "Análisis Causa ¿Porqué 3?": p3, "Análisis Causa ¿Porqué 4?": p4,
                    "Análisis Causa ¿Porqué 5?": p5, "Causa raíz": f_raiz,
                    "Acción Propuesta": f_accion, "Tipo Acción": f_tipo, "Responsable": f_resp,
                    "Fecha Cierre Prevista": str(f_fec_p), "Eficacia de la acción tomada": "Pendiente",
                    "La acción tomada activa gestión del cambio (Si es afirmativo IPVR, IAVI y sus controles)": f_cambio, 
                    "Estado": f_estado
                }])
                try:
                    df_upd = pd.concat([df_acpm_total, nueva_acpm], ignore_index=True)
                    conn.client.open_by_key(ID_ACPM).sheet1.update([df_upd.columns.values.tolist()] + df_upd.values.tolist())
                    st.success("ACPM registrada exitosamente.")
                    st.balloons()
                except: st.error("Error al guardar. Verifique permisos.")

    # --- MÓDULO 3: REPORTE CONDICIONES (REACTIVADO) ---
    elif menu == "🛠️ Reporte Condiciones":
        st.title("🛠️ Inspección de Condiciones de Seguridad")
        with st.form("form_cond_vfull"):
            col1, col2 = st.columns(2)
            with col1:
                f_emp_c = st.text_input("Empresa/Sede")
                f_hall_c = st.text_area("Descripción del Hallazgo")
                f_cat_c = st.selectbox("Condición Crítica", ["Orden y aseo", "Herramientas/Equipos", "Daño locativo", "Sistemas eléctricos", "Ambiental", "Vial", "Otros"])
            with col2:
                f_gtc = st.selectbox("Clasificación Riesgo (GTC 45)", ["Físico", "Químico", "Biológico", "Psicosocial", "Biomecánico", "Seguridad", "Natural"])
                f_prio = st.selectbox("Prioridad", ["Baja", "Media", "Alta"])
                f_est = st.selectbox("Estado", ["Abierto", "En Proceso", "Cerrado"])
            
            if st.form_submit_button("✅ REGISTRAR CONDICIÓN"):
                nueva_cond = pd.DataFrame([{
                    "Nit": str(nit_input), "Empresa": f_emp_c, "Fecha": str(datetime.now().date()), 
                    "Hallazgo": f_hall_c, "Condición Crítica": f_cat_c, "Clasificación del riesgo": f_gtc, 
                    "Componente": "SST", "Responsable del cierre": "Asignado", 
                    "Fecha propuesta para el cierre": str(datetime.now().date()), 
                    "Prioridad": f_prio, "Estado": f_est, "Observación": "Reporte inicial"
                }])
                try:
                    df_u = pd.concat([df_cond_total, nueva_cond], ignore_index=True)
                    conn.client.open_by_key(ID_COND).sheet1.update([df_u.columns.values.tolist()] + df_u.values.tolist())
                    st.success("Condición guardada en BDI.")
                except: st.error("Error de conexión.")

    # --- MÓDULO 4: REPORTE COMPORTAMIENTO (REACTIVADO) ---
    elif menu == "🧠 Reporte Comportamiento":
        st.title("🧠 Observación de Comportamiento y PESV")
        with st.form("form_comp_vfull"):
            c1, c2 = st.columns(2)
            with c1:
                f_ins = st.text_input("Nombre del Observador")
                f_tipo = st.selectbox("Tipo de Inspección", ["Conducta Humana", "Preoperacional PESV", "Tareas Críticas"])
                f_obs_est = st.selectbox("Estado Observado", ["✅ SEGURO", "⚠️ ATÍPICO", "🚫 PELIGROSO"])
            with c2:
                f_factores = st.multiselect("Factores Humanos Detectados", ["Distracción", "Fatiga", "Exceso de confianza", "Prisa", "Desconocimiento"])
                f_detalles = st.text_area("Observaciones detalladas")
            
            if st.form_submit_button("🚀 REGISTRAR COMPORTAMIENTO"):
                nueva_comp = pd.DataFrame([{
                    "Nit": str(nit_input), "ID_Inspección": str(uuid.uuid4())[:8].upper(), 
                    "Fecha/Hora Real": str(datetime.now()), "Inspector": f_ins, 
                    "Tipo de Inspección": f_tipo, "Estado observado": f_obs_est, 
                    "Evidencia Fotográfica": "N/A", "Observaciones Factor Humano": ", ".join(f_factores) + " | " + f_detalles
                }])
                try:
                    df_u = pd.concat([df_comp_total, nueva_comp], ignore_index=True)
                    conn.client.open_by_key(ID_COMP).sheet1.update([df_u.columns.values.tolist()] + df_u.values.tolist())
                    st.success("Observación registrada en BDI.")
                except: st.error("Error de conexión.")
