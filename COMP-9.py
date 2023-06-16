from tkinter import Tk, Label, Entry, Button
from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import tkinter.messagebox as messagebox
from datetime import datetime
import re
import requests
import newspaper
from collections import Counter

def search_keywords():
    # Obtener las palabras clave ingresadas en la caja de texto
    keywords = keyword_entry.get()

    # Ruta del driver de Chrome
    chromedriver_path = "C:/chromedriver_win32/chromedriver.exe"

    # Opciones del driver de Chrome
    options = webdriver.ChromeOptions()

    # Inicializar el driver de Chrome
    driver = webdriver.Chrome(service_log_path='NUL', options=options)

    # Lista para almacenar los resultados
    results = []

    # Realizar la búsqueda en las tres primeras páginas
    num_paginas = 3
    for pagina in range(1, num_paginas + 1):
        # Calcular el índice de inicio de la página actual
        start_index = (pagina - 1) * 10

        # Navegar a la página de Google
        driver.get(f"https://www.google.com/search?q={keywords}&start={start_index}")

        # Esperar a que cargue la página de resultados
        driver.implicitly_wait(20)

        # Obtener el contenido HTML de la página
        html = driver.page_source

        # Crear un objeto BeautifulSoup para analizar el HTML
        soup = BeautifulSoup(html, "lxml")

        # Encontrar los elementos de resultados (títulos, URLs y fechas)
        results_html = soup.select("div.g")

        # Iterar sobre los resultados encontrados
        for result_html in results_html:
            result = {}

            title_element = result_html.select_one("h3")
            if title_element:
                result["title"] = title_element.get_text(strip=True)

            url_element = result_html.select_one("a")
            if url_element:
                url = url_element["href"]
                if "youtube.com" in url or url.endswith(".pdf"):
                    continue  # Omitir enlaces de YouTube y archivos PDF
                result["url"] = url

            date_element = result_html.select_one('div > div > div > span')
            if date_element and date_element.has_attr("aria-label"):
                date_str = date_element["aria-label"].replace("Fecha de publicación: ", "")
                date_match = re.search(r"\d{1,2} \w+ \d{4}", date_str)
                if date_match:
                    date_str = date_match.group()
                    try:
                        date = datetime.strptime(date_str, "%d %B %Y")
                        result["date"] = date
                    except ValueError:
                        pass  # Ignorar si no se puede convertir la fecha

            # Acceder a la página de la noticia

            if "url" in result:
                news_url = result["url"]

                # Descargar el contenido HTML de la página de la noticia
                response = requests.get(news_url, verify=False)  # Desactivar verificación del certificado SSL
                html = response.text

                # Crear un objeto Article de newspaper3k y analizar el contenido HTML descargado
                article = newspaper.Article(news_url)
                article.set_html(html)
                article.parse()

                # Obtener el título completo de la noticia
                result["title_full"] = article.title

                # Obtener los párrafos de la noticia
                paragraphs = article.text.split("\n\n")

                # Buscar los dos párrafos que contengan la mayor cantidad de palabras clave
                keyword_count_list = []

                for paragraph in paragraphs:
                    paragraph_lower = paragraph.lower()
                    keyword_count = sum(keyword in paragraph_lower for keyword in keywords)
                    keyword_count_list.append((keyword_count, paragraph))

                keyword_count_list.sort(reverse=True)

                result["extracts"] = [p for _, p in keyword_count_list[:2]]

            results.append(result)

    # Cerrar el driver de Chrome
    driver.quit()

    # Guardar los resultados en un archivo o realizar cualquier otro procesamiento necesario
    # Modificar la sección de guardar los resultados en el archivo
    with open("resultados-2.txt", "w", encoding="utf-8") as file:
        for result in results:
            file.write(f"Título: {result.get('title', '')}\n")

            # Escribir el título completo de la noticia
            title_full = result.get('title_full', '')
            if title_full:
                file.write(f"Título completo: {title_full}\n")
            else:
                file.write("Título completo: No disponible\n")

            # Escribir la URL como enlace HTML
            url = result.get('url', '')
            if url:
                file.write(f"URL: {url}\n")
            else:
                file.write("URL: No disponible\n")

            # Escribir los extractos
            extracts = result.get('extracts', [])
            if extracts:
                file.write("Extractos:\n")
                for extract in extracts:
                    file.write(f" - {extract}\n")
            else:
                file.write("Extractos: No disponibles\n")

            file.write("-" * 50 + "\n")

    # Mostrar los resultados
    messagebox.showinfo("Resultados", f"Se encontraron {len(results)} resultados.")

# Crear la ventana de la aplicación
window = Tk()

# Configurar la ventana
window.title("Búsqueda de Noticias")
window.geometry("400x150")

# Etiqueta y caja de texto para ingresar las palabras clave
keyword_label = Label(window, text="Palabras clave:")
keyword_label.pack()
keyword_entry = Entry(window)
keyword_entry.pack()

# Botón de búsqueda
search_button = Button(window, text="Buscar", command=search_keywords)
search_button.pack()

# Ejecutar la aplicación
window.mainloop()
