from database.conexion import obtener_conexion

def validar_usuario(usuario, contrasena):
    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)
    cursor.execute(
        "SELECT * FROM usuarios WHERE usuario = %s AND contrasena = %s",
        (usuario, contrasena)
    )
    resultado = cursor.fetchone()
    cursor.close()
    conexion.close()
    return resultado