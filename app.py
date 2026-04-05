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
URL_ACPM = "https://docs.google.com/spreadsheets/d/1yXQNE3PiET-8VOHBWiReht7psRqjbAm5ZnY4P2XQQvg/edit?gid=0#gid=0" 

conn = st.connection("gsheets", type=GSheetsConnection)

# --- FUNCIÓN MAESTRA: GENERADOR DE PDF CON ANÁLISIS ---
class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, 'WCO-SIGMA - SISTEMA DE GESTIÓN INTEGRAL PHVA', 0, 1, 'C')
        self.ln(5)

def generar_reporte_pdf(nit, df_cond, df_comp, an_cond, pl_cond, an_comp, pl_comp):
    pdf = PDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # Portada
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(0, 15, f'INFORME EJECUTIVO DE GESTIÓN SIG', 0, 1, 'C')
    pdf.set_font('Arial', '', 12)
    pdf.cell(0, 10, f'NIT CLIENTE: {nit}', 0, 1, 'C')
    pdf.cell(0, 10, f'FECHA DE GENERACIÓN: {datetime.now().strftime("%d/%m/%Y")}', 0, 1, 'C')
    pdf.ln(10)

    # SECCIÓN 1: CONDICIONES
    pdf.set_fill_color(230, 230, 230)
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, '1. ANÁLISIS DE CONDICIONES HSEQ', 0, 1, 'L', True)
    pdf.ln(5)
    pdf.set_font('Arial', 'B', 11)
    pdf.cell(0, 10, 'Diagnóstico del Auditor:', 0, 1)
    pdf.set_font('Arial', '', 10)
    pdf.multi_cell(0, 7, an_cond if an_cond else "Sin análisis registrado.")
    pdf.ln(5)
    pdf.set_font('Arial', 'B', 11)
    pdf.cell(0, 10, 'Plan de Acción Sugerido:', 0, 1)
    pdf.set_font('Arial', '', 10)
    pdf.multi_cell(0, 7, pl_cond if pl_cond else "Sin plan de acción definido.")
    pdf.ln(10)

    # SECCIÓN 2: COMPORTAMIENTO
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, '2. ANÁLISIS DE COMPORTAMIENTO Y PESV', 0, 1, 'L', True)
    pdf.ln(5)
    pdf.set_font('Arial', 'B', 11)
    pdf.cell(0, 10, 'Diagnóstico de Factor Humano:', 0, 1)
    pdf.set_font('Arial', '', 10)
    pdf.multi_cell(0, 7, an_comp if an_comp else "Sin análisis registrado.")
    pdf.ln(10)

    # Firma
    pdf.ln(20)
    pdf.set_font('Arial', 'I', 10)
    pdf.cell(0, 10, 'Generado automáticamente por WCO-SIGMA HSEQ Platform', 0, 1, 'C')
    
    return pdf.output(dest='S').encode('latin-1', 'ignore')

# 2. ACCESO
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/1063/1063302.png", width=100)
nit_user = st.sidebar.text_input("Ingrese NIT de la Empresa:", "").strip()

if not nit_user:
    st.title("🚀 WCO-SIGMA: Gestión Integral SIG")
    st.info("Ingrese el NIT para activar el Dashboard y el Generador de PDF.")
else:
    # --- CARGA DE DATOS ---
    def cargar(url):
        df = conn.read(spreadsheet=url, ttl=0)
        df.columns = df.columns.str.strip()
        df['Nit'] = df['Nit'].astype(str).apply(lambda x: x.split('.')[0].strip())
        return df, df[df['Nit'] == nit_user]

    df_cond_t, df_cond_e = cargar(URL_COND)
    df_comp_t, df_comp_e = cargar(URL_COMP)
    df_acpm_t, df_acpm_e = cargar(URL_ACPM)

    menu = st.sidebar.radio("Navegación", ["📊 Dashboard & Análisis", "⚖️ Gestión de ACPM", "🛠️ Reporte Condiciones", "🧠 Reporte Comportamiento"])

    # VARIABLES DE ANÁLISIS (ESTADO GLOBAL PARA EL PDF)
    if menu == "📊 Dashboard & Análisis":
        st.title(f"📊 Tablero de Control - NIT: {nit_user}")
        tab1, tab2, tab3 = st.tabs(["🔍 Condiciones", "🧠 Comportamiento", "⚖️ ACPM"])
        
        with tab1:
            st.plotly_chart(px.pie(df_cond_e, names='Estado', title="Estatus General"), use_container_width=True)
            txt_an_cond = st.text_area("Diagnóstico Técnico de Condiciones:", key="pdf_an_cond")
            txt_pl_cond = st.text_area("Plan de Acción Recomendado:", key="pdf_pl_cond")

        with tab2:
            st.plotly_chart(px.bar(df_comp_e, x='Estado observado', title="Cultura de Seguridad"), use_container_width=True)
            txt_an_comp = st.text_area("Análisis de Riesgo Conductual:", key="pdf_an_comp")
            txt_pl_comp = st.text_area("Plan de Intervención PESV:", key="pdf_pl_comp")

        # BOTÓN DE PDF EN LA SIDEBAR (Solo aparece si hay NIT)
        st.sidebar.markdown("---")
        st.sidebar.subheader("📥 Exportación")
        if st.sidebar.button("⚙️ Procesar Informe PDF"):
            pdf_data = generar_reporte_pdf(nit_user, df_cond_e, df_comp_e, txt_an_cond, txt_pl_cond, txt_an_comp, txt_pl_comp)
            st.sidebar.download_button(
                label="⬇️ Descargar Reporte PDF",
                data=pdf_data,
                file_name=f"Informe_SIG_{nit_user}.pdf",
                mime="application/pdf"
            )

    # --- RESTO DE FORMULARIOS (Mismos que ayer) ---
    elif menu == "⚖️ Gestión de ACPM":
        st.title("⚖️ Registro de ACPM")
        # ... (Mantener tu formulario de ACPM funcional aquí) ...
