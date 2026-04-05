import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.express as px
from datetime import datetime
import uuid
from fpdf import FPDF
import io

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="WCO-SIGMA SIG+ACPM", layout="wide")

# --- URLs ---
URL_COND = "https://docs.google.com/spreadsheets/d/18OIJe409rr6o_o4HSweiuncIoOrgJOXEt0GFCmEsL4g/edit"
URL_COMP = "https://docs.google.com/spreadsheets/d/1szrDZsA59e5sMF6OAzPeQ_nDX7E9lMehaXCPHmVNx5o/edit"
URL_ACPM = "https://docs.google.com/spreadsheets/d/1yXQNE3PiET-8VOHBWiReht7psRqjbAm5ZnY4P2XQQvg/edit" 

conn = st.connection("gsheets", type=GSheetsConnection)

# --- FUNCIÓN GENERADORA DE PDF CON GRÁFICOS ---
def crear_pdf_visual(nit, ac, pc, ah, ph, aa, pa, fig1, fig2):
    pdf = FPDF()
    pdf.add_page()
    
    # Encabezado
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "INFORME GERENCIAL INTEGRAL - WCO-SIGMA", ln=True, align="C")
    pdf.set_font("Arial", "", 10)
    pdf.cell(0, 10, f"NIT: {nit} | Generado: {datetime.now().strftime('%d/%m/%Y')}", ln=True, align="C")
    pdf.ln(10)
    
    # SECCIÓN 1: CONDICIONES (Texto + Gráfico)
    pdf.set_font("Arial", "B", 12)
    pdf.set_fill_color(230, 230, 230)
    pdf.cell(0, 10, "1. GESTION DE CONDICIONES HSEQ", ln=True, fill=True)
    pdf.set_font("Arial", "", 10)
    pdf.multi_cell(0, 7, f"DIAGNOSTICO: {ac}\nPLAN: {pc}")
    
    # Insertar Imagen de Gráfico 1 (Condiciones)
    img_buf1 = io.BytesIO()
    fig1.write_image(img_buf1, format="png", width=800, height=400)
    pdf.image(img_buf1, x=10, w=180)
    pdf.ln(5)

    # SECCIÓN 2: MEJORA CONTINUA (Texto + Gráfico)
    pdf.add_page()
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "2. MEJORA CONTINUA (ACPM)", ln=True, fill=True)
    pdf.set_font("Arial", "", 10)
    pdf.multi_cell(0, 7, f"DIAGNOSTICO: {aa}\nPLAN: {pa}")
    
    # Insertar Imagen de Gráfico 2 (ACPM)
    img_buf2 = io.BytesIO()
    fig2.write_image(img_buf2, format="png", width=800, height=400)
    pdf.image(img_buf2, x=10, w=180)
    
    return pdf.output(dest='S').encode('latin-1', 'ignore')

# 2. ACCESO
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/1063/1063302.png", width=100)
nit_user = st.sidebar.text_input("Ingrese NIT:", "").strip()

if not nit_user:
    st.title("🚀 WCO-SIGMA")
else:
    def cargar(url):
        df = conn.read(spreadsheet=url, ttl=0)
        df.columns = df.columns.str.strip()
        col_nit = [c for c in df.columns if c.lower() == 'nit'][0]
        df['Nit_M'] = df[col_nit].astype(str).apply(lambda x: x.split('.')[0].strip())
        return df, df[df['Nit_M'] == nit_user]

    df_cond_t, df_cond_e = cargar(URL_COND)
    df_comp_t, df_comp_e = cargar(URL_COMP)
    df_acpm_t, df_acpm_e = cargar(URL_ACPM)

    menu = st.sidebar.radio("Navegación", ["📊 Dashboard", "⚖️ ACPM", "🛠️ Condiciones", "🧠 Comportamiento"])

    if menu == "📊 Dashboard":
        st.title(f"📊 Control Gerencial - NIT: {nit_user}")
        tab1, tab2, tab3 = st.tabs(["🔍 Condiciones", "🧠 Comportamiento", "⚖️ ACPM"])
        
        with tab1:
            f_cond_pie = px.pie(df_cond_e, names='Estado', title="Estatus de Cierre de Condiciones", color_discrete_sequence=px.colors.qualitative.Pastel)
            st.plotly_chart(f_cond_pie, use_container_width=True)
            txt_an_c = st.text_area("Análisis Condiciones:", key="ac")
            txt_pl_c = st.text_area("Plan Acción:", key="pc")

        with tab2:
            st.plotly_chart(px.bar(df_comp_e, x='Estado observado', title="Cultura"), use_container_width=True)
            txt_an_h = st.text_area("Análisis Comportamiento:", key="ah")
            txt_pl_h = st.text_area("Plan Comportamiento:", key="ph")

        with tab3:
            f_acpm_bar = px.bar(df_acpm_e, x='Estado', color='Tipo Acción', title="Avance de ACPM por Tipo")
            st.plotly_chart(f_acpm_bar, use_container_width=True)
            txt_an_a = st.text_area("Análisis ACPM:", key="aa")
            txt_pl_a = st.text_area("Plan ACPM:", key="pa")

        st.sidebar.markdown("---")
        if st.sidebar.button("📄 Generar Reporte Visual"):
            with st.spinner("Capturando gráficos..."):
                pdf_visual = crear_pdf_visual(nit_user, txt_an_c, txt_pl_c, txt_an_h, txt_pl_h, txt_an_a, txt_pl_a, f_cond_pie, f_acpm_bar)
                st.sidebar.download_button("⬇️ Descargar Reporte con Gráficos", data=pdf_visual, file_name=f"Reporte_Visual_{nit_user}.pdf")

    # --- RESTO DE FORMULARIOS (Igual que antes) ---
    # ... [Omitido por brevedad, mantén tus formularios de registro aquí] ...
