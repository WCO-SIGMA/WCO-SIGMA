import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.express as px
from datetime import datetime
import uuid

# 1. CONFIGURACIÓN
st.set_page_config(page_title="WCO-SIGMA SIG+ACPM", layout="wide")

# --- IDs DE TUS ARCHIVOS (CONFIGURACIÓN CRÍTICA) ---
ID_COND = "18OIJe409rr6o_o4HSweiuncIoOrgJOXEt0GFCmEsL4g"
ID_COMP = "1szrDZsA59e5sMF6OAzPeQ_nDX7E9lMehaXCPHmVNx5o"
ID_ACPM = "TU_ID_DE_LA_BD_ACPM_AQUI" # <--- VERIFICA ESTE ID

conn = st.connection("gsheets", type=GSheetsConnection)

# 2. ACCESO
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/1063/1063302.png", width=100)
nit_input = st.sidebar.text_input("Ingrese NIT de la Empresa:", "").strip()

if not nit_input:
    st.title("🚀 WCO-SIGMA: Sistema de Gestión PHVA")
    st.info("Motores vinculados. Ingrese el NIT para activar el Dashboard y los Reportes.")
else:
    # --- MOTOR DE LECTURA ROBUSTO ---
    def cargar_datos_seguros(sheet_id):
        try:
            df = conn.read(spreadsheet=sheet_id, ttl=0)
            if df is not None and not df.empty:
                df.columns = df.columns.str.strip()
                # Limpieza profunda de la columna Nit
                df['Nit'] = df['Nit'].astype(str).str.split('.').str[0].str.strip()
                return df, df[df['Nit'] == str(nit_input)]
            return pd.DataFrame(), pd.DataFrame()
        except Exception as e:
            return pd.DataFrame(), pd.DataFrame()

    df_cond_total, df_cond_emp = cargar_datos_seguros(ID_COND)
    df_comp_total, df_comp_emp = cargar_datos_seguros(ID_COMP)
    df_acpm_total, df_acpm_emp = cargar_datos_seguros(ID_ACPM)

    menu = st.sidebar.radio("Navegación", ["📊 Dashboard SIG", "⚖️ Gestión de ACPM", "🛠️ Reporte Condiciones", "🧠 Reporte Comportamiento"])

    # --- PANTALLA 1: DASHBOARD (REPARADO) ---
    if menu == "📊 Dashboard SIG":
        st.title(f"📊 Tablero SIG - NIT: {nit_input}")
        tab1, tab2, tab3 = st.tabs(["🔍 Condiciones", "🧠 Comportamiento", "⚖️ ACPM"])
        
        with tab1:
            if not df_cond_emp.empty:
                c1, c2 = st.columns(2)
                with c1: st.plotly_chart(px.pie(df_cond_emp, names='Estado', title="Estatus de Condiciones"), use_container_width=True)
                with c2: st.plotly_chart(px.bar(df_cond_emp, x='Prioridad', color='Prioridad', title="Prioridad de Cierre"), use_container_width=True)
                st.dataframe(df_cond_emp, use_container_width=True)
            else:
                st.warning("⚠️ No se encontraron datos de condiciones para este NIT. Realice un reporte de prueba.")

        with tab2:
            if not df_comp_emp.empty:
                st.plotly_chart(px.bar(df_comp_emp, x='Estado observado', color='Estado observado', title="Análisis Conductual"), use_container_width=True)
                st.dataframe(df_comp_emp, use_container_width=True)
            else: st.warning("⚠️ No hay datos de comportamiento registrados.")

        with tab3:
            if not df_acpm_emp.empty:
                ca1, ca2 = st.columns(2)
                with ca1: st.plotly_chart(px.pie(df_acpm_emp, names='Componente', title="ACPM por Sistema"), use_container_width=True)
                with ca2: st.plotly_chart(px.bar(df_acpm_emp, x='Estado', color='Estado', title="Estado de ACPM"), use_container_width=True)
                st.dataframe(df_acpm_emp, use_container_width=True)
            else: st.warning("⚠️ No hay acciones (ACPM) en la base de datos.")

    # --- PANTALLA 2: GESTIÓN DE ACPM (CONSTRUCTOR SEGURO) ---
    elif menu == "⚖️ Gestión de ACPM":
        st.title("⚖️ Reporte de Acciones ACPM")
        with st.form("form_acpm_v3"):
            c1, c2 = st.columns(2)
            with c1:
                f_emp = st.text_input("Empresa/Sede")
                f_comp = st.selectbox("Componente SIG", ["SST", "Ambiente", "Calidad", "Vial"])
                f_fuente = st.selectbox("Fuente", ["inspecciones", "investigación de incidentes", "auditorías internas y externas", "observación de tareas", "reportes de actos y condiciones", "Legislación o normatividad", "Revisión gerencial"])
                f_desc = st.text_area("Descripción del Hallazgo")
                p1, p2, p3, p4, p5 = st.text_input("¿P1?"), st.text_input("¿P2?"), st.text_input("¿P3?"), st.text_input("¿P4?"), st.text_input("¿P5?")
            with c2:
                f_raiz = st.text_input("Causa Raíz Final")
                f_accion = st.text_area("Acción Propuesta")
                f_tipo = st.radio("Tipo Acción", ["Correctiva", "Preventiva", "Mejora"])
                f_resp = st.text_input("Responsable")
                f_fec_c = st.date_input("Fecha Cierre Prevista")
                f_cambio = st.radio("¿Activa gestión del cambio?", ["No", "Sí"])
                f_estado = st.selectbox("Estado", ["Abierta", "En Ejecución"])

            if st.form_submit_button("💾 GUARDAR ACPM"):
                try:
                    nueva = pd.DataFrame([{
                        "Nit": str(nit_input), "Empresa": f_emp, "Fecha de reporte": str(datetime.now().date()),
                        "Componente": f_comp, "Fuente": f_fuente, "Descripción Hallazgo": f_desc,
                        "Análisis Causa ¿Porqué 1?": p1, "Análisis Causa ¿Porqué 2?": p2,
                        "Análisis Causa ¿Porqué 3?": p3, "Análisis Causa ¿Porqué 4?": p4,
                        "Análisis Causa ¿Porqué 5?": p5, "Causa raíz": f_raiz,
                        "Acción Propuesta": f_accion, "Tipo Acción": f_tipo, "Responsable": f_resp,
                        "Fecha Cierre Prevista": str(f_fec_c), "Eficacia de la acción tomada": "Pendiente",
                        "La acción tomada activa gestión del cambio (Si es afirmativo IPVR, IAVI y sus controles)": f_cambio, 
                        "Estado": f_estado
                    }])
                    df_upd = pd.concat([df_acpm_total, nueva], ignore_index=True)
                    # Sobrescribimos la hoja entera para asegurar consistencia
                    conn.client.open_by_key(ID_ACPM).sheet1.update([df_upd.columns.values.tolist()] + df_upd.values.tolist())
                    st.success("✅ ACPM centralizada correctamente.")
                    st.balloons()
                except Exception as e:
                    st.error(f"❌ Error al guardar: {e}")

    # --- REPORTES RESTAURADOS ---
    elif menu == "🛠️ Reporte Condiciones":
        st.title("🛠️ Registro de Condiciones")
        with st.form("f_cond"):
            f_hall = st.text_area("Hallazgo")
            f_cat = st.selectbox("Categoría", ["Orden y aseo", "Vial", "SST", "Otros"])
            if st.form_submit_button("✅ GUARDAR"):
                try:
                    nueva_c = pd.DataFrame([{"Nit": str(nit_input), "Empresa": "Sede", "Fecha": str(datetime.now().date()), "Hallazgo": f_hall, "Condición Crítica": f_cat, "Clasificación del riesgo": "Seguridad", "Componente": "SST", "Responsable del cierre": "Auditor", "Fecha propuesta para el cierre": str(datetime.now().date()), "Prioridad": "Media", "Estado": "Abierto", "Observación": "Registro inicial"}])
                    df_u = pd.concat([df_cond_total, nueva_c], ignore_index=True)
                    conn.client.open_by_key(ID_COND).sheet1.update([df_u.columns.values.tolist()] + df_u.values.tolist())
                    st.success("Guardado exitoso.")
                except Exception as e: st.error(f"Error: {e}")

    elif menu == "🧠 Reporte Comportamiento":
        st.title("🧠 Registro de Comportamiento")
        with st.form("f_comp"):
            f_obs = st.text_area("Detalle Conducta")
            if st.form_submit_button("🚀 REGISTRAR"):
                try:
                    nueva_comp = pd.DataFrame([{"Nit": str(nit_input), "ID_Inspección": str(uuid.uuid4())[:8], "Fecha/Hora Real": str(datetime.now()), "Inspector": "Auditor", "Tipo de Inspección": "Conducta", "Estado observado": "✅ SEGURO", "Evidencia Fotográfica": "N/A", "Observaciones Factor Humano": f_obs}])
                    df_u = pd.concat([df_comp_total, nueva_comp], ignore_index=True)
                    conn.client.open_by_key(ID_COMP).sheet1.update([df_u.columns.values.tolist()] + df_u.values.tolist())
                    st.success("Registrado.")
                except Exception as e: st.error(f"Error: {e}")
