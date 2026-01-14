# 🎙️ Transcriptor Pro IA

Aplicación de escritorio para la transcripción automática de audio y generación de actas inteligentes utilizando Inteligencia Artificial local y en la nube.

## 🚀 Funcionalidades

- **Transcripción de Audio:** Utiliza el modelo `Whisper` (OpenAI) para convertir audio a texto con alta precisión.
- **Análisis Cognitivo:** Integración con `Llama 3` (vía Groq) para generar resúmenes, detectar tareas y analizar el sentimiento de la reunión.
- **Persistencia de Datos:** Base de datos SQLite para historial de trabajos.
- **Reportes Formales:** Generación automática de PDFs listos para imprimir.
- **Seguridad:** Gestión de credenciales mediante secretos de entorno.

## 🛠️ Tecnologías Usadas

- **Python 3.10+**
- **Streamlit** (Interfaz de Usuario)
- **OpenAI Whisper** (Motor de Audio)
- **Groq API** (Motor de Inferencia LLM)
- **SQLite3** (Base de Datos)
- **FPDF2** (Generación de Documentos)

## 📦 Instalación

1. Clonar el repositorio:
   ```bash
   git clone [https://github.com/TU_USUARIO/transcriptor-pro.git](https://github.com/TU_USUARIO/transcriptor-pro.git)

2. Crear un entorno virtual e instalar dependencias:
    python -m venv venv
    source venv/bin/activate  # En Windows: venv\Scripts\activate
    pip install -r requirements.txt

3. Configurar las claves:

    Crear una carpeta .streamlit

    Crear un archivo secrets.toml dentro con tu API Key de Groq:

    GROQ_API_KEY = "gsk_tu_clave_aqui"

4. Ejecutar la aplicacion:

    streamlit run app.py