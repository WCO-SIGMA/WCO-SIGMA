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

# --- CARGA DE DATOS (CON CACHÉ PARA ESTABILIDAD) ---
@st.cache_data(ttl=60)
def cargar_datos(url, nit):
    try:
        df = conn.read(spreadsheet=url, ttl=0)
        df.columns = df.columns.str.strip()
        col_nit = [c for c in df.columns if 'nit' in c.lower()][0]
        df['Nit_M'] = df[col_nit].astype(str).apply(lambda x: x.split('.')[0].strip())
        return df, df[df['Nit_M'] == nit]
    except:
        return pd.DataFrame(), pd.DataFrame()

# 2. LOGIN
nit_user = st.sidebar.text_input("Identificación Empresa (NIT):", "").strip()

if not nit_user:
    st.title("🚀 WCO-SIGMA PRO")
    st.info("Ingrese su NIT en la barra lateral para activar la plataforma.")
else:
    df_cond_t, df_cond_e = cargar_datos(URL_COND, nit_user)
    df_comp_t, df_comp_e = cargar_datos(URL_COMP, nit_user)
    df_acpm_t, df_acpm_e = cargar_datos(URL_ACPM, nit_user)

    menu = st.sidebar.selectbox("Seleccione Módulo", 
                                ["📊 Dashboard", "🛠️ BDI SIGMA", "🧠 COMPORTAMIENTO", "⚖️ ACPM"])

    # --- PANTALLA 1: DASHBOARD ---
    if menu == "📊 Dashboard":
        st.header(f"📊 Control Gerencial - {nit_user}")
        t1, t2, t3 = st.tabs(["SIGMA", "CULTURA", "ACPM"])
        with t1:
            if not df_cond_e.empty:
                st.plotly_chart(px.bar(df_cond_e, x='Centro de trabajo', color='Prioridad', barmode='group'), use_container_width=True)
            else: st.info("Sin datos.")
        with t2:
            if not df_comp_e.empty:
                st.plotly_chart(px.pie(df_comp_e, names='Estado observado', hole=0.3), use_container_width=True)
            else: st.info("Sin datos.")
        with t3:
            if not df_acpm_e.empty:
                st.plotly_chart(px.bar(df_acpm_e, x='Estado', color='Componente'), use_container_width=True)

    # --- PANTALLA 2: REPORTE CONDICIONES ---
    elif menu == "🛠️ BDI SIGMA":
        st.subheader("🛠️ Reporte de Condiciones")
        with st.form("form_sigma", clear_on_submit=True):
            f_ins = st.text_input("Inspector")
            f_ct = st.text_input("Centro de trabajo")
            f_lg = st.text_input("Lugar")
            f_tr = st.selectbox("Riesgo (GTC 45)", ["Físico", "Químico", "Biológico", "Psicosocial", "Biomecánico", "Seguridad", "Natural"])
            
            # Sub-lista dinámica
            dict_cond = {
                "Seguridad": ["Cables expuestos", "Falta de guardas", "Herramienta defectuosa"],
                "Químico": ["Envases sin rotular", "Falta de MSDS"],
                "Físico": ["Ruido", "Iluminación", "Calor/Frío"]
            }
            f_cc = st.selectbox("Condición Crítica", dict_cond.get(f_tr, ["Otros"]))
            f_pri = st.selectbox("Prioridad", ["Alta", "Moderada", "Baja"])
            f_est = st.selectbox("Estado", ["Abierta", "Trámite", "Cerrada"])
            f_hal = st.text_area("Hallazgo")
            
            st.write("✒️ Espacio para Firma")
            st_canvas(stroke_width=2, stroke_color="#000", background_color="#eee", height=100, key="sig_canvas")
            
            if st.form_submit_button("💾 GUARDAR"):
                id_i = str(uuid.uuid4())[:8].upper()
                nueva = pd.DataFrame([{"Nit":nit_user, "ID_Inspección":id_i, "Fecha/Hora Real":str(datetime.now()), "Inspector":f_ins, "Centro de trabajo":f_ct, "Lugar":f_lg, "Hallazgo":f_hal, "Condición Crítica":f_cc, "Clasificación del riesgo":f_tr, "Prioridad":f_pri, "Estado":f_est}])
                conn.update(spreadsheet=URL_COND, data=pd.concat([df_cond_t, nueva], ignore_index=True))
                st.success("Guardado.")

    # --- PANTALLA 3: COMPORTAMIENTO ---
    elif menu == "🧠 COMPORTAMIENTO":
        st.subheader("🧠 Reporte de Comportamiento")
        with st.form("form_comp", clear_on_submit=True):
            f_in = st.text_input("Inspector")
            f_ct = st.text_input("Centro de trabajo")
            f_obs = st.selectbox("Estado observado", ["✅ SEGURO", "⚠️ ATÍPICO", "🚫 PELIGROSO"])
            f_bar = st.selectbox("Barrera", ["Capacitación", "Herramienta", "EPP", "Presión Tiempo"])
            f_hal = st.text_area("Observaciones")
            
            st.write("✒️ Espacio para Firma")
            st_canvas(stroke_width=2, stroke_color="#000", background_color="#eee", height=100, key="comp_canvas")
            
            if st.form_submit_button("🚀 REGISTRAR"):
                id_i = str(uuid.uuid4())[:8].upper()
                nueva = pd.DataFrame([{"Nit":nit_user, "ID_Inspección":id_i, "Fecha/Hora Real":str(datetime.now()), "Inspector":f_in, "Centro de trabajo":f_ct, "Estado observado":f_obs, "Barrera de Seguridad":f_bar, "Observaciones Factor Humano":f_hal}])
                conn.update(spreadsheet=URL_COMP, data=pd.concat([df_comp_t, nueva], ignore_index=True))
                st.success("Registrado.")

    # --- PANTALLA 4: ACPM ---
    elif menu == "⚖️ ACPM":
        st.subheader("⚖️ Gestión ACPM")
        with st.form("form_acpm"):
            f_co = st.selectbox("Componente", ["SST", "Ambiente", "Vial", "Calidad"])
            f_fu = st.selectbox("Fuente", ["inspecciones", "incidentes", "auditorías", "revisión gerencial"])
            p1, p2, p3 = st.text_input("¿P1?"), st.text_input("¿P2?"), st.text_input("¿P3?")
            f_ra = st.text_input("Causa raíz")
            f_ap = st.text_area("Acción Propuesta")
            f_ti = st.selectbox("Tipo Acción", ["corrección", "correctiva", "preventiva", "mejora"])
            f_gc = st.radio("¿Activa Gestión del Cambio?", ["No", "Si"])
            f_es = st.selectbox("Estado", ["Abierta", "Trámite", "Cerrada"])
            
            if f_gc == "Si": st.warning("⚠️ Recuerde actualizar IPVR e IAVI.")
            
            if st.form_submit_button("💾 GUARDAR"):
                nueva = pd.DataFrame([{"Nit":nit_user, "Fecha de reporte":str(datetime.now().date()), "Componente":f_co, "Fuente":f_fu, "Causa raíz":f_ra, "Acción Propuesta":f_ap, "Tipo Acción":f_ti, "Estado":f_es, "La acción tomada activa gestión del cambio":f_gc}])
                conn.update(spreadsheet=URL_ACPM, data=pd.concat([df_acpm_t, nueva], ignore_index=True))
                st.success("ACPM Guardada.")
