from fpdf import FPDF
import base64

# --- FUNCIÓN MAESTRA PARA GENERAR PDF ---
def generar_pdf(df_cond, df_comp, nit_user):
    pdf = FPDF()
    pdf.add_page()
    
    # Encabezado Corporativo
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(0, 10, f'REPORTE EJECUTIVO SIG - WCO-SIGMA', ln=True, align='C')
    pdf.set_font('Arial', '', 12)
    pdf.cell(0, 10, f'Cliente NIT: {nit_user} | Fecha: {datetime.now().date()}', ln=True, align='C')
    pdf.ln(10)

    # SECCIÓN 1: CONDICIONES HSEQ
    pdf.set_fill_color(200, 220, 255)
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, '1. RESUMEN DE CONDICIONES HSEQ', ln=True, fill=True)
    pdf.set_font('Arial', '', 10)
    
    if not df_cond.empty:
        for i, row in df_cond.iterrows():
            pdf.multi_cell(0, 10, f"- {row['Fecha']} | {row['Centro de trabajo']} | {row['Hallazgo']} | ESTADO: {row['Estado']}")
    else:
        pdf.cell(0, 10, 'No se registran condiciones en el periodo.', ln=True)
    
    pdf.ln(5)

    # SECCIÓN 2: COMPORTAMIENTO
    pdf.set_fill_color(220, 255, 200)
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, '2. OBSERVACIONES DE COMPORTAMIENTO (PESV)', ln=True, fill=True)
    pdf.set_font('Arial', '', 10)
    
    if not df_comp.empty:
        for i, row in df_comp.iterrows():
            pdf.multi_cell(0, 10, f"- {row['Inspector']} en {row['Lugar']}: {row['Estado observado']}")
    else:
        pdf.cell(0, 10, 'No se registran observaciones de comportamiento.', ln=True)

    return pdf.output(dest='S').encode('latin-1')

# --- DENTRO DEL DASHBOARD GERENCIAL (Añadir el botón) ---
if menu == "📊 Dashboard Gerencial":
    # ... (tus pestañas y gráficos actuales) ...
    
    st.sidebar.markdown("---")
    st.sidebar.subheader("📥 Exportar Reporte")
    if st.sidebar.button("📄 Generar PDF Mensual"):
        pdf_bytes = generar_pdf(df_cond_emp, df_comp_emp, nit_user)
        st.sidebar.download_button(
            label="⬇️ Descargar Reporte PDF",
            data=pdf_bytes,
            file_name=f"Reporte_SIG_{nit_user}_{datetime.now().date()}.pdf",
            mime="application/pdf"
        )
