# 1. Usamos una imagen base de Python (ligera)
FROM python:3.11-slim

# 2. Instalamos FFmpeg (NECESARIO para Whisper y yt-dlp)
# "apt-get" es el instalador de Linux (porque el contenedor usa Linux por dentro)
RUN apt-get update && apt-get install -y ffmpeg

# 3. Establecemos la carpeta de trabajo dentro del contenedor
WORKDIR /app

# 4. Copiamos solo el archivo de requerimientos primero (para aprovechar la caché)
COPY requirements.txt .

# 5. Instalamos las librerías
RUN pip install --no-cache-dir -r requirements.txt

# 6. Copiamos todo el resto del código
COPY . .

# 7. Le decimos al mundo que usaremos el puerto 8501 (el de Streamlit)
EXPOSE 8501

# 8. El comando para arrancar la app
CMD ["streamlit", "run", "app.py", "--server.address=0.0.0.0"]