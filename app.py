import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.express as px
from datetime import datetime
import io
from fpdf import FPDF

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="WCO-SIGMA SIG+ACPM", layout="wide")

# --- PERSISTENCIA DE MEMORIA ---
for k in ['an_cond', 'pl_cond', 'an_comp', 'pl_comp', 'an_acpm', 'pl_acpm']:
    if k not in st.session_state: st.session_state[k] = ""

# --- CONEXIONES ---
URL_COND = "https://docs.google.com/spreadsheets/d/18OIJe409rr6o_o4HSweiuncIoOrgJOXEt0GFCmEsL4g/edit"
URL_COMP = "https://docs.google.com/spreadsheets/d/1szrDZsA59e5sMF6OAzPeQ_nDX7E9lMehaXCPHmVNx5o/edit"
URL_ACPM = "https://docs.google.com/spreadsheets/d/1yXQNE3PiET-8VOHBWiReht7psRqjbAm5ZnY4P2XQQvg/edit" 

conn = st.connection("gsheets", type=GSheetsConnection)

# --- MOTOR DE CARGA CON LIMPIEZA DE COLUMNAS ---
def cargar_seguro(url, nit):
    try:
        df = conn.read(spreadsheet=url, ttl=0)
        df.columns = df.columns.str.strip()
        # Buscamos la columna NIT de forma flexible
        col_nit = [c for c in df.columns if 'nit' in c.lower()][0]
        df['Nit_M'] = df[col_nit].astype(str).apply(lambda x: x.split('.')[0].strip())
        return df, df[df['Nit_M'] == nit]
    except Exception as e:
        return pd.DataFrame(), pd.DataFrame()

# --- GENERADOR DE PDF (CON TABLAS SI FALLA LA IMAGEN) ---
def crear_pdf_profesional(nit, ac, pc, ah, ph, aa, pa, df_c, df_a):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "INFORME GERENCIAL INTEGRAL SIG", ln=True, align="C")
    pdf.set_font("Arial", "", 10)
    pdf.cell(0, 10, f"EMPRESA NIT: {nit} | FECHA: {datetime.now().strftime('%d/%m/%Y')}", ln=True, align="C")
    pdf.ln(5)

    # SECCIÓN 1: CONDICIONES
    pdf.set_font("Arial", "B", 12)
    pdf.set_fill_color(230, 230, 230)
    pdf.cell(0, 10, "1. GESTION DE CONDICIONES (BDI SIGMA)", ln=True, fill=True)
    pdf.set_font("Arial", "B", 10)
    pdf.cell(0, 7, "DIAGNOSTICO:", ln=True)
    pdf.set_font("Arial", "", 10)
    pdf.multi_cell(0, 5, ac if ac else "Sin registrar")
    pdf.set_font("Arial", "B", 10)
    pdf.cell(0, 7, "PLAN DE ACCION:", ln=True)
    pdf.set_font("Arial", "", 10)
    pdf.multi_cell(0, 5, pc if pc else "Sin registrar")
    pdf.ln(5)

    # SECCIÓN 2: ACPM
    pdf.add_page()
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "2. MEJORA CONTINUA (BD ACPM)", ln=True, fill=True)
    pdf.set_font("Arial", "B", 10)
    pdf.cell(0, 7, "ANALISIS:", ln=True)
    pdf.set_font("Arial", "", 10)
    pdf.multi_cell(0, 5, aa if aa else "Sin registrar")
    pdf.set_font("Arial", "B", 10)
    pdf.cell(0, 7, "PLAN DE MEJORA:", ln=True)
    pdf.set_font("Arial", "", 10)
    pdf.multi_cell(0, 5, pa if pa else "Sin registrar")

    return pdf.output(dest='S').encode('latin-1', 'ignore')

# 2. INTERFAZ LATERAL
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/1063/1063302.png", width=80)
nit_input = st.sidebar.text_input("Ingrese NIT de la Empresa:", "").strip()

