import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.express as px
from datetime import datetime
import uuid
from streamlit_canvas import st_canvas
# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="WCO-SIGMA PRO", layout="wide")

# --- CONEXIONES ---
URL_COND = "https://docs.google.com/spreadsheets/d/18OIJe409rr6o_o4HSweiuncIoOrgJOXEt0GFCmEsL4g/edit"
URL_COMP = "https://docs.google.com/spreadsheets/d/1szrDZsA59e5sMF6OAzPeQ_nDX7E9lMehaXCPHmVNx5o/edit"
URL_ACPM = "https://docs.google.com/spreadsheets/d/1yXQNE3PiET-8VOHBWiReht7psRqjbAm5ZnY4P2XQQvg/edit" 

conn = st.connection("gsheets", type=GSheetsConnection)

# --- CARGA DE DATOS OPTIMIZADA ---
@st.cache_data(ttl=60) # Esto ayuda a la estabilidad
def cargar_datos(url, nit):
    try:
        df = conn.read(spreadsheet=url, ttl=0)
        df.columns = df.columns.str.strip()
        col_nit = [c for c in df.columns if 'nit' in c.lower()][0]
        df['Nit_M'] = df[col_nit].astype(str).apply(lambda x: x.split('.')[0].strip())
        return df, df[df['Nit_M'] == nit]
    except:
        return pd.DataFrame(), pd.DataFrame()

# 2. LOGIN Y SIDEBAR
st.sidebar.header("🛡️ Acceso WCO-SIGMA")
nit_user = st.sidebar.text_input("Identificación (NIT):", "").strip()

if not nit_user:
    st.title("🚀 WCO-SIGMA PRO")
    st.info("Ingrese su NIT para activar la plataforma.")
