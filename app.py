import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.express as px
from datetime import datetime
import io
from fpdf import FPDF

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="WCO-SIGMA SIG+ACPM", layout="wide")

# --- PERSISTENCIA DE ANÁLISIS ---
for k in ['ac', 'pc', 'ah', 'ph', 'aa', 'pa']:
    if k not in st.session_state: st.session_state[k] = ""

# --- CONEXIONES ---
URL_COND = "https://docs.google.com/spreadsheets/d/18OIJe409rr6o_o4HSweiuncIoOrgJOXEt0GFCmEsL4g/edit"
URL_COMP = "https://docs.google.com/spreadsheets/d/1szrDZsA59e5sMF6OAzPeQ_nDX7E9lMehaXCPHmVNx5o/edit"
URL_ACPM = "https://docs.google.com/spreadsheets/d/1yXQNE3PiET-8VOHBWiReht7psRqjbAm5ZnY4P2XQQvg/edit" 

conn = st.connection("gsheets", type=GSheetsConnection)

# --- FUNCIÓN DE CARGA BLINDADA ---
def cargar_blindado(url, nit):
    try:
        df = conn.read(spreadsheet=url, ttl=0)
        df.columns = df.columns.str.strip() # Limpia espacios invisibles
        col_nit = [c for c in df.columns if 'nit' in c.lower()][0]
        df['Nit_M'] = df[col_nit].astype(str).apply(lambda x: x.split('.')[0].strip())
        return df, df[df['Nit_M'] == nit]
    except:
        return pd.DataFrame(), pd.DataFrame()

# 2. INTERFAZ
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/1063/1063302.png", width=80)
nit_user = st.sidebar.text_input("Identificación Empresa (NIT):", "").strip()

