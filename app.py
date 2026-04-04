import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.express as px
from datetime import datetime

# 1. CONFIGURACIÓN
st.set_page_config(page_title="WCO-SIGMA SIG+PESV", layout="wide")

# 2. CONEXIÓN (ttl=0 para lectura en tiempo real sin memoria vieja)
conn = st.connection("gsheets", type=GSheetsConnection)

# 3. ACCESO
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/1063/1063302.png", width=100)
nit_input = st.sidebar.text_input("Ingrese identificación (NIT/Cédula):", "").strip()

if not nit_input:
    st.title("🚀 WCO-SIGMA: Gestión Integral")
    st.info("Sistema listo. Ingrese su NIT para iniciar sesión.")
else:
    menu = st.sidebar.radio("Menú", ["📊 Dashboard Gerencial", "🔵 Nuevo Reporte SIG/PESV", "📂 Carpeta PHVA"])

    # LECTURA DE DATOS (Forzamos lectura fresca)
    df_total = conn.read(ttl=0)
    df_total.columns = df_total.columns.str.strip()
    
    # Filtrado por NIT
    df_total['Nit'] = df_total['Nit'].astype(str).str.replace('.0', '', regex=False).str.strip()
    df_empresa = df_total[df_total['Nit'] == nit_input]

    # --- PANTALLA 1: DASHBOARD ---
    if menu == "📊 Dashboard Gerencial":
        st.title(f"📊 Dashboard Gerencial - ID: {nit_input}")
        
        if not df_empresa.empty:
            c1, c2, c3 = st.columns(3)
            total = len(df_empresa)
            # Conteo de estados abiertos (case insensitive)
            abiertos = len(df_empresa[df_empresa['Estado'].astype(str).str.upper() == 'ABIERTO'])
            
            c1.metric("Inspecciones", total)
            c2.metric("Pendientes", abiertos, delta_color="inverse")
            c3.metric("Eficacia", f"{int(((total-abiertos)/total)*100)}%" if total > 0 else "0%")

            st.divider()
            col_a, col_b = st.columns(2)
            with col_a:
                if 'Condición Crítica' in df_empresa.columns:
                    fig_c = px.bar(df_empresa['Condición Crítica'].value_counts().reset_index(), 
                                 x='count', y='Condición Crítica', orientation='h', title="🎯 Hallazgos por Condición")
                    st.plotly_chart(fig_c, use_container_width=True)
            with col_b:
                if 'Clasificación del riesgo' in df_empresa.columns:
                    fig_r = px.pie(df_empresa, names='Clasificación del riesgo', title="☣️ Riesgos GTC 45", hole=0.4)
                    st.plotly_chart(fig_r, use_container_width=True)

            st.subheader("📝 Análisis y Plan de Acción")
            st.text_area("Conclusiones del Auditor:", placeholder="Escriba aquí el análisis para el informe...")
            
            st.write("### 📑 Tabla de Seguimiento")
            st.dataframe(df_empresa, use_container_width=True)
        else:
            st.warning("No hay registros para este NIT. Realice un reporte para comenzar.")

    # --- PANTALLA 2: REPORTE (ORDEN EXACTO SOLICITADO) ---
    elif menu == "🔵 Nuevo Reporte SIG/PESV":
        st.title("🔵 Registro Técnico SIG")
        with st.form("form_sig_v4"):
            col1, col2 = st.columns(2)
            with col1:
                f_empresa = st.text_input("Empresa")
                f_fecha = st.date_input("Fecha", datetime.now())
                f_hallazgo = st.text_area("Hallazgo Detallado")
                f_condicion = st.selectbox("Condición Crítica", [
                    "Orden y aseo", "Herramientas/Equipos en mal estado", "Daño locativo", 
                    "Superficies resbalosas", "EPP inapropiado", "Almacenamiento inadecuado", 
                    "Riesgo Químico", "Emergencias/Incendio", "Sistemas eléctricos", 
                    "Alturas/Confinados", "Señalización deficiente", "Ergonómicos/Ambientales", 
                    "Residuos/Fugas/Derrames", "Seguridad Vial (PESV)"])
                
                # LISTA GTC 45
                f_riesgo = st.selectbox("Clasificación del riesgo (GTC 45)", [
                    "Biológico", "Físico", "Químico", "Psicosocial", 
                    "Biomecánico", "Condiciones de Seguridad", "Fenómenos Naturales"])
                
            with col2:
                # LISTA COMPONENTE
                f_componente = st.selectbox("Componente", ["SST", "Ambiente", "Vial", "Calidad"])
                f_responsable = st.text_input("Responsable del cierre")
                f_fecha_p = st.date_input("Fecha propuesta para el cierre", datetime.now())
                f_prioridad = st.selectbox("Prioridad", ["Baja", "Media", "Alta"])
                f_estado = st.selectbox("Estado", ["Abierto", "En Proceso", "Cerrado"])
                f_obs = st.text_area("Observación")
            
            if st.form_submit_button("✅ GUARDAR"):
                # MAPEO ESTRICTO AL NUEVO ORDEN DE TU EXCEL
                nueva_fila = pd.DataFrame([{
                    "Nit": str(nit_input),
                    "Empresa": f_empresa,
                    "Fecha": str(f_fecha),
                    "Hallazgo": f_hallazgo,
                    "Condición Crítica": f_condicion,
                    "Clasificación del riesgo": f_riesgo,
                    "Componente": f_componente,
                    "Responsable del cierre": f_responsable,
                    "Fecha propuesta para el cierre": str(f_fecha_p),
                    "Prioridad": f_prioridad,
                    "Estado": f_estado,
                    "Observación": f_obs
                }])
                
                try:
                    # Forzamos orden de columnas
                    columnas_finales = ["Nit", "Empresa", "Fecha", "Hallazgo", "Condición Crítica", 
                                       "Clasificación del riesgo", "Componente", "Responsable del cierre", 
                                       "Fecha propuesta para el cierre", "Prioridad", "Estado", "Observación"]
                    nueva_fila = nueva_fila[columnas_finales]
                    
                    df_upd = pd.concat([df_total, nueva_fila], ignore_index=True)
                    conn.update(data=df_upd)
                    st.success("¡Sincronización Exitosa!")
                    st.balloons()
                except Exception as e:
                    st.error(f"Error: {e}")

    elif menu == "📂 Carpeta PHVA":
        st.link_button("📁 Abrir Drive", "https://drive.google.com/drive/u/0/folders/17o_kAZMRcGhDeI3vAd0dEk_UQJGYQWBZ")
