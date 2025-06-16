import pymssql
import requests

def fetch_book_details(key):
    url = f"https://openlibrary.org{key}.json"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error al obtener detalles para {key}: {response.status_code}")
        return None

def parse_book_data(raw_book, fixed_genre=None):
    print(f"Procesando libro: {raw_book.get('title', 'Sin título')}")
    title = raw_book.get('title', 'Sin título')
    author = ', '.join(raw_book.get('author_name', [])) if 'author_name' in raw_book else None
    genre = fixed_genre if fixed_genre else None


    description = None
    if 'description' in raw_book:
        if isinstance(raw_book['description'], dict):
            description = raw_book['description'].get('value')
        elif isinstance(raw_book['description'], str):
            description = raw_book['description']

    cover_url = None
    if 'cover_i' in raw_book:
        cover_url = f"https://covers.openlibrary.org/b/id/{raw_book['cover_i']}-L.jpg"


    if not author or not description or not cover_url:
        book_details = fetch_book_details(raw_book['key'])
        if book_details:
            if not author and 'authors' in book_details:      
                author_list = []
                for author_data in book_details['authors']:
                    author_name = author_data.get('name', 'Desconocido')
                    author_list.append(author_name)
                author = ', '.join(author_list)

            if not description and 'description' in book_details:
                if isinstance(book_details['description'], dict):
                    description = book_details['description'].get('value')
                elif isinstance(book_details['description'], str):
                    description = book_details['description']
            
            if not cover_url and 'covers' in book_details:
                cover_url = f"https://covers.openlibrary.org/b/id/{book_details['covers'][0]}-L.jpg"


    description = description or "Descripción no disponible."
    cover_url = cover_url or None
    author = author or "Desconocido"

    return {
        'title': title,
        'author': author,
        'genre': genre,
        'description': description,
        'cover_url': cover_url
    }

def insert_book(conn, cursor, book):
    try:
        cover_url = book['cover_url'][:255] if book['cover_url'] else None

        cursor.execute("""
            INSERT INTO dbo.Libro (titulo, autor, genero, descripcion, portada)
            VALUES (%s, %s, %s, %s, %s)
        """, (book['title'], book['author'], book['genre'], book['description'], cover_url))
        conn.commit()
        print(f"Libro insertado: {book['title']}")
    except pymssql.IntegrityError:
        print(f"Libro ya existe en la base de datos: {book['title']}")
    except Exception as e:
        print(f"Error insertando libro {book['title']}: {e}")

def fetch_books_by_genre(genre, limit=5, language="spa"):
    url = f"http://openlibrary.org/subjects/{genre}.json?limit={limit}&language={language}"
    response = requests.get(url)
    try:
        if response.status_code == 200:
            data = response.json()
            books = data.get('works', [])
            print(f"Se recibieron {len(books)} libros.")
            return books
        else:
            print(f"Error al obtener datos de la API: {response.status_code}")
            print(f"Contenido devuelto: {response.text}")
            return []
    except requests.exceptions.JSONDecodeError as e:
        print("Error al decodificar JSON. Respuesta de la API:")
        print(response.text)
        return []


conn = pymssql.connect(server='HP15', user='', password='', database='BIBLIOTECA')
cursor = conn.cursor()

fixed_genre = "terror"
books_raw = fetch_books_by_genre(fixed_genre, limit=10)

for raw_book in books_raw:
    book = parse_book_data(raw_book, fixed_genre=fixed_genre)
    insert_book(conn, cursor, book)

cursor.close()
conn.close()
