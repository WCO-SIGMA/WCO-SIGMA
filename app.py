import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.express as px
from datetime import datetime
import uuid
from fpdf import FPDF

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="WCO-SIGMA SIG+ACPM", layout="wide")

# --- CONFIGURACIÓN DE CONEXIONES (URLs) ---
URL_COND = "https://docs.google.com/spreadsheets/d/18OIJe409rr6o_o4HSweiuncIoOrgJOXEt0GFCmEsL4g/edit"
URL_COMP = "https://docs.google.com/spreadsheets/d/1szrDZsA59e5sMF6OAzPeQ_nDX7E9lMehaXCPHmVNx5o/edit"
URL_ACPM = "https://docs.google.com/spreadsheets/d/16ZgE9R5o4l8P7Tz7xS9u3v4W3Y1vW-J1/edit" 

conn = st.connection("gsheets", type=GSheetsConnection)

# --- FUNCIÓN PDF ---
def crear_pdf(nit, an_c, pl_c, an_h, pl_h):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "INFORME INTEGRAL PHVA - WCO-SIGMA", ln=True, align="C")
    pdf.ln(10)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, f"NIT: {nit}", ln=True)
    pdf.set_font("Arial", "", 10)
    pdf.multi_cell(0, 7, f"ANALISIS CONDICIONES: {an_c}\nPLAN: {pl_c}")
    pdf.ln(5)
    pdf.multi_cell(0, 7, f"ANALISIS COMPORTAMIENTO: {an_h}\nPLAN: {pl_h}")
    return pdf.output(dest='S').encode('latin-1', 'ignore')

# 2. ACCESO POR NIT
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/1063/1063302.png", width=100)
nit_user = st.sidebar.text_input("Ingrese identificación (NIT/Cédula):", "").strip()

if not nit_user:
    st.title("🚀 WCO-SIGMA: Gestión PHVA")
    st.info("Ingrese su NIT para activar el tablero.")
