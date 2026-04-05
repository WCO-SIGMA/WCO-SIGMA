import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.express as px
from datetime import datetime
import uuid
from fpdf import FPDF

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="WCO-SIGMA SIG+ACPM", layout="wide")

# --- CONFIGURACIÓN DE CONEXIONES (URLs REALES) ---
URL_COND = "https://docs.google.com/spreadsheets/d/18OIJe409rr6o_o4HSweiuncIoOrgJOXEt0GFCmEsL4g/edit"
URL_COMP = "https://docs.google.com/spreadsheets/d/1szrDZsA59e5sMF6OAzPeQ_nDX7E9lMehaXCPHmVNx5o/edit"
URL_ACPM = "https://docs.google.com/spreadsheets/d/16ZgE9R5o4l8P7Tz7xS9u3v4W3Y1vW-J1/edit" # <-- VERIFICA ESTA URL

conn = st.connection("gsheets", type=GSheetsConnection)

# --- FUNCIÓN DE GENERACIÓN DE PDF ---
def generar_reporte_pdf(nit, df_cond, df_comp, an_cond, pl_cond, an_comp, pl_comp):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(0, 10, 'INFORME DE GESTIÓN SIG - WCO-SIGMA', ln=True, align='C')
    pdf.set_font('Arial', '', 12)
    pdf.cell(0, 10, f'NIT: {nit} | Fecha: {datetime.now().date()}', ln=True, align='C')
    pdf.ln(10)
    
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, '1. ANALISIS DE CONDICIONES HSEQ', ln=True)
    pdf.set_font('Arial', '', 10)
    pdf.multi_cell(0, 7, f"Analisis: {an_cond}\nPlan: {pl_cond}")
    pdf.ln(5)
    
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, '2. ANALISIS DE COMPORTAMIENTO', ln=True)
    pdf.set_font('Arial', '', 10)
    pdf.multi_cell(0, 7, f"Analisis: {an_comp}\nPlan: {pl_comp}")
    
    return pdf.output(dest='S').encode('latin-1', 'ignore')

# 2. ACCESO POR NIT
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/1063/1063302.png", width=100)
nit_user = st.sidebar.text_input("Ingrese NIT de la Empresa:", "").strip()

