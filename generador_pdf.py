from fpdf import FPDF

class PDFReporte(FPDF):
    def header(self):
        # self.image("logo.png", 10, 8, 33) # Descomentar si tienes logo
        self.set_font("Arial", "B", 12)
        self.cell(0, 10, "Sistema de Transcripcion Inteligente - Reporte Oficial", border=False, ln=True, align="C")
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font("Arial", "I", 8)
        self.cell(0, 10, f"Pagina {self.page_no()}/{{nb}}", align="C")
    
    def chapter_title(self, label):
        self.set_font('Arial', 'B', 12)
        self.set_fill_color(200, 220, 255) # Azul clarito
        self.cell(0, 6, label, border=0, ln=True, fill=True)
        self.ln(4)

    def chapter_body(self, text):
        self.set_font('Arial', '', 11)
        
        # --- CORRECCIÓN PREVENTIVA DE CARACTERES ---
        # FPDF estándar a veces falla con emojis o caracteres raros de la IA.
        # Esto reemplaza los caracteres imposibles por signos de pregunta para que no explote.
        try:
            text = text.encode('latin-1', 'replace').decode('latin-1')
        except:
            pass
            
        self.multi_cell(0, 6, text) 
        self.ln()     

def generar_pdf(nombre_archivo, transcripcion, analisis):
    pdf = PDFReporte()
    pdf.alias_nb_pages()
    pdf.add_page()

    pdf.set_font("Arial", "B", 16)
    # Limpiamos el nombre del archivo también por si tiene tildes
    nombre_limpio = nombre_archivo.encode('latin-1', 'replace').decode('latin-1')
    pdf.cell(0, 10, f"Acta de Reunion: {nombre_limpio}", ln=True, align="L")
    pdf.ln(10)

    if analisis:
        pdf.chapter_title("ANALISIS DE INTELIGENCIA ARTIFICIAL")
        pdf.chapter_body(analisis)

    pdf.chapter_title("TRANSCRIPCION LITERAL")
    pdf.chapter_body(transcripcion)

    nombre_pdf = "reporte_temporal.pdf"
    pdf.output(nombre_pdf)
    return nombre_pdf