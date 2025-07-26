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

    # Seleccionamos todas las filas anidadas 'tr tr tr' que representan posibles filas con datos
    rows = soup.select('tr tr tr')
    # Filtramos las filas que sí contienen datos (aquellas que tienen al menos un 'td.detail')
    rows = [row for row in rows if row.select('td.detail')]

    # Iteramos sobre cada fila válida
    for row in rows:
        # Seleccionamos solo las celdas que tengan la clase 'detail'
        detail_cells = row.select('td.detail')
        # Extraemos el texto de cada celda
        row_data = [cell.text.strip() for cell in detail_cells]

        # Extraemos los datos específicos
        name = row_data[0]                  # Nombre del senador
        district = int(row_data[3])        # Número del distrito
        party = row_data[4]                # Partido

        # Obtenemos el segundo enlace <a> de la fila (el que apunta a los proyectos de ley)
        href = row.select('a')[1]['href']

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
    # Parseamos con BeautifulSoup (parser por defecto es 'html.parser')
    soup = BeautifulSoup(src, "lxml")

    # Seleccionamos todas las filas potenciales
    rows = soup.select('tr tr tr')
    bills = []

    # Iteramos sobre las filas para encontrar aquellas que representan proyectos de ley
    for row in rows:
        # Buscamos las celdas con clase 'billlist'
        cells = row.select('td.billlist')

        # Solo procesamos las filas que tienen exactamente 5 columnas (para evitar encabezados o vacíos)
        if len(cells) == 5:
            # Extraemos el texto de cada celda
            row_text = [cell.text.strip() for cell in cells]

            # Extraemos la información específica
            bill_id = row_text[0]
            description = row_text[1]
            chamber = row_text[2]
            last_action = row_text[3]
            last_action_date = row_text[4]

            # Creamos una tupla con los datos del proyecto de ley
            bill = (bill_id, description, chamber, last_action, last_action_date)
            # Añadimos a la lista
            bills.append(bill)

    return bills

# Probamos con el primer senador
test_url = senate_members[0][3]
print("\nPrimeros 5 proyectos del primer senador:")
print(get_bills(test_url)[:5])

# Diccionario para guardar los proyectos por distrito
bills_dict = {}

# Iteramos por los primeros 5 senadores (puedes quitar el [:5] para todos)
for member in senate_members[:5]:
    district = member[1]
    bills_dict[district] = get_bills(member[3])
    # Esperamos 1 segundo para no sobrecargar el servidor
    time.sleep(1)

# Mostramos cuántos proyectos tiene un distrito en específico
print(f"\nTotal de proyectos del distrito 52: {len(bills_dict[52])}")