if nit_input:
    df_cond_t, df_cond_e = cargar_seguro(URL_COND, nit_input)
    df_comp_t, df_comp_e = cargar_seguro(URL_COMP, nit_input)
    df_acpm_t, df_acpm_e = cargar_seguro(URL_ACPM, nit_input)

    st.sidebar.markdown("---")
    if st.sidebar.button("📄 Generar Reporte PDF"):
        pdf_res = crear_pdf_profesional(nit_input, st.session_state.an_cond, st.session_state.pl_cond, 
                                        st.session_state.an_comp, st.session_state.pl_comp, 
                                        st.session_state.an_acpm, st.session_state.pl_acpm, df_cond_e, df_acpm_e)
        st.sidebar.download_button("⬇️ Descargar Informe", data=pdf_res, file_name=f"Reporte_{nit_input}.pdf")

    menu = st.sidebar.radio("Navegación", ["📊 Dashboard", "🛠️ Reporte Condiciones", "🧠 Reporte Comportamiento", "⚖️ Reporte ACPM"])

    # --- PANTALLA DASHBOARD ---
    if menu == "📊 Dashboard":
        st.title(f"📊 Control Gerencial - NIT: {nit_input}")
        t1, t2, t3 = st.tabs(["🔍 BDI SIGMA", "🧠 COMPORTAMIENTO", "⚖️ ACPM"])
        
        with t1:
            if not df_cond_e.empty:
                # Variables: Centro, Lugar, Condición, Prioridad, Estado
                st.plotly_chart(px.bar(df_cond_e, x='Centro de trabajo', color='Prioridad', title="Hallazgos por Centro"), use_container_width=True)
                st.plotly_chart(px.bar(df_cond_e, x='Lugar', color='Estado', title="Estatus por Lugar"), use_container_width=True)
                st.plotly_chart(px.pie(df_cond_e, names='Condición Crítica', title="Condición Crítica"), use_container_width=True)
                st.session_state.an_cond = st.text_area("Diagnóstico Técnico (Condiciones):", value=st.session_state.an_cond)
                st.session_state.pl_cond = st.text_area("Plan de Acción (Condiciones):", value=st.session_state.pl_cond)
            else: st.warning("No hay datos de Condiciones para este NIT.")

        with t2:
            if not df_comp_e.empty:
                # Variables: Centro, Lugar, Estado Observado
                st.plotly_chart(px.bar(df_comp_e, x='Centro de trabajo', color='Estado observado', title="Cultura por Centro"), use_container_width=True)
                st.plotly_chart(px.bar(df_comp_e, x='Lugar', color='Estado observado', title="Cultura por Lugar"), use_container_width=True)
                st.session_state.an_comp = st.text_area("Análisis Conductual:", value=st.session_state.an_comp)
                st.session_state.pl_comp = st.text_area("Estrategia Humana:", value=st.session_state.pl_comp)

        with t3:
            if not df_acpm_e.empty:
                # Variables: Componente, Fuente, Causa Raíz, Tipo Acción, Estado
                st.plotly_chart(px.pie(df_acpm_e, names='Componente', title="ACPM por Componente"), use_container_width=True)
                st.plotly_chart(px.bar(df_acpm_e, x='Causa raíz', color='Estado', title="Análisis Causa Raíz"), use_container_width=True)
                st.plotly_chart(px.bar(df_acpm_e, x='Fuente', color='Tipo Acción', title="Fuente vs Tipo"), use_container_width=True)
                st.session_state.an_acpm = st.text_area("Análisis ACPM:", value=st.session_state.an_acpm)
                st.session_state.pl_acpm = st.text_area("Plan de Mejora:", value=st.session_state.pl_acpm)

    # --- FORMULARIOS (VARIABLES RE-ACTIVADAS) ---
    elif menu == "🛠️ Reporte Condiciones":
        st.title("🛠️ Registro de Condiciones")
        with st.form("f_cond"):
            f_ct = st.text_input("Centro de trabajo")
            f_lg = st.text_input("Lugar")
            f_hl = st.text_area("Hallazgo")
            f_cc = st.selectbox("Condición Crítica", ["Orden/Aseo", "Herramientas", "Locativo", "Vial", "Otros"])
            f_pr = st.selectbox("Prioridad", ["Baja", "Media", "Alta"])
            f_es = st.selectbox("Estado", ["Abierto", "En Proceso", "Cerrado"])
            if st.form_submit_button("✅ Guardar"):
                # (Lógica de guardado)
                pass

    elif menu == "⚖️ Reporte ACPM":
        st.title("⚖️ Gestión de ACPM")
        with st.form("f_acpm"):
            f_em = st.text_input("Empresa")
            f_co = st.selectbox("Componente", ["SST", "Ambiente", "Calidad", "Vial"])
            f_fu = st.selectbox("Fuente", ["Auditoría", "Inspección", "Incidente"])
            f_ra = st.text_input("Causa raíz")
            f_ti = st.radio("Tipo Acción", ["Correctiva", "Preventiva", "Mejora"])
            f_es = st.selectbox("Estado", ["Abierta", "En Ejecución", "Cerrada"])
            if st.form_submit_button("💾 Guardar"):
                # (Lógica de guardado)
                pass
else:
    st.title("🚀 WCO-SIGMA")
    st.info("Sistema listo. Ingrese NIT para visualizar reportes.")