else:
    df_cond_t, df_cond_e = cargar_datos(URL_COND, nit_user)
    df_comp_t, df_comp_e = cargar_datos(URL_COMP, nit_user)
    df_acpm_t, df_acpm_e = cargar_datos(URL_ACPM, nit_user)

    menu = st.sidebar.selectbox("Seleccione Módulo", 
                                ["📊 Dashboard Gerencial", "🛠️ Reporte Condiciones", "🧠 Reporte Comportamiento", "⚖️ Gestión ACPM"])

    # --- PANTALLA 1: DASHBOARD (RENDERIZADO SEGURO) ---
    if menu == "📊 Dashboard Gerencial":
        st.header(f"📊 Dashboard de Control - NIT: {nit_user}")
        t1, t2, t3 = st.tabs(["BDI SIGMA", "COMPORTAMIENTO", "ACPM"])
        
        with t1:
            if not df_cond_e.empty:
                st.plotly_chart(px.bar(df_cond_e, x='Centro de trabajo', color='Prioridad', title="Hallazgos"), use_container_width=True)
                st.plotly_chart(px.pie(df_cond_e, names='Estado', title="Estatus General"), use_container_width=True)
            else: st.info("Sin registros.")

        with t2:
            if not df_comp_e.empty:
                st.plotly_chart(px.bar(df_comp_e, x='Estado observado', color='Barrera de Seguridad', title="Cultura"), use_container_width=True)
            else: st.info("Sin registros.")

        with t3:
            if not df_acpm_e.empty:
                st.plotly_chart(px.pie(df_acpm_e, names='Componente', title="ACPM por Sistema"), use_container_width=True)
            else: st.info("Sin registros.")

    # --- PANTALLA 2: REPORTE CONDICIONES (CON LISTAS TÉCNICAS) ---
    elif menu == "🛠️ Reporte Condiciones":
        st.subheader("🛠️ Registro de Actos y Condiciones")
        with st.form("form_cond"):
            c1, c2 = st.columns(2)
            with c1:
                f_ins = st.text_input("Inspector")
                f_ct = st.text_input("Centro de trabajo")
                f_lg = st.text_input("Lugar")
                f_tr = st.selectbox("Riesgo (GTC 45)", ["Físico", "Químico", "Biológico", "Psicosocial", "Biomecánico", "Seguridad", "Natural"])
            with c2:
                # Diccionario de condiciones por riesgo
                dict_cond = {
                    "Seguridad": ["Cables expuestos", "Falta de guardas", "Andamios inestables", "Herramienta defectuosa"],
                    "Químico": ["Envases sin rotular", "Falta de MSDS", "Almacenamiento incompatible"],
                    "Físico": ["Iluminación deficiente", "Ruido alto", "Calor/Frío extremo"],
                    "Biológico": ["Residuos mal dispuestos", "Presencia de vectores"],
                    "Biomecánico": ["Postura prolongada", "Levantamiento de cargas"],
                    "Psicosocial": ["Carga laboral", "Acoso"],
                    "Natural": ["Sismo", "Inundación", "Vendaval"]
                }
                f_cc = st.selectbox("Condición Crítica Detallada", dict_cond.get(f_tr, ["Otros"]))
                f_pr = st.selectbox("Prioridad", ["Alta", "Moderada", "Baja"])
                f_es = st.selectbox("Estado", ["Abierta", "Trámite", "Cerrada"])
            
            f_hal = st.text_area("Descripción del Hallazgo")
            st.write("✒️ Firma del Inspector")
            canvas = st_canvas(stroke_width=2, stroke_color="#000", background_color="#eee", height=100, key="c1")
            
            if st.form_submit_button("💾 GUARDAR"):
                id_i = str(uuid.uuid4())[:8].upper()
                nueva = pd.DataFrame([{"Nit":nit_user, "ID_Inspección":id_i, "Fecha/Hora Real":str(datetime.now()), "Inspector":f_ins, "Centro de trabajo":f_ct, "Lugar":f_lg, "Hallazgo":f_hal, "Condición Crítica":f_cc, "Clasificación del riesgo":f_tr, "Prioridad":f_pr, "Estado":f_es}])
                conn.update(spreadsheet=URL_COND, data=pd.concat([df_cond_t, nueva], ignore_index=True))
                st.success("Inspección Guardada.")

    # --- PANTALLA 3: REPORTE COMPORTAMIENTO ---
    elif menu == "🧠 Reporte Comportamiento":
        st.subheader("🧠 Observación de Comportamiento")
        with st.form("form_comp"):
            f_in = st.text_input("Inspector")
            f_ct = st.text_input("Centro de trabajo")
            f_lg = st.text_input("Lugar")
            f_eo = st.selectbox("Estado observado", ["✅ SEGURO", "⚠️ ATÍPICO", "🚫 PELIGROSO"])
            f_bs = st.selectbox("Barrera de Seguridad", ["Falta de capacitación", "Herramienta inadecuada", "EPP inadecuado", "Presión de tiempo", "Otro"])
            f_ob = st.text_area("Observaciones")
            
            st.write("✒️ Firma")
            st_canvas(stroke_width=2, stroke_color="#000", background_color="#eee", height=100, key="c2")
            
            if st.form_submit_button("🚀 REGISTRAR"):
                id_i = str(uuid.uuid4())[:8].upper()
                nueva = pd.DataFrame([{"Nit":nit_user, "ID_Inspección":id_i, "Fecha/Hora Real":str(datetime.now()), "Inspector":f_in, "Centro de trabajo":f_ct, "Lugar":f_lg, "Estado observado":f_eo, "Barrera de Seguridad":f_bs, "Observaciones Factor Humano":f_ob}])
                conn.update(spreadsheet=URL_COMP, data=pd.concat([df_comp_t, nueva], ignore_index=True))
                st.success("Registrado.")

    # --- PANTALLA 4: GESTIÓN ACPM ---
    elif menu == "⚖️ Gestión ACPM":
        st.subheader("⚖️ Gestión de Mejora (ACPM)")
        with st.form("form_acpm"):
            col1, col2 = st.columns(2)
            with col1:
                f_co = st.selectbox("Componente", ["SST", "Ambiente", "Vial", "Calidad"])
                f_fu = st.selectbox("Fuente", ["inspecciones", "incidentes", "auditorías", "observación tareas", "revisión gerencial"])
                p1, p2, p3 = st.text_input("¿Por qué 1?"), st.text_input("¿Por qué 2?"), st.text_input("¿Por qué 3?")
            with col2:
                f_ra = st.text_input("Causa raíz")
                f_ap = st.text_area("Acción Propuesta")
                f_ti = st.selectbox("Tipo Acción", ["corrección", "correctiva", "preventiva", "mejora"])
                f_gc = st.radio("¿Activa Gestión del Cambio?", ["No", "Si"])
                f_es = st.selectbox("Estado", ["Abierta", "Trámite", "Cerrada"])
            
            if f_gc == "Si": st.warning("⚠️ ALERTA: Esta acción requiere actualizar IPVR e IAVI.")
            
            if st.form_submit_button("💾 GUARDAR"):
                nueva = pd.DataFrame([{"Nit":nit_user, "Fecha de reporte":str(datetime.now().date()), "Componente":f_co, "Fuente":f_fu, "Causa raíz":f_ra, "Acción Propuesta":f_ap, "Tipo Acción":f_ti, "Estado":f_es, "La acción tomada activa gestión del cambio":f_gc}])
                conn.update(spreadsheet=URL_ACPM, data=pd.concat([df_acpm_t, nueva], ignore_index=True))
                st.success("ACPM Guardada.")
