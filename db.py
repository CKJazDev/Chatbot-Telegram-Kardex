import pymysql

def connect_db():
    return pymysql.connect(
        host="localhost",
        user="root",
        password="12345",
        database="Analisis"
    )

def ejecutar_query(query, params=None):
    conexion = connect_db()
    try:
        with conexion.cursor() as cursor:
            cursor.execute(query, params)
            if query.strip().upper().startswith("SELECT"):
                return cursor.fetchall()
            conexion.commit()
    finally:
        conexion.close()
