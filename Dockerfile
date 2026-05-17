FROM mcr.microsoft.com/playwright/python:v1.47.0-jammy

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

# instalar chromium deps ya vienen incluidas en imagen oficial
RUN playwright install chromium

CMD ["gunicorn", "app:app", "-b", "0.0.0.0:8080"]
