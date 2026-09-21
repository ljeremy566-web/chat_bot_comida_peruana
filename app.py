import os
import tempfile
import base64
import requests
import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI

# Cargar variables de entorno desde el archivo .env
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Detectar automáticamente si se usa Gemini o OpenAI
USE_GEMINI = bool(GEMINI_API_KEY and (not OPENAI_API_KEY or OPENAI_API_KEY.startswith("AQ.") or "tu_api_key" in OPENAI_API_KEY))

if USE_GEMINI:
    active_key = GEMINI_API_KEY or OPENAI_API_KEY
    client = OpenAI(
        api_key=active_key,
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
    )
    MODELO_DEFAULT = os.getenv("GEMINI_MODEL", "gemini-3.6-flash")
else:
    active_key = OPENAI_API_KEY
    client = OpenAI(api_key=active_key)
    MODELO_DEFAULT = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

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
    """Consulta al modelo manteniendo el historial de conversación."""
    historial = [
        {"role": "system", "content": SYSTEM_PROMPT}
    ]
    historial.extend(st.session_state.messages)
    historial.append({"role": "user", "content": pregunta})

    respuesta = client.chat.completions.create(
        model=MODELO_DEFAULT,
        messages=historial
    )
    return respuesta.choices[0].message.content

# 1. Entrada por texto
pregunta = st.chat_input("Escribe una pregunta sobre comida peruana")

if pregunta:
    st.session_state.messages.append(
        {"role": "user", "content": pregunta}
    )
    with st.chat_message("user"):
        st.markdown(pregunta)
        
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
        extension = audio.name.split(".")[-1].lower()
        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=f".{extension}"
        ) as archivo_temp:
            archivo_temp.write(audio.getbuffer())
            ruta_temp = archivo_temp.name

        try:
            with st.spinner("Transcribiendo audio..."):
                if USE_GEMINI:
                    with open(ruta_temp, "rb") as f:
                        audio_b64 = base64.b64encode(f.read()).decode("utf-8")
                    
                    mime_types = {
                        "wav": "audio/wav",
                        "m4a": "audio/mp4",
                        "webm": "audio/webm",
                        "mp3": "audio/mpeg",
                    }
                    mime = mime_types[extension]
                    modelo_gemini = os.getenv("GEMINI_MODEL", "gemini-3.6-flash")
                    url = f"https://generativelanguage.googleapis.com/v1beta/models/{modelo_gemini}:generateContent?key={active_key}"
                    payload = {
                        "contents": [{
                            "parts": [
                                {"text": "Transcribe exactamente lo que se dice en este audio en español. Devuelve únicamente el texto transcrito sin comillas ni explicaciones."},
                                {"inlineData": {"mimeType": mime, "data": audio_b64}}
                            ]
                        }]
                    }
                    r = requests.post(url, json=payload, timeout=60)
                    resultado = r.json()
                    if not r.ok or "candidates" not in resultado:
                        mensaje_error = resultado.get("error", {}).get("message", r.text)
                        raise RuntimeError(
                            f"Gemini devolvió un error ({r.status_code}): {mensaje_error}"
                        )
                    texto = resultado["candidates"][0]["content"]["parts"][0]["text"].strip()
                else:
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
