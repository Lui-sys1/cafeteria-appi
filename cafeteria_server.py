import os
import psycopg
from flask import Flask, jsonify, send_from_directory, request
from flask_cors import CORS
import logging

logging.basicConfig(level=logging.INFO)

app = Flask(__name__, static_folder=".")
CORS(app)

# Configuración DB PostgreSQL
DB_HOST = os.getenv("DB_HOST", "dpg-d34rvonfte5s73adba80-a.oregon-postgres.render.com")
DB_PORT = int(os.getenv("DB_PORT", 5432))
DB_NAME = os.getenv("DB_NAME", "conafood")
DB_USER = os.getenv("DB_USER", "luis5531")
DB_PASSWORD = os.getenv("DB_PASSWORD", "q16ddEGzzySuQJeWHHx6iG4GO0rht9kG")

def get_db_connection():
    return psycopg.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        autocommit=True
    )

# Ruta para servir el panel
@app.route("/")
def panel():
    return send_from_directory(".", "panel_cafeteria.html")

# API para obtener pedidos
@app.route("/pedidos", methods=["GET"])
def obtener_pedidos():
    try:
        conn = get_db_connection()
        with conn.cursor(row_factory=psycopg.rows.dict_row) as cursor:
            cursor.execute("SELECT * FROM vista_pedidos ORDER BY fecha DESC;")
            pedidos = cursor.fetchall()
        return jsonify(pedidos)
    except Exception as e:
        logging.error(f"Error obteniendo pedidos: {e}")
        return jsonify({"error": "No se pudieron obtener los pedidos"}), 500

# API para crear un pedido
@app.route("/pedidos", methods=["POST"])
def crear_pedido():
    data = request.json
    usuario = data.get("usuario")
    producto = data.get("producto")
    cantidad = data.get("cantidad")

    if not all([usuario, producto, cantidad]):
        return jsonify({"error": "Faltan datos"}), 400

    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute(
                "INSERT INTO pedidos (usuario, producto, cantidad, estado) VALUES (%s, %s, %s, %s)",
                (usuario, producto, cantidad, "pendiente")
            )
        return jsonify({"message": "Pedido creado correctamente"}), 201
    except Exception as e:
        logging.error(f"Error creando pedido: {e}")
        return jsonify({"error": "No se pudo crear el pedido"}), 500

# API para actualizar pedidos
@app.route("/pedidos/<int:pedido_id>", methods=["PATCH"])
def actualizar_pedido(pedido_id):
    nuevo_estado = request.json.get("estado")
    if nuevo_estado not in ["pendiente", "en_preparacion", "entregado"]:
        return jsonify({"error": "Estado inválido"}), 400
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("UPDATE pedidos SET estado=%s WHERE id_pedido=%s", (nuevo_estado, pedido_id))
        return jsonify({"message": "Pedido actualizado"})
    except Exception as e:
        logging.error(f"Error actualizando pedido: {e}")
        return jsonify({"error": "No se pudo actualizar el pedido"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
