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

# --- URLs DE BASES DE DATOS ---
URL_COND = "https://docs.google.com/spreadsheets/d/18OIJe409rr6o_o4HSweiuncIoOrgJOXEt0GFCmEsL4g/edit"
URL_COMP = "https://docs.google.com/spreadsheets/d/1szrDZsA59e5sMF6OAzPeQ_nDX7E9lMehaXCPHmVNx5o/edit"
URL_ACPM = "https://docs.google.com/spreadsheets/d/1yXQNE3PiET-8VOHBWiReht7psRqjbAm5ZnY4P2XQQvg/edit" 

conn = st.connection("gsheets", type=GSheetsConnection)

# --- FUNCIÓN GENERADORA DE PDF CON GRÁFICOS ---
def crear_pdf_visual(nit, ac, pc, ah, ph, aa, pa, fig1, fig2):
    pdf = FPDF()
    # PÁGINA 1: CONDICIONES
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "INFORME GERENCIAL INTEGRAL - WCO-SIGMA", ln=True, align="C")
    pdf.set_font("Arial", "", 10)
    pdf.cell(0, 10, f"NIT: {nit} | Generado: {datetime.now().strftime('%d/%m/%Y')}", ln=True, align="C")
    pdf.ln(5)
    
    pdf.set_font("Arial", "B", 12)
    pdf.set_fill_color(230, 230, 230)
    pdf.cell(0, 10, "1. GESTION DE CONDICIONES HSEQ", ln=True, fill=True)
    pdf.set_font("Arial", "", 10)
    pdf.multi_cell(0, 7, f"DIAGNOSTICO: {ac}\nPLAN: {pc}")
    
    try:
        img_buf1 = io.BytesIO()
        fig1.write_image(img_buf1, format="png", width=700, height=350)
        pdf.image(img_buf1, x=15, w=170)
    except: pdf.cell(0, 10, "[Error al procesar gráfico de condiciones]", ln=True)

    # PÁGINA 2: COMPORTAMIENTO Y ACPM
    pdf.add_page()
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "2. ANALISIS CONDUCTUAL Y MEJORA (ACPM)", ln=True, fill=True)
    pdf.set_font("Arial", "", 10)
    pdf.multi_cell(0, 7, f"ANALISIS COMPORTAMIENTO: {ah}\nPLAN: {ph}")
    pdf.ln(5)
    pdf.multi_cell(0, 7, f"ANALISIS ACPM: {aa}\nPLAN: {pa}")
    
    try:
        img_buf2 = io.BytesIO()
        fig2.write_image(img_buf2, format="png", width=700, height=350)
        pdf.image(img_buf2, x=15, w=170)
    except: pdf.cell(0, 10, "[Error al procesar gráfico de ACPM]", ln=True)
    
    return pdf.output(dest='S').encode('latin-1', 'ignore')

# 2. ACCESO POR NIT
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/1063/1063302.png", width=100)
nit_user = st.sidebar.text_input("Ingrese identificación (NIT/Cédula):", "").strip()

if not nit_user:
    st.title("🚀 WCO-SIGMA: Suite de Gestión PHVA")
    st.info("Motores conectados. Ingrese el NIT para activar el Dashboard y Reportes.")
