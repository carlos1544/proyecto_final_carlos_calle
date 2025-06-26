import nltk
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from libros.models import Libro
from nltk.corpus import stopwords
import string

# Descargar stopwords solo si no están disponibles
try:
    STOPWORDS = stopwords.words('spanish')
except LookupError:
    nltk.download('stopwords')
    STOPWORDS = stopwords.words('spanish')

# Limpiar y normalizar texto
def limpiar_texto(texto):
    if not isinstance(texto, str):
        texto = ''
    texto = texto.lower().translate(str.maketrans('', '', string.punctuation))
    palabras = texto.split()
    palabras = [palabra for palabra in palabras if palabra not in STOPWORDS and len(palabra) > 2]
    return ' '.join(palabras)

# Vectorización optimizada con preprocesamiento robusto
def vectorizar_datos():
    libros = Libro.objects.all().values('id', 'titulo', 'autor', 'genero', 'descripcion', 'portada')
    libros_df = pd.DataFrame(list(libros))

    # Limpieza y combinación de texto
    for campo in ['titulo', 'genero', 'descripcion']:
        libros_df[campo] = libros_df[campo].fillna('').astype(str)
    
    libros_df['genero'] = libros_df['genero'].str.replace(r'[\[\]"\']', '', regex=True)
    libros_df['contenido'] = (libros_df['titulo'] + ' ' + libros_df['genero'] + ' ' + libros_df['descripcion']).apply(limpiar_texto)

    # Vectorización TF-IDF
    vectorizador = TfidfVectorizer(ngram_range=(1, 2), min_df=1)
    vectores = vectorizador.fit_transform(libros_df['contenido'])

    return vectores, libros_df, vectorizador

# Recomendación basada en similitud de descripción
def recomendar_por_similitud(descripcion, top_n=5):
    vectores, libros_df, vectorizador = vectorizar_datos()
    descripcion_limpia = limpiar_texto(descripcion)
    vector_descripcion = vectorizador.transform([descripcion_limpia])
    similitudes = cosine_similarity(vector_descripcion, vectores).flatten()

    indices_similares = similitudes.argsort()[-top_n:][::-1]
    libros_recomendados = libros_df.iloc[indices_similares]

    return libros_recomendados.to_dict('records')

# Recomendación basada en estado de ánimo
def recomendar_por_estado_animo(estado_animo):
    estados_animo_generos = {
        "feliz": ["comedia", "aventura", "fantasía"],
        "triste": ["drama", "romance", "superación"],
        "emocionado": ["thriller", "acción", "misterio"],
        "relajado": ["poesía", "ensayo", "naturaleza"]
    }

    generos_relacionados = estados_animo_generos.get(estado_animo.lower(), [])
    if not generos_relacionados:
        return []

    libros = Libro.objects.all()
    libros_filtrados = []

    for libro in libros:
        if not libro.genero:
            continue
        genero_limpio = libro.genero.replace('[', '').replace(']', '').replace('"', '').replace("'", '')
        generos = [g.strip().lower() for g in genero_limpio.split(',')]
        if any(gen in generos for gen in generos_relacionados):
            libros_filtrados.append(libro)

    return [ 
        { "id": l.id, "titulo": l.titulo, "autor": l.autor, "genero": l.genero } 
        for l in libros_filtrados 
    ]


# Comparar similitud entre varios libros
def comparar_libros(libro_ids):
    libros = Libro.objects.filter(id__in=libro_ids).values('id', 'titulo', 'genero', 'descripcion')
    libros_df = pd.DataFrame(list(libros))

    for campo in ['titulo', 'genero', 'descripcion']:
        libros_df[campo] = libros_df[campo].fillna('').astype(str)
    libros_df['contenido'] = (libros_df['titulo'] + ' ' + libros_df['genero'] + ' ' + libros_df['descripcion']).apply(limpiar_texto)

    vectorizador = TfidfVectorizer()
    vectores = vectorizador.fit_transform(libros_df['contenido'])
    similitudes = cosine_similarity(vectores)

    comparacion = pd.DataFrame(similitudes, index=libros_df['id'], columns=libros_df['id'])
    return comparacion
