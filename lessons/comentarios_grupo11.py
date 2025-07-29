# ------------------------------------------------------------
# Web Scraping con Beautiful Soup
# ------------------------------------------------------------

# Importamos las librerías necesarias
from bs4 import BeautifulSoup
from datetime import datetime
import requests
import time

# -----------------------------
# Paso 1: Hacer una petición GET a la página del Senado
# -----------------------------
req = requests.get('http://www.ilga.gov/senate/default.asp')
src = req.text  # Obtenemos el contenido HTML
soup = BeautifulSoup(src, 'lxml')  # Parseamos el HTML usando lxml

# -----------------------------
# Paso 2: Encontrar todos los enlaces con clase 'mainmenu'
# -----------------------------
# Esto retorna todos los elementos <a> que tienen la clase CSS 'mainmenu'
mainmenu_links = soup.select("a.mainmenu")

# -----------------------------
# Paso 3: Extraer los href (URLs) de esos enlaces
# -----------------------------
hrefs_mainmenu = [link['href'] for link in mainmenu_links]

# -----------------------------
# Paso 4: Obtener información de senadores
# -----------------------------
req = requests.get('http://www.ilga.gov/senate/default.asp?GA=98')
src = req.text
soup = BeautifulSoup(src, "lxml")

# Lista para almacenar la información de los senadores
members = []

# Extraemos las filas de la tabla HTML (anidadas en 'tr tr tr')
rows = soup.select('tr tr tr')

# Filtramos solo las filas que contienen datos (tienen celdas con clase 'detail')
rows = [row for row in rows if row.select('td.detail')]

# Iteramos sobre cada fila válida
for row in rows:
    detail_cells = row.select('td.detail')  # celdas con información
    row_data = [cell.text for cell in detail_cells]  # solo el texto

    name = row_data[0]        # nombre del senador
    district = int(row_data[3])  # número de distrito
    party = row_data[4]       # partido

    # Obtenemos el segundo enlace <a> del row, que lleva a los proyectos
    href = row.select('a')[1]['href']
    full_path = "http://www.ilga.gov/senate/" + href + "&Primary=True"

    # Guardamos la información como tupla
    senator = (name, district, party, full_path)
    members.append(senator)

# -----------------------------
# Paso 5: Modularizar el código anterior en una función
# -----------------------------
def get_members(url):
    req = requests.get(url)
    src = req.text
    soup = BeautifulSoup(src, "lxml")
    members = []

    rows = soup.select('tr tr tr')
    rows = [row for row in rows if row.select('td.detail')]

    for row in rows:
        detail_cells = row.select('td.detail')
        row_data = [cell.text for cell in detail_cells]

        name = row_data[0]
        district = int(row_data[3])
        party = row_data[4]

        href = row.select('a')[1]['href']
        full_path = "http://www.ilga.gov/senate/" + href + "&Primary=True"

        senator = (name, district, party, full_path)
        members.append(senator)

    return members

# Usamos la función para obtener senadores de la legislatura 98
url = 'http://www.ilga.gov/senate/default.asp?GA=98'
senate_members = get_members(url)
print(f"Total de senadores encontrados: {len(senate_members)}")

# -----------------------------
# Paso 6: Crear función para obtener proyectos de ley
# -----------------------------
def get_bills(url):
    src = requests.get(url).text
    soup = BeautifulSoup(src, "lxml")
    rows = soup.select('tr tr tr')
    bills = []

    for row in rows:
        # Seleccionamos solo las celdas que tengan clase 'billlist'
        cells = row.select('td.billlist')

        if len(cells) == 5:  # solo filas completas
            row_text = [cell.text.strip() for cell in cells]

            bill_id = row_text[0]
            description = row_text[1]
            chamber = row_text[2]
            last_action = row_text[3]
            last_action_date = row_text[4]

            bill = (bill_id, description, chamber, last_action, last_action_date)
            bills.append(bill)

    return bills

# -----------------------------
# Paso 7: Probar con el primer senador
# -----------------------------
if len(senate_members) > 0:
    test_url = senate_members[0][3]
    print("\nPrimeros 5 proyectos del primer senador:")
    print(get_bills(test_url)[:5])
else:
    print("No se encontraron senadores para probar los proyectos.")

# -----------------------------
# Paso 8: Crear diccionario con proyectos por distrito
# -----------------------------
bills_dict = {}

for member in senate_members[:5]:  # solo los primeros 5 para no saturar el sitio
    district = member[1]
    bills_dict[district] = get_bills(member[3])
    time.sleep(1)  # Pausa de 1 segundo entre solicitudes

# Mostramos cuántos proyectos hay para un distrito específico
if 52 in bills_dict:
    print(f"\nTotal de proyectos del distrito 52: {len(bills_dict[52])}")
else:
    print("El distrito 52 no está en los primeros 5 senadores.")