if not nit_user:
    st.title("🚀 WCO-SIGMA: Suite de Gestión PHVA")
    st.info("Motores Sincronizados. Ingrese el NIT para iniciar.")
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
        except:
            return pd.DataFrame(), pd.DataFrame()

    df_cond_t, df_cond_e = cargar(URL_COND)
    df_comp_t, df_comp_e = cargar(URL_COMP)
    df_acpm_t, df_acpm_e = cargar(URL_ACPM)

    menu = st.sidebar.radio("Navegación", ["📊 Dashboard Gerencial", "⚖️ Gestión de ACPM", "🛠️ Reporte Condiciones", "🧠 Reporte Comportamiento"])

    # --- PANTALLA 1: DASHBOARD GERENCIAL ---
    if menu == "📊 Dashboard Gerencial":
        st.title(f"📊 Tablero de Control - NIT: {nit_user}")
        tab1, tab2, tab3 = st.tabs(["🔍 BDI WCO SIGMA", "🧠 BDI COMPORTAMIENTO", "⚖️ BD ACPM"])
        
        with tab1:
            if not df_cond_e.empty:
                c1, c2 = st.columns(2)
                with c1:
                    st.plotly_chart(px.bar(df_cond_e, x='Centro de trabajo', color='Prioridad', title="Hallazgos por Centro"), use_container_width=True)
                    st.plotly_chart(px.pie(df_cond_e, names='Condición Crítica', title="Condiciones Críticas", hole=0.3), use_container_width=True)
                with c2:
                    st.plotly_chart(px.bar(df_cond_e, x='Lugar', color='Estado', title="Hallazgos por Lugar"), use_container_width=True)
                    st.plotly_chart(px.pie(df_cond_e, names='Estado', title="Avance de Cierres"), use_container_width=True)
                st.markdown("---")
                txt_an_cond = st.text_area("Análisis Técnico (Condiciones):", key="an_c")
                txt_pl_cond = st.text_area("Plan de Acción (Condiciones):", key="pl_c")
            else:
                st.warning("Sin datos en BDI WCO SIGMA")

        with tab2:
            if not df_comp_e.empty:
                g1, g2 = st.columns(2)
                with g1: st.plotly_chart(px.bar(df_comp_e, x='Centro de trabajo', color='Estado observado', title="Cultura por Centro"), use_container_width=True)
                with g2: st.plotly_chart(px.pie(df_comp_e, names='Lugar', title="Observaciones por Lugar"), use_container_width=True)
                st.plotly_chart(px.bar(df_comp_e, x='Estado observado', title="Estatus de Comportamientos"), use_container_width=True)
                st.markdown("---")
                txt_an_comp = st.text_area("Análisis de Riesgo Conductual:", key="an_h")
                txt_pl_comp = st.text_area("Plan de Intervención Humana:", key="pl_h")
            else:
                st.warning("Sin datos en BDI COMPORTAMIENTO")

        with tab3:
            st.subheader("⚖️ Gestión de Mejora Continua (ACPM)")
            if df_acpm_t.empty:
                st.error("❌ No se logra leer BD ACPM. Verifique URL.")
            elif df_acpm_e.empty:
                st.warning("⚠️ Sin datos de ACPM para este NIT.")
                with st.expander("🔍 Ver columnas detectadas"):
                    st.write(list(df_acpm_t.columns))
            else:
                ca1, ca2 = st.columns(2)
                with ca1:
                    st.plotly_chart(px.pie(df_acpm_e, names='Componente', title="ACPM por Sistema", hole=0.4), use_container_width=True)
                    st.plotly_chart(px.bar(df_acpm_e, x='Causa raíz', color='Estado', title="Análisis de Causa Raíz"), use_container_width=True)
                with ca2:
                    st.plotly_chart(px.bar(df_acpm_e, x='Fuente', color='Tipo Acción', title="Fuente vs Tipo de Acción"), use_container_width=True)
                    st.plotly_chart(px.pie(df_acpm_e, names='Estado', title="Estatus de ACPM"), use_container_width=True)
                st.text_area("Evaluación Mejora / Plan Acción ACPM:", key="an_m")
                st.dataframe(df_acpm_e)

        # BOTÓN PDF EN LA BARRA LATERAL
        st.sidebar.markdown("---")
        if st.sidebar.button("📄 Generar Reporte PDF"):
            pdf_bytes = generar_reporte_pdf(nit_user, df_cond_e, df_comp_e, "Ver Dashboard", "Ver Dashboard", "Ver Dashboard", "Ver Dashboard")
            st.sidebar.download_button(label="⬇️ Descargar PDF", data=pdf_bytes, file_name=f"SIG_{nit_user}.pdf", mime="application/pdf")

    # --- PANTALLAS DE REPORTE (FORMULARIOS) ---
    elif menu == "⚖️ Gestión de ACPM":
        st.title("⚖️ Registro de ACPM")
        with st.form("f_acpm"):
            f_emp = st.text_input("Empresa")
            f_comp = st.selectbox("Componente", ["SST", "Ambiente", "Calidad", "Vial"])
            f_desc = st.text_area("Hallazgo")
            f_raiz = st.text_input("Causa raíz")
            f_esta = st.selectbox("Estado", ["Abierta", "En Ejecución", "Cerrada"])
            if st.form_submit_button("💾 GUARDAR"):
                n_a = pd.DataFrame([{"Nit":str(nit_user), "Empresa":f_emp, "Fecha de reporte":str(datetime.now().date()), "Componente":f_comp, "Descripción Hallazgo":f_desc, "Causa raíz":f_raiz, "Estado":f_esta}])
                conn.update(spreadsheet="BD ACPM", data=pd.concat([df_acpm_t, n_a], ignore_index=True))
                st.success("Guardado.")

    elif menu == "🛠️ Reporte Condiciones":
        st.title("🛠️ Registro de Condiciones")
        with st.form("f_cond"):
            f_emp_c = st.text_input("Empresa")
            f_ct_c = st.text_input("Centro de trabajo")
            f_l_c = st.text_input("Lugar")
            f_h_c = st.text_area("Hallazgo")
            f_p_c = st.selectbox("Prioridad", ["Baja", "Media", "Alta"])
            f_e_c = st.selectbox("Estado", ["Abierto", "En Proceso", "Cerrado"])
            if st.form_submit_button("✅ GUARDAR"):
                n_c = pd.DataFrame([{"Nit":str(nit_user), "Empresa":f_emp_c, "Centro de trabajo":f_ct_c, "Lugar":f_l_c, "Fecha":str(datetime.now().date()), "Hallazgo":f_h_c, "Condición Crítica":"General", "Clasificación del riesgo":"SST", "Componente":"SST", "Responsable del cierre":"Auditor", "Fecha propuesta para el cierre":str(datetime.now().date()), "Prioridad":f_p_c, "Estado":f_e_c, "Observación":"Registro APP"}])
                conn.update(spreadsheet="BDI WCO SIGMA", data=pd.concat([df_cond_t, n_c], ignore_index=True))
                st.success("Guardado.")

    elif menu == "🧠 Reporte Comportamiento":
        st.title("🧠 Registro de Comportamiento")
        with st.form("f_comp"):
            f_ins = st.text_input("Inspector")
            f_ct_h = st.text_input("Centro de trabajo")
            f_l_h = st.text_input("Lugar")
            f_res = st.selectbox("Estado observado", ["✅ SEGURO", "⚠️ ATÍPICO", "🚫 PELIGROSO"])
            f_obs = st.text_area("Observaciones")
            if st.form_submit_button("🚀 REGISTRAR"):
                n_h = pd.DataFrame([{"Nit":str(nit_user), "ID_Inspección":str(uuid.uuid4())[:8], "Fecha/Hora Real":str(datetime.now()), "Inspector":f_ins, "Centro de trabajo":f_ct_h, "Lugar":f_l_h, "Tipo de Inspección":"Conducta", "Estado observado":f_res, "Evidencia Fotográfica":"N/A", "Observaciones Factor Humano":f_obs}])
                conn.update(spreadsheet="BDI COMPORTAMIENTO", data=pd.concat([df_comp_t, n_h], ignore_index=True))
                st.success("Registrado.")
