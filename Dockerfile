# Usa la imagen oficial de Python como imagen base
FROM python:3.10-slim

# Establece el directorio de trabajo
WORKDIR /app

# Copia los archivos de requerimientos e instala las dependencias
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Copia el código de la aplicación
COPY app.py .
COPY .streamlit .streamlit

# Expone el puerto por defecto de Streamlit
EXPOSE 8501

# Crea un volumen para la base de datos y así asegurar persistencia
VOLUME /app/data

# Corre la aplicación Streamlit
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
