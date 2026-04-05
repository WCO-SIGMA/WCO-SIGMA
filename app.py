import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.express as px
from datetime import datetime
import uuid
from fpdf import FPDF

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="WCO-SIGMA SIG+ACPM", layout="wide")

# --- CONFIGURACIÓN DE CONEXIONES ---
URL_COND = "https://docs.google.com/spreadsheets/d/18OIJe409rr6o_o4HSweiuncIoOrgJOXEt0GFCmEsL4g/edit"
URL_COMP = "https://docs.google.com/spreadsheets/d/1szrDZsA59e5sMF6OAzPeQ_nDX7E9lMehaXCPHmVNx5o/edit"
URL_ACPM = "https://docs.google.com/spreadsheets/d/16ZgE9R5o4l8P7Tz7xS9u3v4W3Y1vW-J1/edit" 

conn = st.connection("gsheets", type=GSheetsConnection)

# --- FUNCIÓN DE PDF ---
def crear_pdf_final(nit, an_c, pl_c, an_h, pl_h):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "REPORTE DE GESTION INTEGRAL - WCO-SIGMA", ln=True, align="C")
    pdf.ln(10)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, f"NIT CLIENTE: {nit}", ln=True)
    pdf.set_font("Arial", "", 10)
    pdf.multi_cell(0, 7, f"ANALISIS CONDICIONES: {an_c}\nPLAN: {pl_c}")
    pdf.ln(5)
    pdf.multi_cell(0, 7, f"ANALISIS COMPORTAMIENTO: {an_h}\nPLAN: {pl_h}")
    return pdf.output(dest='S').encode('latin-1', 'ignore')

# 2. ACCESO POR NIT
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/1063/1063302.png", width=100)
nit_user = st.sidebar.text_input("Ingrese identificación (NIT/Cédula):", "").strip()

if not nit_user:
    st.title("🚀 WCO-SIGMA: Suite de Gestión PHVA")
    st.info("Ingrese su NIT para activar el tablero de control.")
