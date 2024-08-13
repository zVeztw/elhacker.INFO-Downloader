import os
import requests
from bs4 import BeautifulSoup
import urllib.parse
import webbrowser

def print_ascii_art():
    print("▄▄▄ .▄▄▌   ▄ .▄ ▄▄▄·  ▄▄· ▄ •▄ ▄▄▄ .▄▄▄     ▪   ▐ ▄ ·▄▄▄      ")
    print("▀▄.▀·██•  ██▪▐█▐█ ▀█ ▐█ ▌▪█▌▄▌▪▀▄.▀·▀▄ █·   ██ •█▌▐█▐▄▄·▪     ")
    print("▐▀▀▪▄██▪  ██▀▐█▄█▀▀█ ██ ▄▄▐▀▀▄·▐▀▀▪▄▐▀▀▄    ▐█·▐█▐▐▌██▪  ▄█▀▄ ")
    print("▐█▄▄▌▐█▌▐▌██▌▐▀▐█ ▪▐▌▐███▌▐█.█▌▐█▄▄▌▐█•█▌   ▐█▌██▐█▌██▌.▐█▌.▐▌")
    print(" ▀▀▀ .▀▀▀ ▀▀▀ · ▀  ▀ ·▀▀▀ ·▀  ▀ ▀▀▀ .▀  ▀ ▀ ▀▀▀▀▀ █▪▀▀▀  ▀█▄▀▪")

def get_file_links(course_url):
    response = requests.get(course_url)
    soup = BeautifulSoup(response.content, 'html.parser')
    file_links = []
    subfolders = []
    
    for a in soup.find_all('a', href=True):
        href = a['href']
        if not href.endswith('/') and not href.startswith('?'):
            file_links.append(course_url + href)
        elif href.endswith('/') and 'folder2.png' in str(a.find_previous('img')):
            subfolders.append(course_url + href)
    
    return file_links, subfolders

def get_file_date(url):
    response = requests.head(url)
    if 'Last-Modified' in response.headers:
        return response.headers['Last-Modified']
    else:
        return "Fecha no disponible"

def download_files(file_links, course_name):
    if not os.path.exists(course_name):
        os.makedirs(course_name)
    
    for idx, link in enumerate(file_links):
        file_name = urllib.parse.unquote(link.split('/')[-1])
        file_path = os.path.join(course_name, file_name)
        
        os.system(f"wget -O '{file_path}' '{link}'")
        print(f"Downloaded {file_name}")

def process_course(course_url, course_name, depth=0, max_depth=5):
    if depth > max_depth:
        print(f"Reached max depth of {max_depth}, stopping recursion.")
        return
    
    print(f"Processing course: {course_name} at depth {depth}")
    file_links, subfolders = get_file_links(course_url)
    
    if file_links:
        first_file_date = get_file_date(file_links[0])
        if first_file_date != "Fecha no disponible":
            from datetime import datetime
            file_date = datetime.strptime(first_file_date, '%a, %d %b %Y %H:%M:%S %Z')
            if file_date.year <= 2022:
                user_input = input(f"Este curso es algo viejo ({first_file_date}), ¿desea descargarlo? s/n: ")
                if user_input.lower() != 's':
                    return
        
        print(f"Todo listo para descargar: {course_name} ({first_file_date})")
        download_files(file_links, course_name)
    
    for subfolder in subfolders:
        subfolder_name = urllib.parse.unquote(subfolder.split('/')[-2])
        process_course(subfolder, os.path.join(course_name, subfolder_name), depth + 1, max_depth)

def get_courses(page_url):
    response = requests.get(page_url)
    soup = BeautifulSoup(response.content, 'html.parser')
    courses = []
    
    for a in soup.find_all('a', href=True):
        href = a['href']
        if href.endswith('/') and 'folder2.png' in str(a.find_previous('img')):
            course_name = urllib.parse.unquote(href.split('/')[-2])
            courses.append((course_name, page_url + href))
    
    return courses

def list_courses(courses, page):
    print(f"Page {page}")
    for idx, (course_name, course_url) in enumerate(courses):
        print(f"{idx + 1} - {course_name}")

def check_course(course_url):
    file_links, subfolders = get_file_links(course_url)
    print(f"Contenido de {course_url}:")
    for file_link in file_links:
        print(f"Archivo: {urllib.parse.unquote(file_link.split('/')[-1])}")
    for subfolder in subfolders:
        print(f"Carpeta: {urllib.parse.unquote(subfolder.split('/')[-2])}")

def get_books(page_url):
    response = requests.get(page_url)
    soup = BeautifulSoup(response.content, 'html.parser')
    books = []
    
    for a in soup.find_all('a', href=True):
        href = a['href']
        if href.endswith('.pdf'):
            book_name = urllib.parse.unquote(href.split('/')[-1])
            books.append((book_name, page_url + href))
    
    return books

def list_books(books, page):
    print(f"Page {page}")
    for idx, (book_name, book_url) in enumerate(books):
        print(f"{idx + 1} - {book_name}")

def open_pdf(pdf_url):
    response = requests.get(pdf_url)
    pdf_path = "/tmp/temp_pdf.pdf"
    with open(pdf_path, 'wb') as f:
        f.write(response.content)
    webbrowser.open_new(pdf_path)

def main():
    print_ascii_art()
    choice = input("¿Qué quieres descargar?\n1. Cursos\n2. Libros\nElige una opción: ")
    
    if choice == '1':
        base_url = "https://elhacker.info/Cursos/"
        page = 1
        while True:
            courses = get_courses(base_url)
            list_courses(courses[(page-1)*10:page*10], page)
            
            user_input = input("Enter 'page X' to see more courses, 'get Y' to download a course, or 'check Y' to list contents of a course: ")
            if user_input.startswith("page"):
                page = int(user_input.split()[1])
            elif user_input.startswith("get"):
                course_idx = int(user_input.split()[1]) - 1
                course_name, course_url = courses[course_idx]
                process_course(course_url, course_name)
                print("Descarga completada.")
                break
            elif user_input.startswith("check"):
                course_idx = int(user_input.split()[1]) - 1
                course_name, course_url = courses[course_idx]
                check_course(course_url)
    elif choice == '2':
        base_url = "https://elhacker.info/ebooks%20Joas/"
        page = 1
        while True:
            books = get_books(base_url)
            list_books(books[(page-1)*10:page*10], page)
            
            user_input = input("Enter 'page X' to see more books or 'open Y' to open a book: ")
            if user_input.startswith("page"):
                page = int(user_input.split()[1])
            elif user_input.startswith("open"):
                book_idx = int(user_input.split()[1]) - 1
                book_name, book_url = books[book_idx]
                open_pdf(book_url)
                break

if __name__ == "__main__":
    main()
