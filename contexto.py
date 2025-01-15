# Diccionario para guardar el contexto por usuario
contextos = {}

def actualizar_contexto(user_id, mensaje):
    if user_id not in contextos:
        contextos[user_id] = []
    # Agregar el nuevo mensaje al historial del usuario
    contextos[user_id].append(mensaje)
    # Limitar el historial a los últimos 10 mensajes (opcional)
    if len(contextos[user_id]) > 10:
        contextos[user_id] = contextos[user_id][-10:]
    return contextos[user_id]

def obtener_contexto(user_id):
    # Devolver el historial de contexto del usuario
    return contextos.get(user_id, [])
