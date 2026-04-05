import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.express as px
from datetime import datetime
import uuid

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="WCO-SIGMA SIG+ACPM", layout="wide")

# --- CONFIGURACIÓN DE CONEXIONES ---
# Asegúrate de que estos nombres coincidan con tus archivos en Drive
TITULO_COND = "BDI WCO SIGMA"
TITULO_COMP = "BDI COMPORTAMIENTO"
TITULO_ACPM = "BD ACPM" 

conn = st.connection("gsheets", type=GSheetsConnection)

# 2. ACCESO POR NIT
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/1063/1063302.png", width=100)
nit_user = st.sidebar.text_input("Ingrese NIT de la Empresa:", "").strip()

if not nit_user:
    st.title("🚀 WCO-SIGMA: Gestión Integral SIG")
    st.info("Sistemas BDI Sincronizados. Ingrese el NIT para visualizar indicadores y espacios de análisis.")
else:
    # --- MOTOR DE LECTURA ROBUSTO ---
    def cargar_datos(nombre_planilla):
        try:
            # Forzamos TTL=0 para ver cambios en tiempo real
            df = conn.read(spreadsheet=nombre_planilla, ttl=0)
            if df is not None and not df.empty:
                df.columns = df.columns.str.strip()
                # Limpieza profunda de NIT (quitar .0 y espacios)
                df['Nit'] = df['Nit'].astype(str).apply(lambda x: x.split('.')[0].strip())
                df_filtrado = df[df['Nit'] == nit_user]
                return df, df_filtrado
            return pd.DataFrame(), pd.DataFrame()
        except Exception as e:
            return pd.DataFrame(), pd.DataFrame()

    df_cond_total, df_cond_emp = cargar_datos(TITULO_COND)
    df_comp_total, df_comp_emp = cargar_datos(TITULO_COMP)
    df_acpm_total, df_acpm_emp = cargar_datos(TITULO_ACPM)

    menu = st.sidebar.radio("Navegación SIG", ["📊 Dashboard Gerencial", "⚖️ Gestión de ACPM", "🛠️ Reporte Condiciones", "🧠 Reporte Comportamiento"])

    # --- PANTALLA 1: DASHBOARD CON ESPACIOS DE ANÁLISIS ---
    if menu == "📊 Dashboard Gerencial":
        st.title(f"📊 Tablero de Control y Análisis - NIT: {nit_user}")
        tab1, tab2, tab3 = st.tabs(["🔍 Condiciones HSEQ", "🧠 Comportamiento", "⚖️ Mejora (ACPM)"])
        
        with tab1:
            if not df_cond_emp.empty:
                c1, c2 = st.columns(2)
                with c1: st.plotly_chart(px.bar(df_cond_emp, x='Centro de trabajo', color='Prioridad', title="Hallazgos por Centro"), use_container_width=True)
                with c2: st.plotly_chart(px.pie(df_cond_emp, names='Estado', title="Estatus de Cierre", hole=0.4), use_container_width=True)
                
                st.subheader("📝 Análisis y Plan de Acción - Condiciones")
                col_an1, col_an2 = st.columns(2)
                with col_an1: st.text_area("Interpretación de Hallazgos:", placeholder="Describa la tendencia observada...", key="an_cond_1")
                with col_an2: st.text_area("Plan de Acción Propuesto:", placeholder="Medidas correctivas inmediatas...", key="plan_cond_1")
                st.dataframe(df_cond_emp, use_container_width=True)
            else: st.warning(f"Sin datos en {TITULO_COND} para este NIT.")

        with tab2:
            if not df_comp_emp.empty:
                g1, g2 = st.columns(2)
                with g1: st.plotly_chart(px.bar(df_comp_emp, x='Estado observado', color='Estado observado', title="Cultura de Seguridad"), use_container_width=True)
                with g2: st.plotly_chart(px.pie(df_comp_emp, names='Lugar', title="Observaciones por Lugar"), use_container_width=True)
                
                st.subheader("🧠 Análisis Conductual y Plan de Mejora")
                col_ab1, col_ab2 = st.columns(2)
                with col_ab1: st.text_area("Diagnóstico Factor Humano:", placeholder="Análisis de actos inseguros...", key="an_comp_1")
                with col_ab2: st.text_area("Estrategia de Sensibilización:", placeholder="Charlas, capacitaciones...", key="plan_comp_1")
                st.dataframe(df_comp_emp, use_container_width=True)
            else: st.warning(f"Sin datos en {TITULO_COMP} para este NIT.")

        with tab3:
            # Verificación visual de datos para diagnóstico
            if not df_acpm_emp.empty:
                ca1, ca2 = st.columns(2)
                with ca1: st.plotly_chart(px.pie(df_acpm_emp, names='Componente', title="ACPM por Sistema", hole=0.4), use_container_width=True)
                with ca2: st.plotly_chart(px.bar(df_acpm_emp, x='Estado', color='Tipo Acción', title="Avance de Acciones"), use_container_width=True)
                
                st.subheader("⚖️ Evaluación de la Mejora Continua")
                st.text_area("Análisis de Eficacia de las Acciones:", placeholder="¿Las acciones cerradas eliminaron la causa raíz?...", key="an_acpm_1")
                st.dataframe(df_acpm_emp, use_container_width=True)
            else:
                st.error("⚠️ No se encontraron datos en la BD ACPM.")
                st.info("Sugerencia: Verifique que en el Excel 'BD ACPM' existan registros con este NIT y que la columna se llame exactamente 'Nit'.")

    # --- PANTALLA 2: REPORTE ACPM (REHABILITADO) ---
    elif menu == "⚖️ Gestión de ACPM":
        st.title("⚖️ Registro Técnico de ACPM")
        with st.form("form_acpm_vfinal"):
            c1, c2 = st.columns(2)
            with c1:
                f_emp_a = st.text_input("Empresa")
                f_comp_a = st.selectbox("Componente SIG", ["SST", "Ambiente", "Calidad", "Vial"])
                f_fuen_a = st.selectbox("Fuente", ["inspecciones", "auditorías", "incidentes", "revisión gerencial"])
                f_desc_a = st.text_area("Descripción Hallazgo")
                st.markdown("**Análisis de Causa (5 Porqués)**")
                p1, p2, p3, p4, p5 = st.text_input("¿Por qué? 1"), st.text_input("¿Por qué? 2"), st.text_input("¿Por qué? 3"), st.text_input("¿Por qué? 4"), st.text_input("¿Por qué? 5")
            with c2:
                f_raiz_a = st.text_input("Causa raíz")
                f_acci_a = st.text_area("Acción Propuesta (Plan de Acción)")
                f_tipo_a = st.radio("Tipo Acción", ["Correctiva", "Preventiva", "Mejora"])
                f_resp_a = st.text_input("Responsable")
                f_fec_c_a = st.date_input("Fecha Cierre Prevista")
                f_esta_a = st.selectbox("Estado Inicial", ["Abierta", "En Ejecución"])
                f_camb_a = st.radio("¿Gestión del cambio?", ["No", "Sí"])

            if st.form_submit_button("💾 REGISTRAR ACPM"):
                nueva_a = pd.DataFrame([{
                    "Nit": str(nit_user), "Empresa": f_emp_a, "Fecha de reporte": str(datetime.now().date()),
                    "Componente": f_comp_a, "Fuente": f_fuen_a, "Descripción Hallazgo": f_desc_a,
                    "Análisis Causa ¿Porqué 1?": p1, "Análisis Causa ¿Porqué 2?": p2, "Análisis Causa ¿Porqué 3?": p3, 
                    "Análisis Causa ¿Porqué 4?": p4, "Análisis Causa ¿Porqué 5?": p5, "Causa raíz": f_raiz_a,
                    "Acción Propuesta": f_acci_a, "Tipo Acción": f_tipo_a, "Responsable": f_resp_a,
                    "Fecha Cierre Prevista": str(f_fec_c_a), "Eficacia de la acción tomada": "Pendiente",
                    "La acción tomada activa gestión del cambio (Si es afirmativo IPVR, IAVI y sus controles)": f_camb_a, 
                    "Estado": f_esta_a
                }])
                conn.update(spreadsheet=TITULO_ACPM, data=pd.concat([df_acpm_total, nueva_a], ignore_index=True))
                st.success("✅ ACPM Guardada y sincronizada.")
