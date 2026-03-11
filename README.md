# Prompt Manager WebApp

A web application built with Streamlit to help you easily structure, organize, and save your prompts.

## Features

- 📝 **Organizational Structure:** Divide your thoughts into key sections (Objective, Steps, Considerations).
- 💾 **Persistence (SQLite):** Save your prompts locally for future use.
- 📋 **Markdown Export:** Generate text in Markdown format and copy it to the clipboard with a single button.
- 📚 **Sidebar History:** Quickly access your previous prompts from the sidebar.
- 🐳 **Dockerized:** Ready to be deployed in a container.

## Requirements

- Python 3.8 or higher (to run locally)
- Docker (if you want to run it in a container)

## Run Locally with Python

1. Create and activate a virtual environment (optional but recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Linux/Mac
   # venv\Scripts\activate   # On Windows
   ```

2. Install the dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the application:
   ```bash
   streamlit run app.py
   ```

4. Open your browser and go to `http://localhost:8501`.

## Run with Docker

1. Build the Docker image:
   ```bash
   docker build -t prompt-manager .
   ```

2. Run the container (mounting a volume to persist the local database):
   ```bash
   docker run -p 8501:8501 -v $(pwd):/app prompt-manager
   ```
   > **Note:** The database `prompts.db` will be created inside the container. If you want the data to be saved in a different path, make sure to update the `DB_NAME` variable in `app.py`. In the current command we use a volume mapped to `/app/data`, so it is recommended to edit `app.py` like this: `DB_NAME = "data/prompts.db"` to keep the data when restarting the container.
