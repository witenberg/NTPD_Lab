# Lekki obraz Pythona
FROM python:3.13-slim

WORKDIR /app

# Wersja aplikacji bake'owana w obrazie (v1 vs v2 do rolling update)
ARG APP_VERSION=1.0
ENV APP_VERSION=${APP_VERSION}

# Instalacja zaleznosci
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Kod aplikacji
COPY app.py .

EXPOSE 8000

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
