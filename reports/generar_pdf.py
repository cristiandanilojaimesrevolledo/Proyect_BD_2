from fpdf import FPDF
import os

def generar_reporte_inventario(productos):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "Reporte de Inventario - Farmacia", ln=True, align="C")
    pdf.ln(5)

    pdf.set_font("Arial", "B", 10)
    pdf.cell(60, 8, "Producto", border=1)
    pdf.cell(35, 8, "Categoria", border=1)
    pdf.cell(25, 8, "Precio", border=1)
    pdf.cell(20, 8, "Stock", border=1)
    pdf.cell(30, 8, "Estado", border=1)
    pdf.ln()

    pdf.set_font("Arial", "", 10)
    for p in productos:
        pdf.cell(60, 8, str(p['nombre']), border=1)
        pdf.cell(35, 8, str(p['categoria']), border=1)
        pdf.cell(25, 8, f"${p['precio']}", border=1)
        pdf.cell(20, 8, str(p['stock']), border=1)
        pdf.cell(30, 8, str(p['estado_stock']), border=1)
        pdf.ln()

    ruta = os.path.join("static", "pdf", "reporte_inventario.pdf")
    pdf.output(ruta)
    return ruta