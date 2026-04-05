import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.express as px
from datetime import datetime
import uuid
from fpdf import FPDF

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="WCO-SIGMA SIG+ACPM", layout="wide")

# --- URLs DE BASES DE DATOS ---
URL_COND = "https://docs.google.com/spreadsheets/d/18OIJe409rr6o_o4HSweiuncIoOrgJOXEt0GFCmEsL4g/edit"
URL_COMP = "https://docs.google.com/spreadsheets/d/1szrDZsA59e5sMF6OAzPeQ_nDX7E9lMehaXCPHmVNx5o/edit"
URL_ACPM = "https://docs.google.com/spreadsheets/d/1yXQNE3PiET-8VOHBWiReht7psRqjbAm5ZnY4P2XQQvg/edit" 

conn = st.connection("gsheets", type=GSheetsConnection)

# --- FUNCIÓN GENERADORA DE PDF INTEGRAL ---
def crear_pdf_sigma(nit, ac, pc, ah, ph, aa, pa):
    pdf = FPDF()
    pdf.add_page()
    # Encabezado
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "INFORME INTEGRAL DE GESTION - WCO-SIGMA", ln=True, align="C")
    pdf.set_font("Arial", "", 10)
    pdf.cell(0, 10, f"NIT: {nit} | Generado el: {datetime.now().strftime('%d/%m/%Y %H:%M')}", ln=True, align="C")
    pdf.ln(10)
    
    # Bloques de contenido
    secciones = [
        ("1. ANALISIS DE CONDICIONES HSEQ", ac, pc),
        ("2. ANALISIS DE COMPORTAMIENTO", ah, ph),
        ("3. ANALISIS DE MEJORA CONTINUA (ACPM)", aa, pa)
    ]
    
    for titulo, analisis, plan in secciones:
        pdf.set_font("Arial", "B", 12)
        pdf.set_fill_color(230, 230, 230)
        pdf.cell(0, 10, titulo, ln=True, fill=True)
        pdf.set_font("Arial", "", 10)
        pdf.multi_cell(0, 7, f"DIAGNOSTICO:\n{analisis if analisis else 'Sin análisis registrado.'}")
        pdf.multi_cell(0, 7, f"PLAN DE ACCION:\n{plan if plan else 'Sin plan registrado.'}")
        pdf.ln(5)
        
    return pdf.output(dest='S').encode('latin-1', 'ignore')

# 2. ACCESO POR NIT
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/1063/1063302.png", width=100)
nit_user = st.sidebar.text_input("Ingrese NIT de la Empresa:", "").strip()

