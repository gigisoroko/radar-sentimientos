import requests
import pandas as pd
from pysentimiento import create_analyzer
import feedparser
import datetime
import io

# 1. Cargar el cerebro de IA
print("🧠 Cargando inteligencia artificial...")
analyzer = create_analyzer(task="sentiment", lang="es")

USUARIOS_X = ["LuisCaputoAR", "BancoCentral_AR", "pablowniczky", "carodiaz10", "madorni"]

INSTANCIAS_NITTER = [
    "xcancel.com", 
    "nitter.privacyredirect.com", 
    "nitter.space", 
    "nuku.trabun.org"
]

def clasificar_categoria(texto):
    t = texto.lower()
    if any(x in t for x in ["dolar", "mep", "ccl", "blue"]): return "FX"
    if any(x in t for x in ["bono", "al30", "gd30", "tasa", "lecap"]): return "BONOS"
    if any(x in t for x in ["merval", "accion", "galicia", "ypf", "pampa"]): return "EQUITY"
    return "GENERAL"

def extraer_todo_pro():
    ahora = datetime.datetime.now().strftime('%H:%M:%S')
    print(f"\n--- 📡 INICIANDO ESCANEO DE MERCADO [{ahora}] ---")
    
    noticias_x = []
    noticias_medios = []

    # DISFRAZ DE NAVEGADOR (Clave para evitar el bloqueo)
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }

    # --- PARTE A: X (TWITTER) ---
    print("\n🔍 REVISANDO X (TWITTER):")
    for user in USUARIOS_X:
        user_found = False
        for inst in INSTANCIAS_NITTER:
            try:
                url = f"https://{inst}/{user}/rss"
                # Bajamos el contenido con el disfraz
                response = requests.get(url, headers=headers, timeout=10)
                
                if response.status_code == 200:
                    # Parseamos el texto descargado
                    feed = feedparser.parse(io.BytesIO(response.content))
                    
                    if len(feed.entries) > 0:
                        for entry in feed.entries[:5]:
                            noticias_x.append({
                                "titulo": f"@{user}: {entry.title[:120]}...",
                                "fuente": "X_LIVE",
                                "url": entry.link,
                                "fecha": str(datetime.datetime.now()),
                                "categoria": clasificar_categoria(entry.title),
                            })
                        print(f"  ✅ @{user}: ONLINE (vía {inst})")
                        user_found = True
                        break 
                else:
                    continue # Probar siguiente instancia si el status no es 200
            except:
                continue
        if not user_found:
            print(f"  ❌ @{user}: OFFLINE (Bloqueo de bot persistente)")

    # --- PARTE B: MEDIOS TRADICIONALES ---
    print("\n🔍 REVISANDO MEDIOS (CITY PRESS):")
    rss_diarios = {
        "El Cronista": "https://www.cronista.com/rss/economia.xml", 
        "Ámbito": "https://www.ambito.com/rss/pages/finanzas.xml"
    }
    
    for nombre, url in rss_diarios.items():
        try:
            # Los diarios no suelen bloquear, pero usamos el mismo método por seguridad
            resp = requests.get(url, headers=headers, timeout=10)
            feed = feedparser.parse(io.BytesIO(resp.content))
            count_diario = 0
            for entry in feed.entries[:12]:
                noticias_medios.append({
                    "titulo": entry.title,
                    "fuente": "CITY_PRESS",
                    "url": entry.link,
                    "fecha": entry.published if 'published' in entry else str(datetime.datetime.now()),
                    "categoria": clasificar_categoria(entry.title),
                })
                count_diario += 1
            print(f"  ✅ {nombre}: {count_diario} noticias encontradas.")
        except:
            print(f"  ⚠️ {nombre}: No se pudo conectar.")

    # --- PARTE C: PROCESAMIENTO ---
    total_data = noticias_x + noticias_medios
    
    if total_data:
        print("\n🧠 Analizando sentimiento de los eventos...")
        for n in total_data:
            res = analyzer.predict(n["titulo"])
            n["sentimiento"] = res.output
            n["impacto"] = 85 if n["fuente"] == "X_LIVE" else 60

        df = pd.DataFrame(total_data)
        df.to_csv("noticias_argentinas.csv", index=False)
        print(f"\n✅ TOTAL PROCESADO: {len(total_data)}")
    else:
        print("\n❌ ERROR: No se pudo recolectar información.")

if __name__ == "__main__":
    extraer_todo_pro()