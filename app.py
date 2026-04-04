import streamlit as st
import plotly.express as px
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="WCO-SIGMA Pro", layout="wide", page_icon="🛡️")
conn = st.connection("gsheets", type=GSheetsConnection)

# --- LOGIN POR NIT ---
st.sidebar.title("🔐 Acceso Clientes")
nit_usuario = st.sidebar.text_input("Ingrese NIT (sin puntos)", "")

if not nit_usuario:
    st.title("🚀 WCO-SIGMA HSEQ")
    st.info("Ingrese su NIT para gestionar sus inspecciones.")
else:
    menu = st.sidebar.radio("Menú", ["📊 Panel de Control", "🔵 Reportar Inspección", "📂 Carpeta PHVA"])

    # LEER DATOS REALES
    # LEER DATOS REALES Y LIMPIAR TÍTULOS
    df_total = conn.read()
    
    # Esta línea borra espacios invisibles en los títulos
    df_total.columns = df_total.columns.str.strip() 
    
    # Filtramos usando el nombre exacto que pusiste
    # Si pusiste 'Nit' con N mayúscula, esto lo encontrará
    try:
        df_empresa = df_total[df_total['Nit'].astype(str) == str(nit_usuario)]
    except KeyError:
        st.error("⚠️ Error de Estructura: No encontré la columna 'Nit' en tu Excel.")
        st.write("Columnas detectadas en tu archivo:", list(df_total.columns))
        st.stop()
    df_empresa = df_total[df_total['Nit'].astype(str) == str(nit_usuario)]
# --- SISTEMA DE NAVEGACIÓN ---
    menu = st.sidebar.radio("Gestión HSEQ", ["📊 Panel de Control", "🔵 Reportar Inspección", "📂 Carpeta PHVA"])

    # LEER DATOS REALES Y LIMPIAR TÍTULOS
    df_total = conn.read()
    df_total.columns = df_total.columns.str.strip()

    # FILTRAR POR NIT
    df_empresa = df_total[df_total['Nit'].astype(str) == str(nit_usuario)]

    # --- LÓGICA DE PANTALLAS ---
    if menu == "📊 Panel de Control":
        st.title(f"📊 Dashboard Ejecutivo - NIT: {nit_usuario}")
        
        if not df_empresa.empty:
            # 1. MÉTRICAS RÁPIDAS
            c1, c2, c3 = st.columns(3)
            total_h = len(df_empresa)
            abiertos = len(df_empresa[df_empresa['Estado'] == 'Abierto'])
            
            c1.metric("Total Hallazgos", total_h)
            c2.metric("Pendientes (Abiertos)", abiertos, delta_color="inverse")
            c3.metric("Cumplimiento", f"{int(((total_h-abiertos)/total_h)*100)}%" if total_h > 0 else "0%")

            st.divider()

            # 2. CARACTERIZACIÓN GRÁFICA
            col_graf1, col_graf2 = st.columns(2)

            with col_graf1:
                st.write("### ⚖️ Prioridad de Riesgos")
                # Creamos el gráfico de torta
                fig_prioridad = px.pie(df_empresa, names='Prioridad', 
                                     color='Prioridad',
                                     color_discrete_map={'Alta':'#EF553B', 'Media':'#FECB52', 'Baja':'#636EFA'},
                                     hole=0.4)
                st.plotly_chart(fig_prioridad, use_container_width=True)

            with col_graf2:
                st.write("### 📈 Estado de Gestión")
                # Creamos el gráfico de barras
                fig_estado = px.bar(df_empresa, x='Estado', color='Estado',
                                   title="Distribución por Estado")
                st.plotly_chart(fig_estado, use_container_width=True)

            st.write("### 📑 Detalle de Inspecciones")
            st.dataframe(df_empresa, use_container_width=True)
            
        else:
            st.info("Aún no hay datos registrados para este NIT. Comienza en el menú 'Reportar Inspección'.")

    elif menu == "🔵 Reportar Inspección":
        st.title("🔵 Nuevo Reporte Técnico de Inspección")
        with st.form("registro_detallado"):
            col1, col2 = st.columns(2)
            with col1:
                empresa_entrada = st.text_input("Nombre de la Empresa")
                fecha_insp = st.date_input("Fecha", datetime.now())
                componente = st.text_input("Componente (Ej: Extintores, Alturas)")
                hallazgo = st.text_area("Descripción del Hallazgo")
                f_riesgo = st.text_input("Factor de riesgo asociado")
                clasificacion = st.selectbox("Clasificación", ["Físico", "Químico", "Biológico", "Psicosocial", "Biomecánico", "Condiciones de Seguridad", "Fenómenos Naturales"])
            
            with col2:
                prioridad = st.selectbox("Prioridad", ["Baja", "Media", "Alta"])
                responsable = st.text_input("Responsable del cierre")
                fecha_prop = st.date_input("Fecha propuesta para el cierre")
                estado = st.selectbox("Estado", ["Abierto", "En Proceso", "Cerrado"])
                observacion = st.text_area("Observación adicional")

            btn = st.form_submit_button("✅ GUARDAR EN BASE DE DATOS")
            if btn and hallazgo:
                # 1. Organizamos los datos para el DataFrame
                datos_nuevos = pd.DataFrame([{
                    "Nit": str(nit_usuario),
                    "Empresa": empresa_entrada,
                    "Fecha": str(fecha_insp),
                    "Hallazgo": hallazgo,
                    "Componente": componente,
                    "Factor de riesgo asociado": f_riesgo,
                    "Clasificación": clasificacion,
                    "Responsable del cierre": responsable,
                    "Fecha propuesta para el cierre": str(fecha_prop),
                    "Prioridad": prioridad,
                    "Estado": estado,
                    "Observación": observacion
                }])
                
                # 2. INTENTO DE GUARDADO (Con manejo de error de permisos)
                try:
                    # Unimos los datos viejos con el nuevo registro
                    df_actualizado = pd.concat([df_total, datos_nuevos], ignore_index=True)
                    
                    # Intentamos la actualización
                    conn.update(data=df_actualizado)
                    st.success("✅ ¡Registro guardado exitosamente en la nube!")
                    st.balloons()
                except Exception as e:
                    st.error("⚠️ Error de Seguridad de Google")
                    st.warning("Walter, la App procesó el dato, pero Google Sheets bloqueó la escritura por falta de una 'Service Account'.")
                    st.info("Para solucionar esto, necesitamos el archivo JSON de credenciales de Google Cloud.")
                    # Mostramos los datos para que no se pierdan (opcional)
                    st.write("Datos que intentaste guardar:", datos_nuevos)
