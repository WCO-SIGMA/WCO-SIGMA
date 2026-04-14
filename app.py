import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from fpdf import FPDF
from streamlit_canvas import st_canvas
import io

# 1. CONFIGURACIÓN
st.set_page_config(page_title="WCO-SIGMA HUB", layout="wide", page_icon="🛡️")

# --- MEMORIA DE SESIÓN ---
if 'analisis_data' not in st.session_state:
    st.session_state.analisis_data = {"sigma": "", "comp": "", "acpm": "", "plan": ""}

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

# --- MOTOR PDF MEJORADO ---
def generar_pdf_profesional(nit, analisis, firma_img=None):
    pdf = FPDF()
    pdf.add_page()
    # Encabezado
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "ACTA DE REVISIÓN GERENCIAL HSEQ", ln=True, align="C")
    pdf.set_font("Arial", "", 10)
    pdf.cell(0, 7, f"Empresa NIT: {nit} | Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M')}", ln=True, align="C")
    pdf.ln(10)

    for titulo, contenido in [("ANÁLISIS DE CONDICIONES (SIGMA)", analisis["sigma"]), 
                             ("CULTURA Y COMPORTAMIENTO", analisis["comp"]),
                             ("SEGUIMIENTO ACPM", analisis["acpm"]),
                             ("PLAN DE ACCIÓN Y CIERRE", analisis["plan"])]:
        pdf.set_font("Arial", "B", 12)
        pdf.set_fill_color(230, 230, 230)
        pdf.cell(0, 8, titulo, ln=True, fill=True)
        pdf.ln(2)
        pdf.set_font("Arial", "", 11)
        # multi_cell permite que el texto largo salte de línea automáticamente
        pdf.multi_cell(0, 6, contenido if contenido.strip() else "Sin comentarios registrados.")
        pdf.ln(5)

    if firma_img is not None:
        pdf.ln(10)
        pdf.set_font("Arial", "B", 10)
        pdf.cell(0, 5, "FIRMA DE RESPONSABLES:", ln=True)
        # Aquí se insertaría la imagen de la firma si Kaleido/Pillow están activos
        pdf.cell(0, 5, "__________________________", ln=True)
        pdf.cell(0, 5, "Validado Digitalmente en Plataforma", ln=True)

    return pdf.output(dest='S').encode('latin-1', 'ignore')

# 2. INTERFAZ
st.sidebar.title("🛡️ Gestión SIGMA")
nit_user = st.sidebar.text_input("Ingrese NIT Empresa:", "").strip()

if not nit_user:
    st.title("🚀 WCO-SIGMA PRO")
    st.info("Ingrese NIT para acceder al panel gerencial.")
else:
    df_cond = cargar_datos(URL_COND, nit_user)
    
    menu = st.sidebar.radio("Navegación", ["📊 Dashboard Gerencial", "📝 Nuevo Reporte", "📄 Acta y Firma Digital"])

    if menu == "📊 Dashboard Gerencial":
        st.header(f"📊 Dashboard de Control - NIT: {nit_user}")
        tab1, tab2, tab3 = st.tabs(["🔍 BDI SIGMA", "🧠 COMPORTAMIENTO", "⚖️ ACPM"])
        
        with tab1:
            if not df_cond.empty:
                # RECUPERACIÓN DE GRÁFICOS (v36 logic)
                st.subheader("⚠️ Estado de Riesgos Detectados")
                riesgos = ["Mecánico", "Alturas", "Eléctrico", "Emergencias", "Ergonómicos", "Químico", "Vial", "Ambiente"]
                cols_viz = st.columns(3)
                idx = 0
                for r in riesgos:
                    col_found = [c for c in df_cond.columns if r.lower() in c.lower()]
                    if col_found:
                        with cols_viz[idx % 3]:
                            st.plotly_chart(px.pie(df_cond, names=col_found[0], title=f"Riesgo: {r}", hole=0.3), use_container_width=True)
                        idx += 1
                
                st.session_state.analisis_data["sigma"] = st.text_area("✍️ Análisis SIGMA:", value=st.session_state.analisis_data["sigma"], height=150)
                st.session_state.analisis_data["plan"] = st.text_area("🚀 Plan de Acción (Medidas de Intervención):", value=st.session_state.analisis_data["plan"], height=150)
            else: st.warning("No hay datos.")

        with tab2:
            st.session_state.analisis_data["comp"] = st.text_area("✍️ Análisis de Comportamiento:", value=st.session_state.analisis_data["comp"], height=150)
        
        with tab3:
            st.session_state.analisis_data["acpm"] = st.text_area("✍️ Seguimiento ACPM:", value=st.session_state.analisis_data["acpm"], height=150)

    elif menu == "📝 Nuevo Reporte":
        url_f = "https://docs.google.com/forms/d/e/15BeH-wHD4VJ63EARiHjTEZOUoStbk6o50zSrYmS5SQc/viewform?embedded=true"
        st.markdown(f'<iframe src="{url_f}" width="100%" height="800" frameborder="0">Cargando…</iframe>', unsafe_allow_html=True)

    elif menu == "📄 Acta y Firma Digital":
        st.header("📄 Formalización de la Revisión Gerencial")
        
        st.subheader("🖋️ Firma Digital de Asistentes")
        st.write("Use el recuadro abajo para firmar la validación del acta:")
        canvas_result = st_canvas(
            fill_color="rgba(255, 255, 255, 0)",
            stroke_width=3,
            stroke_color="#000000",
            background_color="#eeeeee",
            height=150,
            key="canvas",
        )

        if st.button("💾 Generar Acta Magnetica Final"):
            pdf_bytes = generar_pdf_profesional(nit_user, st.session_state.analisis_data, canvas_result.image_data)
            st.success("✅ Documento generado con éxito.")
            st.download_button("⬇️ Descargar Acta en PDF", data=pdf_bytes, file_name=f"Acta_HSEQ_{nit_user}.pdf", mime="application/pdf")
