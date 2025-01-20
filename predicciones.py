from sklearn.linear_model import LinearRegression
import numpy as np
from db import ejecutar_query

# Opcion 1 
def obtener_calificaciones_por_clasificacion(nombre_alumno):
    query = """
    SELECT c.Nombre, m.Nombre_Materia, cal.Calificacion
    FROM Calificaciones cal
    JOIN Materia m ON cal.ID_Materia = m.ID_Materia
    JOIN Clasificacion c ON m.ID_clasificacion = c.ID_clasificacion
    JOIN Alumno a ON cal.ID_Alumno = a.ID_Alumno
    WHERE a.Nombre = %s
    ORDER BY c.Nombre, m.Nombre_Materia
    """
    return ejecutar_query(query, (nombre_alumno,))

#Opcion 2
def obtener_calificaciones_materia(nombre_materiaPC, nombre_alumno):
    query = """
    SELECT 
        m.Nombre_Materia,
        c.Calificacion
    FROM 
        Calificaciones c
    JOIN 
        Alumno a ON c.ID_Alumno = a.ID_Alumno
    JOIN 
        Materia m ON c.ID_Materia = m.ID_Materia
    JOIN 
        Clasificacion cl ON m.ID_clasificacion = cl.ID_clasificacion
    JOIN 
        MateriaPC pc ON cl.ID_clasificacion = pc.ID_clasificacionPC
    WHERE 
        a.Nombre = %s 
        AND pc.Nombre_MateriaPC = %s
    ORDER BY 
        m.Nombre_Materia
    """
    return ejecutar_query(query, (nombre_alumno, nombre_materiaPC))

#Opcion 3
def obtener_calificaciones_clasificacion(nombre_clasificacion, nombre_alumno):
    query = """
    SELECT 
        m.Nombre_Materia,
        c.Calificacion
    FROM 
        Calificaciones c
    JOIN 
        Alumno a ON c.ID_Alumno = a.ID_Alumno
    JOIN 
        Materia m ON c.ID_Materia = m.ID_Materia
    JOIN 
        Clasificacion cl ON m.ID_clasificacion = cl.ID_clasificacion
    WHERE 
        a.Nombre = %s 
        AND cl.Nombre = %s
    ORDER BY 
        m.Nombre_Materia;
    """
    return ejecutar_query(query, (nombre_alumno, nombre_clasificacion))

def predecir_calificacion(calificaciones):
    if not calificaciones:
        return "No hay suficientes datos para realizar la predicción"
    
    X = np.arange(len(calificaciones)).reshape(-1, 1)
    y = np.array([cal[1] for cal in calificaciones])
    
    modelo = LinearRegression()
    modelo.fit(X, y)
    
    siguiente_materia = len(calificaciones)
    prediccion = modelo.predict([[siguiente_materia]])[0]
    
    return round(prediccion, 2)

