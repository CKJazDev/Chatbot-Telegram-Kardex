import os
from openai import OpenAI
from db import ejecutar_query

# Configura la clave de API
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY", ""))

def formatear_resultados(resultados):
    """
    Convierte los resultados de la consulta en un formato sencillo donde las columnas están separadas por '|'.
    """
    if not resultados:
        return "No se encontraron resultados."

    # Crear filas con los valores separados por " | "
    filas = [" | ".join(map(str, fila)) for fila in resultados]

    # Combinar todo en un solo string
    tabla = "\n".join(filas)
    return f"Aqui tienes los resultados solicitados 😀:\n\n{tabla}"

def procesar_mensaje(mensaje, contexto):
    # Combinar el contexto completo en un solo string
    contexto_completo = "\n".join(contexto)
    
    prompt = f"""
    Eres un asistente inteligente con acceso a una base de datos MySQL. 
    Basándote en el siguiente contexto y mensaje del usuario, genera una consulta SQL válida.
    Devuelve exclusivamente la consulta SQL sin devolver los Id de los datos. Si no puedes generar una consulta válida, responde "Consulta no válida"

    Estructura de la base de datos:
    1. Tabla Clasificacion: ID_clasificacion (INT, PK), Nombre (VARCHAR).
    2. Tabla Materia: ID_Materia (INT, PK), Nombre_Materia (VARCHAR), ID_clasificacion (FK), Semestre (INT).
    3. Tabla Alumno: ID_Alumno (INT, PK), Nombre (VARCHAR).
    4. Tabla Calificaciones: ID_Materia (FK), ID_Alumno (FK), Calificacion (INT).

    Contexto: {contexto_completo}
    Mensaje del usuario: {mensaje}

    Responde excluyendo los id en la consulta 
    """

    try:
        # Crear la solicitud con la API
        respuesta = client.chat.completions.create(

            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Eres un experto en bases de datos."},
                {"role": "user", "content": prompt}
            ]
        )

        # Obtener la consulta generada
        respuesta_texto = respuesta.choices[0].message.content.strip()

        # Limpiar y validar la consulta SQL
        consulta_sql = (
            respuesta_texto
            .replace("```sql", "")  # Eliminar etiquetas de código SQL
            .replace("```", "")     # Eliminar etiquetas restantes
            .strip()                # Eliminar espacios en blanco adicionales
        )

        # Validar si es una consulta válida
        if "no válida" in consulta_sql.lower():
            return "No se pudo encontrar una consulta SQL válida en la respuesta."

        # Ejecutar la consulta
        try:
            resultados = ejecutar_query(consulta_sql)
            return formatear_resultados(resultados)
        except Exception as e:
            return f"Error ejecutando la consulta SQL: {e}"

    except Exception as e:
        return f"Error al procesar el mensaje con OpenAI: {e}"
    
    