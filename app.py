import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.express as px
from datetime import datetime
import uuid

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="WCO-SIGMA SIG+ACPM", layout="wide")

# --- CONFIGURACIÓN DE IDENTIFICADORES ---
TITULO_COND = "BDI WCO SIGMA"
TITULO_COMP = "BDI COMPORTAMIENTO"
TITULO_ACPM = "BD ACPM" 

URL_COND = "https://docs.google.com/spreadsheets/d/18OIJe409rr6o_o4HSweiuncIoOrgJOXEt0GFCmEsL4g/edit"
URL_COMP = "https://docs.google.com/spreadsheets/d/1szrDZsA59e5sMF6OAzPeQ_nDX7E9lMehaXCPHmVNx5o/edit"
URL_ACPM = "TU_URL_DE_BD_ACPM_AQUI" 

conn = st.connection("gsheets", type=GSheetsConnection)

# 2. ACCESO POR NIT
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/1063/1063302.png", width=100)
nit_user = st.sidebar.text_input("Ingrese NIT de la Empresa:", "").strip()

if not nit_user:
    st.title("🚀 WCO-SIGMA: Gestión Integral SIG")
    st.info("Sistemas BDI Sincronizados. Ingrese el NIT para visualizar los nuevos indicadores.")
else:
    # --- MOTOR DE LECTURA ---
    def cargar_datos(url):
        try:
            df = conn.read(spreadsheet=url, ttl=0)
            if df is not None and not df.empty:
                df.columns = df.columns.str.strip()
                df['Nit'] = df['Nit'].astype(str).apply(lambda x: x.split('.')[0].strip())
                return df, df[df['Nit'] == nit_user]
            return pd.DataFrame(), pd.DataFrame()
        except: return pd.DataFrame(), pd.DataFrame()

    df_cond_total, df_cond_emp = cargar_datos(URL_COND)
    df_comp_total, df_comp_emp = cargar_datos(URL_COMP)
    df_acpm_total, df_acpm_emp = cargar_datos(URL_ACPM)

    menu = st.sidebar.radio("Navegación SIG", ["📊 Dashboard Gerencial", "⚖️ Gestión de ACPM", "🛠️ Reporte Condiciones", "🧠 Reporte Comportamiento"])

    # --- PANTALLA 1: DASHBOARD GERENCIAL (INDICADORES SOLICITADOS) ---
    if menu == "📊 Dashboard Gerencial":
        st.title(f"📊 Tablero Gerencial de Control - NIT: {nit_user}")
        tab1, tab2, tab3 = st.tabs(["🔍 Condiciones (SST/HSEQ)", "🧠 Comportamiento (PESV)", "⚖️ Mejora (ACPM)"])
        
        with tab1:
            if not df_cond_emp.empty:
                c1, c2 = st.columns(2)
                with c1:
                    st.plotly_chart(px.bar(df_cond_emp, x='Centro de trabajo', color='Prioridad', title="Hallazgos por Centro de Trabajo"), use_container_width=True)
                    st.plotly_chart(px.pie(df_cond_emp, names='Condición Crítica', title="Distribución por Condición Crítica", hole=0.4), use_container_width=True)
                with c2:
                    st.plotly_chart(px.bar(df_cond_emp, x='Lugar', color='Estado', title="Hallazgos por Lugar y Estado"), use_container_width=True)
                    st.plotly_chart(px.pie(df_cond_emp, names='Prioridad', title="Urgencia de Cierre (Prioridad)"), use_container_width=True)
            else: st.warning("Sin datos en BDI WCO SIGMA.")

        with tab2:
            if not df_comp_emp.empty:
                g1, g2 = st.columns(2)
                with g1:
                    st.plotly_chart(px.bar(df_comp_emp, x='Centro de trabajo', color='Estado observado', barmode='group', title="Desempeño por Centro de Trabajo"), use_container_width=True)
                with g2:
                    st.plotly_chart(px.pie(df_comp_emp, names='Lugar', title="Observaciones por Ubicación Física"), use_container_width=True)
                st.plotly_chart(px.bar(df_comp_emp, x='Estado observado', title="Resumen de Cultura de Seguridad"), use_container_width=True)
            else: st.warning("Sin datos en BDI COMPORTAMIENTO.")

        with tab3:
            if not df_acpm_emp.empty:
                col_a1, col_a2 = st.columns(2)
                with col_a1:
                    st.plotly_chart(px.pie(df_acpm_emp, names='Componente', title="ACPM por Componente SIG", hole=0.4), use_container_width=True)
                    st.plotly_chart(px.bar(df_acpm_emp, x='Fuente', color='Estado', title="Fuente de Hallazgos vs Estado"), use_container_width=True)
                with col_a2:
                    st.plotly_chart(px.bar(df_acpm_emp, x='Tipo Acción', color='Estado', title="Tipo de Acción Ejecutada"), use_container_width=True)
                    st.plotly_chart(px.pie(df_acpm_emp, names='Causa raíz', title="Análisis de Causa Raíz Dominante"), use_container_width=True)
            else: st.warning("Sin datos en BD ACPM.")

    # --- PANTALLA 2: REPORTE ACPM (REACTIVADO CON TODAS LAS VARIABLES) ---
    elif menu == "⚖️ Gestión de ACPM":
        st.title("⚖️ Registro Técnico de ACPM")
        with st.form("form_acpm_reactivado"):
            c1, c2 = st.columns(2)
            with c1:
                f_emp_a = st.text_input("Empresa")
                f_comp_a = st.selectbox("Componente", ["SST", "Ambiente", "Calidad", "Vial"])
                f_fuen_a = st.selectbox("Fuente", ["inspecciones", "auditorías", "incidentes", "revisión gerencial"])
                f_desc_a = st.text_area("Descripción Hallazgo")
                st.subheader("🧠 Análisis de Causa (5 Porqués)")
                p1, p2, p3, p4, p5 = st.text_input("P1"), st.text_input("P2"), st.text_input("P3"), st.text_input("P4"), st.text_input("P5")
            with c2:
                f_raiz_a = st.text_input("Causa raíz")
                f_acci_a = st.text_area("Acción Propuesta")
                f_tipo_a = st.radio("Tipo Acción", ["Correctiva", "Preventiva", "Mejora"])
                f_resp_a = st.text_input("Responsable")
                f_fec_c_a = st.date_input("Fecha Cierre Prevista")
                f_camb_a = st.radio("¿Activa gestión del cambio?", ["No", "Sí"])
                f_esta_a = st.selectbox("Estado", ["Abierta", "En Ejecución", "Cerrada"])

            if st.form_submit_button("💾 GUARDAR ACPM"):
                nueva_a = pd.DataFrame([{
                    "Nit": str(nit_user), "Empresa": f_emp_a, "Fecha de reporte": str(datetime.now().date()),
                    "Componente": f_comp_a, "Fuente": f_fuen_a, "Descripción Hallazgo": f_desc_a,
                    "Análisis Causa ¿Porqué 1?": p1, "Análisis Causa ¿Porqué 2?": p2, "Análisis Causa ¿Porqué 3?": p3, 
                    "Análisis Causa ¿Porqué 4?": p4, "Análisis Causa ¿Porqué 5?": p5, "Causa raíz": f_raiz_a,
                    "Acción Propuesta": f_acci_a, "Tipo Acción": f_tipo_a, "Responsable": f_resp_a,
                    "Fecha Cierre Prevista": str(f_fec_c_a), "Eficacia de la acción tomada": "Pendiente",
                    "La acción tomada activa gestión del cambio (Si es afirmativo IPVR, IAVI y sus controles)": f_camb_a, 
                    "Estado": f_esta_a
                }])
                df_upd_a = pd.concat([df_acpm_total, nueva_a], ignore_index=True)
                conn.update(spreadsheet=TITULO_ACPM, data=df_upd_a)
                st.success("✅ ACPM Guardada con éxito.")

    # --- PANTALLA 3: REPORTE CONDICIONES (ORDEN EXACTO SOLICITADO) ---
    elif menu == "🛠️ Reporte Condiciones":
        st.title("🛠️ Registro de Condiciones HSEQ")
        with st.form("form_cond_v11"):
            c1, c2 = st.columns(2)
            with c1:
                f_emp_c = st.text_input("Empresa")
                f_centro_c = st.text_input("Centro de trabajo")
                f_lugar_c = st.text_input("Lugar")
                f_hall_c = st.text_area("Hallazgo")
            with c2:
                f_cond_c = st.selectbox("Condición Crítica", ["Orden y aseo", "Herramientas", "Locativo", "Eléctrico", "Vial", "Otros"])
                f_ries_c = st.selectbox("Clasificación del riesgo", ["Físico", "Químico", "Biológico", "Psicosocial", "Biomecánico", "Seguridad", "Natural"])
                f_prio_c = st.selectbox("Prioridad", ["Baja", "Media", "Alta"])
                f_est_c = st.selectbox("Estado", ["Abierto", "En Proceso", "Cerrado"])
            
            if st.form_submit_button("✅ GUARDAR INSPECCIÓN"):
                nueva_c = pd.DataFrame([{
                    "Nit": str(nit_user), "Empresa": f_emp_c, "Centro de trabajo": f_centro_c, "Lugar": f_lugar_c, 
                    "Fecha": str(datetime.now().date()), "Hallazgo": f_hall_c, "Condición Crítica": f_cond_c, 
                    "Clasificación del riesgo": f_ries_c, "Componente": "SST", "Responsable del cierre": "Auditor", 
                    "Fecha propuesta para el cierre": str(datetime.now().date()), "Prioridad": f_prio_c, 
                    "Estado": f_est_c, "Observación": "Registro Ubicación"
                }])
                conn.update(spreadsheet=TITULO_COND, data=pd.concat([df_cond_total, nueva_c], ignore_index=True))
                st.success("Condición guardada.")

    # --- PANTALLA 4: REPORTE COMPORTAMIENTO ---
    elif menu == "🧠 Reporte Comportamiento":
        st.title("🧠 Observación de Comportamiento")
        with st.form("form_comp_v11"):
            c1, c2 = st.columns(2)
            with c1:
                f_ins_h = st.text_input("Inspector")
                f_centro_h = st.text_input("Centro de trabajo")
                f_lugar_h = st.text_input("Lugar")
            with c2:
                f_tipo_h = st.selectbox("Tipo de Inspección", ["Conducta Humana", "Preoperacional", "Tareas Críticas"])
                f_est_obs_h = st.selectbox("Estado observado", ["✅ SEGURO", "⚠️ ATÍPICO", "🚫 PELIGROSO"])
                f_obs_fact_h = st.text_area("Observaciones Factor Humano")
            
            if st.form_submit_button("🚀 REGISTRAR COMPORTAMIENTO"):
                nueva_h = pd.DataFrame([{
                    "Nit": str(nit_user), "ID_Inspección": str(uuid.uuid4())[:8].upper(), 
                    "Fecha/Hora Real": str(datetime.now()), "Inspector": f_ins_h, 
                    "Centro de trabajo": f_centro_h, "Lugar": f_lugar_h,
                    "Tipo de Inspección": f_tipo_h, "Estado observado": f_est_obs_h, 
                    "Evidencia Fotográfica": "N/A", "Observaciones Factor Humano": f_obs_fact_h
                }])
                conn.update(spreadsheet=TITULO_COMP, data=pd.concat([df_comp_total, nueva_h], ignore_index=True))
                st.success("Comportamiento registrado.")
