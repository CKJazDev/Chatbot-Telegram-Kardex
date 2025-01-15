import csv
from io import StringIO
from db import connect_db

# Función para registrar un alumno
def registrar_alumno(nombre):
    connection = connect_db()
    cursor = connection.cursor()
    
    try:
        cursor.execute("INSERT INTO Alumno (Nombre) VALUES (%s)", (nombre,))
        connection.commit()
        alumno_id = cursor.lastrowid
        return alumno_id
    except Exception as e:
        return f"Error al registrar al alumno: {e}"
    finally:
        cursor.close()
        connection.close()

# Función para procesar el archivo CSV
def procesar_csv(file_content, alumno_id):
    connection = connect_db()
    cursor = connection.cursor()

    try:
        # Leer el contenido del archivo como texto
        decoded_file = file_content.decode('utf-8')
        csv_reader = csv.DictReader(StringIO(decoded_file))

        # Limpiar encabezados
        csv_reader.fieldnames = [field.strip().lstrip('\ufeff') for field in csv_reader.fieldnames]

        # Verificar si hay datos en el CSV
        filas = list(csv_reader)
        if not filas:
            raise ValueError("El archivo CSV está vacío o tiene formato incorrecto.")

        # Insertar datos en la base de datos
        for row in filas:
            id_materia = row.get("ID_Materia")
            calificacion = row.get("Calificacion")

            if not id_materia or not calificacion:
                raise ValueError(f"Datos incompletos en la fila: {row}")

            cursor.execute("""INSERT INTO Calificaciones (ID_Alumno, ID_Materia, Calificacion)
                            VALUES (%s, %s, %s)""", (alumno_id, id_materia, calificacion))
            connection.commit()

        return "Datos del archivo CSV cargados con éxito. Para volver al menu presiona /start"
    except Exception as e:
        # Si ocurre un error, eliminar al alumno creado
        cursor.execute("DELETE FROM Alumno WHERE ID_Alumno = %s", (alumno_id,))
        connection.commit()
        return f"Error al procesar el archivo CSV: {e}"
    finally:
        cursor.close()
        connection.close()
