import bs4
import requests
import pandas as pd
from datetime import datetime

def obtener_numero_paginas(url):
    resultado = requests.get(url)
    sopa = bs4.BeautifulSoup(resultado.text, "lxml")
    last_page_div = sopa.select_one(".lastPage.pageLink.d-flex.font-weight-bold")
    if last_page_div:
        return int(last_page_div['data-page'])
    return 1

def obtener_datos_pagina(url):
    resultado = requests.get(url)
    sopa = bs4.BeautifulSoup(resultado.text, "lxml")

    nombres = [nombre.getText() for nombre in sopa.select(".card-text")]
    ediciones = [edicion.getText().strip() for edicion in sopa.select(".prod-cat")]

    condiciones = sopa.select(".buying-options-table.pb-3")
    datos = []

    for index, condicion in enumerate(condiciones):
        temporal = condicion.select(".row.position-relative.align-center.py-2.m-auto")
        for temp in temporal:
            condicion_text_list = temp.select(".col-3.text-center.p-1")
            precio_list = temp.select(".col-2.text-center.p-1")
            
            # Manejo de datos faltantes
            condicion_text = condicion_text_list[1].getText().strip() if len(condicion_text_list) > 1 else "No disponible"
            precio = precio_list[2].getText() if len(precio_list) > 2 else "No disponible"
            
            # Manejo de nombres y ediciones con comprobación de longitud
            nombre = nombres[index] if index < len(nombres) else "No disponible"
            edicion = ediciones[index] if index < len(ediciones) else "No disponible"
            datos.append([nombre, edicion, condicion_text, precio, datetime.now().strftime("%Y-%m-%d")])

    return datos

def main(mytimer: func.TimerRequest) -> None:
    url_inicio = "https://www.trollandtoad.com/pokemon/all-singles/7088?Keywords=&min-price=&max-price=&items-pp=60&item-condition=&selected-cat=7088&sort-order=&page-no="
    url_fin = "&view=list&subproduct=0&Rarity=&CardType=&minHitPoints=&maxHitPoints="

    url_primera_pagina = url_inicio + "1" + url_fin
    max_paginas = obtener_numero_paginas(url_primera_pagina)
    
    datos_totales = []

    for i in range(max_paginas):
        url_pagina = url_inicio + str(i + 1) + url_fin
        print(f"Procesando página: {url_pagina}")
        datos_pagina = obtener_datos_pagina(url_pagina)
        datos_totales.extend(datos_pagina)

    df = pd.DataFrame(datos_totales, columns=["Nombre", "Edición", "Condición", "Precio", "Fecha"])
    df.to_csv("/path/to/store/datos_completos.csv", mode='a', header=False, index=False)
