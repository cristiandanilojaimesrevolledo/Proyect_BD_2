from flask import Flask, render_template, request, redirect, url_for, session, send_file
from controllers import usuario_controller, producto_controller, venta_controller
from reports.generar_pdf import generar_reporte_inventario
from config import SECRET_KEY

app = Flask(__name__)
app.secret_key = SECRET_KEY


@app.template_filter('cop')
def formato_cop(valor):
    return f"$ {valor:,.0f}".replace(",", ".")


@app.route('/')
def index():
    if 'usuario' not in session:
        return redirect(url_for('login'))
    return render_template('inicio.html', usuario=session['usuario'], rol=session.get('rol'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        usuario = request.form['usuario']
        contrasena = request.form['contrasena']
        resultado = usuario_controller.validar_usuario(usuario, contrasena)
        if resultado:
            session['usuario'] = resultado['nombre']
            session['id_usuario'] = resultado['id_usuario']
            session['rol'] = resultado['rol']
            return redirect(url_for('index'))
        return render_template('login.html', error="Usuario o contraseña incorrectos.")
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


@app.route('/productos')
def productos():
    if 'usuario' not in session:
        return redirect(url_for('login'))
    return render_template('productos.html', productos=producto_controller.obtener_productos())


@app.route('/productos/nuevo', methods=['POST'])
def nuevo_producto():
    datos = {
        'nombre': request.form['nombre'],
        'laboratorio': request.form['laboratorio'],
        'categoria': request.form['categoria'],
        'precio': request.form['precio'],
        'stock': request.form['stock'],
        'stock_minimo': request.form['stock_minimo'],
        'requiere_receta': 1 if request.form.get('requiere_receta') else 0,
        'fecha_vencimiento': request.form.get('fecha_vencimiento')
    }
    producto_controller.crear_producto(datos)
    return redirect(url_for('productos'))


@app.route('/productos/eliminar/<int:id_producto>')
def eliminar_producto(id_producto):
    producto_controller.eliminar_producto(id_producto)
    return redirect(url_for('productos'))


@app.route('/ventas', methods=['GET', 'POST'])
def ventas():
    if 'usuario' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        id_producto = request.form['id_producto']
        cantidad = int(request.form['cantidad'])
        venta_controller.registrar_venta(session['id_usuario'], id_producto, cantidad)
        return redirect(url_for('ventas'))

    return render_template('ventas.html',
                           productos=producto_controller.obtener_productos(),
                           ventas=venta_controller.obtener_ventas())


@app.route('/reportes')
def reportes():
    if 'usuario' not in session:
        return redirect(url_for('login'))
    return render_template('reportes.html',
                           productos=producto_controller.obtener_productos(),
                           resumen=producto_controller.obtener_resumen())

@app.route('/reportes/pdf')
def reporte_pdf():
    productos = producto_controller.obtener_productos()
    resumen = producto_controller.obtener_resumen()
    ruta = generar_reporte_inventario(productos, resumen)
    return send_file(ruta, as_attachment=True)


if __name__ == '__main__':
  app.run(port=5001, debug=True)