else:
    # --- MOTOR DE LECTURA ROBUSTO ---
    def cargar(url):
        try:
            df = conn.read(spreadsheet=url, ttl=0)
            if df is not None and not df.empty:
                df.columns = df.columns.str.strip()
                # Buscar columna NIT (insensible a mayúsculas)
                col_nit = [c for c in df.columns if c.lower() == 'nit'][0]
                df['Nit_Match'] = df[col_nit].astype(str).apply(lambda x: x.split('.')[0].strip())
                return df, df[df['Nit_Match'] == nit_user]
            return pd.DataFrame(), pd.DataFrame()
        except: return pd.DataFrame(), pd.DataFrame()

    df_cond_t, df_cond_e = cargar(URL_COND)
    df_comp_t, df_comp_e = cargar(URL_COMP)
    df_acpm_t, df_acpm_e = cargar(URL_ACPM)

    menu = st.sidebar.radio("Menú", ["📊 Dashboard Gerencial", "⚖️ Gestión de ACPM", "🛠️ Reporte Condiciones", "🧠 Reporte Comportamiento"])

    # --- PANTALLA 1: DASHBOARD ---
    if menu == "📊 Dashboard Gerencial":
        st.title(f"📊 Control Gerencial - NIT: {nit_user}")
        t1, t2, t3 = st.tabs(["🔍 Condiciones", "🧠 Comportamiento", "⚖️ ACPM"])
        
        with t1:
            if not df_cond_e.empty:
                col_a, col_b = st.columns(2)
                with col_a:
                    st.plotly_chart(px.bar(df_cond_e, x='Centro de trabajo', color='Prioridad', title="Hallazgos por Centro"), use_container_width=True)
                    st.plotly_chart(px.pie(df_cond_e, names='Condición Crítica', title="Condiciones Críticas"), use_container_width=True)
                with col_b:
                    st.plotly_chart(px.bar(df_cond_e, x='Lugar', color='Estado', title="Hallazgos por Lugar"), use_container_width=True)
                    st.plotly_chart(px.pie(df_cond_e, names='Prioridad', title="Urgencia"), use_container_width=True)
                txt_an_c = st.text_area("Análisis Condiciones:", key="ac_v15")
                txt_pl_c = st.text_area("Plan Acción:", key="pc_v15")
            else: st.warning("No hay datos de Condiciones.")

        with t2:
            if not df_comp_e.empty:
                st.plotly_chart(px.bar(df_comp_e, x='Centro de trabajo', color='Estado observado', title="Cultura por Centro"), use_container_width=True)
                st.plotly_chart(px.pie(df_comp_e, names='Estado observado', title="Estatus Observaciones"), use_container_width=True)
                txt_an_h = st.text_area("Análisis Humano:", key="ah_v15")
                txt_pl_h = st.text_area("Plan Comportamiento:", key="ph_v15")
            else: st.warning("No hay datos de Comportamiento.")

        with t3:
            st.subheader("⚖️ Gestión de Mejora (ACPM)")
            if not df_acpm_e.empty:
                ca1, ca2 = st.columns(2)
                with ca1:
                    st.plotly_chart(px.pie(df_acpm_e, names='Componente', title="ACPM por Sistema", hole=0.4), use_container_width=True)
                    st.plotly_chart(px.bar(df_acpm_e, x='Causa raíz', color='Estado', title="Causas Raíz"), use_container_width=True)
                with ca2:
                    st.plotly_chart(px.bar(df_acpm_e, x='Fuente', color='Tipo Acción', title="Fuente vs Acción"), use_container_width=True)
                    st.plotly_chart(px.pie(df_acpm_e, names='Estado', title="Estatus ACPM"), use_container_width=True)
            else:
                st.error("❌ Sin datos en ACPM. Verifique el NIT o que el archivo sea público.")

        if st.sidebar.button("📄 Generar PDF"):
            pdf_bytes = crear_pdf(nit_user, txt_an_c, txt_pl_c, txt_an_h, txt_pl_h)
            st.sidebar.download_button("⬇️ Descargar", data=pdf_bytes, file_name=f"Reporte_{nit_user}.pdf")

    # --- PANTALLAS DE REPORTE (VARIABLES COMPLETAS) ---
    elif menu == "⚖️ Gestión de ACPM":
        st.title("⚖️ Registro de ACPM")
        with st.form("form_acpm"):
            c1, c2 = st.columns(2)
            with c1:
                f_emp = st.text_input("Empresa")
                f_comp = st.selectbox("Componente", ["SST", "Ambiente", "Calidad", "Vial"])
                f_fuen = st.selectbox("Fuente", ["Inspección", "Auditoría", "Incidente", "Sugerencia"])
                f_desc = st.text_area("Hallazgo")
                p1, p2, p3 = st.text_input("P1"), st.text_input("P2"), st.text_input("P3")
            with c2:
                f_raiz = st.text_input("Causa raíz")
                f_acci = st.text_area("Plan Acción")
                f_tipo = st.radio("Tipo Acción", ["Correctiva", "Preventiva", "Mejora"])
                f_esta = st.selectbox("Estado", ["Abierta", "En Ejecución", "Cerrada"])
            if st.form_submit_button("💾 GUARDAR"):
                # Aquí usamos la tabla total para concatenar
                n_a = pd.DataFrame([{"Nit":str(nit_user), "Empresa":f_emp, "Fecha de reporte":str(datetime.now().date()), "Componente":f_comp, "Fuente":f_fuen, "Descripción Hallazgo":f_desc, "Causa raíz":f_raiz, "Acción Propuesta":f_acci, "Tipo Acción":f_tipo, "Estado":f_esta}])
                conn.update(spreadsheet=URL_ACPM, data=pd.concat([df_acpm_t, n_a], ignore_index=True))
                st.success("Guardado.")

    elif menu == "🛠️ Reporte Condiciones":
        st.title("🛠️ Registro de Condiciones")
        with st.form("form_cond"):
            c1, c2 = st.columns(2)
            with c1:
                f_ct = st.text_input("Centro de trabajo")
                f_lg = st.text_input("Lugar")
                f_hl = st.text_area("Hallazgo")
                f_cr = st.selectbox("Condición Crítica", ["Orden/Aseo", "Mecánico", "Eléctrico", "Vial", "Otro"])
            with c2:
                f_cl = st.selectbox("Clasificación Riesgo", ["Físico", "Químico", "Biomecánico", "Seguridad"])
                f_pr = st.selectbox("Prioridad", ["Baja", "Media", "Alta"])
                f_es = st.selectbox("Estado", ["Abierto", "En Proceso", "Cerrado"])
            if st.form_submit_button("✅ GUARDAR"):
                n_c = pd.DataFrame([{"Nit":str(nit_user), "Centro de trabajo":f_ct, "Lugar":f_lg, "Fecha":str(datetime.now().date()), "Hallazgo":f_hl, "Condición Crítica":f_cr, "Clasificación del riesgo":f_cl, "Prioridad":f_pr, "Estado":f_es}])
                conn.update(spreadsheet=URL_COND, data=pd.concat([df_cond_t, n_c], ignore_index=True))
                st.success("Guardado.")

    elif menu == "🧠 Reporte Comportamiento":
        st.title("🧠 Registro de Comportamiento")
        with st.form("form_comp"):
            f_in = st.text_input("Inspector")
            f_ct_h = st.text_input("Centro de trabajo")
            f_lg_h = st.text_input("Lugar")
            f_est = st.selectbox("Estado observado", ["✅ SEGURO", "⚠️ ATÍPICO", "🚫 PELIGROSO"])
            f_obs = st.text_area("Observaciones")
            if st.form_submit_button("🚀 REGISTRAR"):
                n_h = pd.DataFrame([{"Nit":str(nit_user), "Fecha/Hora Real":str(datetime.now()), "Inspector":f_in, "Centro de trabajo":f_ct_h, "Lugar":f_lg_h, "Estado observado":f_est, "Observaciones Factor Humano":f_obs}])
                conn.update(spreadsheet=URL_COMP, data=pd.concat([df_comp_t, n_h], ignore_index=True))
                st.success("Registrado.")
