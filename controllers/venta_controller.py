from database.conexion import obtener_conexion

def registrar_venta(id_usuario, id_producto, cantidad):
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    resultado = cursor.callproc('sp_registrar_venta', (id_usuario, id_producto, cantidad, 0))
    conexion.commit()
    cursor.close()
    conexion.close()
    return resultado[3]  # id_venta generado

def obtener_ventas():
    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)
    cursor.execute("""
        SELECT v.id_venta, v.fecha, v.total, u.nombre AS vendedor
        FROM ventas v
        JOIN usuarios u ON v.id_usuario = u.id_usuario
        ORDER BY v.fecha DESC
    """)
    ventas = cursor.fetchall()
    cursor.close()
    conexion.close()
    return ventas