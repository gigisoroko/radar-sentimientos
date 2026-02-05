# Usamos una imagen de Python oficial (Segura y estable)
FROM python:3.11-slim

# Creamos una carpeta para el proyecto
WORKDIR /app

# Copiamos los archivos
COPY requirements.txt .

# Instalamos las librerías
RUN pip install --no-cache-dir -r requirements.txt

# Copiamos el resto del código
COPY . .

# Comando para encender el radar
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
