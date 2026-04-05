import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.express as px
from datetime import datetime
import io
from fpdf import FPDF

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="WCO-SIGMA SIG+ACPM", layout="wide")

# --- MEMORIA DE SESIÓN ROBUSTA ---
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

# --- MOTOR PDF (SIMPLIFICADO PARA ESTABILIDAD) ---
def crear_pdf_final(nit, ac, pc, ah, ph, aa, pa):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "INFORME ESTRATEGICO - WCO-SIGMA", ln=True, align="C")
    pdf.set_font("Arial", "", 10)
    pdf.cell(0, 10, f"NIT: {nit} | Generado el: {datetime.now().strftime('%d/%m/%Y %H:%M')}", ln=True, align="C")
    pdf.ln(10)
    
    sections = [
        ("1. CONDICIONES HSEQ", ac, pc),
        ("2. COMPORTAMIENTO", ah, ph),
        ("3. MEJORA CONTINUA (ACPM)", aa, pa)
    ]
    
    for titulo, anal, plan in sections:
        pdf.set_font("Arial", "B", 12)
        pdf.set_fill_color(230, 230, 230)
        pdf.cell(0, 10, titulo, ln=True, fill=True)
        pdf.set_font("Arial", "B", 10)
        pdf.cell(0, 7, "ANALISIS:", ln=True)
        pdf.set_font("Arial", "", 10)
        pdf.multi_cell(0, 6, anal if anal else "Sin análisis registrado.")
        pdf.ln(2)
        pdf.set_font("Arial", "B", 10)
        pdf.cell(0, 7, "PLAN DE ACCION:", ln=True)
        pdf.set_font("Arial", "", 10)
        pdf.multi_cell(0, 6, plan if plan else "Sin plan registrado.")
        pdf.ln(5)
        
    return pdf.output(dest='S').encode('latin-1', 'ignore')

# 2. ACCESO Y BARRA LATERAL
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/1063/1063302.png", width=80)
nit_user = st.sidebar.text_input("Identificación (NIT):", "").strip()

# --- BOTÓN DE PDF SIEMPRE VISIBLE EN LA SIDEBAR ---
if nit_user:
    st.sidebar.markdown("---")
    st.sidebar.subheader("📄 Reporte Ejecutivo")
    if st.sidebar.button("⚙️ Procesar Informe"):
        try:
            pdf_out = crear_pdf_final(nit_user, 
                                     st.session_state.an_cond, st.session_state.pl_cond,
                                     st.session_state.an_comp, st.session_state.pl_comp,
                                     st.session_state.an_acpm, st.session_state.pl_acpm)
            st.sidebar.download_button("⬇️ DESCARGAR PDF", data=pdf_out, file_name=f"Reporte_{nit_user}.pdf", mime="application/pdf")
            st.sidebar.success("PDF Listo para descarga")
        except Exception as e:
            st.sidebar.error(f"Error al generar: {e}")
    st.sidebar.markdown("---")

