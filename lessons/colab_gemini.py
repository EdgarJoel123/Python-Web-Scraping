# Importamos las librerías necesarias
from bs4 import BeautifulSoup
from datetime import datetime
import requests
import time

# Función para obtener los senadores desde una URL específica
def get_members(url):
    # Hacemos una solicitud GET a la URL
    req = requests.get(url)
    # Obtenemos el contenido HTML de la respuesta
    src = req.text
    # Analizamos el HTML con BeautifulSoup y el parser 'lxml'
    soup = BeautifulSoup(src, "lxml")

    # Lista para guardar los datos de los senadores
    members = []

    # Seleccionando todas las filas con la clase 'gridTable' que contienen los datos de los senadores
    # Basado en la inspección del código fuente de la página proporcionada
    rows = soup.select('table.gridTable tr')

    # Iterando sobre cada fila, saltando la fila de encabezado
    for row in rows[1:]: # Saltar la primera fila (encabezado)
        # Seleccionando todas las celdas con la clase 'detail' dentro de la fila actual
        detail_cells = row.select('td.detail')

        # Asegurarse de tener suficientes celdas antes de continuar
        if len(detail_cells) >= 5:
            # Extrayendo el texto de cada celda
            row_data = [cell.text.strip() for cell in detail_cells]

            # Extrayendo los datos específicos
            name = row_data[0]                  # Nombre del senador
            district = int(row_data[3])        # Número del distrito
            party = row_data[4]                # Partido

            # Obtenemos el segundo enlace <a> de la fila (el que apunta a los proyectos de ley)
            # Verificar si hay suficientes enlaces
            links = row.select('a')
            if len(links) > 1:
                href = links[1]['href']
                # Creamos la URL completa con el parámetro para solo los proyectos primarios
                full_path = "http://www.ilga.gov/senate/" + href + "&Primary=True"

                # Guardamos los datos como tupla
                senator = (name, district, party, full_path)
                # Añadimos la tupla a la lista
                members.append(senator)

    # Retornamos la lista de senadores
    return members

# Usamos la función con la URL del senado de Illinois
url = 'http://www.ilga.gov/senate/default.asp?GA=98'
senate_members = get_members(url)

# Mostramos cuántos senadores se extrajeron
print(f"Total de senadores encontrados: {len(senate_members)}")

# Función para obtener los proyectos de ley desde una URL de un senador
def get_bills(url):
    # Hacemos la solicitud y obtenemos el contenido HTML
    src = requests.get(url).text
    # Parseamos con BeautifulSoup (el parser por defecto es 'html.parser')
    soup = BeautifulSoup(src, "lxml")

    # Seleccionando todas las filas potenciales
    rows = soup.select('tr tr tr')
    bills = []

    # Iterando sobre las filas para encontrar aquellas que representan proyectos de ley
    for row in rows:
        # Buscando las celdas con la clase 'billlist'
        cells = row.select('td.billlist')

        # Solo procesar las filas que tienen exactamente 5 columnas (para evitar encabezados o filas vacías)
        if len(cells) == 5:
            # Extrayendo el texto de cada celda
            row_text = [cell.text.strip() for cell in cells]

            # Extrayendo la información específica
            bill_id = row_text[0]
            description = row_text[1]
            chamber = row_text[2]
            last_action = row_text[3]
            last_action_date = row_text[4]

            # Creando una tupla con los datos del proyecto de ley
            bill = (bill_id, description, chamber, last_action, last_action_date)
            # Añadiendo a la lista
            bills.append(bill)

    return bills

# Probamos con el primer senador
if senate_members:
    test_url = senate_members[0][3]
    print("\nPrimeros 5 proyectos del primer senador:")
    print(get_bills(test_url)[:5])
else:
    print("\nNo se encontraron senadores para probar la obtención de proyectos de ley.")

# Diccionario para guardar los proyectos por distrito
bills_dict = {}

# Iteramos por los primeros 5 senadores (puedes quitar el [:5] para todos)
if senate_members:
    for member in senate_members[:5]:
        district = member[1]
        bills_dict[district] = get_bills(member[3])
        # Esperamos 1 segundo para no sobrecargar el servidor
        time.sleep(1)

    # Mostramos cuántos proyectos tiene un distrito en específico
    # Verificar si el distrito 52 existe en el diccionario
    if 52 in bills_dict:
        print(f"\nTotal de proyectos del distrito 52: {len(bills_dict[52])}")
    else:
        print("\nEl distrito 52 no se encontró entre los senadores procesados.")
else:
    print("\nNo se encontraron senadores para obtener sus proyectos de ley.")