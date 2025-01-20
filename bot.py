import telebot
from collections import defaultdict
from agregar import procesar_csv, registrar_alumno
from nlp import procesar_mensaje
from contexto import actualizar_contexto
from manejadoresPrediccion import procesar_mensaje_prediccion

# Configurar tokens
TELEGRAM_TOKEN = ""
bot = telebot.TeleBot(TELEGRAM_TOKEN)

# Variable para gestionar estados usando defaultdict
estado_usuario = defaultdict(lambda: {"estado": None, "datos": {}})

# Manejador del comando /start
@bot.message_handler(commands=["Menu"])
def enviar_bienvenida(message):
    user_id = message.chat.id
    # Reiniciar estado al iniciar
    estado_usuario[user_id] = {"estado": None, "datos": {}}  
    mensaje_bienvenida = (
        " 📚 ‧₊˚✧ Bienvenido ✧˚₊‧ 📚  \n"
        "Este bot ayudará a analizar información sobre calificaciones"
        "de los alumnos registrados en nuestra aplicación. \n"
        "Puedes empezar eligiendo una opcion del menu de opciones 📋\n"
        " 🎓 /Agregar \n"
        " 📊 /Analisis \n"
        " ⏰ /Predecir \n"
        " ❇️ /Ayuda \n"
    )

    # Adjuntar una imagen con un pie de foto (mensaje incluido)
    with open("img/start.jpg", "rb") as imagen:
        bot.send_photo(user_id, imagen, caption=mensaje_bienvenida)
        
import re

# Comando /Agregar (Alumno)
@bot.message_handler(commands=["Agregar"])
def agregar_alumno(message):
    user_id = message.chat.id
    if estado_usuario[user_id]["estado"] in ["analisis", "predicciones"]:
        bot.send_message(user_id, "❌ Solicitud inválida. \n ⚠️ Para mas detalles ve a /Ayuda o sal con /Menu.")
        return

    estado_usuario[user_id] = {"estado": "nombre", "datos": {}}
    bot.send_message(user_id, "🎓 Proporciona el nombre del alumno:")

# Manejador para recibir mensajes durante el flujo de "Agregar"
@bot.message_handler(func=lambda message:
    estado_usuario.get(message.chat.id, {}).get("estado") == "nombre")
def registrar_nombre_alumno(message):
    user_id = message.chat.id
    nombre = message.text.strip()

    # Validar que el nombre solo contenga letras y espacios
    if not re.match(r"^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$", nombre):
        bot.send_message(
            user_id,
            "❌ Solo puedo aceptar letras y espacios.\n"
            "✅ Utiliza un nombre válido o sal con /Menu"
        )
        # Reiniciar el proceso de agregar
        estado_usuario[user_id] = {"estado": "nombre", "datos": {}}
        bot.send_message(user_id, "🎓 Proporciona el nombre del alumno:")
        return

    # Guardar el nombre si es válido
    estado_usuario[user_id]["datos"]["nombre"] = nombre
    # Cambiar el estado
    estado_usuario[user_id]["estado"] = "esperando_csv"
    bot.send_message(
        user_id,
        f"Nombre del alumno: {nombre}\n"
        "📃 Envia el archivo CSV con las calificaciones del alumno."
    )

# Manejador para procesar archivos CSV
@bot.message_handler(content_types=["document"])
def manejar_documento(message):
    user_id = message.chat.id
    user_state = estado_usuario[user_id]

    if not user_state or user_state.get("estado") != "esperando_csv":
        bot.send_message(user_id, "❌ Solicitud inválida.\n ⚠️ Para mas detalles ve a /Ayuda o sal con /Menu.")
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
        bot.send_message(user_id, f"❌ Error al manejar el archivo \n ⚠️ Para mas detalles ve a /Ayuda o sal con /Menu: {e}")

    # Resetear el estado después de completar
    estado_usuario[user_id] = {"estado": None, "datos": {}}

# Comando /Analisis
@bot.message_handler(commands=["Analisis"])
def modo_analisis(message):
    user_id = message.chat.id

    # Verificar si el usuario está en un flujo activo
    user_state = estado_usuario[user_id]["estado"]
    if user_state in ["nombre", "esperando_csv"]:
        bot.send_message(user_id, "❌ Solicitud inválida.\n ⚠️ Para mas detalles ve a /Ayuda o sal con /Menu.")
        return

    # Cambiar al estado de análisis
    estado_usuario[user_id] = {"estado": "analisis", "datos": {}}
    bot.send_message(
        user_id,
        "Estás en el modo análisis general.\n"
        "Realiza cualquier pregunta sobre los datos en la BD.\n"
        "Teclea /Menu para volver al menú de opciones."
    )

@bot.message_handler(commands=["Predecir"])
def iniciar_prediccion(message):
    user_id = message.chat.id
    menu = """
    Estás en el modo Predecir.\n
    ⚠️ Puedes encontrar el formato de consulta en /Ayuda:\n
    
    1. 🎓 Calificaciones de cada clasificacion por Alumno\n
    2. ✏ Calificacion en Materia por Alumno\n
    3. 💯 Calificacion en Clasificacion por Alumno\n
    
    Teclea /Menu para volver al menú de opciones.
    """

    estado_usuario[user_id]["estado"] = "prediccion"
    bot.reply_to(message, menu)

@bot.message_handler(func=lambda m: estado_usuario[m.chat.id]["estado"] == "prediccion")
def manejar_prediccion(message):
    user_id = message.chat.id
    respuesta = procesar_mensaje_prediccion(message.text)
    bot.reply_to(message, respuesta)
    estado_usuario[user_id]["estado"] = None
    
# Manejador de mensajes
@bot.message_handler(func=lambda message: True)
def manejar_mensaje(message):
    user_id = message.chat.id
    user_input = message.text

    # Verificar si el usuario está en el estado "analisis"
    user_state = estado_usuario[user_id]["estado"]
    if user_state != "analisis":
        bot.send_message(user_id, "Selecciona una opción válida con /Menu.")
        return

    # Actualizar contexto de conversación
    contexto = actualizar_contexto(user_id, user_input) 

    # Procesar mensaje con NLP (pasamos el contexto completo)
    respuesta = procesar_mensaje(user_input, contexto)

    # Si la respuesta es un archivo de gráfica
    if respuesta.endswith(".png"):
        with open(respuesta, "rb") as imagen:
            bot.send_photo(user_id, imagen, caption="Aquí tienes tu gráfica 📊")
    else:
        # Enviar la respuesta de texto
        bot.send_message(user_id, respuesta)

# Ejecutar el bot
if __name__ == "__main__":
    print("Bot corriendo...")
    bot.infinity_polling()
