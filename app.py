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

# --- BLOQUE DE MEMORIA PERMANENTE (SESSION STATE) ---
# Esto garantiza que tus análisis no se borren al dar enter o cambiar de pestaña
if 'an_cond' not in st.session_state: st.session_state.an_cond = ""
if 'pl_cond' not in st.session_state: st.session_state.pl_cond = ""
if 'an_comp' not in st.session_state: st.session_state.an_comp = ""
if 'pl_comp' not in st.session_state: st.session_state.pl_comp = ""
if 'an_acpm' not in st.session_state: st.session_state.an_acpm = ""
if 'pl_acpm' not in st.session_state: st.session_state.pl_acpm = ""

# --- CONEXIONES ---
URL_COND = "https://docs.google.com/spreadsheets/d/18OIJe409rr6o_o4HSweiuncIoOrgJOXEt0GFCmEsL4g/edit"
URL_COMP = "https://docs.google.com/spreadsheets/d/1szrDZsA59e5sMF6OAzPeQ_nDX7E9lMehaXCPHmVNx5o/edit"
URL_ACPM = "https://docs.google.com/spreadsheets/d/1yXQNE3PiET-8VOHBWiReht7psRqjbAm5ZnY4P2XQQvg/edit" 

conn = st.connection("gsheets", type=GSheetsConnection)

# --- MOTOR PDF PROFESIONAL ---
def generar_pdf_pro(nit, ac, pc, ah, ph, aa, pa, fig1, fig2):
    pdf = FPDF()
    # Página 1: Condiciones
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "INFORME GERENCIAL SIG - WCO-SIGMA", ln=True, align="C")
    pdf.set_font("Arial", "", 10)
    pdf.cell(0, 10, f"NIT CLIENTE: {nit} | Fecha: {datetime.now().strftime('%d/%m/%Y')}", ln=True, align="C")
    pdf.ln(5)
    
    pdf.set_font("Arial", "B", 12)
    pdf.set_fill_color(230, 230, 230)
    pdf.cell(0, 10, "1. GESTION DE CONDICIONES HSEQ", ln=True, fill=True)
    pdf.set_font("Arial", "", 10)
    pdf.multi_cell(0, 6, f"DIAGNOSTICO: {ac}\nPLAN DE ACCION: {pc}")
    
    try:
        img_bytes1 = fig1.to_image(format="png")
        pdf.image(io.BytesIO(img_bytes1), x=15, w=170)
    except: pdf.cell(0, 10, "[Gráfico de Condiciones no disponible en PDF]", ln=True)

    # Página 2: Comportamiento y ACPM
    pdf.add_page()
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "2. COMPORTAMIENTO Y MEJORA CONTINUA", ln=True, fill=True)
    pdf.set_font("Arial", "", 10)
    pdf.multi_cell(0, 6, f"ANALISIS CONDUCTUAL: {ah}\nPLAN CONDUCTUAL: {ph}")
    pdf.ln(5)
    pdf.multi_cell(0, 6, f"ANALISIS MEJORA (ACPM): {aa}\nPLAN DE MEJORA: {pa}")
    
    try:
        img_bytes2 = fig2.to_image(format="png")
        pdf.image(io.BytesIO(img_bytes2), x=15, w=170)
    except: pdf.cell(0, 10, "[Gráfico de ACPM no disponible en PDF]", ln=True)
    
    return pdf.output(dest='S').encode('latin-1', 'ignore')

# 2. ACCESO
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/1063/1063302.png", width=80)
nit_user = st.sidebar.text_input("Ingrese NIT Empresa:", "").strip()

if not nit_user:
    st.title("🚀 WCO-SIGMA: Suite de Gestión PHVA")
    st.info("Sistemas conectados. Ingrese el NIT para cargar datos.")
