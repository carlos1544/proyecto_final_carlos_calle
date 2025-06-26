import os
import time
import random
import requests
import pyodbc
from collections import Counter, defaultdict
from biblioteca_virtual.settings import DATABASES

# Constantes API
GOOGLE_BOOKS_API_URL = "https://www.googleapis.com/books/v1/volumes"
OPENLIBRARY_API_URL = "https://openlibrary.org/search.json"

# Contadores globales para métricas y descartes
descartes = Counter()
search_stats = defaultdict(int)


# === Conexión a base de datos ===
def get_connection():
    """Establecer conexión a BD usando configuración existente"""
    config = DATABASES['default']
    driver = config['OPTIONS']['driver']
    trusted = config['OPTIONS'].get('trusted_connection', 'no')

    conn_str = (
        f"DRIVER={{{driver}}};"
        f"SERVER={config['HOST']},{config['PORT']};"
        f"DATABASE={config['NAME']};"
        f"Trusted_Connection={trusted};"
    )
    return pyodbc.connect(conn_str)


# === Estrategias de búsqueda por género ===
def get_genre_search_strategies(genre):
    """Generar múltiples estrategias de búsqueda para un género dado"""
    strategies = [
        f"subject:{genre}",
        f"categories:{genre}",
        f"intitle:{genre}",
        f"{genre}",
        f"genre:{genre}",
    ]

    genre_variations = {
        'fantasia': ['fantasy', 'magia', 'magic', 'dragons', 'dragones', 'elfos', 'elves', 'aventura'],
        'romance': ['amor', 'love', 'romantic', 'romantico', 'corazón', 'heart'],
        'misterio': ['mystery', 'detective', 'crimen', 'crime', 'suspense', 'thriller'],
        'ciencia_ficcion': ['science fiction', 'sci-fi', 'futuro', 'future', 'space', 'espacio'],
        'terror': ['horror', 'miedo', 'fear', 'supernatural', 'sobrenatural', 'ghost'],
        'aventura': ['adventure', 'action', 'accion', 'journey', 'viaje', 'exploration'],
        'biografia': ['biography', 'biografía', 'memoir', 'memorias', 'life story'],
        'historia': ['history', 'historical', 'historico', 'past', 'pasado', 'war'],
        'autoayuda': ['self help', 'personal development', 'desarrollo personal', 'motivational']
    }

    variations = genre_variations.get(genre, [genre])

    for variation in variations:
        strategies.extend([
            f"subject:{variation}",
            f"intitle:{variation}",
            f"{variation}",
            f"categories:{variation}"
        ])

    strategies.extend([
        f"subject:{genre} OR categories:{genre}",
        f"intitle:{genre} OR subject:{genre}",
        f"{genre} fiction",
        f"{genre} novela",
        f"libro {genre}",
        f"book {genre}"
    ])

    return list(set(strategies))  # Eliminar duplicados


# === Obtención de libros con estrategia ===
def fetch_books_with_strategy(strategy, genre, target_count=40, max_pages=5):
    """Obtener libros usando una estrategia de búsqueda específica"""
    print(f"\n[fetch_books_with_strategy] Estrategia: '{strategy}' - Objetivo: {target_count} libros")

    collected_books = []
    start_index = 0
    max_results = 40
    empty_pages = 0
    consecutive_failures = 0

    while len(collected_books) < target_count and empty_pages < max_pages:
        if start_index > 0:
            time.sleep(random.uniform(0.5, 1.5))

        params = {
            'q': strategy,
            'langRestrict': 'es',
            'printType': 'books',
            'maxResults': max_results,
            'startIndex': start_index,
            'orderBy': 'relevance'
        }

        try:
            response = requests.get(GOOGLE_BOOKS_API_URL, params=params, timeout=15)
            response.raise_for_status()
            data = response.json()
            items = data.get('items', [])

            search_stats[f"pages_fetched_{strategy[:20]}"] += 1
            print(f"[fetch_books_with_strategy] Página {start_index // max_results + 1}: {len(items)} libros recibidos")

            if not items:
                empty_pages += 1
                consecutive_failures += 1
                if consecutive_failures >= 3:
                    params['orderBy'] = 'newest'
                    consecutive_failures = 0
                start_index += max_results
                continue

            empty_pages = 0
            consecutive_failures = 0

            for item in items:
                parsed = parse_book_data_improved(item, fixed_genre=genre)
                if parsed and not any(book['title'].lower() == parsed['title'].lower() for book in collected_books):
                    collected_books.append(parsed)
                    if len(collected_books) >= target_count:
                        break

            start_index += max_results

        except requests.RequestException as e:
            print(f"[fetch_books_with_strategy][ERROR] {e}")
            empty_pages += 1
            if empty_pages >= 3:
                break
            time.sleep(2)

    search_stats[f"books_found_{strategy[:20]}"] = len(collected_books)
    print(f"[fetch_books_with_strategy] Estrategia '{strategy}' obtuvo {len(collected_books)} libros válidos")
    return collected_books