if not nit_user:
    st.title("🚀 WCO-SIGMA: Suite PHVA")
    st.info("Motores BDI conectados. Ingrese NIT para visualizar reportes.")
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

    menu = st.sidebar.radio("Menú", ["📊 Dashboard Gerencial", "⚖️ Gestión de ACPM", "🛠️ Reporte Condiciones", "🧠 Reporte Comportamiento"])

    if menu == "📊 Dashboard Gerencial":
        st.title(f"📊 Tablero Gerencial - NIT: {nit_user}")
        tab1, tab2, tab3 = st.tabs(["🔍 Condiciones", "🧠 Comportamiento", "⚖️ ACPM"])
        
        with tab1:
            if not df_cond_e.empty:
                c1, c2 = st.columns(2)
                with c1:
                    st.plotly_chart(px.bar(df_cond_e, x='Centro de trabajo', color='Prioridad', title="Hallazgos por Centro"), use_container_width=True)
                    st.plotly_chart(px.pie(df_cond_e, names='Condición Crítica', title="Condiciones Críticas"), use_container_width=True)
                with c2:
                    st.plotly_chart(px.bar(df_cond_e, x='Lugar', color='Estado', title="Estatus por Lugar"), use_container_width=True)
                    st.plotly_chart(px.pie(df_cond_e, names='Prioridad', title="Urgencia"), use_container_width=True)
                st.markdown("---")
                txt_an_c = st.text_area("Análisis Técnico (Condiciones):", key="ac_v_final")
                txt_pl_c = st.text_area("Plan de Acción (Condiciones):", key="pc_v_final")
            else: st.warning("Sin datos en Condiciones.")

        with tab2:
            if not df_comp_e.empty:
                g1, g2 = st.columns(2)
                with g1: st.plotly_chart(px.bar(df_comp_e, x='Centro de trabajo', color='Estado observado', title="Cultura por Centro"), use_container_width=True)
                with g2: st.plotly_chart(px.pie(df_comp_e, names='Lugar', title="Observaciones por Lugar"), use_container_width=True)
                st.markdown("---")
                txt_an_h = st.text_area("Análisis Conductual:", key="ah_v_final")
                txt_pl_h = st.text_area("Estrategia Humana:", key="ph_v_final")
            else: st.warning("Sin datos en Comportamiento.")

        with tab3:
            st.subheader("⚖️ Gestión de Mejora (ACPM)")
            if not df_acpm_e.empty:
                ca1, ca2 = st.columns(2)
                with ca1:
                    st.plotly_chart(px.pie(df_acpm_e, names='Componente', title="ACPM por Sistema", hole=0.4), use_container_width=True)
                    st.plotly_chart(px.bar(df_acpm_e, x='Causa raíz', color='Estado', title="Causas Raíz"), use_container_width=True)
                with ca2:
                    st.plotly_chart(px.bar(df_acpm_e, x='Fuente', color='Tipo Acción', title="Fuente vs Acción"), use_container_width=True)
                    st.plotly_chart(px.pie(df_acpm_e, names='Estado', title="Estatus ACPM"), use_container_width=True)
                st.markdown("---")
                txt_an_a = st.text_area("Análisis de Tendencias (ACPM):", key="aa_v_final")
                txt_pl_a = st.text_area("Plan de Mejora Continua:", key="pa_v_final")
                st.dataframe(df_acpm_e)
            else: st.error("❌ No se detectan datos de ACPM para este NIT.")

        # PROCESO DE PDF
        st.sidebar.markdown("---")
        if st.sidebar.button("📄 Generar Informe PDF"):
            # Pasamos todos los cuadros de análisis al generador
            pdf_out = crear_pdf_sigma(nit_user, txt_an_c, txt_pl_c, txt_an_h, txt_pl_h, txt_an_a, txt_pl_a)
            st.sidebar.download_button("⬇️ Descargar Reporte", data=pdf_out, file_name=f"Reporte_SIG_{nit_user}.pdf", mime="application/pdf")

    # --- FORMULARIOS (MANTENIENDO TODAS LAS VARIABLES) ---
    elif menu == "⚖️ Gestión de ACPM":
        st.title("⚖️ Registro Técnico de ACPM")
        with st.form("f_acpm_v_final"):
            c1, c2 = st.columns(2)
            with c1:
                f_emp = st.text_input("Empresa")
                f_comp = st.selectbox("Componente", ["SST", "Ambiente", "Calidad", "Vial"])
                f_fuen = st.selectbox("Fuente", ["Inspección", "Auditoría", "Incidente", "Gerencia"])
                f_desc = st.text_area("Descripción Hallazgo")
                p1, p2, p3, p4, p5 = st.text_input("P1"), st.text_input("P2"), st.text_input("P3"), st.text_input("P4"), st.text_input("P5")
            with c2:
                f_raiz = st.text_input("Causa raíz")
                f_acci = st.text_area("Acción Propuesta")
                f_tipo = st.radio("Tipo Acción", ["Correctiva", "Preventiva", "Mejora"])
                f_esta = st.selectbox("Estado", ["Abierta", "En Ejecución", "Cerrada"])
                f_cambio = st.radio("⚠️ ¿Gestión del Cambio?", ["No", "Sí"])
            if st.form_submit_button("💾 GUARDAR"):
                n_a = pd.DataFrame([{"Nit":str(nit_user), "Empresa":f_emp, "Fecha de reporte":str(datetime.now().date()), "Componente":f_comp, "Fuente":f_fuen, "Descripción Hallazgo":f_desc, "Análisis Causa ¿Porqué 1?":p1, "Análisis Causa ¿Porqué 2?":p2, "Análisis Causa ¿Porqué 3?":p3, "Análisis Causa ¿Porqué 4?":p4, "Análisis Causa ¿Porqué 5?":p5, "Causa raíz":f_raiz, "Acción Propuesta":f_acci, "Tipo Acción":f_tipo, "La acción tomada activa gestión del cambio (Si es afirmativo IPVR, IAVI y sus controles)":f_cambio, "Estado":f_esta}])
                conn.update(spreadsheet=URL_ACPM, data=pd.concat([df_acpm_t, n_a], ignore_index=True))
                st.success("Guardado.")

    elif menu == "🛠️ Reporte Condiciones":
        st.title("🛠️ Registro de Condiciones HSEQ")
        with st.form("f_cond_v_final"):
            c1, c2 = st.columns(2)
            with c1:
                f_ct = st.text_input("Centro de trabajo")
                f_lg = st.text_input("Lugar")
                f_hl = st.text_area("Descripción Hallazgo")
                f_cc = st.selectbox("Condición Crítica", ["Orden/Aseo", "Herramientas", "Locativo", "Vial", "Otros"])
            with c2:
                f_ries = st.selectbox("Riesgo (GTC 45)", ["Físico", "Químico", "Biológico", "Psicosocial", "Biomecánico", "Seguridad", "Natural"])
                f_pr = st.selectbox("Prioridad", ["Baja", "Media", "Alta"])
                f_es = st.selectbox("Estado", ["Abierto", "En Proceso", "Cerrado"])
            if st.form_submit_button("✅ GUARDAR"):
                n_c = pd.DataFrame([{"Nit":str(nit_user), "Empresa":"Sede", "Centro de trabajo":f_ct, "Lugar":f_lg, "Fecha":str(datetime.now().date()), "Hallazgo":f_hl, "Condición Crítica":f_cc, "Clasificación del riesgo":f_ries, "Prioridad":f_pr, "Estado":f_es}])
                conn.update(spreadsheet=URL_COND, data=pd.concat([df_cond_t, n_c], ignore_index=True))
                st.success("Guardado.")

    elif menu == "🧠 Reporte Comportamiento":
        st.title("🧠 Registro de Comportamiento")
        with st.form("f_comp_v_final"):
            c1, c2 = st.columns(2)
            with c1:
                f_in = st.text_input("Inspector")
                f_cth = st.text_input("Centro de trabajo")
            with c2:
                f_lgh = st.text_input("Lugar")
                f_est = st.selectbox("Estado observado", ["✅ SEGURO", "⚠️ ATÍPICO", "🚫 PELIGROSO"])
            if st.form_submit_button("🚀 REGISTRAR"):
                n_h = pd.DataFrame([{"Nit":str(nit_user), "Fecha/Hora Real":str(datetime.now()), "Inspector":f_in, "Centro de trabajo":f_cth, "Lugar":f_lgh, "Estado observado":f_est}])
                conn.update(spreadsheet=URL_COMP, data=pd.concat([df_comp_t, n_h], ignore_index=True))
                st.success("Registrado.")
