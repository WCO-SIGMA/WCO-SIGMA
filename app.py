import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.express as px
from datetime import datetime
import io
from fpdf import FPDF

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="WCO-SIGMA SIG+ACPM", layout="wide")

# --- MEMORIA DE SESIÓN (PERSISTENCIA) ---
for key in ['an_cond', 'pl_cond', 'an_comp', 'pl_comp', 'an_acpm', 'pl_acpm']:
    if key not in st.session_state: st.session_state[key] = ""

# --- CONEXIONES ---
URL_COND = "https://docs.google.com/spreadsheets/d/18OIJe409rr6o_o4HSweiuncIoOrgJOXEt0GFCmEsL4g/edit"
URL_COMP = "https://docs.google.com/spreadsheets/d/1szrDZsA59e5sMF6OAzPeQ_nDX7E9lMehaXCPHmVNx5o/edit"
URL_ACPM = "https://docs.google.com/spreadsheets/d/1yXQNE3PiET-8VOHBWiReht7psRqjbAm5ZnY4P2XQQvg/edit" 

conn = st.connection("gsheets", type=GSheetsConnection)

# --- MOTOR DE CARGA ROBUSTO ---
def cargar_datos(url, nit):
    try:
        df = conn.read(spreadsheet=url, ttl=0)
        df.columns = df.columns.str.strip()
        # Buscar columna NIT sin importar mayúsculas
        col_nit = [c for c in df.columns if c.lower() == 'nit'][0]
        df['Nit_M'] = df[col_nit].astype(str).apply(lambda x: x.split('.')[0].strip())
        return df, df[df['Nit_M'] == nit]
    except:
        return pd.DataFrame(), pd.DataFrame()

# 2. ACCESO
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/1063/1063302.png", width=80)
nit_user = st.sidebar.text_input("Identificación Empresa (NIT):", "").strip()

if not nit_user:
    st.title("🚀 WCO-SIGMA: Suite de Gestión")
    st.info("Ingrese el NIT para activar los tableros de control.")
