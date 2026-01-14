import streamlit as st
import os
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
    st.title("🤖 Transcriptor con Inteligencia Artificial")
    inicializar_db()

    archivo_subido = st.file_uploader("Arrastra tu audio aquí", type=["mp3", "wav", "m4a"])

    if archivo_subido is not None:
        # Botón principal
        if st.button("✨ Procesar Audio con IA"):
            
            # Guardado temporal del audio
            nombre_temp = archivo_subido.name
            with open(nombre_temp, "wb") as f:
                f.write(archivo_subido.getbuffer())
            
            # --- PROCESAMIENTO ---
            with st.spinner('👂 Escuchando y transcribiendo...'):
                texto = transcribir_audio(nombre_temp)
            
            if texto:
                with st.spinner('🧠 Analizando con Llama 3 (Groq)...'):
                    analisis = generar_resumen(texto)

                # --- ¡AQUÍ ESTÁ EL TRUCO! ---
                # Guardamos los resultados en la memoria (session_state)
                # Así, aunque se recargue la página, los datos siguen vivos.
                st.session_state.transcripcion_actual = texto
                st.session_state.analisis_actual = analisis
                st.session_state.nombre_archivo_actual = nombre_temp
                
                # Guardamos en DB y borramos temporal
                guardar_en_db(nombre_temp, texto, analisis)
                st.toast("Guardado en base de datos", icon="💾")
                os.remove(nombre_temp)

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
        
        # Botón para limpiar y empezar de cero
        if st.button("🔄 Nueva Transcripción"):
            # Borramos la memoria
            st.session_state.transcripcion_actual = None
            st.session_state.analisis_actual = None
            st.rerun()

if __name__ == "__main__":
    main()