else:
    def cargar(url):
        try:
            df = conn.read(spreadsheet=url, ttl=0)
            if df is not None and not df.empty:
                df.columns = df.columns.str.strip()
                col_nit = [c for c in df.columns if c.lower() == 'nit'][0]
                df['Nit_M'] = df[col_nit].astype(str).apply(lambda x: x.split('.')[0].strip())
                return df, df[df['Nit_M'] == nit_user]
            return pd.DataFrame(), pd.DataFrame()
        except: return pd.DataFrame(), pd.DataFrame()

    df_cond_t, df_cond_e = cargar(URL_COND)
    df_comp_t, df_comp_e = cargar(URL_COMP)
    df_acpm_t, df_acpm_e = cargar(URL_ACPM)

    menu = st.sidebar.radio("Navegación", ["📊 Dashboard Gerencial", "⚖️ Gestión de ACPM", "🛠️ Reporte Condiciones", "🧠 Reporte Comportamiento"])

    # --- PANTALLA 1: DASHBOARD ---
    if menu == "📊 Dashboard Gerencial":
        st.title(f"📊 Control Gerencial - NIT: {nit_user}")
        tab1, tab2, tab3 = st.tabs(["🔍 Condiciones", "🧠 Comportamiento", "⚖️ ACPM"])
        
        with tab1:
            f_cond_pie = px.pie(df_cond_e, names='Estado', title="Estatus de Cierre", hole=0.3)
            st.plotly_chart(f_cond_pie, use_container_width=True)
            txt_an_c = st.text_area("Análisis Condiciones:", key="ac_v16")
            txt_pl_c = st.text_area("Plan Acción:", key="pc_v16")

        with tab2:
            st.plotly_chart(px.bar(df_comp_e, x='Estado observado', title="Cultura de Seguridad"), use_container_width=True)
            txt_an_h = st.text_area("Análisis Conductual:", key="ah_v16")
            txt_pl_h = st.text_area("Estrategia Humana:", key="ph_v16")

        with tab3:
            f_acpm_bar = px.bar(df_acpm_e, x='Estado', color='Componente', title="Avance de ACPM")
            st.plotly_chart(f_acpm_bar, use_container_width=True)
            txt_an_a = st.text_area("Análisis ACPM:", key="aa_v16")
            txt_pl_a = st.text_area("Plan Mejora:", key="pa_v16")

        if st.sidebar.button("📄 Generar Reporte con Gráficos"):
            with st.spinner("Procesando imágenes..."):
                pdf_bytes = crear_pdf_visual(nit_user, txt_an_c, txt_pl_c, txt_an_h, txt_pl_h, txt_an_a, txt_pl_a, f_cond_pie, f_acpm_bar)
                st.sidebar.download_button("⬇️ Descargar Reporte PDF", data=pdf_bytes, file_name=f"Reporte_Visual_{nit_user}.pdf", mime="application/pdf")

    # --- PANTALLA 2: GESTIÓN DE ACPM ---
    elif menu == "⚖️ Gestión de ACPM":
        st.title("⚖️ Registro de ACPM")
        with st.form("f_acpm_v16"):
            c1, c2 = st.columns(2)
            with c1:
                f_emp = st.text_input("Empresa")
                f_comp = st.selectbox("Componente", ["SST", "Ambiente", "Calidad", "Vial"])
                f_desc = st.text_area("Hallazgo")
                p1, p2, p3, p4, p5 = st.text_input("P1"), st.text_input("P2"), st.text_input("P3"), st.text_input("P4"), st.text_input("P5")
            with c2:
                f_raiz = st.text_input("Causa raíz")
                f_acci = st.text_area("Acción Propuesta")
                f_tipo = st.radio("Tipo Acción", ["Correctiva", "Preventiva", "Mejora"])
                f_esta = st.selectbox("Estado", ["Abierta", "En Ejecución", "Cerrada"])
            if st.form_submit_button("💾 GUARDAR ACPM"):
                n_a = pd.DataFrame([{"Nit":str(nit_user), "Empresa":f_emp, "Fecha de reporte":str(datetime.now().date()), "Componente":f_comp, "Descripción Hallazgo":f_desc, "Análisis Causa ¿Porqué 1?":p1, "Análisis Causa ¿Porqué 2?":p2, "Análisis Causa ¿Porqué 3?":p3, "Análisis Causa ¿Porqué 4?":p4, "Análisis Causa ¿Porqué 5?":p5, "Causa raíz":f_raiz, "Acción Propuesta":f_acci, "Tipo Acción":f_tipo, "Estado":f_esta}])
                conn.update(spreadsheet=URL_ACPM, data=pd.concat([df_acpm_t, n_a], ignore_index=True))
                st.success("Guardado.")

    # --- PANTALLA 3: REPORTE CONDICIONES ---
    elif menu == "🛠️ Reporte Condiciones":
        st.title("🛠️ Registro de Condiciones HSEQ")
        with st.form("f_cond_v16"):
            c1, c2 = st.columns(2)
            with c1:
                f_ct = st.text_input("Centro de trabajo")
                f_lg = st.text_input("Lugar")
                f_hl = st.text_area("Hallazgo")
            with c2:
                f_cc = st.selectbox("Condición Crítica", ["Orden/Aseo", "Herramientas", "Locativo", "Vial", "Otros"])
                f_pr = st.selectbox("Prioridad", ["Baja", "Media", "Alta"])
                f_es = st.selectbox("Estado", ["Abierto", "En Proceso", "Cerrado"])
            if st.form_submit_button("✅ GUARDAR CONDICIÓN"):
                n_c = pd.DataFrame([{"Nit":str(nit_user), "Empresa":"Sede", "Centro de trabajo":f_ct, "Lugar":f_lg, "Fecha":str(datetime.now().date()), "Hallazgo":f_hl, "Condición Crítica":f_cc, "Prioridad":f_pr, "Estado":f_es}])
                conn.update(spreadsheet=URL_COND, data=pd.concat([df_cond_t, n_c], ignore_index=True))
                st.success("Guardado.")

    # --- PANTALLA 4: REPORTE COMPORTAMIENTO ---
    elif menu == "🧠 Reporte Comportamiento":
        st.title("🧠 Registro de Comportamiento")
        with st.form("f_comp_v16"):
            f_in = st.text_input("Inspector")
            f_cth = st.text_input("Centro de trabajo")
            f_lgh = st.text_input("Lugar")
            f_est = st.selectbox("Estado observado", ["✅ SEGURO", "⚠️ ATÍPICO", "🚫 PELIGROSO"])
            if st.form_submit_button("🚀 REGISTRAR"):
                n_h = pd.DataFrame([{"Nit":str(nit_user), "Fecha/Hora Real":str(datetime.now()), "Inspector":f_in, "Centro de trabajo":f_cth, "Lugar":f_lgh, "Estado observado":f_est}])
                conn.update(spreadsheet=URL_COMP, data=pd.concat([df_comp_t, n_h], ignore_index=True))
                st.success("Registrado.")
