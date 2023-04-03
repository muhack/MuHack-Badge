import requests
from random import randint

url = "http://192.168.1.187/drawVector"

for i in range(100):
    # Genera valori casuali per i parametri "x", "y", "z" e "max_value"
    # NOTA: assicurati che i valori siano numeri interi con segno
    x = randint(-100, 100)
    y = randint(-100, 100)
    z = randint(-100, 100)
    max_value = randint(-100, 100)

    # Aggiungi i parametri all'URL
    params = {
        "x": x,
        "y": y,
        "z": z,
        "max_value": max_value
    }

    # Esegui la richiesta HTTP GET
    response = requests.get(url, params=params)

    # Stampa la risposta
    print(response.text)
