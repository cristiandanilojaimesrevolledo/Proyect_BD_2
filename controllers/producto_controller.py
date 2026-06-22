from database.conexion import obtener_conexion

def obtener_productos():
    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)
    cursor.execute("SELECT * FROM vista_inventario")
    productos = cursor.fetchall()
    cursor.close()
    conexion.close()
    return productos

def obtener_resumen():
    """KPIs para la pantalla de reportes."""
    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)
    cursor.execute("""
        SELECT
            COUNT(*) AS total_productos,
            COALESCE(SUM(precio * stock), 0) AS valor_inventario,
            SUM(CASE WHEN stock <= stock_minimo THEN 1 ELSE 0 END) AS alertas_criticas
        FROM productos
    """)
    resumen = cursor.fetchone()
    cursor.close()
    conexion.close()
    return resumen

def crear_producto(datos):
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    fecha_vencimiento = datos.get('fecha_vencimiento') or None  # evita error si llega vacío
    cursor.execute(
        """INSERT INTO productos (nombre, laboratorio, categoria, precio, stock, stock_minimo, requiere_receta, fecha_vencimiento)
           VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
        (datos['nombre'], datos['laboratorio'], datos['categoria'], datos['precio'],
         datos['stock'], datos['stock_minimo'], datos['requiere_receta'], fecha_vencimiento)
    )
    conexion.commit()
    cursor.close()
    conexion.close()

def eliminar_producto(id_producto):
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    cursor.execute("DELETE FROM productos WHERE id_producto = %s", (id_producto,))
    conexion.commit()
    cursor.close()
    conexion.close()