else:
    df_cond_t, df_cond_e = cargar_datos(URL_COND, nit_user)
    df_comp_t, df_comp_e = cargar_datos(URL_COMP, nit_user)
    df_acpm_t, df_acpm_e = cargar_datos(URL_ACPM, nit_user)

    menu = st.sidebar.radio("Navegación", ["📊 Dashboard Gerencial", "⚖️ Gestión ACPM", "🛠️ Reporte Condiciones", "🧠 Reporte Comportamiento"])

    # --- PANTALLA DASHBOARD (TODAS LAS VARIABLES SOLICITADAS) ---
    if menu == "📊 Dashboard Gerencial":
        st.title(f"📊 Dashboard Gerencial - NIT: {nit_user}")
        tab1, tab2, tab3 = st.tabs(["🔍 BDI WCO SIGMA", "🧠 BDI COMPORTAMIENTO", "⚖️ BD ACPM"])
        
        with tab1: # CONDICIONES
            if not df_cond_e.empty:
                c1, c2 = st.columns(2)
                with c1:
                    st.plotly_chart(px.bar(df_cond_e, x='Centro de trabajo', color='Prioridad', title="Hallazgos por Centro"), use_container_width=True)
                    st.plotly_chart(px.pie(df_cond_e, names='Condición Crítica', title="Condición Crítica", hole=0.3), use_container_width=True)
                with c2:
                    st.plotly_chart(px.bar(df_cond_e, x='Lugar', color='Estado', title="Estatus por Lugar"), use_container_width=True)
                    st.plotly_chart(px.pie(df_cond_e, names='Prioridad', title="Prioridad / Urgencia"), use_container_width=True)
                st.session_state.an_cond = st.text_area("Análisis (Condiciones):", value=st.session_state.an_cond, key="k1")
                st.session_state.pl_cond = st.text_area("Plan Acción (Condiciones):", value=st.session_state.pl_cond, key="k2")
            else: st.warning("Sin datos en Condiciones.")

        with tab2: # COMPORTAMIENTO
            if not df_comp_e.empty:
                g1, g2 = st.columns(2)
                with g1:
                    st.plotly_chart(px.bar(df_comp_e, x='Centro de trabajo', color='Estado observado', title="Cultura por Centro"), use_container_width=True)
                with g2:
                    st.plotly_chart(px.bar(df_comp_e, x='Lugar', color='Estado observado', title="Cultura por Lugar"), use_container_width=True)
                st.session_state.an_comp = st.text_area("Análisis (Comportamiento):", value=st.session_state.an_comp, key="k3")
                st.session_state.pl_comp = st.text_area("Plan Acción (Comportamiento):", value=st.session_state.pl_comp, key="k4")
            else: st.warning("Sin datos en Comportamiento.")

        with tab3: # ACPM
            if not df_acpm_e.empty:
                a1, a2 = st.columns(2)
                with a1:
                    st.plotly_chart(px.pie(df_acpm_e, names='Componente', title="ACPM por Componente"), use_container_width=True)
                    st.plotly_chart(px.bar(df_acpm_e, x='Causa raíz', color='Estado', title="Causa Raíz vs Estado"), use_container_width=True)
                with a2:
                    st.plotly_chart(px.bar(df_acpm_e, x='Fuente', color='Tipo Acción', title="Fuente vs Tipo de Acción"), use_container_width=True)
                    st.plotly_chart(px.pie(df_acpm_e, names='Estado', title="Estatus General ACPM", hole=0.3), use_container_width=True)
                st.session_state.an_acpm = st.text_area("Análisis (ACPM):", value=st.session_state.an_acpm, key="k5")
                st.session_state.pl_acpm = st.text_area("Plan Acción (ACPM):", value=st.session_state.pl_acpm, key="k6")
            else: st.warning("Sin datos en ACPM.")

    # --- FORMULARIOS (RESTAURADOS Y VISIBLES) ---
    elif menu == "🛠️ Reporte Condiciones":
        st.title("🛠️ Registro de Condiciones")
        with st.form("form_cond"):
            col1, col2 = st.columns(2)
            with col1:
                f_ct = st.text_input("Centro de trabajo")
                f_lg = st.text_input("Lugar")
                f_hl = st.text_area("Descripción Hallazgo")
            with col2:
                f_cc = st.selectbox("Condición Crítica", ["Orden/Aseo", "Herramientas", "Locativo", "Vial", "Otros"])
                f_tr = st.selectbox("Riesgo (GTC 45)", ["Físico", "Químico", "Biológico", "Seguridad", "Natural"])
                f_pr = st.selectbox("Prioridad", ["Baja", "Media", "Alta"])
                f_es = st.selectbox("Estado", ["Abierto", "En Proceso", "Cerrado"])
            if st.form_submit_button("💾 GUARDAR CONDICIÓN"):
                nueva = pd.DataFrame([{"Nit":str(nit_user), "Centro de trabajo":f_ct, "Lugar":f_lg, "Fecha":str(datetime.now().date()), "Hallazgo":f_hl, "Condición Crítica":f_cc, "Clasificación del riesgo":f_tr, "Prioridad":f_pr, "Estado":f_es}])
                conn.update(spreadsheet=URL_COND, data=pd.concat([df_cond_t, nueva], ignore_index=True))
                st.success("Guardado correctamente.")

    elif menu == "🧠 Reporte Comportamiento":
        st.title("🧠 Registro de Comportamiento")
        with st.form("form_comp"):
            f_in = st.text_input("Inspector")
            f_ct = st.text_input("Centro de trabajo")
            f_lg = st.text_input("Lugar")
            f_eo = st.selectbox("Estado observado", ["✅ SEGURO", "⚠️ ATÍPICO", "🚫 PELIGROSO"])
            if st.form_submit_button("🚀 REGISTRAR COMPORTAMIENTO"):
                nueva = pd.DataFrame([{"Nit":str(nit_user), "Fecha/Hora Real":str(datetime.now()), "Inspector":f_in, "Centro de trabajo":f_ct, "Lugar":f_lg, "Estado observado":f_eo}])
                conn.update(spreadsheet=URL_COMP, data=pd.concat([df_comp_t, nueva], ignore_index=True))
                st.success("Registrado.")

    elif menu == "⚖️ Gestión ACPM":
        st.title("⚖️ Gestión de Mejora (ACPM)")
        with st.form("form_acpm"):
            c1, c2 = st.columns(2)
            with c1:
                f_em = st.text_input("Empresa")
                f_co = st.selectbox("Componente", ["SST", "Ambiente", "Calidad", "Vial"])
                f_fu = st.selectbox("Fuente", ["Auditoría", "Inspección", "Incidente"])
                p1, p2, p3, p4, p5 = st.text_input("P1"), st.text_input("P2"), st.text_input("P3"), st.text_input("P4"), st.text_input("P5")
            with c2:
                f_ra = st.text_input("Causa raíz")
                f_ti = st.radio("Tipo Acción", ["Correctiva", "Preventiva", "Mejora"])
                f_gc = st.radio("¿Activa Gestión del Cambio?", ["No", "Sí"])
                f_es = st.selectbox("Estado", ["Abierta", "En Ejecución", "Cerrada"])
            if st.form_submit_button("💾 GUARDAR ACPM"):
                nueva = pd.DataFrame([{"Nit":str(nit_user), "Empresa":f_em, "Componente":f_co, "Fuente":f_fu, "Análisis Causa ¿Porqué 1?":p1, "Análisis Causa ¿Porqué 2?":p2, "Análisis Causa ¿Porqué 3?":p3, "Análisis Causa ¿Porqué 4?":p4, "Análisis Causa ¿Porqué 5?":p5, "Causa raíz":f_ra, "Tipo Acción":f_ti, "Estado":f_es}])
                conn.update(spreadsheet=URL_ACPM, data=pd.concat([df_acpm_t, nueva], ignore_index=True))
                st.success("ACPM guardada.")
