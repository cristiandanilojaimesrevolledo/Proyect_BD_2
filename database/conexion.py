import mysql.connector
from config import DB_CONFIG

def obtener_conexion():
    return mysql.connector.connect(**DB_CONFIG)