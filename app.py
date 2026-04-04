import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.express as px
from datetime import datetime

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="WCO-SIGMA SIG+PESV", layout="wide")

# 2. CONEXIÓN (Sin memoria caché para leer datos frescos)
conn = st.connection("gsheets", type=GSheetsConnection)

# 3. ACCESO (BARRA LATERAL)
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/1063/1063302.png", width=100)
nit_input = st.sidebar.text_input("Ingrese NIT o Cédula:", "").strip()

if not nit_input:
    st.title("🚀 WCO-SIGMA: Gestión Integral")
    st.info("Ingrese su identificación para sincronizar los datos del SIG.")
else:
    menu = st.sidebar.radio("Menú Principal", ["📊 Dashboard Gerencial", "🔵 Reportar Hallazgo SIG/PESV", "📂 Carpeta PHVA"])

    # LECTURA DE DATOS EN VIVO
    df_total = conn.read(ttl=0) 
    df_total.columns = df_total.columns.str.strip()
    
    # Limpieza de NIT para comparación
    df_total['Nit'] = df_total['Nit'].astype(str).str.replace('.0', '', regex=False).str.strip()
    df_empresa = df_total[df_total['Nit'] == nit_input]

    # --- PANTALLA 1: DASHBOARD ---
    if menu == "📊 Dashboard Gerencial":
        st.title(f"📊 Informe Gerencial SIG - ID: {nit_input}")
        
        if not df_empresa.empty:
            c1, c2, c3 = st.columns(3)
            total = len(df_empresa)
            abiertos = len(df_empresa[df_empresa['Estado'].astype(str).str.contains('Abierto', case=False, na=False)])
            
            c1.metric("Hallazgos Totales", total)
            c2.metric("Pendientes", abiertos, delta_color="inverse")
            c3.metric("% Eficacia", f"{int(((total-abiertos)/total)*100)}%" if total > 0 else "0%")

            st.divider()
            g1, g2 = st.columns(2)
            with g1:
                if 'Condición Crítica' in df_empresa.columns:
                    fig_cond = px.bar(df_empresa['Condición Crítica'].value_counts().reset_index(), 
                                    x='count', y='Condición Crítica', orientation='h',
                                    title="🎯 Hallazgos por Condición", color='count')
                    st.plotly_chart(fig_cond, use_container_width=True)
            with g2:
                if 'Clasificación del riesgo' in df_empresa.columns:
                    fig_riesgo = px.pie(df_empresa, names='Clasificación del riesgo', title="☣️ Riesgos GTC 45", hole=0.4)
                    st.plotly_chart(fig_riesgo, use_container_width=True)

            st.subheader("📝 Análisis de Resultados")
            st.text_area("Causa Raíz y Plan de Acción:", placeholder="Escriba aquí el análisis del auditor...")

            st.write("### 📑 Tabla de Inspecciones (Orden Actualizado)")
            st.dataframe(df_empresa, use_container_width=True)
        else:
            st.warning("No se encontraron registros.")

    # --- PANTALLA 2: REPORTE (ORDEN EXACTO SOLICITADO) ---
    elif menu == "🔵 Reportar Hallazgo SIG/PESV":
        st.title("🔵 Registro Técnico SIG")
        with st.form("form_sig"):
            col1, col2 = st.columns(2)
            with col1:
                f_empresa = st.text_input("Empresa")
                f_fecha = st.date_input("Fecha", datetime.now())
                f_hallazgo = st.text_area("Hallazgo Detallado")
                
                # LISTA COMPLETA DE CONDICIONES CRÍTICAS
                f_condicion = st.selectbox("Condición Crítica", [
                    "Orden y aseo", "Herramientas, máquinas y/o equipos en mal estado",
                    "Daño/Ausencia de guardas o bloqueos", "Daño locativo (pisos, paredes, techos)",
                    "Superficies resbalosas", "EPP mal estado o inapropiado",
                    "Almacenamiento inadecuado", "Riesgo Químico (Sustancias/Rotulado)",
                    "Emergencias y Contra Incendios", "Sistemas eléctricos",
                    "Alturas y Espacios Confinados", "Señalización y demarcación deficiente",
                    "Factores Ergonómicos y Ambientales", "Disposición de residuos",
                    "Fugas o derrames", "Seguridad Vial (Vías internas/PESV)"
                ])
                
                # NUEVA LISTA DESPLEGABLE GTC 45
                f_riesgo = st.selectbox("Clasificación del riesgo (GTC 45)", [
                    "Biológico", "Físico", "Químico", "Psicosocial", 
                    "Biomecánico", "Condiciones de Seguridad", "Fenómenos Naturales"
                ])
                
            with col2:
                f_componente = st.selectbox("Componente", ["SST", "Ambiente", "Vial", "Calidad"])
                f_responsable = st.text_input("Responsable del cierre")
                f_fecha_p = st.date_input("Fecha propuesta para el cierre", datetime.now())
                f_prioridad = st.selectbox("Prioridad", ["Baja", "Media", "Alta"])
                f_estado = st.selectbox("Estado", ["Abierto", "En Proceso", "Cerrado"])
                f_obs = st.text_area("Observación")
            
            if st.form_submit_button("✅ GUARDAR Y SINCRONIZAR"):
                # ORDEN ESTRICTO DE COLUMNAS SEGÚN TU SOLICITUD
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
                    # Forzamos el orden de las columnas antes de concatenar
                    columnas_ordenadas = [
                        "Nit", "Empresa", "Fecha", "Hallazgo", "Condición Crítica", 
                        "Clasificación del riesgo", "Componente", "Responsable del cierre", 
                        "Fecha propuesta para el cierre", "Prioridad", "Estado", "Observación"
                    ]
                    nueva_fila = nueva_fila[columnas_ordenadas]
                    
                    df_actualizado = pd.concat([df_total, nueva_fila], ignore_index=True)
                    conn.update(data=df_actualizado)
                    st.success("¡Registro guardado en el orden correcto!")
                    st.balloons()
                except Exception as e:
                    st.error(f"Error de sincronización: {e}")

    elif menu == "📂 Carpeta PHVA":
        st.link_button("📁 Abrir Drive", "https://drive.google.com/drive/u/0/folders/17o_kAZMRcGhDeI3vAd0dEk_UQJGYQWBZ")