if nit_user:
    df_cond_t, df_cond_e = cargar_blindado(URL_COND, nit_user)
    df_comp_t, df_comp_e = cargar_blindado(URL_COMP, nit_user)
    df_acpm_t, df_acpm_e = cargar_blindado(URL_ACPM, nit_user)

    menu = st.sidebar.radio("Navegación PHVA", ["📊 Dashboard Gerencial", "⚖️ Registro ACPM", "🛠️ Reporte Condiciones", "🧠 Reporte Comportamiento"])

    # --- DASHBOARD GERENCIAL (GRÁFICOS ESTABLES) ---
    if menu == "📊 Dashboard Gerencial":
        st.title(f"📊 Dashboard Gerencial - NIT: {nit_user}")
        t1, t2, t3 = st.tabs(["🔍 BDI SIGMA", "🧠 COMPORTAMIENTO", "⚖️ ACPM"])
        
        with t1:
            if not df_cond_e.empty:
                c1, c2 = st.columns(2)
                c1.plotly_chart(px.bar(df_cond_e, x='Centro de trabajo', color='Prioridad', title="Prioridad por Centro"), use_container_width=True)
                c2.plotly_chart(px.bar(df_cond_e, x='Lugar', color='Estado', title="Estatus por Lugar"), use_container_width=True)
                st.plotly_chart(px.pie(df_cond_e, names='Condición Crítica', title="Condiciones Críticas"), use_container_width=True)
                st.session_state.ac = st.text_area("Análisis Condiciones:", value=st.session_state.ac)
                st.session_state.pc = st.text_area("Plan Acción Condiciones:", value=st.session_state.pc)
            else: st.warning("Sin datos en Condiciones.")

        with t2:
            if not df_comp_e.empty:
                st.plotly_chart(px.bar(df_comp_e, x='Centro de trabajo', color='Estado observado', title="Cultura por Centro"), use_container_width=True)
                st.plotly_chart(px.pie(df_comp_e, names='Lugar', title="Observaciones por Lugar"), use_container_width=True)
                st.session_state.ah = st.text_area("Análisis Comportamiento:", value=st.session_state.ah)
                st.session_state.ph = st.text_area("Estrategia Humana:", value=st.session_state.ph)

        with t3:
            if not df_acpm_e.empty:
                a1, a2 = st.columns(2)
                a1.plotly_chart(px.pie(df_acpm_e, names='Componente', title="ACPM por Componente"), use_container_width=True)
                a2.plotly_chart(px.bar(df_acpm_e, x='Causa raíz', color='Estado', title="Causa Raíz vs Estado"), use_container_width=True)
                st.plotly_chart(px.bar(df_acpm_e, x='Fuente', color='Tipo Acción', title="Fuente de Hallazgos"), use_container_width=True)
                st.session_state.aa = st.text_area("Análisis ACPM:", value=st.session_state.aa)
                st.session_state.pa = st.text_area("Plan de Mejora:", value=st.session_state.pa)

    # --- FORMULARIOS (TODAS LAS VARIABLES SOLICITADAS) ---
    elif menu == "⚖️ Registro ACPM":
        st.title("⚖️ Gestión de Mejora Continua (ACPM)")
        with st.form("f_acpm_full"):
            c1, c2 = st.columns(2)
            with c1:
                f_em = st.text_input("Empresa")
                f_fe = st.date_input("Fecha de reporte")
                f_fu = st.selectbox("Fuente", ["inspecciones", "investigación de incidentes", "auditorías internas y externas", "observación de tareas", "reportes de actos y condiciones", "Legislación o normatividad", "Revisión gerencial"])
                f_co = st.selectbox("Componente", ["SST", "Ambiente", "Calidad", "Vial"])
                p1, p2, p3, p4, p5 = st.text_input("¿Por qué 1?"), st.text_input("¿Por qué 2?"), st.text_input("¿Por qué 3?"), st.text_input("¿Por qué 4?"), st.text_input("¿Por qué 5?")
            with c2:
                f_de = st.text_area("Descripción Hallazgo")
                f_ra = st.text_input("Causa raíz")
                f_ap = st.text_area("Acción Propuesta")
                f_ti = st.radio("Tipo Acción", ["Correctiva", "Preventiva", "Mejora"])
                f_re = st.text_input("Responsable")
                f_gc = st.radio("¿Activa Gestión del Cambio? (IPVR/IAVI)", ["No", "Sí"])
                f_es = st.selectbox("Estado", ["Abierta", "En Ejecución", "Cerrada"])
            if st.form_submit_button("💾 GUARDAR ACPM"):
                # Aquí se concatena con el total para no perder datos
                nueva = pd.DataFrame([{"Nit":str(nit_user), "Empresa":f_em, "Fecha de reporte":str(f_fe), "Fuente":f_fu, "Componente":f_co, "Descripción Hallazgo":f_de, "Análisis Causa ¿Porqué 1?":p1, "Análisis Causa ¿Porqué 2?":p2, "Análisis Causa ¿Porqué 3?":p3, "Análisis Causa ¿Porqué 4?":p4, "Análisis Causa ¿Porqué 5?":p5, "Causa raíz":f_ra, "Acción Propuesta":f_ap, "Tipo Acción":f_ti, "Responsable":f_re, "La acción tomada activa gestión del cambio (Si es afirmativo IPVR, IAVI y sus controles)":f_gc, "Estado":f_es}])
                conn.update(spreadsheet=URL_ACPM, data=pd.concat([df_acpm_t, nueva], ignore_index=True))
                st.success("Registrado en BD ACPM")

    elif menu == "🛠️ Reporte Condiciones":
        st.title("🛠️ Registro de Condiciones HSEQ")
        with st.form("f_cond_full"):
            col1, col2 = st.columns(2)
            with col1:
                f_ct = st.text_input("Centro de trabajo")
                f_lg = st.text_input("Lugar")
                f_hl = st.text_area("Hallazgo")
            with col2:
                f_cc = st.selectbox("Condición Crítica", ["Orden/Aseo", "Mecánico", "Eléctrico", "Locativo", "Vial", "Otros"])
                f_pr = st.selectbox("Prioridad", ["Baja", "Media", "Alta"])
                f_es = st.selectbox("Estado", ["Abierto", "En Proceso", "Cerrado"])
            if st.form_submit_button("✅ GUARDAR CONDICIÓN"):
                nueva = pd.DataFrame([{"Nit":str(nit_user), "Centro de trabajo":f_ct, "Lugar":f_lg, "Hallazgo":f_hl, "Condición Crítica":f_cc, "Prioridad":f_pr, "Estado":f_es, "Fecha":str(datetime.now().date())}])
                conn.update(spreadsheet=URL_COND, data=pd.concat([df_cond_t, nueva], ignore_index=True))
                st.success("Guardado en BDI SIGMA")

    # (Botón PDF en Sidebar)
    st.sidebar.markdown("---")
    if st.sidebar.button("📄 Generar Informe"):
        # Lógica de PDF básica para estabilidad
        st.sidebar.write("PDF Generado (Simulación)")

else:
    st.title("🚀 Suite WCO-SIGMA")
    st.info("Ingrese NIT para visualizar.")
