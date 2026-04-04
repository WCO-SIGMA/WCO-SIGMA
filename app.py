import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.express as px
from datetime import datetime
import uuid

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="WCO-SIGMA SIG+ACPM", layout="wide")

# --- CONFIGURACIÓN DE IDENTIFICADORES ---
# Nombres exactos de los archivos en tu Google Drive (PARA GUARDAR)
TITULO_COND = "BDI WCO SIGMA"
TITULO_COMP = "BDI COMPORTAMIENTO"
TITULO_ACPM = "BD ACPM" 

# URLs completas (PARA LEER/DASHBOARD)
URL_COND = "https://docs.google.com/spreadsheets/d/18OIJe409rr6o_o4HSweiuncIoOrgJOXEt0GFCmEsL4g/edit"
URL_COMP = "https://docs.google.com/spreadsheets/d/1szrDZsA59e5sMF6OAzPeQ_nDX7E9lMehaXCPHmVNx5o/edit"
# ⚠️ ASEGÚRATE DE QUE ESTA URL SEA LA DE TU BD ACPM
URL_ACPM = "PEGA_AQUI_TU_URL_DE_BD_ACPM" 

conn = st.connection("gsheets", type=GSheetsConnection)

# 2. ACCESO POR NIT
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/1063/1063302.png", width=100)
nit_user = st.sidebar.text_input("Ingrese NIT de la Empresa:", "").strip()

if not nit_user:
    st.title("🚀 WCO-SIGMA: Gestión Integrada PHVA")
    st.info("Sistema conectado. Ingrese el NIT para visualizar indicadores y reportar.")