else:
    def cargar(url):
        try:
            df = conn.read(spreadsheet=url, ttl=0)
            df.columns = df.columns.str.strip()
            col_nit = [c for c in df.columns if c.lower() == 'nit'][0]
            df['Nit_M'] = df[col_nit].astype(str).apply(lambda x: x.split('.')[0].strip())
            return df, df[df['Nit_M'] == nit_user]
        except: return pd.DataFrame(), pd.DataFrame()

    df_cond_t, df_cond_e = cargar(URL_COND)
    df_comp_t, df_comp_e = cargar(URL_COMP)
    df_acpm_t, df_acpm_e = cargar(URL_ACPM)

    menu = st.sidebar.radio("Navegación", ["📊 Dashboard Gerencial", "⚖️ Registro ACPM", "🛠️ Registro Condiciones", "🧠 Registro Comportamiento"])

    # --- PANTALLA DASHBOARD ---
    if menu == "📊 Dashboard Gerencial":
        st.title(f"📊 Control Gerencial - NIT: {nit_user}")
        t1, t2, t3 = st.tabs(["🔍 Condiciones", "🧠 Comportamiento", "⚖️ ACPM"])
        
        with t1:
            if not df_cond_e.empty:
                f_c = px.pie(df_cond_e, names='Estado', title="Estatus General de Condiciones", hole=0.3)
                st.plotly_chart(f_c, use_container_width=True)
                # Vinculación directa a la MEMORIA
                st.session_state.an_cond = st.text_area("Análisis Condiciones:", value=st.session_state.an_cond, key="txt_ac")
                st.session_state.pl_cond = st.text_area("Plan de Acción:", value=st.session_state.pl_cond, key="txt_pc")
            else: st.warning("Sin datos.")

        with t2:
            if not df_comp_e.empty:
                st.plotly_chart(px.bar(df_comp_e, x='Estado observado', title="Cultura de Seguridad"), use_container_width=True)
                st.session_state.an_comp = st.text_area("Análisis Conductual:", value=st.session_state.an_comp, key="txt_ah")
                st.session_state.pl_comp = st.text_area("Estrategia Humana:", value=st.session_state.pl_comp, key="txt_ph")

        with t3:
            if not df_acpm_e.empty:
                f_a = px.bar(df_acpm_e, x='Estado', color='Componente', title="Avance de ACPM")
                st.plotly_chart(f_a, use_container_width=True)
                st.session_state.an_acpm = st.text_area("Análisis ACPM:", value=st.session_state.an_acpm, key="txt_aa")
                st.session_state.pl_acpm = st.text_area("Plan Mejora Continua:", value=st.session_state.pl_acpm, key="txt_pa")
                st.dataframe(df_acpm_e)

        # BOTÓN PDF
        st.sidebar.markdown("---")
        if st.sidebar.button("📄 Procesar Reporte Final"):
            with st.spinner("Generando Informe..."):
                pdf_res = generar_pdf_pro(nit_user, st.session_state.an_cond, st.session_state.pl_cond, 
                                          st.session_state.an_comp, st.session_state.pl_comp, 
                                          st.session_state.an_acpm, st.session_state.pl_acpm, f_c, f_a)
                st.sidebar.download_button("⬇️ Descargar PDF", data=pdf_res, file_name=f"Informe_SIG_{nit_user}.pdf")

    # --- LOS FORMULARIOS SIGUEN IGUAL (MANTENIENDO TODAS LAS VARIABLES) ---
    elif menu == "⚖️ Registro ACPM":
        st.title("⚖️ Registro de ACPM")
        with st.form("f_acpm"):
            # (Variables de ayer: 5 porqués, gestión del cambio, etc.)
            col1, col2 = st.columns(2)
            with col1:
                f_em = st.text_input("Empresa")
                f_co = st.selectbox("Componente", ["SST", "Ambiente", "Calidad", "Vial"])
                f_de = st.text_area("Hallazgo")
                p1, p2, p3, p4, p5 = st.text_input("P1"), st.text_input("P2"), st.text_input("P3"), st.text_input("P4"), st.text_input("P5")
            with col2:
                f_ra = st.text_input("Causa raíz")
                f_ac = st.text_area("Acción Propuesta")
                f_ti = st.radio("Tipo Acción", ["Correctiva", "Preventiva", "Mejora"])
                f_es = st.selectbox("Estado", ["Abierta", "En Ejecución", "Cerrada"])
                f_gc = st.radio("¿Activa Gestión del Cambio?", ["No", "Sí"])
            if st.form_submit_button("💾 GUARDAR"):
                n_a = pd.DataFrame([{"Nit":str(nit_user), "Empresa":f_em, "Fecha de reporte":str(datetime.now().date()), "Componente":f_co, "Fuente":"Auditoría", "Descripción Hallazgo":f_de, "Análisis Causa ¿Porqué 1?":p1, "Análisis Causa ¿Porqué 2?":p2, "Análisis Causa ¿Porqué 3?":p3, "Análisis Causa ¿Porqué 4?":p4, "Análisis Causa ¿Porqué 5?":p5, "Causa raíz":f_ra, "Acción Propuesta":f_ac, "Tipo Acción":f_ti, "La acción tomada activa gestión del cambio":f_gc, "Estado":f_es}])
                conn.update(spreadsheet=URL_ACPM, data=pd.concat([df_acpm_t, n_a], ignore_index=True))
                st.success("Guardado.")
    # (Resto de formularios se mantienen igual)
