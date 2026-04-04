# --- PANTALLA: GESTIÓN DE ACPM (VERSION FINAL CON COMPONENTE) ---
    if menu == "⚖️ Gestión de ACPM":
        st.title("⚖️ Central de Acciones Correctivas, Preventivas y de Mejora")
        st.info("Este módulo centraliza hallazgos de todas las fuentes para el ciclo PHVA.")
        
        with st.expander("➕ REGISTRAR NUEVA ACPM (Análisis de Causa Raíz)"):
            with st.form("form_acpm_v2"):
                col1, col2 = st.columns(2)
                
                with col1:
                    f_empresa = st.text_input("Unidad de Negocio / Sede")
                    f_componente = st.selectbox("Componente del SIG", ["SST", "Ambiente", "Calidad", "Vial"])
                    f_fuente = st.selectbox("Fuente del Hallazgo", [
                        "inspecciones", "investigación de incidentes", 
                        "auditorías internas y externas", "observación de tareas", 
                        "reportes de actos y condiciones", "Legislación o normatividad", 
                        "Revisión gerencial"
                    ])
                    f_desc = st.text_area("Descripción del Hallazgo")
                    
                    st.subheader("🧠 Metodología de los 5 Porqués")
                    p1 = st.text_input("¿Por qué 1? (Problema directo)")
                    p2 = st.text_input("¿Por qué 2?")
                    p3 = st.text_input("¿Por qué 3?")
                    p4 = st.text_input("¿Por qué 4?")
                    p5 = st.text_input("¿Por qué 5? (Causa Raíz)")
                    f_raiz = st.text_input("Definición Causa Raíz Final")

                with col2:
                    f_tipo = st.radio("Tipo de Acción", ["Correctiva", "Preventiva", "Mejora"])
                    f_accion = st.text_area("Acción Propuesta (Medida de Intervención)")
                    f_resp = st.text_input("Responsable de Ejecución")
                    f_fec_c = st.date_input("Fecha Cierre Prevista", datetime.now())
                    f_cambio = st.radio("¿Activa Gestión del Cambio? (IPVR / IAVI)", ["No", "Sí"])
                    f_eficacia = st.selectbox("Eficacia de la acción", ["Pendiente", "Eficaz", "No Eficaz"])
                    f_estado = st.selectbox("Estado de la ACPM", ["Abierta", "En Ejecución", "Cerrada"])
                
                if st.form_submit_button("💾 REGISTRAR ACCIÓN EN BDI"):
                    # Lógica de nota para Gestión del Cambio
                    nota_cambio = "Requiere actualización IPVR/IAVI" if f_cambio == "Sí" else "N/A"
                    
                    nueva_acpm = pd.DataFrame([{
                        "Nit": str(nit_input), 
                        "Empresa": f_empresa, 
                        "Fecha de reporte": str(datetime.now().date()),
                        "Componente": f_componente,
                        "Fuente": f_fuente, 
                        "Descripción Hallazgo": f_desc,
                        "Análisis Causa ¿Porqué 1?": p1, 
                        "Análisis Causa ¿Porqué 2?": p2,
                        "Análisis Causa ¿Porqué 3?": p3, 
                        "Análisis Causa ¿Porqué 4?": p4,
                        "Análisis Causa ¿Porqué 5?": p5, 
                        "Causa raíz": f_raiz,
                        "Acción Propuesta": f_accion, 
                        "Tipo Acción": f_tipo,
                        "Responsable": f_resp, 
                        "Fecha Cierre Prevista": str(f_fec_c),
                        "Eficacia de la acción tomada": f_eficacia,
                        "Gestión del Cambio": f"{f_cambio} - {nota_cambio}", 
                        "Estado": f_estado
                    }])
                    
                    # Unión y guardado (Uso de URL_ACPM definida anteriormente)
                    df_upd = pd.concat([df_acpm_total, nueva_acpm], ignore_index=True)
                    conn.update(spreadsheet=URL_ACPM, data=df_upd)
                    st.success("ACPM centralizada y lista para seguimiento.")
                    st.balloons()

        st.markdown("---")
        st.write(f"### 📑 Plan de Acción Unificado - {nit_input}")
        
        # Filtro rápido por Componente en la visualización
        filtro_comp = st.multiselect("Filtrar por Componente:", ["SST", "Ambiente", "Calidad", "Vial"], default=["SST", "Ambiente", "Calidad", "Vial"])
        
        if not df_acpm_emp.empty:
            df_vis = df_acpm_emp[df_acpm_emp['Componente'].isin(filtro_comp)]
            st.dataframe(df_vis, use_container_width=True)
        else:
            st.info("No hay acciones registradas para este NIT.")
