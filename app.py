import streamlit as st
import os
from main import responder_pregunta
from main import transcribir_audio, guardar_en_db, inicializar_db, obtener_historial, generar_resumen
from generador_pdf import generar_pdf # Asegúrate de que este nombre coincida con tu archivo

st.set_page_config(page_title="Transcriptor Pro IA", page_icon="🤖", layout="wide")

def main():
    # --- 1. MEMORIA DE SESIÓN (La Mochila) ---
    # Si no existe la variable 'transcripcion_actual' en la memoria, la creamos vacía.
    if 'transcripcion_actual' not in st.session_state:
        st.session_state.transcripcion_actual = None
    if 'analisis_actual' not in st.session_state:
        st.session_state.analisis_actual = None
    if 'nombre_archivo_actual' not in st.session_state:
        st.session_state.nombre_archivo_actual = None

    # --- BARRA LATERAL ---
    st.sidebar.title("🗄️ Historial")
    lista_trabajos = obtener_historial()
    
    for trabajo in lista_trabajos:
        id_trabajo, fecha, nombre, contenido, analisis = trabajo
        
        with st.sidebar.expander(f"{fecha} - {nombre}"):
            st.caption(f"ID: {id_trabajo}")
            tab1, tab2 = st.tabs(["🤖 Análisis", "📝 Texto"])
            with tab1:
                if analisis: st.markdown(analisis)
                else: st.info("Sin análisis")
            with tab2:
                st.text_area("Original:", contenido, height=100, key=f"hist_{id_trabajo}")

    # --- PANTALLA PRINCIPAL ---
    st.title("🤖 Transcriptor Pro: IA + Internet")
    st.write("Obtén resúmenes de audios, conferencias o videos de internet.")
    
    inicializar_db()

    # Pestañas para elegir la fuente
    tab_upload, tab_link = st.tabs(["📂 Subir Archivo", "🌍 Desde URL (YouTube/Web)"])
    
    archivo_procesar = None
    es_descarga_web = False # Bandera para saber si tenemos que borrar un archivo descargado

    with tab_upload:
        archivo_subido = st.file_uploader("Arrastra tu audio aquí", type=["mp3", "wav", "m4a"])
        if archivo_subido:
            archivo_procesar = archivo_subido

    with tab_link:
        url_input = st.text_input("Pega el link aquí (YouTube, Vimeo, etc):")
    
    # Botón único para ambos casos
    if st.button("✨ Procesar Audio con IA"):
        
        # CASO 1: Es una URL
        if url_input and not archivo_subido:
            with st.spinner('🌍 Descargando audio de internet... (Esto puede tardar unos segundos)'):
                from main import descargar_audio_internet # Importación tardía
                ruta_descargada = descargar_audio_internet(url_input)
                
                if ruta_descargada:
                    archivo_procesar = ruta_descargada
                    es_descarga_web = True
                else:
                    st.error("No se pudo descargar el video. Verifica el link.")

        # CASO 2: Es un archivo subido
        elif archivo_subido:
            # Guardar temporalmente
            with open(archivo_subido.name, "wb") as f:
                f.write(archivo_subido.getbuffer())
            archivo_procesar = archivo_subido.name
            es_descarga_web = True # Lo marcamos para borrado automático también

        # --- FLUJO COMÚN DE PROCESAMIENTO ---
        if archivo_procesar:
            # 1. Transcribir
            with st.spinner('👂 Escuchando y transcribiendo...'):
                texto = transcribir_audio(archivo_procesar)
            
            if texto:
                # 2. Analizar
                with st.spinner('🧠 Analizando con Llama 3...'):
                    analisis = generar_resumen(texto)

                # 3. Guardar en Memoria
                st.session_state.transcripcion_actual = texto
                st.session_state.analisis_actual = analisis
                # Usamos el nombre del archivo o la URL como referencia
                if url_input:
                    nombre_ref = f"Web_{url_input[-10:]}" # Usamos los ultimos caracteres del link
                else:
                    nombre_ref = archivo_subido.name
                
                st.session_state.nombre_archivo_actual = nombre_ref
                
                # 4. Guardar en DB
                guardar_en_db(nombre_ref, texto, analisis)
                st.toast("Guardado en base de datos", icon="💾")
                
                # 5. Limpieza
                if es_descarga_web:
                    os.remove(archivo_procesar)
        else:
            st.warning("Por favor, sube un archivo o pega un link válido.")


    # --- RENDERIZADO DE RESULTADOS (FUERA DEL BOTÓN) ---
    # Preguntamos: "¿Hay algo guardado en la memoria?"
    if st.session_state.transcripcion_actual:
        
        st.success("¡Resultados listos!")
        
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("📝 Transcripción")
            st.text_area("Texto:", st.session_state.transcripcion_actual, height=400)
        
        with col2:
            st.subheader("🤖 Análisis")
            st.info(st.session_state.analisis_actual)
            
        # --- ZONA DE DESCARGA ---
        st.write("---")
        st.subheader("📂 Exportar")
        
        # Generamos el PDF usando los datos de la memoria
        # Lo hacemos aquí mismo para evitar el "botón dentro de botón"
        nombre_pdf_temp = generar_pdf(
            st.session_state.nombre_archivo_actual, 
            st.session_state.transcripcion_actual, 
            st.session_state.analisis_actual
        )
        
        # Leemos el PDF generado
        with open(nombre_pdf_temp, "rb") as pdf_file:
            pdf_bytes = pdf_file.read()
            
        # Este botón YA NO ESTÁ ANIDADO. Vive fuera, sostenido por la memoria.
        st.download_button(
            label="⬇️ Descargar Reporte PDF",
            data=pdf_bytes,
            file_name=f"Reporte_{st.session_state.nombre_archivo_actual}.pdf",
            mime="application/pdf"
        )

        # ... (código anterior del PDF) ...

        st.write("---")
        st.subheader("💬 Chat con el Audio")
        st.caption("Pregúntale detalles específicos que no salieron en el resumen.")

        # 1. Inicializar historial de chat si no existe
        if "mensajes_chat" not in st.session_state:
            st.session_state.mensajes_chat = []

        # 2. Mostrar mensajes anteriores (para que no se borren al recargar)
        for mensaje in st.session_state.mensajes_chat:
            with st.chat_message(mensaje["role"]):
                st.markdown(mensaje["content"])

        # 3. Input del usuario (La cajita de texto abajo)
        if prompt := st.chat_input("Ej: ¿Mencionaron algún precio?"):
            
            # A) Mostrar pregunta del usuario
            with st.chat_message("user"):
                st.markdown(prompt)
            # Guardar en historial
            st.session_state.mensajes_chat.append({"role": "user", "content": prompt})

            # B) Generar respuesta
            with st.chat_message("assistant"):
                with st.spinner("Pensando..."):
                    # IMPORTANTE: Le pasamos lo que preguntó Y el texto completo del audio
                    respuesta = responder_pregunta(prompt, st.session_state.transcripcion_actual)
                    st.markdown(respuesta)
            
            # Guardar respuesta en historial
            st.session_state.mensajes_chat.append({"role": "assistant", "content": respuesta})
        
        # Botón para limpiar y empezar de cero
        if st.button("🔄 Nueva Transcripción"):
            # Borramos la memoria
            st.session_state.transcripcion_actual = None
            st.session_state.analisis_actual = None
            st.session_state.nombre_archivo_actual = None
            st.session_state.mensajes_chat = [] # <--- NUEVA LÍNEA: Borrar chat
            st.rerun()

if __name__ == "__main__":
    main()