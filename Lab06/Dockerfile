# Lekki obraz pythona
FROM python:3.13-slim

# Katalog roboczy w kontenerze
WORKDIR /app

# Kopiowanie listy zależności
COPY requirements.txt .

# Instalacja bibliotek (bez cache aby zmniejszyć rozmiar obrazu)
RUN pip install --no-cache-dir -r requirements.txt

# Kopiowanie pliku aplikacji
COPY app.py .

# Wystawienie portu
EXPOSE 8000

# Komenda do uruchomienia serwera
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]