# === Parsing y validación avanzada de datos de libro ===
def parse_book_data_improved(book_item, fixed_genre=None):
    """Parseo mejorado de datos de libro con validaciones flexibles"""
    volume_info = book_item.get("volumeInfo", {})

    language = volume_info.get("language", "").lower()
    if language and language not in ['es', 'es-es', 'spanish', 'spa']:
        title = volume_info.get("title", "").lower()
        description = volume_info.get("description", "").lower()
        spanish_indicators = ['ñ', 'está', 'año', 'niño', 'español', 'méxico', 'argentina', 'chile']
        if not any(ind in title + description for ind in spanish_indicators):
            descartes["No español"] += 1
            return None

    title = volume_info.get("title", "").strip()
    if not title or title == "Sin título":
        descartes["Sin título"] += 1
        return None
    if len(title) < 2:
        descartes["Título muy corto"] += 1
        return None

    authors = volume_info.get("authors", []) or ["Autor desconocido"]
    description = volume_info.get("description", "").strip()

    if len(description) < 10:
        alt_desc = fetch_openlibrary_description_improved(title, authors[0] if authors else None)
        if alt_desc:
            description = alt_desc
        else:
            subtitle = volume_info.get("subtitle", "")
            categories = volume_info.get("categories", [])
            description = (f"{subtitle}. " if subtitle else "") + (f"Categorías: {', '.join(categories[:3])}." if categories else "")

    if len(description.strip()) < 5:
        descartes["Descripción insuficiente"] += 1
        return None

    image_links = volume_info.get("imageLinks", {})
    cover_url = (
        image_links.get("thumbnail") or
        image_links.get("smallThumbnail") or
        image_links.get("small") or
        image_links.get("medium") or
        image_links.get("large") or
        ""
    )
    if not cover_url:
        cover_url = generate_placeholder_cover_url(title, authors[0] if authors else "")

    published_date = volume_info.get("publishedDate", "")
    publisher = volume_info.get("publisher", "")
    page_count = volume_info.get("pageCount", 0)

    url_para_leer = volume_info.get("previewLink") or volume_info.get("infoLink") or ""

    quality_score = calculate_book_quality_score(volume_info)

    return {
        'title': title,
        'author': ', '.join(authors[:3]),
        'genre': fixed_genre,
        'description': description.strip()[:1000],
        'cover_url': cover_url.strip()[:255],
        'published_date': published_date,
        'publisher': publisher,
        'page_count': page_count,
        'quality_score': quality_score,
        'url_para_leer': url_para_leer
    }


# === Cálculo de calidad para priorización ===
def calculate_book_quality_score(volume_info):
    """Calcular puntaje de calidad para priorizar libros"""
    score = 0
    if len(volume_info.get("title", "")) > 5:
        score += 1
    desc_len = len(volume_info.get("description", ""))
    if desc_len > 50:
        score += 2
    elif desc_len > 20:
        score += 1
    if volume_info.get("imageLinks", {}).get("thumbnail"):
        score += 2
    if volume_info.get("authors"):
        score += 1
    if volume_info.get("publisher"):
        score += 1
    if volume_info.get("pageCount", 0) > 0:
        score += 1
    if volume_info.get("categories"):
        score += 1
    if volume_info.get("averageRating", 0) > 0:
        score += 2
    return score


# === URL placeholder para portada ===
def generate_placeholder_cover_url(title, author):
    """Generar URL placeholder para portada si no existe"""
    return f"https://via.placeholder.com/128x192/cccccc/000000?text={title[:10]}"


# === Consulta de descripción en OpenLibrary ===
def fetch_openlibrary_description_improved(title, author=None):
    """Obtención mejorada de descripción desde OpenLibrary"""
    if not title:
        return None

    search_attempts = [
        {'title': title},
        {'q': title},
        {'title': title, 'author': author} if author else None,
        {'q': f"{title} {author}"} if author else None
    ]

    for params in search_attempts:
        if params is None:
            continue
        try:
            resp = requests.get(OPENLIBRARY_API_URL, params=params, timeout=10)
            resp.raise_for_status()
            data = resp.json()
            docs = data.get('docs', [])
            for doc in docs:
                for field in ['description', 'first_sentence', 'subtitle', 'notes', 'table_of_contents']:
                    desc = doc.get(field)
                    if desc:
                        if isinstance(desc, dict):
                            desc = desc.get('value') or desc.get('description')
                        elif isinstance(desc, list):
                            desc = ' '.join(str(i) for i in desc[:3])
                        if isinstance(desc, str) and len(desc.strip()) >= 10:
                            return desc.strip()[:500]
        except Exception as e:
            print(f"[fetch_openlibrary_description_improved][ERROR] {e}")
            continue
    return None