else:
    # --- MOTOR DE LECTURA (DASHBOARD) ---
    def cargar_datos(url):
        try:
            df = conn.read(spreadsheet=url, ttl=0)
            if df is not None and not df.empty:
                df.columns = df.columns.str.strip()
                # Limpieza de NIT para evitar errores de punto decimal
                df['Nit'] = df['Nit'].astype(str).apply(lambda x: x.split('.')[0].strip())
                return df, df[df['Nit'] == nit_user]
            return pd.DataFrame(), pd.DataFrame()
        except:
            return pd.DataFrame(), pd.DataFrame()

    df_cond_total, df_cond_emp = cargar_datos(URL_COND)
    df_comp_total, df_comp_emp = cargar_datos(URL_COMP)
    df_acpm_total, df_acpm_emp = cargar_datos(URL_ACPM)

    menu = st.sidebar.radio("Navegación", ["📊 Dashboard SIG", "⚖️ Gestión de ACPM", "🛠️ Reporte Condiciones", "🧠 Reporte Comportamiento"])

    # --- PANTALLA: DASHBOARD ---
    if menu == "📊 Dashboard SIG":
        st.title(f"📊 Tablero Ejecutivo - NIT: {nit_user}")
        tab1, tab2, tab3 = st.tabs(["🔍 Condiciones", "🧠 Comportamiento", "⚖️ Mejora (ACPM)"])
        
        with tab1:
            if not df_cond_emp.empty:
                c1, c2 = st.columns(2)
                with c1: st.plotly_chart(px.pie(df_cond_emp, names='Estado', title="Estado Condiciones", hole=0.4), use_container_width=True)
                with c2: st.plotly_chart(px.bar(df_cond_emp, x='Prioridad', color='Prioridad', title="Urgencia de Cierre"), use_container_width=True)
                st.dataframe(df_cond_emp, use_container_width=True)
            else: st.warning("Sin datos de inspecciones para este NIT.")

        with tab2:
            if not df_comp_emp.empty:
                st.plotly_chart(px.bar(df_comp_emp, x='Estado observado', color='Estado observado', title="Análisis Conductual"), use_container_width=True)
                st.dataframe(df_comp_emp, use_container_width=True)
            else: st.warning("Sin datos de comportamiento.")

        with tab3:
            if not df_acpm_emp.empty:
                ca1, ca2 = st.columns(2)
                with ca1: st.plotly_chart(px.pie(df_acpm_emp, names='Componente', title="ACPM por SIG"), use_container_width=True)
                with ca2: st.plotly_chart(px.bar(df_acpm_emp, x='Estado', color='Estado', title="Avance de Tareas"), use_container_width=True)
                st.dataframe(df_acpm_emp, use_container_width=True)
            else: st.warning("No hay registros de mejora (ACPM).")

    # --- PANTALLA: GESTIÓN DE ACPM (RESTAURADA) ---
    elif menu == "⚖️ Gestión de ACPM":
        st.title("⚖️ Reporte de Acciones Correctivas (ACPM)")
        with st.form("form_acpm_vfull"):
            col1, col2 = st.columns(2)
            with col1:
                f_emp = st.text_input("Empresa/Sede")
                f_comp = st.selectbox("Componente", ["SST", "Ambiente", "Calidad", "Vial"])
                f_fuen = st.selectbox("Fuente", ["inspecciones", "investigación de incidentes", "auditorías internas y externas", "observación de tareas", "reportes de actos y condiciones", "Legislación o normatividad", "Revisión gerencial"])
                f_desc = st.text_area("Descripción Hallazgo")
                st.subheader("Análisis 5 Porqués")
                p1, p2, p3, p4, p5 = st.text_input("P1"), st.text_input("P2"), st.text_input("P3"), st.text_input("P4"), st.text_input("P5")
            with col2:
                f_raiz = st.text_input("Causa Raíz")
                f_acci = st.text_area("Plan de Acción Propuesto")
                f_tipo = st.radio("Tipo de Acción", ["Correctiva", "Preventiva", "Mejora"])
                f_resp = st.text_input("Responsable de Ejecución")
                f_fec_c = st.date_input("Fecha Cierre Prevista")
                # VARIABLE GESTIÓN DEL CAMBIO ACTIVADA
                f_camb = st.radio("¿La acción activa gestión del cambio? (IPVR, IAVI y controles)", ["No", "Sí"])
                f_esta = st.selectbox("Estado Actual", ["Abierta", "En Ejecución"])

            if st.form_submit_button("💾 GUARDAR EN BD ACPM"):
                nueva_acpm = pd.DataFrame([{
                    "Nit": str(nit_user), "Empresa": f_emp, "Fecha de reporte": str(datetime.now().date()),
                    "Componente": f_comp, "Fuente": f_fuen, "Descripción Hallazgo": f_desc,
                    "Análisis Causa ¿Porqué 1?": p1, "Análisis Causa ¿Porqué 2?": p2,
                    "Análisis Causa ¿Porqué 3?": p3, "Análisis Causa ¿Porqué 4?": p4,
                    "Análisis Causa ¿Porqué 5?": p5, "Causa raíz": f_raiz,
                    "Acción Propuesta": f_acci, "Tipo Acción": f_tipo, "Responsable": f_resp,
                    "Fecha Cierre Prevista": str(f_fec_c), "Eficacia de la acción tomada": "Pendiente",
                    "La acción tomada activa gestión del cambio (Si es afirmativo IPVR, IAVI y sus controles)": f_camb, 
                    "Estado": f_esta
                }])
                # GUARDADO USANDO EL TÍTULO DEL ARCHIVO
                df_upd = pd.concat([df_acpm_total, nueva_acpm], ignore_index=True)
                conn.update(spreadsheet=TITULO_ACPM, data=df_upd)
                st.success("✅ ¡Acción Correctiva Registrada con Éxito!")
                st.balloons()

    # --- OTROS REPORTES (RESTAURADOS) ---
    elif menu == "🛠️ Reporte Condiciones":
        st.title("🛠️ Registro de Condiciones HSEQ")
        with st.form("f_cond"):
            c1, c2 = st.columns(2)
            with c1:
                f_h = st.text_area("Hallazgo")
                f_cat = st.selectbox("Categoría", ["Orden y aseo", "Vial", "SST", "Otros"])
            with c2:
                f_prio = st.selectbox("Prioridad", ["Baja", "Media", "Alta"])
                f_est_c = st.selectbox("Estado", ["Abierto", "En Proceso", "Cerrado"])
            if st.form_submit_button("✅ GUARDAR CONDICIÓN"):
                nueva_c = pd.DataFrame([{"Nit": str(nit_user), "Empresa": "Sede Principal", "Fecha": str(datetime.now().date()), "Hallazgo": f_h, "Condición Crítica": f_cat, "Clasificación del riesgo": "Seguridad", "Componente": "SST", "Responsable del cierre": "Auditor", "Fecha propuesta para el cierre": str(datetime.now().date()), "Prioridad": f_prio, "Estado": f_est_c, "Observación": "Registro inicial"}])
                conn.update(spreadsheet=TITULO_COND, data=pd.concat([df_cond_total, nueva_c], ignore_index=True))
                st.success("Guardado en BDI WCO SIGMA.")

    elif menu == "🧠 Reporte Comportamiento":
        st.title("🧠 Registro de Comportamiento y PESV")
        with st.form("f_comp"):
            f_ins = st.text_input("Inspector")
            f_o = st.text_area("Detalle de la conducta observada")
            f_res = st.selectbox("Resultado", ["✅ SEGURO", "⚠️ ATÍPICO", "🚫 PELIGROSO"])
            if st.form_submit_button("🚀 REGISTRAR EN BDI COMPORTAMIENTO"):
                nueva_comp = pd.DataFrame([{"Nit": str(nit_user), "ID_Inspección": str(uuid.uuid4())[:8].upper(), "Fecha/Hora Real": str(datetime.now()), "Inspector": f_ins, "Tipo de Inspección": "Conducta", "Estado observado": f_res, "Evidencia Fotográfica": "N/A", "Observaciones Factor Humano": f_o}])
                conn.update(spreadsheet=TITULO_COMP, data=pd.concat([df_comp_total, nueva_comp], ignore_index=True))
                st.success("Reporte de Comportamiento Registrado.")
