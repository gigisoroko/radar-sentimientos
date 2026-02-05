from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
from pysentimiento import create_analyzer
import os

# --- INICIALIZACIÓN ---
app = FastAPI()

# Configuración de CORS para que el Radar de React (puerto 3000) pueda leer los datos
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

CSV_FILE = "noticias_argentinas.csv"

# Cargamos la IA de sentimientos (esto puede tardar unos segundos)
print("⌛ Cargando IA de sentimientos (pysentimiento)...")
analyzer = create_analyzer(task="sentiment", lang="es")
print("✅ IA lista para recibir notificaciones desde MacroDroid.")

# --- RUTA 1: RECIBIR DATOS DEL CELULAR (WEBHOOK) ---
@app.post("/webhook")
async def recibir_tweet(request: Request):
    try:
        data = await request.json()
        texto_sucio = data.get("texto", "").strip()

        # Filtro de seguridad: Ignorar si la variable no se procesó en el celular
        if not texto_sucio or "{notificacion}" in texto_sucio or "[not_text]" in texto_sucio:
            print("⚠️ Petición ignorada: El texto está vacío o la variable no se reemplazó.")
            return {"status": "ignored"}

        print(f"\n📡 NOTIFICACIÓN RECIBIDA: {texto_sucio}")

        # Análisis de sentimiento con la IA
        res = analyzer.predict(texto_sucio)
        sentimiento = res.output # Esto devuelve 'POS', 'NEG' o 'NEU'

        # Preparar el dato para el CSV
        nuevo_dato = {
            "title": texto_sucio,
            "sentiment": sentimiento,
            "date": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        # Guardar en el CSV (si no existe, crea la cabecera)
        df_nuevo = pd.DataFrame([nuevo_dato])
        header_needed = not os.path.exists(CSV_FILE)
        df_nuevo.to_csv(CSV_FILE, mode='a', index=False, header=header_needed)

        print(f"✅ Análisis: {sentimiento} | Guardado en CSV.")
        return {"status": "success", "analisis": sentimiento}

    except Exception as e:
        print(f"❌ Error procesando el webhook: {e}")
        return {"status": "error", "message": str(e)}

# --- RUTA 2: ENVIAR DATOS AL RADAR (REACT) ---
@app.get("/api/noticias")
def get_noticias():
    try:
        if not os.path.exists(CSV_FILE):
            return []

        # Leemos el CSV
        df = pd.read_csv(CSV_FILE)

        # Limpieza crucial: Reemplaza valores vacíos (NaN) por texto vacío
        # Esto evita el error "Out of range float values are not JSON compliant"
        df = df.fillna("")

        # Convertimos a formato lista de diccionarios para React
        return df.to_dict(orient="records")

    except Exception as e:
        print(f"❌ Error al leer el CSV para React: {e}")
        return []

# Para ejecutarlo manual si no usás el comando