import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.express as px
from datetime import datetime

# 1. CONFIGURACIÓN
st.set_page_config(page_title="WCO-SIGMA SIG+PESV", layout="wide")
conn = st.connection("gsheets", type=GSheetsConnection)

# 2. ACCESO
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/1063/1063302.png", width=100)
nit_input = st.sidebar.text_input("Ingrese NIT o Cédula:", "").strip()

if not nit_input:
    st.title("🚀 WCO-SIGMA: Sistema Integrado de Gestión")
    st.info("Ingrese su identificación para acceder a los indicadores de HSEQ y Seguridad Vial.")
else:
    menu = st.sidebar.radio("Gestión Integral", ["📊 Dashboard Gerencial", "🔵 Reportar Hallazgo SIG/PESV", "📂 Carpeta PHVA"])

    # LECTURA DE DATOS
    df_total = conn.read()
    df_total.columns = df_total.columns.str.strip()
    df_total['Nit'] = df_total['Nit'].astype(str).str.replace('.0', '', regex=False).str.strip()
    df_empresa = df_total[df_total['Nit'] == nit_input]

    # --- PANTALLA 1: DASHBOARD ---
    if menu == "📊 Dashboard Gerencial":
        st.title(f"📊 Análisis de Gestión SIG & PESV - ID: {nit_input}")
        
        if not df_empresa.empty:
            c1, c2, c3 = st.columns(3)
            total = len(df_empresa)
            abiertos = len(df_empresa[df_empresa['Estado'].str.contains('Abierto', case=False, na=False)])
            c1.metric("Hallazgos Totales", total)
            c2.metric("Pendientes", abiertos, delta_color="inverse")
            c3.metric("% Eficacia", f"{int(((total-abiertos)/total)*100)}%")

            st.divider()

            g1, g2 = st.columns(2)
            with g1:
                # Caracterización por Condición (PESV + HSEQ + AMBIENTE)
                if 'Condición Crítica' in df_empresa.columns:
                    fig_cond = px.bar(df_empresa['Condición Crítica'].value_counts().reset_index(), 
                                    x='count', y='Condición Crítica', orientation='h',
                                    title="🎯 Caracterización de Hallazgos (SIG)",
                                    color='count', color_continuous_scale='Reds')
                    st.plotly_chart(fig_cond, use_container_width=True)
            with g2:
                fig_prio = px.pie(df_empresa, names='Prioridad', title="⚖️ Nivel de Riesgo", hole=0.4)
                st.plotly_chart(fig_prio, use_container_width=True)

            # ESPACIO DE ANÁLISIS PARA AUDITORÍA RUC / PESV
            st.subheader("📝 Conclusiones de Auditoría y Plan de Acción")
            analisis = st.text_area("Determine aquí la causa raíz y las medidas de control sugeridas:", 
                                   placeholder="Ej: Se detecta recurrencia en fallas de seguridad vial interna. Se requiere re-inducción en el PESV...")

            st.write("### 📑 Trazabilidad de Registros")
            st.dataframe(df_empresa, use_container_width=True)
        else:
            st.warning("No hay registros vinculados a este NIT.")

    # --- PANTALLA 2: REPORTE INTEGRADO ---
    elif menu == "🔵 Reportar Hallazgo SIG/PESV":
        st.title("🔵 Registro Multidimensional SIG + PESV")
        with st.form("form_sig"):
            col1, col2 = st.columns(2)
            with col1:
                empresa = st.text_input("Empresa")
                fecha = st.date_input("Fecha", datetime.now())
                
                # LISTA INTEGRADA: HSEQ + AMBIENTE + PESV
                condicion = st.selectbox("Condición Detectada", [
                    "-- SEGURIDAD Y SALUD (RUC) --",
                    "Orden y aseo", "Herramientas, máquinas y/o equipos en mal estado",
                    "Daño/Ausencia de guardas o bloqueos", "Daño locativo",
                    "EPP mal estado o inapropiado", "Sistemas eléctricos",
                    "Alturas y Espacios Confinados", "Factores Ergonómicos",
                    "-- MEDIO AMBIENTE (ISO 14001) --",
                    "Disposición inadecuada de residuos", "Fugas o goteos de sustancias",
                    "Derrames de hidrocarburos/químicos", "Consumo excesivo de recursos",
                    "Ausencia de kits de derrames",
                    "-- SEGURIDAD VIAL (PESV) --",
                    "Exceso de velocidad en vías internas", "Vehículos sin inspección pre-operacional",
                    "Señalización vial interna deficiente", "Uso inadecuado de parqueaderos",
                    "Fallas mecánicas en flota", "No uso de cinturón/casco en planta"
                ])
                
                hallazgo = st.text_area("Descripción del Evento")
                
            with col2:
                prioridad = st.selectbox("Prioridad/Gravedad", ["Baja", "Media", "Alta"])
                estado = st.selectbox("Estado de Gestión", ["Abierto", "En Proceso", "Cerrado"])
                responsable = st.text_input("Responsable Asignado")
                obs = st.text_area("Plan de Acción Inmediato")
            
            if st.form_submit_button("✅ GUARDAR EN EL SIG"):
                nueva_fila = pd.DataFrame([{
                    "Nit": str(nit_input), "Empresa": empresa, "Fecha": str(fecha),
                    "Condición Crítica": condicion, "Hallazgo": hallazgo,
                    "Prioridad": prioridad, "Estado": estado, "Responsable": responsable, "Observación": obs
                }])
                try:
                    df_total = pd.concat([df_total, nueva_fila], ignore_index=True)
                    conn.update(data=df_total)
                    st.success("¡Hallazgo integrado al Sistema de Gestión!")
                    st.balloons()
                except:
                    st.error("Error al sincronizar con la nube.")

    elif menu == "📂 Carpeta PHVA":
        st.link_button("📁 Ver Documentación PHVA (Drive)", "https://drive.google.com/drive/u/0/folders/17o_kAZMRcGhDeI3vAd0dEk_UQJGYQWBZ")
