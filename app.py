import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from fpdf import FPDF
import io

# Intento de importación para el componente de firma
try:
    from streamlit_canvas import st_canvas
    CANVAS_OK = True
except ImportError:
    CANVAS_OK = False

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="WCO-SIGMA HUB", layout="wide", page_icon="🛡️")

# --- SISTEMA DE PERSISTENCIA (FIX) ---
if "sigma_txt" not in st.session_state: st.session_state["sigma_txt"] = ""
if "comp_txt" not in st.session_state: st.session_state["comp_txt"] = ""
if "acpm_txt" not in st.session_state: st.session_state["acpm_txt"] = ""
if "plan_txt" not in st.session_state: st.session_state["plan_txt"] = ""

# --- CARGA DE DATOS ---
URL_COND = "https://docs.google.com/spreadsheets/d/18OIJe409rr6o_o4HSweiuncIoOrgJOXEt0GFCmEsL4g/export?format=csv&gid=2138172721"

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

# --- MOTOR DE PDF OPTIMIZADO ---
def crear_pdf(nit, s1, s2, s3, s4):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    
    # Encabezado Profesional
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "ACTA DE REVISIÓN GERENCIAL HSEQ", ln=True, align="C")
    pdf.set_font("Arial", "", 10)
    pdf.cell(0, 7, f"NIT: {nit} | Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M')}", ln=True, align="C")
    pdf.ln(10)

    secciones = [
        ("ANÁLISIS SIGMA", s1),
        ("CULTURA Y COMPORTAMIENTO", s2),
        ("SEGUIMIENTO ACPM", s3),
        ("PLAN DE ACCIÓN Y CIERRE", s4)
    ]

    for titulo, contenido in secciones:
        pdf.set_font("Arial", "B", 12)
        pdf.set_fill_color(240, 240, 240)
        pdf.cell(0, 8, titulo, ln=True, fill=True)
        pdf.ln(2)
        pdf.set_font("Arial", "", 11)
        # Limpieza de caracteres para evitar errores en PDF
        texto = contenido if contenido.strip() else "Sin comentarios."
        pdf.multi_cell(0, 6, texto.encode('latin-1', 'ignore').decode('latin-1'))
        pdf.ln(5)

    pdf.ln(20)
    pdf.cell(0, 5, "__________________________________________", ln=True)
    pdf.cell(0, 5, "Firma de Responsable / Validación Digital", ln=True)
    
    return pdf.output(dest='S').encode('latin-1')

# 2. INTERFAZ PRINCIPAL
nit_user = st.sidebar.text_input("Ingrese NIT Empresa:", "").strip()

if not nit_user:
    st.title("🛡️ WCO-SIGMA HUB")
    st.info("Ingrese NIT para activar funciones.")
else:
    df_cond = cargar_datos(URL_COND, nit_user)
    menu = st.sidebar.radio("Menú", ["📊 Dashboard Gerencial", "📝 Nuevo Reporte", "📄 Generar Acta"])

    if menu == "📊 Dashboard Gerencial":
        st.header(f"📊 Dashboard - NIT: {nit_user}")
        tab1, tab2, tab3 = st.tabs(["🔍 BDI SIGMA", "🧠 COMPORTAMIENTO", "⚖️ ACPM"])
        
        with tab1:
            if not df_cond.empty:
                # Mostrar gráficos de riesgos
                riesgos = ["Mecánico", "Alturas", "Eléctrico", "Vial", "Ambiente"]
                cols = st.columns(len(riesgos))
                for i, r in enumerate(riesgos):
                    c_f = [c for c in df_cond.columns if r.lower() in c.lower()]
                    if c_f: cols[i].plotly_chart(px.pie(df_cond, names=c_f[0], title=r, hole=0.3), use_container_width=True)
                
                # Áreas de texto con LLAVE de sesión
                st.session_state["sigma_txt"] = st.text_area("✍️ Análisis SIGMA:", value=st.session_state["sigma_txt"], height=150, key="ta_sigma")
                st.session_state["plan_txt"] = st.text_area("🚀 Plan de Acción:", value=st.session_state["plan_txt"], height=150, key="ta_plan")
            else: st.warning("No hay datos.")

        with tab2:
            st.session_state["comp_txt"] = st.text_area("✍️ Análisis Comportamiento:", value=st.session_state["comp_txt"], key="ta_comp")
        with tab3:
            st.session_state["acpm_txt"] = st.text_area("✍️ Seguimiento ACPM:", value=st.session_state["acpm_txt"], key="ta_acpm")

    elif menu == "📝 Nuevo Reporte":
        st.markdown(f'<iframe src="https://docs.google.com/forms/d/15BeH-wHD4VJ63EARiHjTEZOUoStbk6o50zSrYmS5SQc/viewform?embedded=true" width="100%" height="800" frameborder="0"></iframe>', unsafe_allow_html=True)

    elif menu == "📄 Generar Acta":
        st.header("📄 Formalización del Acta")
        
        if CANVAS_OK:
            st.subheader("🖋️ Firma Digital del Dispositivo")
            st.write("Firme en el recuadro gris con su dedo o mouse:")
            st_canvas(stroke_width=3, stroke_color="#000", background_color="#eee", height=150, key="canvas_firma")
        
        if st.button("🔄 Sincronizar y Generar PDF"):
            # Generar los bytes del PDF usando el estado actual de la sesión
            pdf_bytes = crear_pdf(
                nit_user, 
                st.session_state["sigma_txt"], 
                st.session_state["comp_txt"], 
                st.session_state["acpm_txt"], 
                st.session_state["plan_txt"]
            )
            st.success("✅ Datos sincronizados. Ya puede descargar.")
            st.download_button("⬇️ Descargar Acta PDF", data=pdf_bytes, file_name=f"Acta_{nit_user}.pdf")
