import whisper #para transcribir
import streamlit as st
import os #para habla con el SO
import warnings #para silenciar las advetencias de whisper
import sqlite3 #para gestionar la base de datos
from groq import Groq 
from datetime import datetime #para guardar fecha y hora exacta


warnings.filterwarnings("ignore") #si van a molestar que sea solo con advetencias rojas


def transcribir_audio(ruta_archivo):
    
    if not os.path.exists(ruta_archivo): 
        print(f"ERROR: la ruta del archivo: {ruta_archivo} no existe")
        return None
    
    
    print(f"procesando: {ruta_archivo}...")
    
    #cargar el modelo base de whisper en la variable model
    model = whisper.load_model("base")

     
    respuesta = model.transcribe(ruta_archivo, fp16=False)# respuesta es un diccionario con muchas palabras para cada etiqueta
    
    texto_final = respuesta["text"]# solo quiero las palabras de la etiqueta text
    return texto_final



def guardar_texto(nombre, audio_texto):
    
    nombre_base = os.path.splitext(nombre)[0]#separo el nombre del audio de la extension mp3
    nombre_txt = f"{nombre_base}.txt"
    
    print(f"Guardando archivo: {nombre_txt}...")
    
    with open(nombre_txt, "w", encoding="utf-8") as archivo:
        archivo.write(audio_texto)
    
    print("Archivo guardado correctamente.")
    
    
    
    
def inicializar_db():
    
    
    conexion = sqlite3.connect("transcripciones.db")#esto conectaria el codigo con la base de datos
    cursor = conexion.cursor()# este seria el mozo que nos trae cada cosa que le pedimos
    
    try: 
        cursor.execute("ALTER TABLE trabajos ADD COLUMN analisis TEXT")
    
    except sqlite3.OperationalError:
        pass

    sql = """ 
        CREATE TABLE IF NOT EXISTS trabajos (
        id integer PRIMARY KEY AUTOINCREMENT,
        nombre_archivo TEXT,
        contenido TEXT,
        analisis TEXT,
        fecha TEXT
        )
    """
    
    cursor.execute(sql)

    conexion.commit()
    conexion.close()
    print("Base de datos creada y verificada.")
    
def guardar_en_db(nombre, audio_texto, analisis_ia):
    
    conexion = sqlite3.connect("transcripciones.db")#esto conectaria el codigo con la base de datos
    cursor = conexion.cursor()# este seria el mozo que nos trae cada cosa que le pedimos
    
    fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    sql = """INSERT INTO trabajos (nombre_archivo, contenido, analisis, fecha) VALUES (?, ?, ?, ?)""" #Consulta Parametrizada. Evita un ataque llamado SQL Injection

    datos = (nombre, audio_texto, analisis_ia, fecha_actual)
    
    cursor.execute(sql, datos)
    
    conexion.commit()
    conexion.close()
    print(f"Guardado en Base de Datos (ID generando automaticamente)")

def generar_resumen(texto_completo):
    #Envia el texto a grok para que puede resumir y estructurar el texto


    print("Enviando texto al cerebro artificial (Groq)...")

    try:
        clave_secreta = st.secrets["GROQ_API_KEY"]

    except FileNotFoundError:
        return "Error: no se Encontro archivo: .streamlit/secrets.toml"
    

    #Se inicia 
    cliente = Groq(api_key=clave_secreta)

    prompt_sistema = """ 
        Eres un experto secretario legal y administrativo.
    Tu tarea es analizar la transcripción de una reunión.
    Debes generar un reporte con el siguiente formato exacto:
    
    RESUMEN EJECUTIVO:
    (Un párrafo de 3 lineas resumiendo el tema principal)
    
    PUNTOS CLAVE:
    - (Lista de bullet points con los temas discutidos)
    
    TAREAS Y ACUERDOS:
    - (Lista de tareas asignadas, quién debe hacerlas y fechas si las hay)
    
    SENTIMIENTO:
    (Neutral, Tenso, Positivo, etc.)
  """


    chat_completion = cliente.chat.completions.create(
        messages=[
            {
            "role": "system",
            "content": prompt_sistema,
            },
            {
            "role": "user",
            "content": texto_completo, 
            }
        ],
        model = "llama-3.3-70b-versatile", #Llam3 version rapida
        temperature = 0.5, #Creatividad media                               
    )

    analisis = chat_completion.choices[0].message.content
    return analisis

def obtener_historial():
    conexion = sqlite3.connect("transcripciones.db")
    cursor = conexion.cursor()

    sql = "SELECT id, fecha, nombre_archivo, contenido, analisis FROM trabajos ORDER BY id DESC"


    cursor.execute(sql)
    datos = cursor.fetchall()
    conexion.close()
    return datos


if __name__ == "__main__":
    archivo = "prueba2.mp3"
    
    print("INICIANDO SISTEMA DE TRANSCRIPCION")
    inicializar_db()
    resultado = transcribir_audio(archivo)
    
    if resultado:
        print("-----TRANSCRIPCION-----")
        print(resultado[:100]+"...")
        print("-----------------------")

        guardar_en_db(archivo, resultado)



 