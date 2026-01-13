FROM python:3.12

# Establecer el directorio de trabajo
WORKDIR /app

# Copiar requirements e instalarlos
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código del proyecto
COPY . .

# 👇 Aquí el cambio importante
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]
