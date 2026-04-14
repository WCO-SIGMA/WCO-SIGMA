import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from fpdf import FPDF
import io

# --- INTENTO DE IMPORTACIÓN PROTEGIDA ---
try:
    from streamlit_canvas import st_canvas
    CANVAS_DISPONIBLE = True
except ImportError:
    CANVAS_DISPONIBLE = False

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

# --- MOTOR PDF MULTI-PÁGINA ---
def generar_pdf_profesional(nit, analisis):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "ACTA DE REVISIÓN GERENCIAL HSEQ", ln=True, align="C")
    pdf.set_font("Arial", "", 10)
    pdf.cell(0, 7, f"NIT: {nit} | Generado: {datetime.now().strftime('%d/%m/%Y %H:%M')}", ln=True, align="C")
    pdf.ln(10)

    secciones = [
        ("ANÁLISIS DE CONDICIONES (SIGMA)", analisis["sigma"]),
        ("CULTURA Y COMPORTAMIENTO", analisis["comp"]),
        ("SEGUIMIENTO ACPM", analisis["acpm"]),
        ("PLAN DE ACCIÓN Y MEDIDAS DE CIERRE", analisis["plan"])
    ]

    for titulo, contenido in secciones:
        pdf.set_font("Arial", "B", 12)
        pdf.set_fill_color(230, 230, 230)
        pdf.cell(0, 8, titulo, ln=True, fill=True)
        pdf.ln(2)
        pdf.set_font("Arial", "", 11)
        # Multi_cell evita que el texto se corte
        pdf.multi_cell(0, 6, contenido if contenido.strip() else "Sin comentarios.")
        pdf.ln(5)

    pdf.ln(10)
    pdf.cell(0, 5, "__________________________", ln=True)
    pdf.cell(0, 5, "Validación Digital WCO-SIGMA", ln=True)
    return pdf.output(dest='S').encode('latin-1', 'ignore')

# 2. INTERFAZ
nit_user = st.sidebar.text_input("Ingrese NIT Empresa:", "").strip()

if not nit_user:
    st.title("🚀 WCO-SIGMA PRO")
    st.info("Ingrese su NIT para activar el Dashboard.")
else:
    df_cond = cargar_datos(URL_COND, nit_user)
    menu = st.sidebar.radio("Navegación", ["📊 Dashboard Gerencial", "📝 Nuevo Reporte", "📄 Acta y Firma"])

    if menu == "📊 Dashboard Gerencial":
        st.header(f"📊 Dashboard de Control - NIT: {nit_user}")
        t1, t2, t3 = st.tabs(["🔍 BDI SIGMA", "🧠 COMPORTAMIENTO", "⚖️ ACPM"])
        
        with t1:
            if not df_cond.empty:
                st.subheader("⚠️ Riesgos Identificados")
                riesgos = ["Mecánico", "Alturas", "Eléctrico", "Emergencias", "Ergonómicos", "Químico", "Vial", "Ambiente"]
                viz_cols = st.columns(3)
                idx = 0
                for r in riesgos:
                    c_found = [c for c in df_cond.columns if r.lower() in c.lower()]
                    if c_found:
                        with viz_cols[idx % 3]:
                            st.plotly_chart(px.pie(df_cond, names=c_found[0], title=f"Riesgo: {r}", hole=0.3), use_container_width=True)
                        idx += 1
                
                st.session_state.analisis_data["sigma"] = st.text_area("✍️ Análisis SIGMA:", value=st.session_state.analisis_data["sigma"])
                st.session_state.analisis_data["plan"] = st.text_area("🚀 Plan de Acción:", value=st.session_state.analisis_data["plan"])
            else: st.warning("No hay datos para este NIT.")

        with t2:
            st.session_state.analisis_data["comp"] = st.text_area("Análisis Comportamiento:", value=st.session_state.analisis_data["comp"])
        with t3:
            st.session_state.analisis_data["acpm"] = st.text_area("Seguimiento ACPM:", value=st.session_state.analisis_data["acpm"])

    elif menu == "📝 Nuevo Reporte":
        url_f = "https://docs.google.com/forms/d/e/15BeH-wHD4VJ63EARiHjTEZOUoStbk6o50zSrYmS5SQc/viewform?embedded=true"
        st.markdown(f'<iframe src="{url_f}" width="100%" height="800" frameborder="0"></iframe>', unsafe_allow_html=True)

    elif menu == "📄 Acta y Firma":
        st.header("📄 Generación de Acta Gerencial")
        if CANVAS_DISPONIBLE:
            st.write("🖋️ Firme aquí antes de generar:")
            st_canvas(stroke_width=3, stroke_color="#000", background_color="#eee", height=150, key="canvas")
        else:
            st.warning("⚠️ El módulo de firma se está instalando. Puede generar el acta sin firma por ahora.")

        if st.button("💾 Generar Acta PDF"):
            pdf_out = generar_pdf_profesional(nit_user, st.session_state.analisis_data)
            st.download_button("⬇️ Descargar PDF", data=pdf_out, file_name=f"Acta_{nit_user}.pdf")
