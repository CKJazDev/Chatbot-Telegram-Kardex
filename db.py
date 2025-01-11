import pymysql

def connect_db():
    return pymysql.connect(
        host="localhost",
        user="root",
        password="12345",
        database="Analisis",
        cursorclass=pymysql.cursors.Cursor  # Para devolver resultados en formato legible
    )

def ejecutar_query(query, params=None):
    conexion = connect_db()
    try:
        with conexion.cursor() as cursor:
            cursor.execute(query, params)
            if query.strip().upper().startswith("SELECT"):
                # Devuelve todos los resultados como una lista de tuplas
                return cursor.fetchall()
            else:
                conexion.commit()
                return None
    except Exception as e:
        raise RuntimeError(f"Error al ejecutar la consulta: {e}")
    finally:
        conexion.close()