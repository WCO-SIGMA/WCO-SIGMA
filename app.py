import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.express as px
from datetime import datetime
import uuid

# 1. CONFIGURACIÓN
st.set_page_config(page_title="WCO-SIGMA SIG+PESV", layout="wide")

# --- URLs DE TUS BASES DE DATOS ---
URL_COND = "https://docs.google.com/spreadsheets/d/18OIJe409rr6o_o4HSweiuncIoOrgJOXEt0GFCmEsL4g/edit"
URL_COMP = "https://docs.google.com/spreadsheets/d/1szrDZsA59e5sMF6OAzPeQ_nDX7E9lMehaXCPHmVNx5o/edit"

conn = st.connection("gsheets", type=GSheetsConnection)

# 2. ACCESO POR NIT
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/1063/1063302.png", width=100)
nit_input = st.sidebar.text_input("Ingrese identificación (NIT/Cédula):", "").strip()

if not nit_input:
    st.title("🚀 WCO-SIGMA: Gestión Integral")
    st.success("✅ Conexión con Motores BDI establecida.")
    st.info("Ingrese el NIT para visualizar los tableros de control segregados.")
else:
    # --- PROCESAMIENTO INDEPENDIENTE DE DATOS ---
    # LECTURA CONDICIONES
    try:
        df_cond_total = conn.read(spreadsheet=URL_COND, ttl=0)
        df_cond_total.columns = df_cond_total.columns.str.strip()
        df_cond_total['Nit'] = df_cond_total['Nit'].astype(str).str.replace('.0', '', regex=False).str.strip()
        df_cond_emp = df_cond_total[df_cond_total['Nit'] == nit_input]
    except:
        df_cond_total = pd.DataFrame()
        df_cond_emp = pd.DataFrame()

    # LECTURA COMPORTAMIENTO
    try:
        df_comp_total = conn.read(spreadsheet=URL_COMP, ttl=0)
        df_comp_total.columns = df_comp_total.columns.str.strip()
        df_comp_total['Nit'] = df_comp_total['Nit'].astype(str).str.replace('.0', '', regex=False).str.strip()
        df_comp_emp = df_comp_total[df_comp_total['Nit'] == nit_input]
    except:
        df_comp_total = pd.DataFrame()
        df_comp_emp = pd.DataFrame()

    menu = st.sidebar.radio("Navegación", ["📊 Dashboard Gerencial", "🛠️ Reporte Condiciones", "🧠 Reporte Comportamiento", "📂 Carpeta PHVA"])

    # --- PANTALLA 1: DASHBOARD GERENCIAL (TABLEROS SEPARADOS) ---
    if menu == "📊 Dashboard Gerencial":
        st.title(f"📊 Dashboard Ejecutivo - NIT: {nit_input}")
        tab1, tab2 = st.tabs(["🔍 Gestión de Condiciones HSEQ", "🧠 Comportamiento & PESV"])
        
        # --- TAB 1: CONDICIONES ---
        with tab1:
            if not df_cond_emp.empty:
                c1, c2, c3 = st.columns(3)
                total_c = len(df_cond_emp)
                abiertos = len(df_cond_emp[df_cond_emp['Estado'].astype(str).str.upper() == 'ABIERTO'])
                c1.metric("Total Condiciones", total_c)
                c2.metric("Pendientes", abiertos, delta_color="inverse")
                c3.metric("% Eficacia", f"{int(((total_c-abiertos)/total_c)*100)}%" if total_c > 0 else "0%")
                
                g1, g2 = st.columns(2)
                with g1:
                    st.plotly_chart(px.pie(df_cond_emp, names='Estado', title="Estatus de Cierre", hole=0.4), use_container_width=True)
                with g2:
                    st.plotly_chart(px.bar(df_cond_emp['Condición Crítica'].value_counts().reset_index(), x='count', y='Condición Crítica', orientation='h', title="Hallazgos por Tipología"), use_container_width=True)
                st.dataframe(df_cond_emp, use_container_width=True)
            else:
                st.warning("Sin datos en la base de Condiciones.")

        # --- TAB 2: COMPORTAMIENTO (NUEVOS GRÁFICOS) ---
        with tab2:
            if not df_comp_emp.empty:
                m1, m2, m3 = st.columns(3)
                total_comp = len(df_comp_emp)
                seguros = len(df_comp_emp[df_comp_emp['Estado observado'].astype(str).str.contains('SEGURO', case=False)])
                m1.metric("Total Observaciones", total_comp)
                m2.metric("Actos Seguros", seguros)
                m3.metric("% Cultura Preventiva", f"{int((seguros/total_comp)*100)}%" if total_comp > 0 else "0%")

                col_comp1, col_comp2 = st.columns(2)
                with col_comp1:
                    # Gráfico de barras por tipo de inspección
                    fig_tipo = px.bar(df_comp_emp['Tipo de Inspección'].value_counts().reset_index(), 
                                    x='Tipo de Inspección', y='count', title="Distribución por Tipo de Auditoría",
                                    color='Tipo de Inspección')
                    st.plotly_chart(fig_tipo, use_container_width=True)
                with col_comp2:
                    # Gráfico de pastel por estado observado
                    fig_est = px.pie(df_comp_emp, names='Estado observado', title="Análisis de Riesgo Conductual", 
                                   color='Estado observado', color_discrete_map={'✅ SEGURO':'green', '⚠️ ATÍPICO':'orange', '🚫 PELIGROSO':'red'})
                    st.plotly_chart(fig_est, use_container_width=True)
                
                st.write("### 📋 Detalle de Observaciones de Factor Humano")
                st.dataframe(df_comp_emp, use_container_width=True)
            else:
                st.warning("Sin datos en la base de Comportamiento. Realice un registro para activar este tablero.")

    # --- RESTO DE MÓDULOS (REPORTES) ---
    elif menu == "🛠️ Reporte Condiciones":
        st.title("🛠️ Registro de Condiciones HSEQ")
        with st.form("form_cond"):
            col1, col2 = st.columns(2)
            with col1:
                f_emp = st.text_input("Empresa")
                f_hall = st.text_area("Hallazgo")
                f_cond = st.selectbox("Condición", ["Orden y aseo", "Herramientas/Equipos", "Daño locativo", "Sistemas eléctricos", "Alturas/Confinados", "Ambiental", "Vial", "Otros"])
            with col2:
                f_riesgo = st.selectbox("GTC 45", ["Físico", "Químico", "Biológico", "Psicosocial", "Biomecánico", "Seguridad", "Natural"])
                f_est = st.selectbox("Estado", ["Abierto", "En Proceso", "Cerrado"])
                f_obs = st.text_area("Plan de Acción")
            
            if st.form_submit_button("✅ GUARDAR CONDICIÓN"):
                nueva = pd.DataFrame([{"Nit":str(nit_input), "Empresa":f_emp, "Fecha":str(datetime.now().date()), "Hallazgo":f_hall, "Condición Crítica":f_cond, "Clasificación del riesgo":f_riesgo, "Componente":"SST", "Responsable del cierre":"Auditor", "Fecha propuesta para el cierre":str(datetime.now().date()), "Prioridad":"Media", "Estado":f_est, "Observación":f_obs}])
                conn.update(spreadsheet=URL_COND, data=pd.concat([df_cond_total, nueva], ignore_index=True))
                st.success("Guardado en BDI Condiciones.")
                st.balloons()

    elif menu == "🧠 Reporte Comportamiento":
        st.title("🧠 Registro de Comportamiento y PESV")
        id_gen = str(uuid.uuid4())[:8].upper()
        with st.form("form_comp"):
            c1, c2 = st.columns(2)
            with c1:
                f_ins = st.text_input("Nombre del Inspector")
                f_tipo = st.selectbox("Tipo de Inspección", ["Conducta Humana", "Preoperacional Vehículo (PESV)", "Tareas Críticas"])
                f_est_obs = st.selectbox("Estado Observado", ["✅ SEGURO", "⚠️ ATÍPICO", "🚫 PELIGROSO"])
            with c2:
                f_humano = st.multiselect("Factores Humanos", ["Distracción", "Fatiga", "Exceso de confianza", "Omisión de norma"])
                f_detalles = st.text_area("Descripción Detallada")
            
            if st.form_submit_button("🚀 REGISTRAR COMPORTAMIENTO"):
                nueva_c = pd.DataFrame([{"Nit":str(nit_input), "ID_Inspección":id_gen, "Fecha/Hora Real":str(datetime.now()), "Inspector":f_ins, "Tipo de Inspección":f_tipo, "Estado observado":f_est_obs, "Evidencia Fotográfica":"N/A", "Observaciones Factor Humano":", ".join(f_humano) + " | " + f_detalles}])
                conn.update(spreadsheet=URL_COMP, data=pd.concat([df_comp_total, nueva_c], ignore_index=True))
                st.success(f"Reporte {id_gen} guardado exitosamente.")

    elif menu == "📂 Carpeta PHVA":
        st.link_button("📁 Abrir Drive", "https://drive.google.com/drive/u/0/folders/17o_kAZMRcGhDeI3vAd0dEk_UQJGYQWBZ")
