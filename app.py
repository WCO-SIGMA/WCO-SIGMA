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

# --- CONEXIONES ---
URL_COND = "https://docs.google.com/spreadsheets/d/18OIJe409rr6o_o4HSweiuncIoOrgJOXEt0GFCmEsL4g/edit"
URL_COMP = "https://docs.google.com/spreadsheets/d/1szrDZsA59e5sMF6OAzPeQ_nDX7E9lMehaXCPHmVNx5o/edit"
URL_ACPM = "https://docs.google.com/spreadsheets/d/1yXQNE3PiET-8VOHBWiReht7psRqjbAm5ZnY4P2XQQvg/edit" 

conn = st.connection("gsheets", type=GSheetsConnection)

# --- MOTOR PDF ---
def crear_pdf_visual(nit, ac, pc, ah, ph, aa, pa, fig1, fig2):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "INFORME GERENCIAL INTEGRAL - WCO-SIGMA", ln=True, align="C")
    pdf.ln(5)
    
    # Sección Condiciones
    pdf.set_font("Arial", "B", 12)
    pdf.set_fill_color(230, 230, 230)
    pdf.cell(0, 10, "1. GESTION DE CONDICIONES HSEQ", ln=True, fill=True)
    pdf.set_font("Arial", "", 10)
    pdf.multi_cell(0, 7, f"DIAGNOSTICO: {ac}\nPLAN: {pc}")
    try:
        buf1 = io.BytesIO()
        fig1.write_image(buf1, format="png", width=700, height=350)
        pdf.image(buf1, x=15, w=170)
    except: pdf.cell(0, 10, "[Gráfico de Condiciones no disponible]", ln=True)

    # Sección ACPM
    pdf.add_page()
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "2. MEJORA CONTINUA (ACPM)", ln=True, fill=True)
    pdf.set_font("Arial", "", 10)
    pdf.multi_cell(0, 7, f"ANALISIS ACPM: {aa}\nPLAN: {pa}")
    try:
        buf2 = io.BytesIO()
        fig2.write_image(buf2, format="png", width=700, height=350)
        pdf.image(buf2, x=15, w=170)
    except: pdf.cell(0, 10, "[Gráfico de ACPM no disponible]", ln=True)
    
    return pdf.output(dest='S').encode('latin-1', 'ignore')

# 2. ACCESO
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/1063/1063302.png", width=100)
nit_user = st.sidebar.text_input("Ingrese identificación (NIT/Cédula):", "").strip()

