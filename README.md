# Prompt Manager WebApp

Una aplicación web creada con Streamlit para ayudarte a estructurar, organizar y guardar tus prompts de forma sencilla.

## Características

- 📝 **Estructura Organizacional:** Divide tus pensamientos en secciones clave (Objetivo, Pasos, Consideraciones).
- 💾 **Persistencia (SQLite):** Guarda tus prompts localmente para su uso futuro.
- 📋 **Exportación en Markdown:** Genera el texto en formato Markdown y cópialo al portapapeles con un solo botón.
- 📚 **Historial Lateral:** Accede rápidamente a tus comandos anteriores desde la barra lateral.
- 🐳 **Dockerizado:** Listo para ser desplegado en un contenedor.

## Requisitos

- Python 3.8 o superior (para ejecutar locamente)
- Docker (si se desea ejecutar en contenedor)

## Ejecutar localmente con Python

1. Crea y activa un entorno virtual (opcional pero recomendado):
   ```bash
   python -m venv venv
   source venv/bin/activate  # En Linux/Mac
   # venv\Scripts\activate   # En Windows
   ```

2. Instala las dependencias:
   ```bash
   pip install -r requirements.txt
   ```

3. Ejecuta la aplicación:
   ```bash
   streamlit run app.py
   ```

4. Abre tu navegador y dirígete a `http://localhost:8501`.

## Ejecutar con Docker

1. Construye la imagen de Docker:
   ```bash
   docker build -t prompt-manager .
   ```

2. Ejecuta el contenedor (montando un volumen para persistir la base de datos local):
   ```bash
   docker run -p 8501:8501 -v $(pwd):/app prompt-manager
   ```
   > **Nota:** La base de datos `prompts.db` se creará dentro del contenedor. Si deseas que los datos se guarden en una ruta diferente, asegúrate de actualizar la variable `DB_NAME` en `app.py`. En el comando actual usamos un volumen mapeado a `/app/data`, por lo que es recomendable editar `app.py` así: `DB_NAME = "data/prompts.db"` para mantener los datos al reiniciar el contenedor.
