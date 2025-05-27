# Base image con Python
FROM python:3.12-slim

# Imposta working directory
WORKDIR /app

# Copia solo i file necessari
COPY requirements_flask.py ./
RUN pip install --no-cache-dir -r requirements_flask.py

# Copia tutto il progetto (puoi filtrare in .dockerignore)
COPY know_your_worth/ ./know_your_worth/
COPY setup.py ./

# Installa il pacchetto (opzionale)
RUN pip install -e .

COPY configs.yaml /app/configs.yaml

# Espone la porta del manager (supponiamo sia 8004)
EXPOSE 5001

# Comando per avviare manager.py
CMD ["python", "know_your_worth/questionnaire/flask_questionnaire.py"]
