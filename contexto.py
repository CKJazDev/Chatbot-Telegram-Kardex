# Diccionario para guardar el contexto por usuario
contextos = {}

def actualizar_contexto(user_id, mensaje):
    if user_id not in contextos:
        contextos[user_id] = []
    contextos[user_id].append(mensaje)
    return contextos[user_id]

def obtener_contexto(user_id):
    return contextos.get(user_id, [])
