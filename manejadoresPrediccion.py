# manejadoresPrediccion.py
from predicciones import (
    obtener_calificaciones_por_clasificacion,
    obtener_calificaciones_materia,
    obtener_calificaciones_clasificacion,
    predecir_calificacion
)

# manejadoresPrediccion.py
def procesar_mensaje_prediccion(mensaje):
    try:
        partes = [parte.strip() for parte in mensaje.strip().split(',')]
        if not partes:
            return "❌ Por favor ingresa una opción válida"
        
        # La primera parte debe contener la opción
        try:
            opcion = int(partes[0])
        except ValueError:
            return "❌ Sigue el formato de consulta ( Opcion, Nombre, Nombre Alumno), ⚠️ ve a /Ayuda o sal con /Menu"
            
        if opcion == 1:
            if len(partes) < 2:
                return "Formato: 1, NombreAlumno"
            nombre_alumno = partes[1]
            return procesar_prediccion(1, nombre_alumno)
            
        elif opcion == 2:
            if len(partes) < 3:
                return "Formato: 2, NOMBRE_MATERIA, NombreAlumno"
            materia_pc = partes[1]
            nombre_alumno = partes[2]
            return procesar_prediccion(2, materia_pc, nombre_alumno)
            
        elif opcion == 3:
            if len(partes) < 3:
                return "Formato: 3, Clasificacion, NombreAlumno"
            clasificacion = partes[1]
            nombre_alumno = partes[2]
            return procesar_prediccion(3, clasificacion, nombre_alumno)
            
        else:
            return """Opción no válida. Formatos válidos:
                    1, Nombre Alumno
                    2, Nombre Materia, Nombre Alumno
                    3, Clasificacion, Nombre Alumno"""
            
    except Exception as e:
        return f"❌ Error al procesar el mensaje.\n ⚠️ Para mas detalles ve a /Ayuda o sal con /Menu: {str(e)}"

def procesar_prediccion(opcion, *args):
    try:
        if opcion == 1:
            nombre_alumno = args[0]
            calificaciones = obtener_calificaciones_por_clasificacion(nombre_alumno)
            if not calificaciones:
                return "No se encontraron calificaciones para el alumno ☹️"
            
            resultados = []
            clasificacion_actual = None
            calif_por_clasificacion = []
            
            for c in calificaciones:
                if c[0] != clasificacion_actual:
                    if clasificacion_actual:
                        prediccion = predecir_calificacion(calif_por_clasificacion)
                        resultados.append(f"Predicción para {clasificacion_actual}: {prediccion}.\n Para hacer otra prediccion teclea /Predecir")
                    clasificacion_actual = c[0]
                    calif_por_clasificacion = []
                calif_por_clasificacion.append((c[1], c[2]))
            
            if calif_por_clasificacion:
                prediccion = predecir_calificacion(calif_por_clasificacion)
                resultados.append(f"Predicción para {clasificacion_actual}: {prediccion}.\n Para hacer otra prediccion teclea /Predecir")
                
            return "\n".join(resultados)
            
        elif opcion == 2:
            materia_pc, nombre_alumno = args
            calificaciones = obtener_calificaciones_materia(materia_pc, nombre_alumno)
            if not calificaciones:
                return f"No se encontraron calificaciones relacionadas con la materia {materia_pc} para el alumno {nombre_alumno} ☹️"
            
            prediccion = predecir_calificacion(calificaciones)
            if isinstance(prediccion, str):  # Si es un mensaje de error
                return prediccion
                
            return f"Para la materia {materia_pc}, la calificación predicha es: {prediccion}.\n Para hacer otra prediccion teclea /Predecir"
            
        elif opcion == 3:
            clasificacion, nombre_alumno = args
            calificaciones = obtener_calificaciones_clasificacion(clasificacion, nombre_alumno)
            if not calificaciones:
                return f"No se encontraron calificaciones para la clasificación {clasificacion} del alumno {nombre_alumno} ☹️"
            
            prediccion = predecir_calificacion(calificaciones)
            if isinstance(prediccion, str):
                return prediccion
                
            return f"Para la clasificación {clasificacion}, la calificación predicha es: {prediccion}.\n Para hacer otra prediccion teclea /Predecir "
            
        else:
            return "Opción no válida"
            
    except Exception as e:
        return f"Error al procesar la predicción.\n ⚠️ Para mas detalles ve a /Ayuda o sal con /Menu: {str(e)}"