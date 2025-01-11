import telebot
from nlp import procesar_mensaje
from contexto import actualizar_contexto, obtener_contexto

# Configurar tokens


# Manejador de mensajes
@bot.message_handler(func=lambda message: True)
def manejar_mensaje(message):
    user_id = message.chat.id
    user_input = message.text

    # Actualizar contexto de conversación
    contexto = obtener_contexto(user_id)
    actualizar_contexto(user_id, user_input)

    # Procesar mensaje con NLP
    respuesta = procesar_mensaje(user_input, contexto)

    # Enviar respuesta al usuario
    bot.send_message(user_id, respuesta)

# Ejecutar el bot
if __name__ == "__main__":
    print("Bot corriendo...")
    bot.infinity_polling()
