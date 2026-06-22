CREATE DATABASE IF NOT EXISTS farmacia_db;
USE farmacia_db;

-- ===================== TABLAS =====================
-- Guardan los datos crudos del sistema
CREATE TABLE usuarios (
    id_usuario INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    usuario VARCHAR(50) UNIQUE NOT NULL,
    contrasena VARCHAR(255) NOT NULL,
    rol VARCHAR(20) DEFAULT 'vendedor'
);

CREATE TABLE productos (
    id_producto INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(150) NOT NULL,
    laboratorio VARCHAR(100),
    categoria VARCHAR(50),
    precio DECIMAL(10,2) NOT NULL,
    stock INT NOT NULL DEFAULT 0,
    stock_minimo INT DEFAULT 5,
    requiere_receta BOOLEAN DEFAULT FALSE,
    fecha_vencimiento DATE,
    fecha_registro DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE ventas (
    id_venta INT AUTO_INCREMENT PRIMARY KEY,
    id_usuario INT NOT NULL,
    fecha DATETIME DEFAULT CURRENT_TIMESTAMP,
    total DECIMAL(10,2) DEFAULT 0,
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario)
);

CREATE TABLE detalle_venta (
    id_detalle INT AUTO_INCREMENT PRIMARY KEY,
    id_venta INT NOT NULL,
    id_producto INT NOT NULL,
    cantidad INT NOT NULL,
    precio_unitario DECIMAL(10,2) NOT NULL,
    subtotal DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (id_venta) REFERENCES ventas(id_venta),
    FOREIGN KEY (id_producto) REFERENCES productos(id_producto)
);

CREATE TABLE movimientos_inventario (
    id_movimiento INT AUTO_INCREMENT PRIMARY KEY,
    id_producto INT NOT NULL,
    tipo_movimiento VARCHAR(20) NOT NULL,
    cantidad INT NOT NULL,
    fecha DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_producto) REFERENCES productos(id_producto)
);

-- ===================== VISTA =====================
-- Calcula el estado del stock al vuelo, sin guardar un campo redundante en la tabla
CREATE VIEW vista_inventario AS
SELECT id_producto, nombre, laboratorio, categoria, precio, stock, stock_minimo,
    CASE WHEN stock <= stock_minimo THEN 'BAJO' ELSE 'OK' END AS estado_stock
FROM productos;

-- ===================== FUNCIÓN =====================
-- Recibe un id_producto y devuelve cuánto vale ese producto en inventario (precio * stock)
DELIMITER //
CREATE FUNCTION fn_valor_inventario(p_id_producto INT) RETURNS DECIMAL(10,2)
DETERMINISTIC
BEGIN
    DECLARE valor DECIMAL(10,2);
    SELECT precio * stock INTO valor FROM productos WHERE id_producto = p_id_producto;
    RETURN valor;
END //
DELIMITER ;

-- ===================== PROCEDIMIENTO =====================
-- Encapsula la lógica de registrar una venta completa (cabecera + detalle) en una sola llamada
DELIMITER //
CREATE PROCEDURE sp_registrar_venta(
    IN p_id_usuario INT,
    IN p_id_producto INT,
    IN p_cantidad INT,
    OUT p_id_venta INT
)
BEGIN
    DECLARE v_precio DECIMAL(10,2);
    DECLARE v_subtotal DECIMAL(10,2);

    SELECT precio INTO v_precio FROM productos WHERE id_producto = p_id_producto;
    SET v_subtotal = v_precio * p_cantidad;

    INSERT INTO ventas (id_usuario, total) VALUES (p_id_usuario, v_subtotal);
    SET p_id_venta = LAST_INSERT_ID();

    INSERT INTO detalle_venta (id_venta, id_producto, cantidad, precio_unitario, subtotal)
    VALUES (p_id_venta, p_id_producto, p_cantidad, v_precio, v_subtotal);
END //
DELIMITER ;

-- ===================== TRIGGER =====================
-- Cada vez que se inserta un detalle_venta, automáticamente descuenta el stock
-- y registra el movimiento de inventario. Así nunca se puede "olvidar" actualizar el stock.
DELIMITER //
CREATE TRIGGER trg_actualizar_inventario
AFTER INSERT ON detalle_venta
FOR EACH ROW
BEGIN
    UPDATE productos
    SET stock = stock - NEW.cantidad
    WHERE id_producto = NEW.id_producto;

    INSERT INTO movimientos_inventario (id_producto, tipo_movimiento, cantidad)
    VALUES (NEW.id_producto, 'salida', NEW.cantidad);
END //
DELIMITER ;

-- ===================== DATOS DE PRUEBA =====================
INSERT INTO usuarios (nombre, usuario, contrasena, rol) VALUES
('Administrador', 'admin', 'admin123', 'administrador'),
('Vendedor Uno', 'vendedor', 'vendedor123', 'vendedor');

INSERT INTO productos (nombre, laboratorio, categoria, precio, stock, stock_minimo, requiere_receta, fecha_vencimiento) VALUES
('Paracetamol 500mg', 'Genfar', 'Analgésico', 3500, 100, 10, FALSE, '2027-06-01'),
('Amoxicilina 500mg', 'MK', 'Antibiótico', 8500, 50, 10, TRUE, '2026-12-15'),
('Loratadina 10mg', 'Bayer', 'Antialérgico', 4200, 80, 10, FALSE, '2027-03-20'),
('Ibuprofeno 400mg', 'Genfar', 'Antiinflamatorio', 3800, 60, 10, FALSE, '2027-01-10'),
('Omeprazol 20mg', 'MK', 'Gastrointestinal', 5200, 40, 10, FALSE, '2026-11-30');