# Chatbot Multimodal de Comida Peruana
> Práctica S06.s1 - Creación de Chatbots y Aplicación de Modelos de OpenAI (Whisper + Chat Completions)  
> **Curso:** Herramientas de Desarrollo Profesional - TIC  
> **Unidad:** Prompt Engineering e Inteligencia Artificial

---

## Descripción del Proyecto
Esta aplicación es un chatbot interactivo y multimodal desarrollado con **Python** y **Streamlit**. Está especializado en **gastronomía peruana** y cuenta con dos modalidades de entrada:
1. **Consulta por Texto:** Permite a los usuarios realizar preguntas escritas sobre platos, recetas, ingredientes e historia culinaria del Perú.
2. **Consulta por Audio:** Permite subir archivos de voz (`.mp3`, `.wav`, `.m4a`, `.webm`), transcribirlos automáticamente usando el modelo **Whisper-1** de OpenAI y procesar el texto resultante en la conversación.


## 🚀 Guía de Instalación y Ejecución

### 1. Requisitos Previos
- Python 3.11 o superior instalado.
- Cuenta de OpenAI con API Key activa.

Configuración del Entorno Virtual
Abre una terminal en esta carpeta y ejecuta:

**En Windows (PowerShell):**
```powershell
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```
=gpt-4o-mini
```
*(Nota: En la guía de clase se hace referencia a `gpt-5.6-luna` como modelo referencial de laboratorio; si no está disponible, `gpt-4o-mini` funciona de manera óptima y económica).*

### 4. Iniciar la Aplicación
Con el entorno virtual activo:
```bash
streamlit run app.py
```
Streamlit abrirá automáticamente la aplicación en tu navegador web en `http://localhost:8501`.

---

## 🧪 Banco de Pruebas Requeridas

| # | Prueba | Entrada | Resultado Esperado |
|---|--------|---------|--------------------|
| **1** | Texto | `¿Qué ingredientes lleva el ají de gallina?` | Responde con la lista de ingredientes tradicionales (pechuga, ají amarillo, pan, leche, etc.). |
| **2** | Texto | `¿Cuál es el origen del ceviche peruano?` | Responde sobre la historia y raíces peruanas del plato. |
| **3** | Fuera de dominio | `¿Cómo configuro un router Cisco?` | Declina cordialmente e indica que solo responde sobre comida peruana. |
| **4** | Audio | Subir `audios_prueba/pregunta_causa_limena.wav` | Whisper transcribe la pregunta y el bot responde cómo preparar la causa limeña. |
| **5** | Contexto | Tras preguntar por ceviche: `¿qué pescado se recomienda?` | Entiende que te refieres al pescado para ceviche gracias al historial de mensajes. |

---



   - Respuesta generada a partir de la transcripción de audio.
   - Prueba fuera de dominio rechazada.
3. **Enlace al repositorio GitHub.**
4. Puedes utilizar el documento pre-formateado `Informe_Chatbot_Multimodal_Comida_Peruana.docx`, pegar las capturas y guardarlo como PDF.
