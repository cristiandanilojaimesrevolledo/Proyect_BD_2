from fpdf import FPDF
from datetime import datetime
import os

# Paleta de colores (coincide con el verde de FarmaControl en el frontend)
VERDE_PRIMARIO = (0, 108, 73)       # #006c49
VERDE_CLARO = (224, 247, 237)       # fondo fila alterna / KPIs
ROJO_CLARO = (255, 218, 214)        # fondo fila con alerta de stock
GRIS_TEXTO = (60, 74, 66)
GRIS_PIE = (130, 130, 130)


class ReportePDF(FPDF):
    """Encabezado y pie de página que se repiten automáticamente en cada hoja."""

    def header(self):
        self.set_fill_color(*VERDE_PRIMARIO)
        self.rect(0, 0, self.w, 22, style="F")

        self.set_xy(10, 6)
        self.set_text_color(255, 255, 255)
        self.set_font("Arial", "B", 16)
        self.cell(0, 8, "FarmaControl", ln=True)

        self.set_x(10)
        self.set_font("Arial", "", 10)
        self.cell(0, 6, "Reporte de Inventario", ln=True)

        self.set_text_color(*GRIS_TEXTO)
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font("Arial", "I", 8)
        self.set_text_color(*GRIS_PIE)
        fecha = datetime.now().strftime("%d/%m/%Y %H:%M")
        self.cell(0, 10, f"Generado el {fecha}  |  Pagina {self.page_no()}", align="C")


def _cop(valor):
    """Da formato de pesos colombianos: 3500 -> '$ 3.500'."""
    return f"$ {float(valor):,.0f}".replace(",", ".")


COLUMNAS = [
    ("ID", 12, "C"),
    ("Producto", 48, "L"),
    ("Laboratorio", 32, "L"),
    ("Categoria", 30, "L"),
    ("Precio", 25, "R"),
    ("Stock", 16, "C"),
    ("Estado", 19, "C"),
]


def _dibujar_encabezado_tabla(pdf):
    pdf.set_font("Arial", "B", 9)
    pdf.set_fill_color(*VERDE_PRIMARIO)
    pdf.set_text_color(255, 255, 255)
    for titulo, ancho, alineacion in COLUMNAS:
        pdf.cell(ancho, 9, titulo, border=0, align="C", fill=True)
    pdf.ln()
    pdf.set_text_color(*GRIS_TEXTO)


def _dibujar_kpis(pdf, resumen):
    ancho_kpi, alto_kpi, espacio = 58, 22, 4
    y_kpi = pdf.get_y()
    kpis = [
        ("TOTAL PRODUCTOS", str(resumen.get("total_productos", 0))),
        ("VALOR INVENTARIO", _cop(resumen.get("valor_inventario", 0))),
        ("ALERTAS CRITICAS", str(resumen.get("alertas_criticas", 0))),
    ]
    for i, (titulo, valor) in enumerate(kpis):
        x = 10 + i * (ancho_kpi + espacio)
        pdf.set_fill_color(*VERDE_CLARO)
        pdf.rect(x, y_kpi, ancho_kpi, alto_kpi, style="F")

        pdf.set_xy(x + 4, y_kpi + 3)
        pdf.set_font("Arial", "", 8)
        pdf.set_text_color(*GRIS_TEXTO)
        pdf.cell(ancho_kpi - 8, 5, titulo)

        pdf.set_xy(x + 4, y_kpi + 10)
        pdf.set_font("Arial", "B", 14)
        pdf.cell(ancho_kpi - 8, 8, valor)

    pdf.set_y(y_kpi + alto_kpi + 8)


def generar_reporte_inventario(productos, resumen=None):
    pdf = ReportePDF()
    pdf.set_auto_page_break(auto=True, margin=20)
    pdf.add_page()

    if resumen:
        _dibujar_kpis(pdf, resumen)

    _dibujar_encabezado_tabla(pdf)

    pdf.set_font("Arial", "", 9)
    fila_alterna = False

    for p in productos:
        # Si no cabe otra fila antes del pie de página, salta de hoja y repite el encabezado
        if pdf.get_y() > 270:
            pdf.add_page()
            _dibujar_encabezado_tabla(pdf)
            pdf.set_font("Arial", "", 9)

        sin_stock = p.get("stock", 0) == 0
        stock_bajo = p.get("estado_stock") == "BAJO"

        if sin_stock or stock_bajo:
            pdf.set_fill_color(*ROJO_CLARO)
        elif fila_alterna:
            pdf.set_fill_color(*VERDE_CLARO)
        else:
            pdf.set_fill_color(255, 255, 255)

        estado_texto = "AGOTADO" if sin_stock else ("BAJO" if stock_bajo else "OK")

        valores = [
            str(p["id_producto"]),
            str(p["nombre"]),
            str(p.get("laboratorio") or "-"),
            str(p.get("categoria") or "-"),
            _cop(p["precio"]),
            str(p["stock"]),
            estado_texto,
        ]

        for valor, (_, ancho, alineacion) in zip(valores, COLUMNAS):
            pdf.cell(ancho, 8, valor, border="B", align=alineacion, fill=True)
        pdf.ln()
        fila_alterna = not fila_alterna

    carpeta_pdf = os.path.join("static", "pdf")
    os.makedirs(carpeta_pdf, exist_ok=True)  # crea la carpeta si no existe (ej: tras clonar el repo)

    ruta = os.path.join(carpeta_pdf, "reporte_inventario.pdf")
    pdf.output(ruta)
    return ruta
