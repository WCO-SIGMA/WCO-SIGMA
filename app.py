import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.express as px
from datetime import datetime
import uuid

# --- INTENTO DE CARGA DE LIBRERÍA DE FIRMA ---
try:
    from streamlit_canvas import st_canvas
    CANVAS_OK = True
except ImportError:
    CANVAS_OK = False

# 1. CONFIGURACIÓN
st.set_page_config(page_title="WCO-SIGMA PRO", layout="wide")

# --- CONEXIONES ---
URL_COND = "https://docs.google.com/spreadsheets/d/18OIJe409rr6o_o4HSweiuncIoOrgJOXEt0GFCmEsL4g/edit"
URL_COMP = "https://docs.google.com/spreadsheets/d/1szrDZsA59e5sMF6OAzPeQ_nDX7E9lMehaXCPHmVNx5o/edit"
URL_ACPM = "https://docs.google.com/spreadsheets/d/1yXQNE3PiET-8VOHBWiReht7psRqjbAm5ZnY4P2XQQvg/edit" 

conn = st.connection("gsheets", type=GSheetsConnection)

# --- CARGA DE DATOS ---
def cargar_seguro(url, nit):
    try:
        df = conn.read(spreadsheet=url, ttl=0)
        df.columns = df.columns.str.strip()
        col_nit = [c for c in df.columns if 'nit' in c.lower()][0]
        df['Nit_Match'] = df[col_nit].astype(str).apply(lambda x: x.split('.')[0].strip())
        return df, df[df['Nit_Match'] == nit]
    except: return pd.DataFrame(), pd.DataFrame()

# 2. LOGIN
st.sidebar.title("🛡️ WCO-SIGMA")
nit_user = st.sidebar.text_input("Ingrese NIT:", "").strip()

if not nit_user:
    st.title("🚀 WCO-SIGMA PRO")
    st.info("Ingrese el NIT en la barra lateral para activar los módulos.")
