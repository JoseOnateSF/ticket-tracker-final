FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# 🔥 Inyectamos el puerto dinámico de Railway de forma segura
CMD sh -c "gunicorn app:app -b 0.0.0.0:${PORT:-8080}"
