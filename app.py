import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.express as px
from datetime import datetime
import uuid
from fpdf import FPDF

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="WCO-SIGMA SIG+ACPM", layout="wide")

# --- CONFIGURACIÓN DE CONEXIONES ---
URL_COND = "https://docs.google.com/spreadsheets/d/18OIJe409rr6o_o4HSweiuncIoOrgJOXEt0GFCmEsL4g/edit"
URL_COMP = "https://docs.google.com/spreadsheets/d/1szrDZsA59e5sMF6OAzPeQ_nDX7E9lMehaXCPHmVNx5o/edit"
URL_ACPM = "https://docs.google.com/spreadsheets/d/16ZgE9R5o4l8P7Tz7xS9u3v4W3Y1vW-J1/edit" 

conn = st.connection("gsheets", type=GSheetsConnection)

# --- FUNCIÓN DE GENERACIÓN DE PDF ---
def generar_pdf_sigma(nit, df_cond, df_comp, an_c, pl_c, an_h, pl_h):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(0, 10, 'INFORME DE GESTIÓN INTEGRAL - WCO-SIGMA', ln=True, align='C')
    pdf.set_font('Arial', '', 10)
    pdf.cell(0, 10, f'NIT CLIENTE: {nit} | FECHA: {datetime.now().strftime("%d/%m/%Y")}', ln=True, align='C')
    pdf.ln(10)
    
    # Secciones de Análisis
    sections = [
        ("1. ANALISIS DE CONDICIONES HSEQ", an_c, pl_c),
        ("2. ANALISIS DE COMPORTAMIENTO Y PESV", an_h, pl_h)
    ]
    
    for title, an, pl in sections:
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 10, title, ln=True, fill=False)
        pdf.set_font('Arial', '', 10)
        pdf.multi_cell(0, 7, f"DIAGNOSTICO: {an if an else 'N/A'}")
        pdf.multi_cell(0, 7, f"PLAN DE ACCION: {pl if pl else 'N/A'}")
        pdf.ln(5)
        
    return pdf.output(dest='S').encode('latin-1', 'ignore')

# 2. ACCESO POR NIT
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/1063/1063302.png", width=100)
nit_user = st.sidebar.text_input("Ingrese identificación (NIT/Cédula):", "").strip()

if not nit_user:
    st.title("🚀 WCO-SIGMA: Suite PHVA Multiempresa")
    st.info("Motores BDI Vinculados. Ingrese el NIT para activar el tablero gerencial.")
