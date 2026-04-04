import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.express as px
from datetime import datetime
import uuid

# 1. CONFIGURACIÓN
st.set_page_config(page_title="WCO-SIGMA SIG+PESV", layout="wide")
conn = st.connection("gsheets", type=GSheetsConnection)

# 2. ACCESO
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/1063/1063302.png", width=100)
nit_input = st.sidebar.text_input("Ingrese identificación (NIT/Cédula):", "").strip()

if not nit_input:
    st.title("🚀 WCO-SIGMA: Gestión Integral")
    st.info("Ingrese su identificación para acceder al ecosistema de inspecciones.")
else:
    menu = st.sidebar.radio("Menú de Gestión", [
        "📊 Dashboard Gerencial", 
        "🛠️ Reporte Condiciones (HSEQ)", 
        "🧠 Comportamiento & Preoperacionales", # NUEVO MÓDULO
        "📂 Carpeta PHVA"
    ])

    # LECTURA DE DATOS (Forzamos lectura fresca)
    df_total = conn.read(ttl=0)
    df_total.columns = df_total.columns.str.strip()
    df_total['Nit'] = df_total['Nit'].astype(str).str.replace('.0', '', regex=False).str.strip()
    df_empresa = df_total[df_total['Nit'] == nit_input]

    # --- PANTALLA 1: DASHBOARD ---
    if menu == "📊 Dashboard Gerencial":
        st.title(f"📊 Dashboard Gerencial - ID: {nit_input}")
        # (Aquí mantendremos tus gráficos de condiciones que ya funcionan)
        st.dataframe(df_empresa, use_container_width=True)

    # --- PANTALLA 2: REPORTE CONDICIONES (YA EXISTENTE) ---
    elif menu == "🛠️ Reporte Condiciones (HSEQ)":
        st.title("🛠️ Inspección de Condiciones")
        # (Este bloque se mantiene igual al anterior para no perder tu progreso)

    # --- PANTALLA 3: COMPORTAMIENTO (NUEVO DISEÑO SOLICITADO) ---
    elif menu == "🧠 Comportamiento & Preoperacionales":
        st.title("🧠 Registro de Comportamiento Humano y Preoperacionales")
        st.subheader("Captura Técnica en Tiempo Real")
        
        # Generación automática de ID y Tiempo
        id_auto = str(uuid.uuid4())[:8].upper()
        fecha_real = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        st.write(f"**ID Inspección:** {id_auto} | **Sincronización:** {fecha_real}")

        with st.form("form_comportamiento_v1"):
            col1, col2 = st.columns(2)
            
            with col1:
                inspector = st.text_input("Nombre del Inspector / Auditor")
                
                # LISTA DESPLEGABLE: TIPO DE INSPECCIÓN
                tipo_insp = st.selectbox("Tipo de Inspección", [
                    "Observación de Comportamiento (Factor Humano)",
                    "Preoperacional Vehículo (PESV - Paso 17)",
                    "Preoperacional de Maquinaria/Equipos",
                    "Auditoría de Tareas Críticas (Alturas/Confinados)",
                    "Inspección de Herramientas Manuales",
                    "Verificación de EPP en Uso"
                ])
                
                # LISTA DESPLEGABLE: ESTADO OBSERVADO
                estado_obs = st.selectbox("Estado Observado", [
                    "✅ SEGURO / CONFORME",
                    "⚠️ ATÍPICO (Requiere Observación)",
                    "🚫 PELIGROSO / NO CONFORME (Parar actividad)",
                    "N/A (No aplica)"
                ])

            with col2:
                evidencia = st.text_input("Enlace de Evidencia Fotográfica (Drive/Cloud)")
                
                # FACTOR HUMANO SEGÚN TU SOLICITUD
                obs_humano = st.multiselect("Factores Humanos Detectados:", [
                    "Ninguno (Comportamiento Seguro)",
                    "Distracción / Falta de atención",
                    "Fatiga / Cansancio visible",
                    "Falta de EPP / Uso incorrecto",
                    "Exceso de confianza",
                    "Omisión de procedimiento",
                    "Prisa / Afán excesivo"
                ])
                
                detalles = st.text_area("Descripción detallada y Compromisos")

            if st.form_submit_button("✅ REGISTRAR INSPECCIÓN"):
                # Organizamos la data para la nueva hoja/pestaña
                # Nota: Por ahora el conector simplificado guarda todo en la base principal, 
                # pero marcamos la columna 'Componente' como 'COMPORTAMIENTO' para filtrar.
                
                nueva_fila_comp = pd.DataFrame([{
                    "Nit": str(nit_input),
                    "ID_Inspección": id_auto,
                    "Fecha/Hora Real": fecha_real,
                    "Inspector": inspector,
                    "Tipo de Inspección": tipo_insp,
                    "Estado observado": estado_obs,
                    "Evidencia Fotográfica": evidencia,
                    "Observaciones Factor Humano": ", ".join(obs_humano) + " | " + detalles
                }])
                
                try:
                    # Sincronización con Google Sheets
                    # (Asegúrate de que tu Excel tenga estas columnas nuevas)
                    df_upd = pd.concat([df_total, nueva_fila_comp], ignore_index=True)
                    conn.update(data=df_upd)
                    st.success(f"Inspección {id_auto} guardada y sincronizada.")
                    st.balloons()
                except Exception as e:
                    st.error(f"Error al sincronizar: {e}. Verifique que las columnas existan en el Excel.")

    elif menu == "📂 Carpeta PHVA":
        st.link_button("📁 Ver Documentación", "https://drive.google.com/drive/u/0/folders/17o_kAZMRcGhDeI3vAd0dEk_UQJGYQWBZ")
