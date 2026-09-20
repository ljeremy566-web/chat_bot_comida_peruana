import os
import tempfile
import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI

# Cargar variables de entorno desde el archivo .env
load_dotenv()

# Inicializar cliente de OpenAI
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

# Configuración de la interfaz en Streamlit
st.set_page_config(
    page_title="Chatbot de comida peruana",
    page_icon="🍲",
    layout="centered"
)

st.title("🍲 Chatbot de comida peruana")
st.caption("Consulta por texto o carga un audio.")

# Definición del Prompt de Sistema
SYSTEM_PROMPT = """
Eres un asistente especializado en gastronomía peruana.
Responde únicamente consultas relacionadas con comida peruana:
platos, ingredientes, regiones, preparación, historia culinaria
y recomendaciones gastronómicas.
Si la pregunta no corresponde al tema, indícalo cordialmente
y orienta al usuario a formular una consulta sobre gastronomía peruana.
Responde en español y con explicaciones claras para estudiantes.
"""

# Inicialización del historial de mensajes en la sesión
if "messages" not in st.session_state:
    st.session_state.messages = []

# Renderizado de los mensajes previos
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

def consultar_chatbot(pregunta):
    """Consulta al modelo de OpenAI manteniendo el historial de conversación."""
    historial = [
        {"role": "system", "content": SYSTEM_PROMPT}
    ]
    historial.extend(st.session_state.messages)
    historial.append({"role": "user", "content": pregunta})

    # Si en el entorno o .env se define un modelo (ej. gpt-4o-mini o gpt-5.6-luna), se usa ese
    modelo = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    
    respuesta = client.chat.completions.create(
        model=modelo,
        messages=historial
    )
    return respuesta.choices[0].message.content

# 1. Entrada por texto
pregunta = st.chat_input("Escribe una pregunta sobre comida peruana")

if pregunta:
    # Agregar y mostrar mensaje del usuario
    st.session_state.messages.append(
        {"role": "user", "content": pregunta}
    )
    with st.chat_message("user"):
        st.markdown(pregunta)
        
    # Obtener y mostrar respuesta del asistente
    with st.chat_message("assistant"):
        with st.spinner("Generando respuesta..."):
            respuesta = consultar_chatbot(pregunta)
            st.markdown(respuesta)
            
    st.session_state.messages.append(
        {"role": "assistant", "content": respuesta}
    )

st.divider()

# 2. Entrada por audio
st.subheader("🎤 Consulta mediante audio")
audio = st.file_uploader(
    "Carga un audio",
    type=["mp3", "wav", "m4a", "webm"]
)

if audio is not None:
    st.audio(audio)
    if st.button("Transcribir y consultar"):
        extension = audio.name.split(".")[-1]
        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=f".{extension}"
        ) as archivo_temp:
            archivo_temp.write(audio.getbuffer())
            ruta_temp = archivo_temp.name

        try:
            # Transcripción con Whisper
            with open(ruta_temp, "rb") as archivo_audio:
                transcripcion = client.audio.transcriptions.create(
                    model="whisper-1",
                    file=archivo_audio,
                    language="es"
                )
            texto = transcripcion.text
            st.success("Audio transcrito correctamente.")
            st.write("**Texto transcrito:**")
            st.write(texto)

            # Enviar la transcripción al chatbot
            st.session_state.messages.append(
                {"role": "user", "content": texto}
            )
            with st.chat_message("user"):
                st.markdown(f"🎤 {texto}")
            with st.chat_message("assistant"):
                with st.spinner("Generando respuesta..."):
                    respuesta = consultar_chatbot(texto)
                    st.markdown(respuesta)
            st.session_state.messages.append(
                {"role": "assistant", "content": respuesta}
            )
        finally:
            if os.path.exists(ruta_temp):
                os.remove(ruta_temp)

st.divider()

# 3. Botón para reiniciar historial
if st.button("Limpiar conversación"):
    st.session_state.messages = []
    st.rerun()
