# Usa una imagen oficial de Python como base
FROM python:3.9-slim

# Establece el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copia el archivo de requerimientos y los instala
# Se hace en dos pasos para aprovechar el caché de Docker
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copia todo el código de tu proyecto al contenedor
# (esto incluye app.py y scrubbed.csv)
COPY . .

# Expone el puerto que usa Streamlit
EXPOSE 8501

# El comando para correr tu aplicación (usando tu archivo app.py)
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.headless=true"]