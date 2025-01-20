import os
from openai import OpenAI
from db import ejecutar_query
import matplotlib.pyplot as plt
import numpy as np

# Configura la clave de API
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY", 
    ""))

def guardar_grafica(resultados, nombre_archivo):
    """
    Genera y guarda una gráfica de barras basada en los resultados.
    """
    # Suponiendo que `resultados` es una lista de tuplas]
    x_labels = [fila[0] for fila in resultados]
    y_values = [fila[1] for fila in resultados]

    # Crear la gráfica
    plt.figure(figsize=(10, 6))
    plt.bar(x_labels, y_values, color='skyblue')
    plt.xlabel('Categoría')  # Cambia según los datos
    plt.ylabel('Valor')      # Cambia según los datos
    plt.title('✨ Resultados de la consulta ✨')

    # Guardar la gráfica como imagen
    plt.tight_layout()
    plt.savefig(nombre_archivo)
    plt.close()
    
def formatear_resultados(resultados):
    """
    Convierte los resultados de la consulta en un formato sencillo'|'.
    """
    if not resultados:
        return "Peticion efectuada. No se devolvieron datos"

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
    Basándote en el siguiente contexto y mensaje del usuario, genera 
    una consulta SQL válida. Devuelve exclusivamente la consulta SQL 
    sin devolver los Id de los datos. 
    Si no puedes generar una consulta válida, responde "Consulta no válida"
    Si el usuario intenta alterar la estructura de la base de daatos, responde "Sin permisos para esta accion"

    Estructura de las tablas base de datos:
    1. Tabla Clasificacion: ID_clasificacion (INT, PK), Nombre (VARCHAR).
    2. Tabla Materia: ID_Materia (INT, PK), Nombre_Materia (VARCHAR), 
    ID_clasificacion (FK), Semestre (INT).
    3. Tabla Alumno: ID_Alumno (INT, PK), Nombre (VARCHAR).
    4. Tabla Calificaciones: ID_Materia (FK), ID_Alumno (FK), 
    Calificacion (INT).
    5. Tabla Materia por cursar: ID_MateriaPC (INT, PK), Nombre_MateriaPC
    (VARCHAR), ID_clasificacionPC (FK), Semestre (INT).

    Contexto: {contexto_completo}
    Mensaje del usuario: {mensaje}

    Responde excluyendo los id en la consulta a menos que el usuario lo solicite, si la consulta es sobre calificaciones
    agrega el nombre de la materia correspondiente
    """

    try:
        # Crear la solicitud con la API
        respuesta = client.chat.completions.create(
            
            model="gpt-3.5-turbo",
            messages=[
                {"role": 
                    "system", 
                    "content": 
                        "Eres un experto en bases de datos."},
                {"role": 
                    "user", 
                    "content": 
                        prompt}
            ]
        )

        # Obtener la consulta generada
        respuesta_texto = respuesta.choices[0].message.content.strip()

        # Limpiar y validar la consulta SQL
        consulta_sql = (
            respuesta_texto
            .replace("```sql", "")  # Eliminar etiquetas de código SQL
            .replace("```", "")     # Eliminar etiquetas restantes
            .strip()                # Eliminar espacios en adicionales
        )

        # Validar si es una consulta válida
        if "no válida" in consulta_sql.lower():
            return "❌ No se pudo encontrar una respuesta válida. Plantea diferente tu consulta o sal con /Menu"

        # Ejecutar la consulta
        try:
            resultados = ejecutar_query(consulta_sql)

            if resultados and len(resultados[0]) == 2:
                nombre_archivo = "grafica.png"
                guardar_grafica(resultados, nombre_archivo)
                # Devuelve el nombre del archivo generado
                return nombre_archivo  

            # Si no son aptos para graficar, retorna los resultados 
            return formatear_resultados(resultados)

        except Exception as e:
            return f"❌ Error ejecutando la consulta \n ⚠️ Para mas detalles ve a /Ayuda o sal con /Menu: {e}"

    except Exception as e:
        return f"❌ Error al procesar el mensaje con OpenAI \n ⚠️ Para mas detalles ve a /Ayuda o sal con /Menu: {e}"