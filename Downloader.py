import os
import requests
from bs4 import BeautifulSoup
import urllib.parse

# Este script fue hecho usando Copilot. (GPT-4)
# Esta función obtiene los enlaces de los videos y subcarpetas de un curso dado.
def get_video_links(course_url):
    response = requests.get(course_url)
    soup = BeautifulSoup(response.content, 'html.parser')
    video_links = []
    subfolders = []
    
    # Recorre todos los enlaces en la página y los clasifica en videos o subcarpetas.
    for a in soup.find_all('a', href=True):
        href = a['href']
        if href.endswith('.mp4'):
            video_links.append(course_url + href)
        elif href.endswith('/') and 'folder2.png' in str(a.find_previous('img')):
            subfolders.append(course_url + href)
    
    return video_links, subfolders

# Esta función obtiene la fecha de modificación de un archivo en línea.
def get_file_date(url):
    response = requests.head(url)
    if 'Last-Modified' in response.headers:
        return response.headers['Last-Modified']
    else:
        return "Fecha no disponible"

# Esta función descarga los videos de una lista de enlaces y los guarda en una carpeta específica.
def download_videos(video_links, course_name):
    if not os.path.exists(course_name):
        os.makedirs(course_name)
    
    # Descarga cada video y lo guarda con un nombre específico.
    for idx, link in enumerate(video_links):
        video_name = f"{idx + 1}-Capitulo {idx + 1}.mp4"
        video_path = os.path.join(course_name, video_name)
        
        os.system(f"wget -O '{video_path}' '{link}'")
        print(f"Downloaded {video_name}")

# Esta función procesa un curso, descargando sus videos y subcarpetas recursivamente.
def process_course(course_url, course_name):
    video_links, subfolders = get_video_links(course_url)
    
    # Si hay videos, verifica la fecha del primer video y pregunta al usuario si desea descargarlo si es antiguo.
    if video_links:
        first_video_date = get_file_date(video_links[0])
        if first_video_date != "Fecha no disponible":
            from datetime import datetime
            file_date = datetime.strptime(first_video_date, '%a, %d %b %Y %H:%M:%S %Z')
            if file_date.year <= 2022:
                user_input = input(f"Este curso es algo viejo ({first_video_date}), ¿desea descargarlo? s/n: ")
                if user_input.lower() != 's':
                    return
        
        download_videos(video_links, course_name)
    
    # Procesa recursivamente cada subcarpeta encontrada.
    for subfolder in subfolders:
        subfolder_name = urllib.parse.unquote(subfolder.split('/')[-2])
        process_course(subfolder, os.path.join(course_name, subfolder_name))

# Función principal que solicita al usuario el enlace del curso y lo procesa.
def main():
    while True:
        course_url = input("Introduce el enlace del curso: ")
        if not course_url.endswith('/'):
            course_url += '/'
        course_name = course_url.split('/')[-2]
        course_name = urllib.parse.unquote(course_name)
        
        process_course(course_url, course_name)
        break

if __name__ == "__main__":
    main()