else:
    # --- MOTOR DE LECTURA ---
    def cargar(url):
        try:
            df = conn.read(spreadsheet=url, ttl=0)
            if df is not None and not df.empty:
                df.columns = df.columns.str.strip()
                df['Nit'] = df['Nit'].astype(str).apply(lambda x: x.split('.')[0].strip())
                return df, df[df['Nit'] == nit_user]
            return pd.DataFrame(), pd.DataFrame()
        except: return pd.DataFrame(), pd.DataFrame()

    df_cond_t, df_cond_e = cargar(URL_COND)
    df_comp_t, df_comp_e = cargar(URL_COMP)
    df_acpm_t, df_acpm_e = cargar(URL_ACPM)

    menu = st.sidebar.radio("Navegación", ["📊 Dashboard Gerencial", "⚖️ Gestión de ACPM", "🛠️ Reporte Condiciones", "🧠 Reporte Comportamiento"])

    # --- PANTALLA 1: DASHBOARD (RESTAURACIÓN DE GRÁFICOS) ---
    if menu == "📊 Dashboard Gerencial":
        st.title(f"📊 Tablero de Control - NIT: {nit_user}")
        tab1, tab2, tab3 = st.tabs(["🔍 BDI WCO SIGMA", "🧠 BDI COMPORTAMIENTO", "⚖️ BD ACPM"])
        
        with tab1:
            if not df_cond_e.empty:
                c1, c2 = st.columns(2)
                with c1:
                    st.plotly_chart(px.bar(df_cond_e, x='Centro de trabajo', color='Prioridad', title="Hallazgos por Centro"), use_container_width=True)
                    st.plotly_chart(px.pie(df_cond_e, names='Condición Crítica', title="Distribución por Condición", hole=0.3), use_container_width=True)
                with c2:
                    st.plotly_chart(px.bar(df_cond_e, x='Lugar', color='Estado', title="Estatus por Lugar"), use_container_width=True)
                    st.plotly_chart(px.pie(df_cond_e, names='Prioridad', title="Urgencia (Prioridad)"), use_container_width=True)
                st.markdown("---")
                txt_an_c = st.text_area("Análisis Técnico (Condiciones):", key="an_c_v12")
                txt_pl_c = st.text_area("Plan de Acción (Condiciones):", key="pl_c_v12")
            else: st.warning("Sin datos en Condiciones.")

        with tab2:
            if not df_comp_e.empty:
                g1, g2 = st.columns(2)
                with g1: st.plotly_chart(px.bar(df_comp_e, x='Centro de trabajo', color='Estado observado', title="Cultura por Centro"), use_container_width=True)
                with g2: st.plotly_chart(px.pie(df_comp_e, names='Lugar', title="Observaciones por Lugar"), use_container_width=True)
                st.plotly_chart(px.bar(df_comp_e, x='Estado observado', title="Estatus de Comportamientos"), use_container_width=True)
                st.markdown("---")
                txt_an_h = st.text_area("Análisis de Riesgo Conductual:", key="an_h_v12")
                txt_pl_h = st.text_area("Plan de Intervención Humana:", key="pl_h_v12")
            else: st.warning("Sin datos en Comportamiento.")

        with tab3:
            st.subheader("⚖️ Gestión de Mejora (ACPM)")
            if df_acpm_e.empty:
                st.error("❌ Sin datos en BD ACPM o URL incorrecta.")
                with st.expander("Diagnóstico de Datos"):
                    st.write("Columnas detectadas:", list(df_acpm_t.columns))
            else:
                ca1, ca2 = st.columns(2)
                with ca1:
                    st.plotly_chart(px.pie(df_acpm_e, names='Componente', title="ACPM por Sistema", hole=0.4), use_container_width=True)
                    st.plotly_chart(px.bar(df_acpm_e, x='Causa raíz', color='Estado', title="Análisis de Causa Raíz"), use_container_width=True)
                with ca2:
                    st.plotly_chart(px.bar(df_acpm_e, x='Fuente', color='Tipo Acción', title="Fuente vs Tipo Acción"), use_container_width=True)
                    st.plotly_chart(px.pie(df_acpm_e, names='Estado', title="Estatus de ACPM"), use_container_width=True)
                st.dataframe(df_acpm_e, use_container_width=True)

        # BOTÓN PDF
        if st.sidebar.button("📄 Procesar Reporte PDF"):
            pdf_bytes = generar_pdf_sigma(nit_user, df_cond_e, df_comp_e, txt_an_c, txt_pl_c, txt_an_h, txt_pl_h)
            st.sidebar.download_button("⬇️ Descargar Informe", data=pdf_bytes, file_name=f"SIG_{nit_user}.pdf", mime="application/pdf")

    # --- PANTALLA: REPORTE ACPM (VARIABLES COMPLETAS) ---
    elif menu == "⚖️ Gestión de ACPM":
        st.title("⚖️ Registro Técnico de ACPM (PHVA)")
        with st.form("form_acpm_full"):
            col1, col2 = st.columns(2)
            with col1:
                f_emp_a = st.text_input("Empresa")
                f_comp_a = st.selectbox("Componente", ["SST", "Ambiente", "Calidad", "Vial"])
                f_fuen_a = st.selectbox("Fuente", ["inspecciones", "auditorías", "incidentes", "revisión gerencial"])
                f_desc_a = st.text_area("Descripción Hallazgo")
                p1, p2, p3, p4, p5 = st.text_input("P1"), st.text_input("P2"), st.text_input("P3"), st.text_input("P4"), st.text_input("P5")
            with col2:
                f_raiz_a = st.text_input("Causa raíz")
                f_acci_a = st.text_area("Plan de Acción")
                f_tipo_a = st.radio("Tipo Acción", ["Correctiva", "Preventiva", "Mejora"])
                f_esta_a = st.selectbox("Estado", ["Abierta", "En Ejecución", "Cerrada"])
            if st.form_submit_button("💾 GUARDAR ACPM"):
                n_a = pd.DataFrame([{"Nit":str(nit_user), "Empresa":f_emp_a, "Fecha de reporte":str(datetime.now().date()), "Componente":f_comp_a, "Fuente":f_fuen_a, "Descripción Hallazgo":f_desc_a, "Análisis Causa ¿Porqué 1?":p1, "Análisis Causa ¿Porqué 2?":p2, "Análisis Causa ¿Porqué 3?":p3, "Análisis Causa ¿Porqué 4?":p4, "Análisis Causa ¿Porqué 5?":p5, "Causa raíz":f_raiz_a, "Acción Propuesta":f_acci_a, "Tipo Acción":f_tipo_a, "Responsable":"SIG", "Fecha Cierre Prevista":str(datetime.now().date()), "Eficacia de la acción tomada":"Pendiente", "La acción tomada activa gestión del cambio (Si es afirmativo IPVR, IAVI y sus controles)":"No", "Estado":f_esta_a}])
                conn.update(spreadsheet="BD ACPM", data=pd.concat([df_acpm_t, n_a], ignore_index=True))
                st.success("ACPM Registrada.")

    # --- PANTALLA: REPORTE CONDICIONES (VARIABLES COMPLETAS) ---
    elif menu == "🛠️ Reporte Condiciones":
        st.title("🛠️ Registro de Condiciones HSEQ")
        with st.form("form_cond_full"):
            c1, c2 = st.columns(2)
            with c1:
                f_emp_c = st.text_input("Empresa")
                f_centro_c = st.text_input("Centro de trabajo")
                f_lugar_c = st.text_input("Lugar")
                f_hall_c = st.text_area("Hallazgo")
            with c2:
                f_cond_c = st.selectbox("Condición Crítica", ["Orden y aseo", "Herramientas", "Locativo", "Vial", "Otros"])
                f_ries_c = st.selectbox("Clasificación del riesgo", ["Físico", "Químico", "Biológico", "Psicosocial", "Biomecánico", "Seguridad", "Natural"])
                f_prio_c = st.selectbox("Prioridad", ["Baja", "Media", "Alta"])
                f_est_c = st.selectbox("Estado", ["Abierto", "En Proceso", "Cerrado"])
            if st.form_submit_button("✅ GUARDAR CONDICIÓN"):
                n_c = pd.DataFrame([{"Nit":str(nit_user), "Empresa":f_emp_c, "Centro de trabajo":f_centro_c, "Lugar":f_lugar_c, "Fecha":str(datetime.now().date()), "Hallazgo":f_hall_c, "Condición Crítica":f_cond_c, "Clasificación del riesgo":f_ries_c, "Componente":"SST", "Responsable del cierre":"Auditor", "Fecha propuesta para el cierre":str(datetime.now().date()), "Prioridad":f_prio_c, "Estado":f_est_c, "Observación":"Registro APP"}])
                conn.update(spreadsheet="BDI WCO SIGMA", data=pd.concat([df_cond_t, n_c], ignore_index=True))
                st.success("Condición guardada.")

    # --- PANTALLA: REPORTE COMPORTAMIENTO (VARIABLES COMPLETAS) ---
    elif menu == "🧠 Reporte Comportamiento":
        st.title("🧠 Registro de Comportamiento")
        with st.form("form_comp_full"):
            c1, c2 = st.columns(2)
            with c1:
                f_ins = st.text_input("Inspector")
                f_centro_h = st.text_input("Centro de trabajo")
                f_lugar_h = st.text_input("Lugar")
            with c2:
                f_tipo_h = st.selectbox("Tipo de Inspección", ["Conducta Humana", "Preoperacional", "Tareas Críticas"])
                f_est_h = st.selectbox("Estado observado", ["✅ SEGURO", "⚠️ ATÍPICO", "🚫 PELIGROSO"])
                f_obs_h = st.text_area("Observaciones")
            if st.form_submit_button("🚀 REGISTRAR COMPORTAMIENTO"):
                n_h = pd.DataFrame([{"Nit":str(nit_user), "ID_Inspección":str(uuid.uuid4())[:8].upper(), "Fecha/Hora Real":str(datetime.now()), "Inspector":f_ins, "Centro de trabajo":f_centro_h, "Lugar":f_lugar_h, "Tipo de Inspección":f_tipo_h, "Estado observado":f_est_h, "Evidencia Fotográfica":"N/A", "Observaciones Factor Humano":f_obs_h}])
                conn.update(spreadsheet="BDI COMPORTAMIENTO", data=pd.concat([df_comp_t, n_h], ignore_index=True))
                st.success("Comportamiento registrado.")
