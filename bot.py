import telebot
from collections import defaultdict
from agregar import procesar_csv, registrar_alumno
from nlp import procesar_mensaje
from contexto import actualizar_contexto

# Configurar tokens
TELEGRAM_TOKEN = ""
bot = telebot.TeleBot(TELEGRAM_TOKEN)

# Variable para gestionar estados usando defaultdict
estado_usuario = defaultdict(lambda: {"estado": None, "datos": {}})

# Manejador del comando /start
@bot.message_handler(commands=["start"])
def enviar_bienvenida(message):
    user_id = message.chat.id
    # Reiniciar estado al iniciar
    estado_usuario[user_id] = {"estado": None, "datos": {}}  
    mensaje_bienvenida = (
        " 📚 ‧₊˚✧ Bienvenido ✧˚₊‧ 📚  \n"
        "Este bot te ayudará a analizar información sobre las calificaciones"
        "de los alumnos registrados en nuestra aplicación. \n"
        "Puedes empezar eligiendo una opcion del menu de opciones 📋\n"
        " 🎓 /Agregar \n"
        " 📊 /Analisis \n"
        " ⏰ /Predicciones \n"
        " ❓ /Ayuda \n"
    )

    # Adjuntar una imagen con un pie de foto (mensaje incluido)
    with open("img/start.jpg", "rb") as imagen:
        bot.send_photo(user_id, imagen, caption=mensaje_bienvenida)
        
# Comando /Agregar (Alumno)
@bot.message_handler(commands=["Agregar"])
def agregar_alumno(message):
    user_id = message.chat.id
    if estado_usuario[user_id]["estado"] in ["analisis", "predicciones"]:
        bot.send_message(user_id, "Solicitud inválida. Sal con /start.")
        return

    estado_usuario[user_id] = {"estado": "nombre", "datos": {}}
    bot.send_message(user_id, "Proporciona el nombre del alumno a agregar:")


# Manejador para recibir mensajes durante el flujo de "Agregar"
@bot.message_handler(func=lambda message: estado_usuario.get(message.chat.id, {}).get("estado") == "nombre")
def registrar_nombre_alumno(message):
    user_id = message.chat.id
    # Guardar el nombre
    estado_usuario[user_id]["datos"]["nombre"] = message.text 
    # Cambiar el estado 
    estado_usuario[user_id]["estado"] = "esperando_csv"  
    bot.send_message(
        user_id,
        f"Nombre del alumno registrado: {message.text}\n"
        "Ahora, sube el archivo CSV con las calificaciones del alumno."
    )


# Manejador para procesar archivos CSV
@bot.message_handler(content_types=["document"])
def manejar_documento(message):
    user_id = message.chat.id
    user_state = estado_usuario[user_id]

    if not user_state or user_state.get("estado") != "esperando_csv":
        bot.send_message(user_id, "Solicitud es inválida. Sal con /start.")
        return

    nombre_alumno = user_state["datos"]["nombre"]

    # Descargar el archivo
    try:
        file_info = bot.get_file(message.document.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        # Registra el alumno y obtén su ID
        alumno_id = registrar_alumno(nombre_alumno)  

        if isinstance(alumno_id, str):  # Si hay un error al registrar
            bot.send_message(user_id, alumno_id)
            return

        # Procesar el archivo CSV
        resultado = procesar_csv(downloaded_file, alumno_id)
        bot.send_message(user_id, resultado)

    except Exception as e:
        bot.send_message(user_id, f"Error al manejar el archivo: {e}")

    # Resetear el estado después de completar
    estado_usuario[user_id] = {"estado": None, "datos": {}}

@bot.message_handler(commands=["Analisis"])
def modo_analisis(message):
    user_id = message.chat.id

    # Verificar si el usuario está en un flujo activo
    user_state = estado_usuario[user_id]["estado"]
    if user_state in ["nombre", "esperando_csv"]:
        bot.send_message(user_id, "Solicitud es inválida. Sal con /start.")
        return

    # Cambiar al estado de análisis
    estado_usuario[user_id] = {"estado": "analisis", "datos": {}}
    bot.send_message(
        user_id,
        "Estás en el modo análisis general.\n"
        "Realiza cualquier pregunta sobre los datos en la BD.\n"
        "Teclea /start para volver al menú de opciones."
    )

# Comando /Predicciones
@bot.message_handler(commands=["Predicciones"])
def modo_predicciones(message):
    user_id = message.chat.id
    if estado_usuario[user_id]["estado"] in ["nombre", "analisis"]:
        bot.send_message(user_id, "Solicitud invalida. Sal con /start.")
        return

    bot.send_message(user_id, "Función en desarrollo")


# Comando /Ayuda
@bot.message_handler(commands=["Ayuda"])
def modo_ayuda(message):
    user_id = message.chat.id
    bot.send_message(user_id, "Función en desarrollo")

# Manejador de mensajes
@bot.message_handler(func=lambda message: True)
def manejar_mensaje(message):
    user_id = message.chat.id
    user_input = message.text

    # Verificar si el usuario está en el estado "analisis"
    user_state = estado_usuario[user_id]["estado"]
    if user_state != "analisis":
        bot.send_message(user_id, "Selecciona una opción válida del menú.")
        return

    # Actualizar contexto de conversación
    contexto = actualizar_contexto(user_id, user_input) 

    # Procesar mensaje con NLP (pasamos el contexto completo)
    respuesta = procesar_mensaje(user_input, contexto)

    # Enviar respuesta al usuario
    bot.send_message(user_id, respuesta)


# Ejecutar el bot
if __name__ == "__main__":
    print("Bot corriendo...")
    bot.infinity_polling()
