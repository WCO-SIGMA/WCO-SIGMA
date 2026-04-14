import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from fpdf import FPDF
import io

# 1. CONFIGURACIÓN
st.set_page_config(page_title="WCO-SIGMA HUB", layout="wide", page_icon="🛡️")

# --- MEMORIA DE SESIÓN PARA ANÁLISIS ---
if 'analisis_data' not in st.session_state:
    st.session_state.analisis_data = {"sigma": "", "comp": "", "acpm": "", "plan": ""}

# --- ENLACES DE LECTURA ---
URL_COND = "https://docs.google.com/spreadsheets/d/18OIJe409rr6o_o4HSweiuncIoOrgJOXEt0GFCmEsL4g/export?format=csv&gid=2138172721"
URL_COMP = "https://docs.google.com/spreadsheets/d/1szrDZsA59e5sMF6OAzPeQ_nDX7E9lMehaXCPHmVNx5o/export?format=csv&gid=980289568"
URL_ACPM = "https://docs.google.com/spreadsheets/d/1yXQNE3PiET-8VOHBWiReht7psRqjbAm5ZnY4P2XQQvg/export?format=csv&gid=1969292888"

@st.cache_data(ttl=10)
def cargar_datos(url, nit):
    try:
        df = pd.read_csv(url)
        df.columns = df.columns.str.strip()
        col_nit = [c for c in df.columns if 'nit' in c.lower() or 'identificación' in c.lower()]
        if not col_nit: return pd.DataFrame()
        df['Nit_M'] = df[col_nit[0]].astype(str).apply(lambda x: x.split('.')[0].strip())
        return df[df['Nit_M'] == nit]
    except: return pd.DataFrame()

# --- MOTOR DE GENERACIÓN PDF ---
def generar_pdf(nit, analisis):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "ACTA DE REUNIÓN GERENCIAL HSEQ", ln=True, align="C")
    pdf.set_font("Arial", "", 10)
    pdf.cell(0, 10, f"Empresa NIT: {nit} | Fecha: {datetime.now().strftime('%d/%m/%Y')}", ln=True, align="C")
    
    for modulo, texto in analisis.items():
        pdf.ln(5)
        pdf.set_font("Arial", "B", 12)
        pdf.set_fill_color(240, 240, 240)
        pdf.cell(0, 10, f"Módulo: {modulo.upper()}", ln=True, fill=True)
        pdf.set_font("Arial", "", 10)
        pdf.multi_cell(0, 6, texto if texto else "No se registraron comentarios.")
        
    pdf.ln(10)
    pdf.set_font("Arial", "I", 8)
    pdf.cell(0, 10, "Evidencia digital generada por WCO-SIGMA - Práctica amigable con el ambiente.", align="C")
    
    return pdf.output(dest='S').encode('latin-1', 'ignore')

# 2. INTERFAZ
st.sidebar.title("🛡️ Panel Gerencial")
nit_user = st.sidebar.text_input("Ingrese NIT Empresa:", "").strip()

if not nit_user:
    st.title("🚀 WCO-SIGMA PRO")
    st.info("Ingrese el NIT para habilitar el Dashboard y la generación de Actas.")
else:
    df_cond = cargar_datos(URL_COND, nit_user)
    
    menu = st.sidebar.radio("Navegación", ["📊 Dashboard Gerencial", "📝 Nuevo Reporte", "📄 Generar Acta PDF"])

    if menu == "📊 Dashboard Gerencial":
        st.header(f"📊 Dashboard Estratégico - NIT: {nit_user}")
        t1, t2, t3 = st.tabs(["🔍 BDI SIGMA", "🧠 COMPORTAMIENTO", "⚖️ ACPM"])
        
        with t1:
            if not df_cond.empty:
                st.plotly_chart(px.bar(df_cond, x=df_cond.columns[4], title="Estado de Inspecciones"), use_container_width=True)
                # Espacio de Análisis
                st.session_state.analisis_data["sigma"] = st.text_area("Análisis de Condiciones Críticas:", value=st.session_state.analisis_data["sigma"])
                st.session_state.analisis_data["plan"] = st.text_area("Plan de Acción Propuesto:", value=st.session_state.analisis_data["plan"])
            else: st.warning("Sin datos.")

        with t2:
            st.session_state.analisis_data["comp"] = st.text_area("Análisis de Cultura y Comportamiento:", value=st.session_state.analisis_data["comp"])

        with t3:
            st.session_state.analisis_data["acpm"] = st.text_area("Seguimiento a Medidas de Intervención (ACPM):", value=st.session_state.analisis_data["acpm"])

    elif menu == "📝 Nuevo Reporte":
        st.header("📝 Registro de Inspección")
        url_f = "https://docs.google.com/forms/d/e/15BeH-wHD4VJ63EARiHjTEZOUoStbk6o50zSrYmS5SQc/viewform?embedded=true"
        st.markdown(f'<iframe src="{url_f}" width="100%" height="800" frameborder="0">Cargando…</iframe>', unsafe_allow_html=True)

    elif menu == "📄 Generar Acta PDF":
        st.header("📄 Generación de Acta de Revisión Gerencial")
        st.write("El documento incluirá los análisis y planes de acción redactados en el Dashboard.")
        
        if st.button("⚙️ Procesar Documento Magnetico"):
            pdf_bytes = generar_pdf(nit_user, st.session_state.analisis_data)
            st.success("✅ Acta generada correctamente.")
            st.download_button(label="⬇️ Descargar Acta (PDF)", data=pdf_bytes, file_name=f"Acta_HSEQ_{nit_user}.pdf", mime="application/pdf")
            
        st.info("💡 Consejo: Firme digitalmente el documento una vez descargado o use una herramienta de firma sobre el PDF para evitar impresiones.")
