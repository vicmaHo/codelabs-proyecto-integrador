import sounddevice as sd
from scipy.io.wavfile import write
import speech_recognition as sr
import tempfile, os
import requests
import webbrowser
import re

import urllib

SRATE = 16000
DUR = 6

r = sr.Recognizer()

print("Asistente iniciado. Di 'salir' para terminar.")


def grabar_audio(duracion=DUR):
    print("Escuchando...")
    audio = sd.rec(int(duracion * SRATE), samplerate=SRATE, channels=1, dtype='int16')
    sd.wait()
    tmp_wav = tempfile.mktemp(suffix=".wav")
    write(tmp_wav, SRATE, audio)
    return tmp_wav


def reconocer_audio(tmp_wav):
    try:
        with sr.AudioFile(tmp_wav) as source:
            data = r.record(source)
        texto = r.recognize_google(data, language="es-ES").lower()
        return texto
    except sr.UnknownValueError:
        return ""
    except sr.RequestError as e:
        print("Error en el reconocimiento:", e)
        return ""
    finally:
        if os.path.exists(tmp_wav):
            os.remove(tmp_wav)


def escuchar_respuesta(prompt="Di sí o no", duracion=3):
    print(prompt)
    tmp_wav = grabar_audio(duracion)
    texto = reconocer_audio(tmp_wav)
    if texto:
        print("Dijiste:", texto)
    else:
        print("No se entendió el audio.")
    return texto


# FUNCIONES PRINCIPALES


# YOUTUBE Videos
def buscar_youtube(query):
    print(f"Buscando en YouTube: {query}...")
    url = "https://www.youtube.com/results?search_query=" + urllib.parse.quote(query)
    respuesta = requests.get(url).text

    video_ids = re.findall(r"watch\?v=(.{11})", respuesta)

    video_ids = list(dict.fromkeys(video_ids))[:3]

    resultados = []
    for vid in video_ids:
        video_url = f"https://www.youtube.com/watch?v={vid}"
        match = re.search(rf'"videoId":"{vid}".*?"title":{{"runs":\[{{"text":"(.*?)"}}', respuesta)
        titulo = match.group(1) if match else "Video sin título"
        resultados.append((titulo, video_url))

    return resultados


def elegir_video(resultados):
    print("\nResultados encontrados:")
    for i, (titulo, _) in enumerate(resultados, 1):
        print(f"{i}. {titulo}")

    resp = escuchar_respuesta("Di 'pon el 1', 'pon el 2', 'pon el 3' o 'cancelar'", duracion=4)

    if "uno" in resp or "1" in resp or "primero" in resp:
        webbrowser.open(resultados[0][1])
        print("Reproduciendo:", resultados[0][0])
    elif "dos" in resp or "2" in resp or "segundo" in resp and len(resultados) > 1:
        webbrowser.open(resultados[1][1])
        print("Reproduciendo:", resultados[1][0])
    elif "tres" in resp or "3" in resp or "tercero" in resp and len(resultados) > 2:
        webbrowser.open(resultados[2][1])
        print("Reproduciendo:", resultados[2][0])
    elif "cancelar" in resp:
        print("Cancelado.")
    else:
        print("No entendí tu elección.")

# PARTIDOS resultados
def obtener_resultado(equipo1, equipo2, temporada="2024-2025"):
    url = f"https://www.thesportsdb.com/api/v1/json/3/searchevents.php?e={equipo1}_vs_{equipo2}&s={temporada}"

    try:
        respuesta = requests.get(url)
        data = respuesta.json()

        if not data.get("event"):
            print("No encontré ese partido en la base de datos.")
            return

        partido = data["event"][0]
        home = partido.get("strHomeTeam")
        away = partido.get("strAwayTeam")
        score = partido.get("intHomeScore"), partido.get("intAwayScore")
        video = partido.get("strVideo")

        print(f"Resultado: {home} {score[0]} - {score[1]} {away}")
        print(f"fuentes: {url}")

        if video:
            while True:
                resp = escuchar_respuesta("¿Quieres ver el resumen del partido?", duracion=3)
                if "si" in resp or "sí" in resp:
                    print("Abriendo resumen...")
                    webbrowser.open(video)
                    break
                elif "no" in resp:
                    print("No se abrirá el resumen")
                    break
                else:
                    print("No entendí tu respuesta. repite por favor (di 'Sí' o 'No')")
        else:
                print("No hay video disponible para este partido.")

    except Exception as e:
        print("Error al consultar la API:", e)


# LOOP PRINCIPAL
while True:
    tmp_wav = grabar_audio()
    cmd = reconocer_audio(tmp_wav)

    if not cmd:
        print("No se entendió el comando, intenta de nuevo.")
        continue

    print("Dijiste:", cmd)

    if "salir" in cmd:
        print("¡Hasta luego!")
        break

    elif "hola" in cmd:
        print("¡Hola, bienvenido al curso!")

    elif "mostrar clima" in cmd:
        try:
            respuesta = requests.get("https://wttr.in/bogota?format=3")
            if respuesta.status_code == 200:
                print("Clima actual en Bogotá:", respuesta.text)
            else:
                print("No se pudo obtener el clima.")
        except Exception as e:
            print("Error al obtener clima:", e)

    elif "abrir youtube" in cmd:
        print("Abriendo YouTube...")
        webbrowser.open("https://www.youtube.com/")

    elif "abrir chat gpt" in cmd:
        print("Abriendo ChatGPT...")
        webbrowser.open("https://chat.openai.com/")
    elif "buscar en youtube" in cmd:
        query = cmd.replace("buscar en youtube", "").strip()
        if query:
            resultados = buscar_youtube(query)
            if resultados:
                elegir_video(resultados)
            else:
                print("No encontré resultados en YouTube.")
        else:
            print("No especificaste qué buscar.")
    elif "cuánto quedó el partido" in cmd:
        match = re.search(r"entre (.+?) (?:y|contra) (.+)", cmd, re.IGNORECASE)
        if match:
            equipo1 = match.group(1).strip()
            equipo2 = match.group(2).strip()
            print(f"Buscando resultado entre {equipo1} y {equipo2}...")
            obtener_resultado(equipo1, equipo2)
        else:
            print("No pude identificar los equipos. Di: 'entre EQUIPO1 y EQUIPO2'.")

    else:
        print("Comando no reconocido.")