# 3. CARGA Y VISUALIZACIÓN
if not nit_user:
    st.title("🚀 WCO-SIGMA")
    st.info("Ingrese NIT para activar Dashboard.")
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

    menu = st.sidebar.radio("Menú Principal", ["📊 Dashboard Gerencial", "⚖️ Registro ACPM", "🛠️ Registro Condiciones", "🧠 Registro Comportamiento"])

    if menu == "📊 Dashboard Gerencial":
        st.title(f"📊 Control Gerencial - NIT: {nit_user}")
        t1, t2, t3 = st.tabs(["🔍 BDI SIGMA", "🧠 BDI COMPORTAMIENTO", "⚖️ BD ACPM"])
        
        with t1: # CONDICIONES
            if not df_cond_e.empty:
                c1, c2 = st.columns(2)
                c1.plotly_chart(px.bar(df_cond_e, x='Centro de trabajo', color='Prioridad', title="Hallazgos por Centro"), use_container_width=True)
                c2.plotly_chart(px.bar(df_cond_e, x='Lugar', color='Estado', title="Estatus por Lugar"), use_container_width=True)
                st.plotly_chart(px.pie(df_cond_e, names='Condición Crítica', title="Condiciones Críticas Detectadas"), use_container_width=True)
                # MEMORIA
                st.session_state.an_cond = st.text_area("Diagnóstico (Condiciones):", value=st.session_state.an_cond)
                st.session_state.pl_cond = st.text_area("Plan Acción (Condiciones):", value=st.session_state.pl_cond)
            else: st.warning("Sin datos en Condiciones.")

        with t2: # COMPORTAMIENTO
            if not df_comp_e.empty:
                st.plotly_chart(px.bar(df_comp_e, x='Centro de trabajo', color='Estado observado', title="Cultura por Centro"), use_container_width=True)
                st.plotly_chart(px.bar(df_comp_e, x='Lugar', color='Estado observado', title="Cultura por Lugar"), use_container_width=True)
                st.session_state.an_comp = st.text_area("Análisis (Comportamiento):", value=st.session_state.an_comp)
                st.session_state.pl_comp = st.text_area("Plan Acción (Comportamiento):", value=st.session_state.pl_comp)
            else: st.warning("Sin datos en Comportamiento.")

        with t3: # ACPM
            if not df_acpm_e.empty:
                a1, a2 = st.columns(2)
                a1.plotly_chart(px.pie(df_acpm_e, names='Componente', title="ACPM por Componente"), use_container_width=True)
                a2.plotly_chart(px.bar(df_acpm_e, x='Causa raíz', color='Estado', title="Causa Raíz"), use_container_width=True)
                st.plotly_chart(px.bar(df_acpm_e, x='Fuente', color='Tipo Acción', title="Fuente vs Tipo Acción"), use_container_width=True)
                st.session_state.an_acpm = st.text_area("Análisis (ACPM):", value=st.session_state.an_acpm)
                st.session_state.pl_acpm = st.text_area("Plan Acción (ACPM):", value=st.session_state.pl_acpm)
            else: st.warning("Sin datos en ACPM.")

    # --- FORMULARIOS (MANTENIENDO VISIBILIDAD) ---
    elif menu == "🛠️ Registro Condiciones":
        st.title("🛠️ Registro de Condiciones")
        with st.form("f_cond"):
            f_ct = st.text_input("Centro de trabajo")
            f_lg = st.text_input("Lugar")
            f_hl = st.text_area("Hallazgo")
            f_cc = st.selectbox("Condición Crítica", ["Orden/Aseo", "Herramientas", "Locativo", "Vial", "Otros"])
            f_tr = st.selectbox("Riesgo", ["Físico", "Químico", "Biológico", "Seguridad", "Natural"])
            f_pr = st.selectbox("Prioridad", ["Baja", "Media", "Alta"])
            f_es = st.selectbox("Estado", ["Abierto", "En Proceso", "Cerrado"])
            if st.form_submit_button("💾 GUARDAR"):
                nueva = pd.DataFrame([{"Nit":str(nit_user), "Centro de trabajo":f_ct, "Lugar":f_lg, "Hallazgo":f_hl, "Condición Crítica":f_cc, "Clasificación del riesgo":f_tr, "Prioridad":f_pr, "Estado":f_es, "Fecha":str(datetime.now().date())}])
                conn.update(spreadsheet=URL_COND, data=pd.concat([df_cond_t, nueva], ignore_index=True))
                st.success("Guardado.")

    elif menu == "🧠 Registro Comportamiento":
        st.title("🧠 Registro de Comportamiento")
        with st.form("f_comp"):
            f_in = st.text_input("Inspector")
            f_ct = st.text_input("Centro de trabajo")
            f_lg = st.text_input("Lugar")
            f_eo = st.selectbox("Estado observado", ["✅ SEGURO", "⚠️ ATÍPICO", "🚫 PELIGROSO"])
            if st.form_submit_button("🚀 REGISTRAR"):
                nueva = pd.DataFrame([{"Nit":str(nit_user), "Fecha/Hora Real":str(datetime.now()), "Inspector":f_in, "Centro de trabajo":f_ct, "Lugar":f_lg, "Estado observado":f_eo}])
                conn.update(spreadsheet=URL_COMP, data=pd.concat([df_comp_t, nueva], ignore_index=True))
                st.success("Registrado.")

    elif menu == "⚖️ Registro ACPM":
        st.title("⚖️ Gestión de Mejora (ACPM)")
        with st.form("f_acpm"):
            f_em = st.text_input("Empresa")
            f_co = st.selectbox("Componente", ["SST", "Ambiente", "Calidad", "Vial"])
            f_fu = st.selectbox("Fuente", ["Auditoría", "Inspección", "Incidente"])
            p1 = st.text_input("¿Por qué 1?")
            f_ra = st.text_input("Causa raíz")
            f_ti = st.radio("Tipo Acción", ["Correctiva", "Preventiva", "Mejora"])
            f_es = st.selectbox("Estado", ["Abierta", "En Ejecución", "Cerrada"])
            if st.form_submit_button("💾 GUARDAR ACPM"):
                nueva = pd.DataFrame([{"Nit":str(nit_user), "Empresa":f_em, "Componente":f_co, "Fuente":f_fu, "Análisis Causa ¿Porqué 1?":p1, "Causa raíz":f_ra, "Tipo Acción":f_ti, "Estado":f_es}])
                conn.update(spreadsheet=URL_ACPM, data=pd.concat([df_acpm_t, nueva], ignore_index=True))
                st.success("Guardado.")