# === Búsqueda de libros usando todas las estrategias ===
def fetch_books_by_genre_comprehensive(genre, target_count=100):
    """Búsqueda integral de libros usando varias estrategias"""
    print(f"\n[fetch_books_by_genre_comprehensive] Buscando {target_count} libros del género '{genre}'")

    all_books = []
    seen_titles = set()
    strategies = get_genre_search_strategies(genre)

    strategy_priorities = {
        'subject:': 3,
        'categories:': 3,
        'intitle:': 2,
        'genre:': 2,
        '': 1
    }

    def strategy_score(strategy):
        for key, score in strategy_priorities.items():
            if strategy.startswith(key):
                return score
        return 1

    strategies.sort(key=strategy_score, reverse=True)

    books_per_strategy = max(10, target_count // len(strategies))

    print(f"[fetch_books_by_genre_comprehensive] Usando {len(strategies)} estrategias diferentes")

    for i, strategy in enumerate(strategies):
        if len(all_books) >= target_count:
            break

        print(f"\n--- Estrategia {i+1}/{len(strategies)}: {strategy} ---")

        remaining_needed = target_count - len(all_books)
        strategy_target = min(books_per_strategy, remaining_needed + 10)

        books = fetch_books_with_strategy(strategy, genre, target_count=strategy_target)

        new_books = 0
        for book in books:
            title_lower = book['title'].lower()
            if title_lower not in seen_titles:
                all_books.append(book)
                seen_titles.add(title_lower)
                new_books += 1

        print(f"[fetch_books_by_genre_comprehensive] Agregados {new_books} libros nuevos (Total: {len(all_books)})")

        if len(all_books) >= target_count:
            break

    all_books.sort(key=lambda x: x.get('quality_score', 0), reverse=True)

    print(f"\n[fetch_books_by_genre_comprehensive] Total final: {len(all_books)} libros")
    print(f"[fetch_books_by_genre_comprehensive] Estadísticas de descarte: {dict(descartes)}")
    print(f"[fetch_books_by_genre_comprehensive] Estadísticas de búsqueda: {dict(search_stats)}")

    return all_books[:target_count]


# === Inserción mejorada de libros en la BD ===
def insert_book_improved(conn, cursor, book):
    """Inserción mejorada con soporte para url de lectura"""
    print(f"[insert_book_improved] Insertando: {book['title'][:50]}...")

    try:
        cursor.execute(
            """
            INSERT INTO dbo.Libro (titulo, autor, genero, descripcion, portada, url_para_leer)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (book['title'], book['author'], book['genre'], book['description'], book['cover_url'], book['url_para_leer'])
        )
        conn.commit()
        print(f"[insert_book_improved] ✓ Insertado exitosamente")
        return True

    except pyodbc.IntegrityError:
        print(f"[insert_book_improved][AVISO] Ya existe o violación de integridad: {book['title'][:30]}...")
        return False
    except Exception as e:
        print(f"[insert_book_improved][ERROR] {e}")
        return False


# === Función principal ===
def main():
    """Función principal con manejo avanzado de errores y reporte"""
    print("[main] Inicio del proceso mejorado de recopilación de libros")

    try:
        conn = get_connection()
        cursor = conn.cursor()

        genre = "drama"
        target_count = 5  # Objetivo aumentado

        print(f"[main] Configuración: Género='{genre}', Objetivo={target_count} libros")

        books = fetch_books_by_genre_comprehensive(genre, target_count=target_count)

        if not books:
            print("[main] No se encontraron libros válidos")
            return

        print(f"\n[main] Iniciando inserción de {len(books)} libros en la base de datos...")

        inserted_count = 0
        for i, book in enumerate(books, 1):
            print(f"\n[main] Procesando libro {i}/{len(books)}")
            if insert_book_improved(conn, cursor, book):
                inserted_count += 1

        print(f"\n[main] Resumen final:")
        print(f"[main] - Libros encontrados: {len(books)}")
        print(f"[main] - Libros insertados: {inserted_count}")
        print(f"[main] - Libros duplicados/fallidos: {len(books) - inserted_count}")
        print(f"[main] - Motivos de descarte durante búsqueda: {dict(descartes)}")

        cursor.close()
        conn.close()
        print("[main] Proceso finalizado exitosamente")

    except Exception as e:
        print(f"[main][ERROR CRÍTICO] {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
