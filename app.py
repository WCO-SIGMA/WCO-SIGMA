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

# --- MOTOR DE PDF ---
def generar_pdf_final(nit, an_c, pl_c, an_h, pl_h):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "INFORME DE GESTION SIG - WCO-SIGMA", ln=True, align="C")
    pdf.set_font("Arial", "", 10)
    pdf.cell(0, 10, f"NIT: {nit} | Fecha: {datetime.now().strftime('%d/%m/%Y')}", ln=True, align="C")
    pdf.ln(10)
    
    # Análisis Condiciones
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "1. ANALISIS DE CONDICIONES HSEQ", ln=True)
    pdf.set_font("Arial", "", 10)
    pdf.multi_cell(0, 7, f"DIAGNOSTICO: {an_c}\nPLAN: {pl_c}")
    pdf.ln(5)
    
    # Análisis Comportamiento
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "2. ANALISIS DE COMPORTAMIENTO", ln=True)
    pdf.set_font("Arial", "", 10)
    pdf.multi_cell(0, 7, f"DIAGNOSTICO: {an_h}\nPLAN: {pl_h}")
    
    return pdf.output(dest='S').encode('latin-1', 'ignore')

# 2. ACCESO
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/1063/1063302.png", width=100)
nit_user = st.sidebar.text_input("Ingrese identificación (NIT/Cédula):", "").strip()

if not nit_user:
    st.title("🚀 WCO-SIGMA: Suite de Gestión PHVA")
    st.info("Ingrese su NIT para activar el sistema integral.")