else:
    # --- MOTOR DE LECTURA INTELIGENTE (ESCANEO DE PESTAÑAS) ---
    def cargar_datos_auto(url, nombre_log):
        try:
            # Intentamos leer. Si falla por pestaña, Streamlit GSheets lanza error
            df = conn.read(spreadsheet=url, ttl=0)
            if df is not None and not df.empty:
                df.columns = df.columns.str.strip()
                # Buscamos la columna Nit sin importar mayúsculas
                col_nit = [c for c in df.columns if c.lower() == 'nit']
                if col_nit:
                    df['Nit_Clean'] = df[col_nit[0]].astype(str).apply(lambda x: x.split('.')[0].strip())
                    return df, df[df['Nit_Clean'] == nit_user]
            return pd.DataFrame(), pd.DataFrame()
        except:
            return pd.DataFrame(), pd.DataFrame()

    df_cond_t, df_cond_e = cargar_datos_auto(URL_COND, "CONDICIONES")
    df_comp_t, df_comp_e = cargar_datos_auto(URL_COMP, "COMPORTAMIENTO")
    df_acpm_t, df_acpm_e = cargar_datos_auto(URL_ACPM, "ACPM")

    menu = st.sidebar.radio("Navegación", ["📊 Dashboard Gerencial", "⚖️ Gestión de ACPM", "🛠️ Reporte Condiciones", "🧠 Reporte Comportamiento"])

    if menu == "📊 Dashboard Gerencial":
        st.title(f"📊 Tablero Gerencial - NIT: {nit_user}")
        tab1, tab2, tab3 = st.tabs(["🔍 Condiciones HSEQ", "🧠 Comportamiento", "⚖️ Mejora (ACPM)"])
        
        with tab1:
            if not df_cond_e.empty:
                c1, c2 = st.columns(2)
                with c1:
                    st.plotly_chart(px.bar(df_cond_e, x='Centro de trabajo', color='Prioridad', title="Hallazgos por Centro"), use_container_width=True)
                    st.plotly_chart(px.pie(df_cond_e, names='Condición Crítica', title="Condiciones Críticas", hole=0.3), use_container_width=True)
                with c2:
                    st.plotly_chart(px.bar(df_cond_e, x='Lugar', color='Estado', title="Hallazgos por Lugar"), use_container_width=True)
                    st.plotly_chart(px.pie(df_cond_e, names='Estado', title="Avance de Cierres"), use_container_width=True)
                st.markdown("---")
                a1, a2 = st.columns(2)
                txt_an_c = a1.text_area("Análisis Técnico (Condiciones):", key="an_c_v14")
                txt_pl_c = a2.text_area("Plan de Acción (Condiciones):", key="pl_c_v14")
            else: st.warning("Sin datos en BDI WCO SIGMA")

        with tab2:
            if not df_comp_e.empty:
                g1, g2 = st.columns(2)
                with g1: st.plotly_chart(px.bar(df_comp_e, x='Centro de trabajo', color='Estado observado', title="Cultura por Centro"), use_container_width=True)
                with g2: st.plotly_chart(px.pie(df_comp_e, names='Lugar', title="Observaciones por Lugar"), use_container_width=True)
                st.plotly_chart(px.bar(df_comp_e, x='Estado observado', title="Estatus de Comportamientos"), use_container_width=True)
                st.markdown("---")
                a3, a4 = st.columns(2)
                txt_an_h = a3.text_area("Análisis de Riesgo Conductual:", key="an_h_v14")
                txt_pl_h = a4.text_area("Plan de Intervención Humana:", key="pl_h_v14")
            else: st.warning("Sin datos en BDI COMPORTAMIENTO")

        with tab3:
            st.subheader("⚖️ Gestión de Mejora Continua (ACPM)")
            if not df_acpm_e.empty:
                ca1, ca2 = st.columns(2)
                with ca1:
                    st.plotly_chart(px.pie(df_acpm_e, names='Componente', title="ACPM por Sistema", hole=0.4), use_container_width=True)
                    st.plotly_chart(px.bar(df_acpm_e, x='Causa raíz', color='Estado', title="Análisis de Causa Raíz"), use_container_width=True)
                with ca2:
                    st.plotly_chart(px.bar(df_acpm_e, x='Fuente', color='Tipo Acción', title="Fuente vs Tipo de Acción"), use_container_width=True)
                    st.plotly_chart(px.pie(df_acpm_e, names='Estado', title="Estatus de ACPM"), use_container_width=True)
                st.dataframe(df_acpm_e, use_container_width=True)
            else:
                st.error("❌ No se detectan datos de ACPM para este NIT.")
                if not df_acpm_t.empty:
                    with st.expander("Verificar Estructura del Excel"):
                        st.write("Columnas detectadas:", list(df_acpm_t.columns))
                        st.write("NITs disponibles:", df_acpm_t['Nit'].unique() if 'Nit' in df_acpm_t.columns else "No hay columna Nit")

        # BOTÓN PDF
        st.sidebar.markdown("---")
        if st.sidebar.button("📄 Procesar Reporte PDF"):
            pdf_data = crear_pdf_final(nit_user, txt_an_c, txt_pl_c, txt_an_h, txt_pl_h)
            st.sidebar.download_button("⬇️ Descargar Informe PDF", data=pdf_data, file_name=f"SIG_{nit_user}.pdf", mime="application/pdf")

    # --- FORMULARIOS ---
    elif menu == "⚖️ Gestión de ACPM":
        st.title("⚖️ Registro Técnico de ACPM")
        with st.form("f_acpm_v14"):
            col1, col2 = st.columns(2)
            with col1:
                f_emp = st.text_input("Empresa")
                f_comp = st.selectbox("Componente", ["SST", "Ambiente", "Calidad", "Vial"])
                f_desc = st.text_area("Descripción Hallazgo")
                p1, p2, p3, p4, p5 = st.text_input("P1"), st.text_input("P2"), st.text_input("P3"), st.text_input("P4"), st.text_input("P5")
            with col2:
                f_raiz = st.text_input("Causa raíz")
                f_acci = st.text_area("Acción Propuesta")
                f_tipo = st.radio("Tipo Acción", ["Correctiva", "Preventiva", "Mejora"])
                f_esta = st.selectbox("Estado", ["Abierta", "En Ejecución", "Cerrada"])
            if st.form_submit_button("💾 GUARDAR"):
                n_a = pd.DataFrame([{"Nit":str(nit_user), "Empresa":f_emp, "Fecha de reporte":str(datetime.now().date()), "Componente":f_comp, "Descripción Hallazgo":f_desc, "Análisis Causa ¿Porqué 1?":p1, "Análisis Causa ¿Porqué 2?":p2, "Análisis Causa ¿Porqué 3?":p3, "Análisis Causa ¿Porqué 4?":p4, "Análisis Causa ¿Porqué 5?":p5, "Causa raíz":f_raiz, "Acción Propuesta":f_acci, "Tipo Acción":f_tipo, "Responsable":"Auditor", "Fecha Cierre Prevista":str(datetime.now().date()), "Eficacia de la acción tomada":"Pendiente", "La acción tomada activa gestión del cambio (Si es afirmativo IPVR, IAVI y sus controles)":"No", "Estado":f_esta}])
                conn.update(spreadsheet="BD ACPM", data=pd.concat([df_acpm_t, n_a], ignore_index=True))
                st.success("Guardado.")

    elif menu == "🛠️ Reporte Condiciones":
        st.title("🛠️ Registro de Condiciones HSEQ")
        with st.form("f_cond_v14"):
            c1, c2 = st.columns(2)
            with c1:
                f_emp_c = st.text_input("Empresa")
                f_ct_c = st.text_input("Centro de trabajo")
                f_l_c = st.text_input("Lugar")
            with c2:
                f_h_c = st.text_area("Hallazgo")
                f_prio_c = st.selectbox("Prioridad", ["Baja", "Media", "Alta"])
                f_est_c = st.selectbox("Estado", ["Abierto", "En Proceso", "Cerrado"])
            if st.form_submit_button("✅ GUARDAR"):
                n_c = pd.DataFrame([{"Nit":str(nit_user), "Empresa":f_emp_c, "Centro de trabajo":f_ct_c, "Lugar":f_l_c, "Fecha":str(datetime.now().date()), "Hallazgo":f_h_c, "Condición Crítica":"General", "Clasificación del riesgo":"SST", "Componente":"SST", "Responsable del cierre":"Auditor", "Fecha propuesta para el cierre":str(datetime.now().date()), "Prioridad":f_prio_c, "Estado":f_est_c, "Observación":"APP"}])
                conn.update(spreadsheet="BDI WCO SIGMA", data=pd.concat([df_cond_t, n_c], ignore_index=True))
                st.success("Guardado.")

    elif menu == "🧠 Reporte Comportamiento":
        st.title("🧠 Observación de Comportamiento")
        with st.form("f_comp_v14"):
            c1, c2 = st.columns(2)
            with c1:
                f_ins = st.text_input("Inspector")
                f_ct_h = st.text_input("Centro de trabajo")
            with c2:
                f_l_h = st.text_input("Lugar")
                f_obs = st.text_area("Observación")
            if st.form_submit_button("🚀 REGISTRAR"):
                n_h = pd.DataFrame([{"Nit":str(nit_user), "ID_Inspección":str(uuid.uuid4())[:8].upper(), "Fecha/Hora Real":str(datetime.now()), "Inspector":f_ins, "Centro de trabajo":f_ct_h, "Lugar":f_l_h, "Tipo de Inspección":"Conducta", "Estado observado":"Auditado", "Evidencia Fotográfica":"N/A", "Observaciones Factor Humano":f_obs}])
                conn.update(spreadsheet="BDI COMPORTAMIENTO", data=pd.concat([df_comp_t, n_h], ignore_index=True))
                st.success("Registrado.")
