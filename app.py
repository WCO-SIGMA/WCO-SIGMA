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

# --- CARGA DE DATOS ---
def cargar(url, nit):
    try:
        df = conn.read(spreadsheet=url, ttl=0)
        df.columns = df.columns.str.strip()
        col_nit = [c for c in df.columns if 'nit' in c.lower()][0]
        df['Nit_M'] = df[col_nit].astype(str).apply(lambda x: x.split('.')[0].strip())
        return df, df[df['Nit_M'] == nit]
    except: return pd.DataFrame(), pd.DataFrame()

# 2. LOGIN Y SIDEBAR
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/1063/1063302.png", width=80)
nit_user = st.sidebar.text_input("Identificación Empresa (NIT):", "").strip()

if not nit_user:
    st.title("🚀 WCO-SIGMA PRO: Gestión Integral PHVA")
    st.info("Sistema de Auditoría Técnica. Ingrese NIT para comenzar.")
else:
    df_cond_t, df_cond_e = cargar(URL_COND, nit_user)
    df_comp_t, df_comp_e = cargar(URL_COMP, nit_user)
    df_acpm_t, df_acpm_e = cargar(URL_ACPM, nit_user)

    menu = st.sidebar.radio("Navegación", ["📊 Dashboard Gerencial", "🛠️ Reporte Condiciones (BDI)", "🧠 Reporte Comportamiento", "⚖️ Gestión ACPM"])

    # --- PANTALLA 1: DASHBOARD CON TODAS LAS VARIABLES ---
    if menu == "📊 Dashboard Gerencial":
        st.title(f"📊 Dashboard Gerencial - NIT: {nit_user}")
        tab1, tab2, tab3 = st.tabs(["🔍 BDI SIGMA", "🧠 COMPORTAMIENTO", "⚖️ ACPM"])
        
        with tab1: # Gráficos BDI SIGMA
            if not df_cond_e.empty:
                vars_cond = ['Centro de trabajo', 'Lugar', 'Condición Crítica', 'Prioridad', 'Estado']
                for v in vars_cond:
                    st.plotly_chart(px.bar(df_cond_e, x=v, title=f"Distribución por {v}", color=v), use_container_width=True)
            else: st.warning("Sin datos en BDI SIGMA")

        with tab2: # Gráficos COMPORTAMIENTO
            if not df_comp_e.empty:
                vars_comp = ['Centro de trabajo', 'Lugar', 'Estado observado', 'Barrera de Seguridad']
                for v in vars_comp:
                    st.plotly_chart(px.bar(df_comp_e, x=v, title=f"Tendencia de {v}", color=v), use_container_width=True)
            else: st.warning("Sin datos en Comportamiento")

        with tab3: # Gráficos ACPM
            if not df_acpm_e.empty:
                vars_acpm = ['Componente', 'Fuente', 'Causa raíz', 'Tipo Acción', 'Estado']
                for v in vars_acpm:
                    st.plotly_chart(px.pie(df_acpm_e, names=v, title=f"Proporción de {v}"), use_container_width=True)
            else: st.warning("Sin datos en ACPM")

    # --- PANTALLA 2: REPORTE CONDICIONES (CON GTC 45 Y FIRMA) ---
    elif menu == "🛠️ Reporte Condiciones (BDI)":
        st.title("🛠️ Registro de Actos y Condiciones")
        with st.form("form_cond_pro"):
            c1, c2 = st.columns(2)
            with c1:
                f_ins = st.text_input("Inspector")
                f_ct = st.text_input("Centro de trabajo")
                f_lg = st.text_input("Lugar")
                f_hal = st.text_area("Descripción Hallazgo")
            with c2:
                # Lógica GTC 45
                f_ries = st.selectbox("Clasificación del Riesgo (GTC 45)", 
                                     ["Físico", "Químico", "Biológico", "Psicosocial", "Biomecánico", "Seguridad", "Natural"])
                # Lógica Condición Crítica Dinámica
                lista_cond = {
                    "Seguridad": ["Cables desprotegidos", "Falta de guardas", "Andamios inseguros"],
                    "Químico": ["Recipientes sin rotulación", "Falta de diques", "Derrame de sustancias"],
                    "Físico": ["Ruido excesivo", "Iluminación deficiente", "Temperaturas extremas"]
                }.get(f_ries, ["General - Otros"])
                
                f_cc = st.selectbox("Condición Crítica", lista_cond)
                f_comp = st.selectbox("Componente", ["SST", "Ambiente", "Calidad", "Vial"])
                f_pri = st.selectbox("Prioridad", ["Alta", "Moderada", "Baja"])
                f_est = st.selectbox("Estado", ["Abierta", "Trámite", "Cerrada"])
            
            st.write("✒️ Firma Electrónica del Inspector")
            canvas_result = st_canvas(fill_color="rgba(255, 255, 255, 0.3)", stroke_width=2, stroke_color="#000000", background_color="#eee", height=150, key="canvas_cond")
            
            if st.form_submit_button("✅ REGISTRAR INSPECCIÓN"):
                id_ins = str(uuid.uuid4())[:8].upper()
                nueva_fila = pd.DataFrame([{
                    "Nit": nit_user, "ID_Inspección": id_ins, "Fecha/Hora Real": str(datetime.now()),
                    "Inspector": f_ins, "Centro de trabajo": f_ct, "Lugar": f_lg, "Fecha": str(datetime.now().date()),
                    "Hallazgo": f_hal, "Condición Crítica": f_cc, "Clasificación del riesgo": f_ries,
                    "Componente": f_comp, "Prioridad": f_pri, "Estado": f_est
                }])
                conn.update(spreadsheet=URL_COND, data=pd.concat([df_cond_t, nueva_fila], ignore_index=True))
                st.success(f"Registrado. ID: {id_ins}")

    # --- PANTALLA 3: REPORTE COMPORTAMIENTO (CON BARRERAS Y FIRMA) ---
    elif menu == "🧠 Reporte Comportamiento":
        st.title("🧠 Observación de Comportamiento")
        with st.form("form_comp_pro"):
            f_in = st.text_input("Inspector")
            f_ct = st.text_input("Centro de trabajo")
            f_lg = st.text_input("Lugar")
            f_obs = st.selectbox("Estado observado", ["✅ SEGURO", "⚠️ ATÍPICO", "🚫 PELIGROSO"])
            f_bar = st.selectbox("Barrera de Seguridad", ["Falta de capacitación", "Herramienta inadecuada", "EPP inadecuado", "Otro"])
            f_hal = st.text_area("Observaciones Factor Humano")
            
            st.write("✒️ Firma Electrónica")
            canvas_comp = st_canvas(fill_color="#eee", stroke_width=2, stroke_color="#000", height=150, key="canvas_comp")
            
            if st.form_submit_button("🚀 REGISTRAR COMPORTAMIENTO"):
                id_ins = str(uuid.uuid4())[:8].upper()
                nueva = pd.DataFrame([{
                    "Nit": nit_user, "ID_Inspección": id_ins, "Fecha/Hora Real": str(datetime.now()),
                    "Inspector": f_in, "Centro de trabajo": f_ct, "Lugar": f_lg, 
                    "Estado observado": f_obs, "Barrera de Seguridad": f_bar, "Observaciones Factor Humano": f_hal
                }])
                conn.update(spreadsheet=URL_COMP, data=pd.concat([df_comp_t, nueva], ignore_index=True))
                st.success("Registrado.")

    # --- PANTALLA 4: GESTIÓN ACPM (CON ALERTA DE CAMBIO) ---
    elif menu == "⚖️ Gestión ACPM":
        st.title("⚖️ Gestión de Mejora Continua (ACPM)")
        with st.form("form_acpm_pro"):
            col1, col2 = st.columns(2)
            with col1:
                f_fe = st.date_input("Fecha de reporte")
                f_co = st.selectbox("Componente", ["SST", "Ambiente", "Vial", "Calidad"])
                f_fu = st.selectbox("Fuente", ["inspecciones", "investigación de incidentes", "auditorías internas y externas", "observación de tareas", "reportes de actos y condiciones", "acciones administrativas", "Revisión gerencial"])
                p1, p2, p3, p4, p5 = st.text_input("¿Por qué 1?"), st.text_input("¿Por qué 2?"), st.text_input("¿Por qué 3?"), st.text_input("¿Por qué 4?"), st.text_input("¿Por qué 5?")
            with col2:
                f_de = st.text_area("Descripción Hallazgo")
                f_ra = st.text_input("Causa raíz")
                f_ap = st.text_area("Acción Propuesta")
                f_ti = st.selectbox("Tipo Acción", ["corrección", "correctiva", "preventiva", "mejora"])
                f_es = st.selectbox("Estado", ["Abierta", "Trámite", "Cerrada"])
                f_gc = st.radio("¿Activa Gestión del Cambio?", ["No", "Si"])
            
            if f_gc == "Si":
                st.warning("⚠️ ALERTA: La selección activa Gestión del Cambio. Recuerde actualizar IPVR e IAVI.")
            
            if st.form_submit_button("💾 GUARDAR ACPM"):
                nueva = pd.DataFrame([{
                    "Nit": nit_user, "Fecha de reporte": str(f_fe), "Componente": f_co, "Fuente": f_fu,
                    "Descripción Hallazgo": f_de, "¿Porqué 1?": p1, "¿Porqué 2?": p2, "¿Porqué 3?": p3,
                    "¿Porqué 4?": p4, "¿Porqué 5?": p5, "Causa raíz": f_ra, "Acción Propuesta": f_ap,
                    "Tipo Acción": f_ti, "Estado": f_es, "La acción tomada activa gestión del cambio": f_gc
                }])
                conn.update(spreadsheet=URL_ACPM, data=pd.concat([df_acpm_t, nueva], ignore_index=True))
                st.success("ACPM Registrada.")