else:
    df_cond_t, df_cond_e = cargar_seguro(URL_COND, nit_user)
    df_comp_t, df_comp_e = cargar_seguro(URL_COMP, nit_user)
    df_acpm_t, df_acpm_e = cargar_seguro(URL_ACPM, nit_user)

    menu = st.sidebar.selectbox("Módulo Principal", ["📊 Dashboard", "🛠️ BDI SIGMA", "🧠 COMPORTAMIENTO", "⚖️ ACPM"])

    # --- DASHBOARD ---
    if menu == "📊 Dashboard":
        st.header(f"📊 Dashboard Gerencial - NIT: {nit_user}")
        t1, t2, t3 = st.tabs(["BDI SIGMA", "COMPORTAMIENTO", "ACPM"])
        
        with t1:
            if not df_cond_e.empty:
                st.plotly_chart(px.bar(df_cond_e, x='Centro de trabajo', color='Prioridad', title="Indicador por Centro"), use_container_width=True)
                st.plotly_chart(px.pie(df_cond_e, names='Estado', title="Estatus de Condiciones"), use_container_width=True)
            else: st.warning("Sin datos en BDI SIGMA")

        with t2:
            if not df_comp_e.empty:
                st.plotly_chart(px.bar(df_comp_e, x='Estado observado', color='Barrera de Seguridad', title="Cultura de Seguridad"), use_container_width=True)
            else: st.warning("Sin datos en Comportamiento")

        with t3:
            if not df_acpm_e.empty:
                st.plotly_chart(px.pie(df_acpm_e, names='Componente', title="ACPM por Sistema"), use_container_width=True)
                st.plotly_chart(px.bar(df_acpm_e, x='Causa raíz', color='Estado', title="Análisis de Causa"), use_container_width=True)

    # --- BDI SIGMA ---
    elif menu == "🛠️ BDI SIGMA":
        st.header("🛠️ Reporte BDI WCO SIGMA")
        with st.form("f_sigma"):
            c1, c2 = st.columns(2)
            with c1:
                f_ins = st.text_input("Inspector")
                f_ct = st.text_input("Centro de trabajo")
                f_lg = st.text_input("Lugar")
                f_fe = st.date_input("Fecha")
                f_hal = st.text_area("Hallazgo")
            with c2:
                f_cc = st.selectbox("Condición Crítica", ["Cables desprotegidos", "Recipientes sin rotulación", "Falta de guardas", "Iluminación deficiente", "Otros"])
                f_tr = st.selectbox("Clasificación del riesgo (GTC 45)", ["Físico", "Químico", "Biológico", "Psicosocial", "Biomecánico", "Seguridad", "Natural"])
                f_co = st.selectbox("Componente", ["SST", "Ambiente", "Calidad", "Vial"])
                f_pri = st.selectbox("Prioridad", ["Alta", "Moderada", "Baja"])
                f_est = st.selectbox("Estado", ["Abierta", "Trámite", "Cerrada"])
            
            if CANVAS_OK:
                st.write("✒️ Firma Inspector")
                st_canvas(stroke_width=2, stroke_color="#000", background_color="#eee", height=100, key="c_sig")
            
            if st.form_submit_button("💾 GUARDAR INSPECCIÓN"):
                id_i = str(uuid.uuid4())[:8].upper()
                nueva = pd.DataFrame([{"Nit":nit_user, "ID_Inspección":id_i, "Fecha/Hora Real":str(datetime.now()), "Inspector":f_ins, "Centro de trabajo":f_ct, "Lugar":f_lg, "Fecha":str(f_fe), "Hallazgo":f_hal, "Condición Crítica":f_cc, "Clasificación del riesgo":f_tr, "Componente":f_co, "Prioridad":f_pri, "Estado":f_est}])
                conn.update(spreadsheet=URL_COND, data=pd.concat([df_cond_t, nueva], ignore_index=True))
                st.success("Guardado.")

    # --- COMPORTAMIENTO ---
    elif menu == "🧠 COMPORTAMIENTO":
        st.header("🧠 Reporte BDI COMPORTAMIENTO")
        with st.form("f_comp"):
            f_in = st.text_input("Inspector")
            f_ct = st.text_input("Centro de trabajo")
            f_lg = st.text_input("Lugar")
            f_eo = st.selectbox("Estado observado", ["Seguro", "Atípico", "Peligroso"])
            f_bs = st.selectbox("Barrera de Seguridad", ["Falta de capacitación", "Herramienta inadecuada", "EPP inadecuado", "Otro"])
            f_ob = st.text_area("Observaciones Factor Humano")
            
            if CANVAS_OK:
                st.write("✒️ Firma")
                st_canvas(stroke_width=2, stroke_color="#000", background_color="#eee", height=100, key="c_comp")
            
            if st.form_submit_button("🚀 REGISTRAR COMPORTAMIENTO"):
                id_i = str(uuid.uuid4())[:8].upper()
                nueva = pd.DataFrame([{"Nit":nit_user, "ID_Inspección":id_i, "Fecha/Hora Real":str(datetime.now()), "Inspector":f_in, "Centro de trabajo":f_ct, "Lugar":f_lg, "Estado observado":f_eo, "Barrera de Seguridad":f_bs, "Observaciones Factor Humano":f_ob}])
                conn.update(spreadsheet=URL_COMP, data=pd.concat([df_comp_t, nueva], ignore_index=True))
                st.success("Registrado.")

    # --- ACPM ---
    elif menu == "⚖️ ACPM":
        st.header("⚖️ Registro BD ACPM")
        with st.form("f_acpm"):
            col1, col2 = st.columns(2)
            with col1:
                f_fe = st.date_input("Fecha de reporte")
                f_co = st.selectbox("Componente", ["SST", "ambiente", "Vial", "Calidad"])
                f_fu = st.selectbox("Fuente", ["inspecciones", "investigación de incidentes", "auditorías", "observación de tareas", "reportes de actos y condiciones", "acciones administrativas"])
                f_de = st.text_area("Descripción Hallazgo")
                p1, p2, p3, p4, p5 = st.text_input("P1"), st.text_input("P2"), st.text_input("P3"), st.text_input("P4"), st.text_input("P5")
            with col2:
                f_ra = st.text_input("Causa raíz")
                f_ap = st.text_area("Acción Propuesta")
                f_ti = st.selectbox("Tipo Acción", ["corrección", "correctiva", "preventiva", "mejora"])
                f_re = st.text_input("Responsable")
                f_gc = st.radio("¿Activa Gestión del Cambio?", ["No", "Si"])
                f_es = st.selectbox("Estado", ["Cerrada", "Trámite", "Abierta"])
            
            if f_gc == "Si": st.warning("⚠️ ALERTA: Requiere actualizar IPVR e IAVI.")
            
            if st.form_submit_button("💾 GUARDAR ACPM"):
                nueva = pd.DataFrame([{"Nit":nit_user, "Fecha de reporte":str(f_fe), "Componente":f_co, "Fuente":f_fu, "Descripción Hallazgo":f_de, "¿Porqué 1?":p1, "¿Porqué 2?":p2, "¿Porqué 3?":p3, "¿Porqué 4?":p4, "¿Porqué 5?":p5, "Causa raíz":f_ra, "Acción Propuesta":f_ap, "Tipo Acción":f_ti, "Responsable":f_re, "La acción tomada activa gestión del cambio":f_gc, "Estado":f_es}])
                conn.update(spreadsheet=URL_ACPM, data=pd.concat([df_acpm_t, nueva], ignore_index=True))
                st.success("ACPM Guardada.")
