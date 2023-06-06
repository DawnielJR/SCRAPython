from tkinter import Tk, Label, Entry, Button
from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import tkinter.messagebox as messagebox
from datetime import datetime
import re

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
                driver.get(news_url)
                driver.implicitly_wait(20)

                # Obtener el contenido HTML de la página de la noticia
                news_html = driver.page_source

                # Crear un objeto BeautifulSoup para analizar el HTML de la noticia
                news_soup = BeautifulSoup(news_html, "lxml")

                # Encontrar los subtítulos de la noticia
                subtitles = news_soup.find_all(["h1", "h2", "h3", "h4"])

                # Extraer el texto de los subtítulos
                subtitle_text = [subtitle.get_text(strip=True) for subtitle in subtitles]

                result["subtitles"] = subtitle_text

            results.append(result)

    # Cerrar el driver de Chrome
    driver.quit()

    # Guardar los resultados en un archivo o realizar cualquier otro procesamiento necesario
    # Modificar la sección de guardar los resultados en el archivo
    with open("resultados-2.txt", "w", encoding="utf-8") as file:
        for result in results:
            file.write(f"Título: {result.get('title', '')}\n")

            # Escribir la URL como enlace HTML
            url = result.get('url', '')
            if url:
                file.write(f"URL: {url}\n")
            else:
                file.write("URL: No disponible\n")

            # Escribir los extractos
            subtitle_text = result.get('subtitles', [])
            if subtitle_text:
                file.write(f"Extracto: {', '.join(subtitle_text)}\n")
            else:
                file.write("Extracto: No disponible\n")

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