else:
    # --- CARGA DE DATOS ---
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

    # --- DASHBOARD ---
    if menu == "📊 Dashboard Gerencial":
        st.title(f"📊 Tablero Gerencial - NIT: {nit_user}")
        t1, t2, t3 = st.tabs(["🔍 Condiciones", "🧠 Comportamiento", "⚖️ ACPM"])
        
        with t1:
            if not df_cond_e.empty:
                c1, c2 = st.columns(2)
                with c1:
                    st.plotly_chart(px.bar(df_cond_e, x='Centro de trabajo', color='Prioridad', title="Hallazgos por Centro"), use_container_width=True)
                    st.plotly_chart(px.pie(df_cond_e, names='Condición Crítica', title="Condiciones Críticas"), use_container_width=True)
                with c2:
                    st.plotly_chart(px.bar(df_cond_e, x='Lugar', color='Estado', title="Estatus por Lugar"), use_container_width=True)
                    st.plotly_chart(px.pie(df_cond_e, names='Prioridad', title="Urgencia"), use_container_width=True)
                st.markdown("---")
                txt_an_c = st.text_area("Análisis Técnico (Condiciones):", key="an_c_final")
                txt_pl_c = st.text_area("Plan de Acción (Condiciones):", key="pl_c_final")
            else: st.warning("Sin datos en Condiciones.")

        with t2:
            if not df_comp_e.empty:
                g1, g2 = st.columns(2)
                with g1: st.plotly_chart(px.bar(df_comp_e, x='Centro de trabajo', color='Estado observado', title="Cultura por Centro"), use_container_width=True)
                with g2: st.plotly_chart(px.pie(df_comp_e, names='Lugar', title="Observaciones por Lugar"), use_container_width=True)
                txt_an_h = st.text_area("Análisis Conductual:", key="an_h_final")
                txt_pl_h = st.text_area("Estrategia Humana:", key="pl_h_final")
            else: st.warning("Sin datos en Comportamiento.")

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
                st.dataframe(df_acpm_e)
            else: st.error("❌ Sin datos en ACPM. Verifique el NIT o la URL.")

        # BOTÓN PDF SIDEBAR
        st.sidebar.markdown("---")
        if st.sidebar.button("📄 Procesar PDF"):
            pdf_b = generar_pdf_final(nit_user, txt_an_c, txt_pl_c, txt_an_h, txt_pl_h)
            st.sidebar.download_button("⬇️ Descargar", data=pdf_b, file_name=f"Reporte_{nit_user}.pdf", mime="application/pdf")

    # --- FORMULARIOS (VARIABLES RESTAURADAS) ---
    elif menu == "⚖️ Gestión de ACPM":
        st.title("⚖️ Registro Técnico de ACPM")
        with st.form("f_acpm"):
            col1, col2 = st.columns(2)
            with col1:
                f_emp = st.text_input("Empresa")
                f_comp = st.selectbox("Componente", ["SST", "Ambiente", "Calidad", "Vial"])
                f_fuen = st.selectbox("Fuente", ["Inspección", "Auditoría", "Incidente", "Gerencia"])
                f_desc = st.text_area("Descripción Hallazgo")
                p1, p2, p3, p4, p5 = st.text_input("¿Por qué? 1"), st.text_input("¿Por qué? 2"), st.text_input("¿Por qué? 3"), st.text_input("¿Por qué? 4"), st.text_input("¿Por qué? 5")
            with col2:
                f_raiz = st.text_input("Causa raíz")
                f_acci = st.text_area("Acción Propuesta")
                f_tipo = st.radio("Tipo Acción", ["Correctiva", "Preventiva", "Mejora"])
                f_esta = st.selectbox("Estado", ["Abierta", "En Ejecución", "Cerrada"])
                f_cambio = st.radio("⚠️ ¿Activa Gestión del Cambio? (IPVR/IAVI)", ["No", "Sí"])
            if st.form_submit_button("💾 GUARDAR ACPM"):
                n_a = pd.DataFrame([{"Nit":str(nit_user), "Empresa":f_emp, "Fecha de reporte":str(datetime.now().date()), "Componente":f_comp, "Fuente":f_fuen, "Descripción Hallazgo":f_desc, "Análisis Causa ¿Porqué 1?":p1, "Análisis Causa ¿Porqué 2?":p2, "Análisis Causa ¿Porqué 3?":p3, "Análisis Causa ¿Porqué 4?":p4, "Análisis Causa ¿Porqué 5?":p5, "Causa raíz":f_raiz, "Acción Propuesta":f_acci, "Tipo Acción":f_tipo, "Responsable":"Auditor", "Fecha Cierre Prevista":str(datetime.now().date()), "Eficacia de la acción tomada":"Pendiente", "La acción tomada activa gestión del cambio (Si es afirmativo IPVR, IAVI y sus controles)":f_cambio, "Estado":f_esta}])
                conn.update(spreadsheet=URL_ACPM, data=pd.concat([df_acpm_t, n_a], ignore_index=True))
                st.success("Registrado.")

    elif menu == "🛠️ Reporte Condiciones":
        st.title("🛠️ Registro de Condiciones HSEQ")
        with st.form("f_cond"):
            c1, c2 = st.columns(2)
            with c1:
                f_ct = st.text_input("Centro de trabajo")
                f_lg = st.text_input("Lugar")
                f_hl = st.text_area("Descripción Hallazgo")
                f_cc = st.selectbox("Condición Crítica", ["Orden/Aseo", "Herramientas", "Locativo", "Sistemas Eléctricos", "Vial", "Otros"])
            with c2:
                f_ries = st.selectbox("Clasificación del riesgo (GTC 45)", ["Físico", "Químico", "Biológico", "Psicosocial", "Biomecánico", "Seguridad", "Natural"])
                f_pr = st.selectbox("Prioridad", ["Baja", "Media", "Alta"])
                f_es = st.selectbox("Estado", ["Abierto", "En Proceso", "Cerrado"])
                f_obs = st.text_area("Observaciones Adicionales")
            if st.form_submit_button("✅ GUARDAR CONDICIÓN"):
                n_c = pd.DataFrame([{"Nit":str(nit_user), "Empresa":"Sede", "Centro de trabajo":f_ct, "Lugar":f_lg, "Fecha":str(datetime.now().date()), "Hallazgo":f_hl, "Condición Crítica":f_cc, "Clasificación del riesgo":f_ries, "Componente":"SST", "Responsable del cierre":"Auditor", "Fecha propuesta para el cierre":str(datetime.now().date()), "Prioridad":f_pr, "Estado":f_es, "Observación":f_obs}])
                conn.update(spreadsheet=URL_COND, data=pd.concat([df_cond_t, n_c], ignore_index=True))
                st.success("Guardado.")

    elif menu == "🧠 Reporte Comportamiento":
        st.title("🧠 Registro de Comportamiento")
        with st.form("f_comp"):
            c1, c2 = st.columns(2)
            with c1:
                f_in = st.text_input("Inspector")
                f_cth = st.text_input("Centro de trabajo")
                f_lgh = st.text_input("Lugar")
            with c2:
                f_tipo = st.selectbox("Tipo de Inspección", ["Conducta Humana", "Preoperacional", "Tareas Críticas"])
                f_est = st.selectbox("Estado observado", ["✅ SEGURO", "⚠️ ATÍPICO", "🚫 PELIGROSO"])
                f_obs = st.text_area("Observaciones Factor Humano")
            if st.form_submit_button("🚀 REGISTRAR"):
                n_h = pd.DataFrame([{"Nit":str(nit_user), "ID_Inspección":str(uuid.uuid4())[:8].upper(), "Fecha/Hora Real":str(datetime.now()), "Inspector":f_in, "Centro de trabajo":f_cth, "Lugar":f_lgh, "Tipo de Inspección":f_tipo, "Estado observado":f_est, "Evidencia Fotográfica":"N/A", "Observaciones Factor Humano":f_obs}])
                conn.update(spreadsheet=URL_COMP, data=pd.concat([df_comp_t, n_h], ignore_index=True))
                st.success("Registrado.")
