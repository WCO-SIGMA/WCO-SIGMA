import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from fpdf import FPDF
import io

# --- INTENTO DE IMPORTACIÓN DE FIRMA ---
try:
    from streamlit_canvas import st_canvas
    CANVAS_DISPONIBLE = True
except ImportError:
    CANVAS_DISPONIBLE = False

# 1. CONFIGURACIÓN
st.set_page_config(page_title="WCO-SIGMA HUB", layout="wide", page_icon="🛡️")

# --- PERSISTENCIA DE DATOS (CRÍTICO) ---
# Usamos llaves específicas para que el texto no se borre al cambiar de pestaña
if "sigma_txt" not in st.session_state: st.session_state.sigma_txt = ""
if "comp_txt" not in st.session_state: st.session_state.comp_txt = ""
if "acpm_txt" not in st.session_state: st.session_state.acpm_txt = ""
if "plan_txt" not in st.session_state: st.session_state.plan_txt = ""

# --- ENLACES DE LECTURA ---
URL_COND = "https://docs.google.com/spreadsheets/d/18OIJe409rr6o_o4HSweiuncIoOrgJOXEt0GFCmEsL4g/export?format=csv&gid=2138172721"
URL_COMP = "https://docs.google.com/spreadsheets/d/1szrDZsA59e5sMF6OAzPeQ_nDX7E9lMehaXCPHmVNx5o/export?format=csv&gid=980289568"
URL_ACPM = "https://docs.google.com/spreadsheets/d/1yXQNE3PiET-8VOHBWiReht7psRqjbAm5ZnY4P2XQQvg/export?format=csv&gid=1969292888"

@st.cache_data(ttl=5)
def cargar_datos(url, nit):
    try:
        df = pd.read_csv(url)
        df.columns = df.columns.str.strip()
        col_nit = [c for c in df.columns if 'nit' in c.lower() or 'identificación' in c.lower()]
        if not col_nit: return pd.DataFrame()
        df['Nit_M'] = df[col_nit[0]].astype(str).apply(lambda x: x.split('.')[0].strip())
        return df[df['Nit_M'] == nit]
    except: return pd.DataFrame()

# --- MOTOR PDF CORREGIDO ---
def generar_pdf_final(nit, s1, s2, s3, s4):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    
    # Encabezado con estilo
    pdf.set_font("Arial", "B", 16)
    pdf.set_text_color(44, 62, 80)
    pdf.cell(0, 10, "ACTA DE REVISIÓN GERENCIAL HSEQ", ln=True, align="C")
    
    pdf.set_font("Arial", "", 10)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 7, f"NIT Empresa: {nit} | Fecha de Emisión: {datetime.now().strftime('%d/%m/%Y %H:%M')}", ln=True, align="C")
    pdf.ln(10)

    secciones = [
        ("1. ANÁLISIS DE CONDICIONES (SIGMA)", s1),
        ("2. CULTURA Y COMPORTAMIENTO", s2),
        ("3. SEGUIMIENTO DE ACCIONES (ACPM)", s3),
        ("4. PLAN DE ACCIÓN Y CIERRE DE MEDIDAS", s4)
    ]

    for titulo, contenido in secciones:
        pdf.set_font("Arial", "B", 11)
        pdf.set_fill_color(230, 233, 237)
        pdf.cell(0, 8, titulo, ln=True, fill=True)
        pdf.ln(2)
        pdf.set_font("Arial", "", 10)
        # multi_cell procesa el texto largo correctamente
        txt = contenido if contenido.strip() else "Sin comentarios registrados en esta sección."
        pdf.multi_cell(0, 6, txt.encode('latin-1', 'ignore').decode('latin-1'))
        pdf.ln(4)

    pdf.ln(10)
    pdf.line(10, pdf.get_y(), 80, pdf.get_y())
    pdf.set_font("Arial", "I", 8)
    pdf.cell(0, 5, "Firma de Responsable / Validación Digital WCO-SIGMA", ln=True)
    
    return pdf.output(dest='S').encode('latin-1')

# 2. INTERFAZ
nit_user = st.sidebar.text_input("Ingrese NIT Empresa:", "").strip()

if not nit_user:
    st.title("🚀 WCO-SIGMA HUB PRO")
    st.info("Sistema listo. Ingrese NIT para comenzar el análisis.")
else:
    df_cond = cargar_datos(URL_COND, nit_user)
    menu = st.sidebar.radio("Navegación", ["📊 Dashboard Gerencial", "📝 Nuevo Reporte", "📄 Generar Acta Final"])

    if menu == "📊 Dashboard Gerencial":
        st.header(f"📊 Control de Indicadores - NIT: {nit_user}")
        t1, t2, t3 = st.tabs(["🔍 BDI SIGMA", "🧠 COMPORTAMIENTO", "⚖️ ACPM"])
        
        with t1:
            if not df_cond.empty:
                st.subheader("⚠️ Riesgos Identificados")
                riesgos = ["Mecánico", "Alturas", "Eléctrico", "Emergencias", "Ergonómicos", "Químico", "Vial", "Ambiente"]
                v_cols = st.columns(3)
                idx = 0
                for r in riesgos:
                    c_f = [c for c in df_cond.columns if r.lower() in c.lower()]
                    if c_f:
                        with v_cols[idx % 3]:
                            st.plotly_chart(px.pie(df_cond, names=c_f[0], title=f"Riesgo: {r}", hole=0.3), use_container_width=True)
                        idx += 1
                
                # Campos de texto vinculados a la sesión
                st.session_state.sigma_txt = st.text_area("✍️ Análisis de Hallazgos SIGMA:", value=st.session_state.sigma_txt, height=150)
                st.session_state.plan_txt = st.text_area("🚀 Plan de Acción Detallado:", value=st.session_state.plan_txt, height=150)
            else: st.warning("No hay datos.")

        with t2:
            st.session_state.comp_txt = st.text_area("✍️ Análisis de Comportamiento:", value=st.session_state.comp_txt, height=150)
        with t3:
            st.session_state.acpm_txt = st.text_area("✍️ Seguimiento ACPM:", value=st.session_state.acpm_txt, height=150)

    elif menu == "📝 Nuevo Reporte":
        url_f = f"https://docs.google.com/forms/d/15BeH-wHD4VJ63EARiHjTEZOUoStbk6o50zSrYmS5SQc/viewform?embedded=true"
        st.markdown(f'<iframe src="{url_f}" width="100%" height="800" frameborder="0"></iframe>', unsafe_allow_html=True)

    elif menu == "📄 Generar Acta Final":
        st.header("📄 Consolidación de Acta Magnetica")
        st.write("Verifique que sus análisis estén completos antes de generar el documento.")
        
        if CANVAS_DISPONIBLE:
            st.subheader("🖋️ Firma Digital")
            st_canvas(stroke_width=2, stroke_color="#000", background_color="#f0f0f0", height=100, key="c_final")
        
        # Botón que procesa los datos actuales de la sesión
        if st.button("🔥 Procesar y Preparar PDF"):
            pdf_data = generar_pdf_final(
                nit_user, 
                st.session_state.sigma_txt, 
                st.session_state.comp_txt, 
                st.session_state.acpm_txt, 
                st.session_state.plan_txt
            )
            st.success("✅ Documento listo para descarga.")
            st.download_button(
                label="⬇️ Descargar Acta PDF",
                data=pdf_data,
                file_name=f"Acta_Gerencial_{nit_user}_{datetime.now().strftime('%Y%m%d')}.pdf",
                mime="application/pdf"
            )