if not nit_user:
    st.title("🚀 WCO-SIGMA: Suite PHVA")
    st.info("Motores vinculados. Ingrese el NIT para activar el tablero gerencial.")
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

    menu = st.sidebar.radio("Navegación", ["📊 Dashboard Gerencial", "⚖️ Gestión de ACPM", "🛠️ Reporte Condiciones", "🧠 Reporte Comportamiento"])

    # --- DASHBOARD GERENCIAL (RESTAURACIÓN TOTAL DE GRÁFICOS) ---
    if menu == "📊 Dashboard Gerencial":
        st.title(f"📊 Control Gerencial de Indicadores - NIT: {nit_user}")
        t1, t2, t3 = st.tabs(["🔍 BDI WCO SIGMA", "🧠 BDI COMPORTAMIENTO", "⚖️ BD ACPM"])
        
        with t1:
            if not df_cond_e.empty:
                c1, c2 = st.columns(2)
                with c1:
                    st.plotly_chart(px.bar(df_cond_e, x='Centro de trabajo', color='Prioridad', title="Hallazgos por Centro de Trabajo"), use_container_width=True)
                    st.plotly_chart(px.pie(df_cond_e, names='Condición Crítica', title="Distribución por Condición Crítica", hole=0.3), use_container_width=True)
                with c2:
                    st.plotly_chart(px.bar(df_cond_e, x='Lugar', color='Estado', title="Estatus de Hallazgos por Lugar"), use_container_width=True)
                    st.plotly_chart(px.pie(df_cond_e, names='Prioridad', title="Urgencia (Prioridad)"), use_container_width=True)
                
                # Para el PDF (Capturamos el estatus de cierre)
                f1_pdf = px.pie(df_cond_e, names='Estado', title="Estatus General de Condiciones")
                
                st.markdown("---")
                txt_ac = st.text_area("Análisis Técnico (Condiciones):", key="ac_v18")
                txt_pc = st.text_area("Plan de Acción (Condiciones):", key="pc_v18")
            else: st.warning("Sin datos en Condiciones.")

        with t2:
            if not df_comp_e.empty:
                g1, g2 = st.columns(2)
                with g1:
                    st.plotly_chart(px.bar(df_comp_e, x='Centro de trabajo', color='Estado observado', title="Cultura por Centro de Trabajo"), use_container_width=True)
                with g2:
                    st.plotly_chart(px.pie(df_comp_e, names='Lugar', title="Observaciones por Lugar"), use_container_width=True)
                
                st.plotly_chart(px.bar(df_comp_e, x='Estado observado', color='Estado observado', title="Resumen de Cultura de Seguridad"), use_container_width=True)
                
                st.markdown("---")
                txt_ah = st.text_area("Análisis Conductual:", key="ah_v18")
                txt_ph = st.text_area("Estrategia Humana:", key="ph_v18")
            else: st.warning("Sin datos en Comportamiento.")

        with t3:
            if not df_acpm_e.empty:
                ca1, ca2 = st.columns(2)
                with ca1:
                    st.plotly_chart(px.pie(df_acpm_e, names='Componente', title="ACPM por Sistema SIG", hole=0.4), use_container_width=True)
                    st.plotly_chart(px.bar(df_acpm_e, x='Causa raíz', color='Estado', title="Análisis de Causa Raíz Dominante"), use_container_width=True)
                with ca2:
                    st.plotly_chart(px.bar(df_acpm_e, x='Fuente', color='Tipo Acción', title="Fuente de Hallazgos vs Tipo de Acción"), use_container_width=True)
                    st.plotly_chart(px.pie(df_acpm_e, names='Estado', title="Estatus de Avance ACPM"), use_container_width=True)
                
                # Para el PDF (Capturamos el avance por tipo de acción)
                f2_pdf = px.bar(df_acpm_e, x='Estado', color='Tipo Acción', title="Avance ACPM")
                
                st.markdown("---")
                txt_aa = st.text_area("Análisis de Mejora Continua:", key="aa_v18")
                txt_pa = st.text_area("Plan de Mejora Continua:", key="pa_v18")
                st.dataframe(df_acpm_e, use_container_width=True)
            else: st.error("Sin datos en ACPM.")

        # BOTÓN PDF
        st.sidebar.markdown("---")
        if st.sidebar.button("📄 Generar Informe con Gráficos"):
            with st.spinner("Procesando Reporte..."):
                pdf_res = crear_pdf_visual(nit_user, txt_ac, txt_pc, txt_ah, txt_ph, txt_aa, txt_pa, f1_pdf, f2_pdf)
                st.sidebar.download_button("⬇️ Descargar Reporte", data=pdf_res, file_name=f"Reporte_SIG_{nit_user}.pdf", mime="application/pdf")

    # --- FORMULARIOS (VARIABLES RESTAURADAS) ---
    elif menu == "⚖️ Gestión de ACPM":
        st.title("⚖️ Registro Técnico de ACPM")
        with st.form("f_acpm_v18"):
            c1, c2 = st.columns(2)
            with c1:
                f_em = st.text_input("Empresa")
                f_co = st.selectbox("Componente", ["SST", "Ambiente", "Calidad", "Vial"])
                f_fu = st.selectbox("Fuente", ["Inspección", "Auditoría", "Incidente", "Gerencia"])
                f_de = st.text_area("Descripción Hallazgo")
                p1, p2, p3, p4, p5 = st.text_input("P1"), st.text_input("P2"), st.text_input("P3"), st.text_input("P4"), st.text_input("P5")
            with c2:
                f_ra = st.text_input("Causa raíz")
                f_ac = st.text_area("Acción Propuesta")
                f_ti = st.radio("Tipo Acción", ["Correctiva", "Preventiva", "Mejora"])
                f_es = st.selectbox("Estado", ["Abierta", "En Ejecución", "Cerrada"])
                f_gc = st.radio("⚠️ ¿Activa Gestión del Cambio?", ["No", "Sí"])
            if st.form_submit_button("💾 GUARDAR"):
                n_a = pd.DataFrame([{"Nit":str(nit_user), "Empresa":f_em, "Fecha de reporte":str(datetime.now().date()), "Componente":f_co, "Fuente":f_fu, "Descripción Hallazgo":f_de, "Análisis Causa ¿Porqué 1?":p1, "Análisis Causa ¿Porqué 2?":p2, "Análisis Causa ¿Porqué 3?":p3, "Análisis Causa ¿Porqué 4?":p4, "Análisis Causa ¿Porqué 5?":p5, "Causa raíz":f_ra, "Acción Propuesta":f_ac, "Tipo Acción":f_ti, "La acción tomada activa gestión del cambio (Si es afirmativo IPVR, IAVI y sus controles)":f_gc, "Estado":f_es}])
                conn.update(spreadsheet=URL_ACPM, data=pd.concat([df_acpm_t, n_a], ignore_index=True))
                st.success("ACPM Registrada.")

    elif menu == "🛠️ Reporte Condiciones":
        st.title("🛠️ Registro de Condiciones HSEQ")
        with st.form("f_cond_v18"):
            c1, c2 = st.columns(2)
            with c1:
                f_ct = st.text_input("Centro de trabajo")
                f_lg = st.text_input("Lugar")
                f_hl = st.text_area("Hallazgo")
                f_cc = st.selectbox("Condición Crítica", ["Orden/Aseo", "Herramientas", "Locativo", "Vial", "Otros"])
            with c2:
                f_tr = st.selectbox("Clasificación del Riesgo (GTC 45)", ["Físico", "Químico", "Biológico", "Psicosocial", "Biomecánico", "Seguridad", "Natural"])
                f_pr = st.selectbox("Prioridad", ["Baja", "Media", "Alta"])
                f_es = st.selectbox("Estado", ["Abierto", "En Proceso", "Cerrado"])
                f_ob = st.text_area("Observaciones")
            if st.form_submit_button("✅ GUARDAR"):
                n_c = pd.DataFrame([{"Nit":str(nit_user), "Empresa":"Sede", "Centro de trabajo":f_ct, "Lugar":f_lg, "Fecha":str(datetime.now().date()), "Hallazgo":f_hl, "Condición Crítica":f_cc, "Clasificación del riesgo":f_tr, "Prioridad":f_pr, "Estado":f_es, "Observación":f_ob}])
                conn.update(spreadsheet=URL_COND, data=pd.concat([df_cond_t, n_c], ignore_index=True))
                st.success("Condición guardada.")

    elif menu == "🧠 Reporte Comportamiento":
        st.title("🧠 Registro de Comportamiento")
        with st.form("f_comp_v18"):
            c1, c2 = st.columns(2)
            with c1:
                f_in = st.text_input("Inspector")
                f_cth = st.text_input("Centro de trabajo")
            with c2:
                f_lgh = st.text_input("Lugar")
                f_eo = st.selectbox("Estado observado", ["✅ SEGURO", "⚠️ ATÍPICO", "🚫 PELIGROSO"])
                f_obh = st.text_area("Observaciones Factor Humano")
            if st.form_submit_button("🚀 REGISTRAR"):
                n_h = pd.DataFrame([{"Nit":str(nit_user), "Fecha/Hora Real":str(datetime.now()), "Inspector":f_in, "Centro de trabajo":f_cth, "Lugar":f_lgh, "Estado observado":f_eo, "Observaciones Factor Humano":f_obh}])
                conn.update(spreadsheet=URL_COMP, data=pd.concat([df_comp_t, n_h], ignore_index=True))
                st.success("Registrado.")
