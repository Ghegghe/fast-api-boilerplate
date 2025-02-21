# Usa un'immagine base di Python
FROM python:3.12.2-slim

# Imposta la directory di lavoro nel container
WORKDIR /app

# Copia il file requirements.txt e installa le dipendenze
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia il resto del codice dell'applicazione
COPY . .

# Esponi la porta su cui l'applicazione verrà eseguita
EXPOSE 8000

# Comando per avviare l'applicazione
CMD ["fastapi", "run", "app.py"]
