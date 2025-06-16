import nltk
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from libros.models import Libro  
from nltk.corpus import stopwords
import pandas as pd


nltk.download('stopwords')

STOPWORDS = stopwords.words('spanish')

def limpiar_texto(texto):
    if not isinstance(texto, str):
        texto = ''
    texto = texto.lower()
    texto = ''.join(c for c in texto if c.isalnum() or c.isspace())
    palabras = texto.split()
    palabras = [palabra for palabra in palabras if palabra not in STOPWORDS]
    return ' '.join(palabras)

def vectorizar_datos():
    libros = Libro.objects.all().values('id', 'titulo', 'autor', 'genero', 'descripcion', 'portada')

    libros_df = pd.DataFrame(list(libros))

    libros_df['titulo'] = libros_df['titulo'].fillna('')
    libros_df['genero'] = libros_df['genero'].fillna('')
    libros_df['descripcion'] = libros_df['descripcion'].fillna('')
    libros_df['contenido'] = libros_df['titulo'] + ' ' + libros_df['genero'] + ' ' + libros_df['descripcion']
    libros_df['contenido'] = libros_df['contenido'].fillna('')
    libros_df['contenido'] = libros_df['contenido'].apply(limpiar_texto)

    vectorizador = TfidfVectorizer()
    vectores = vectorizador.fit_transform(libros_df['contenido'])
    return vectores, libros_df, vectorizador


def recomendar_por_similitud(descripcion, top_n=5):
    vectores, libros_df, vectorizador = vectorizar_datos()
    descripcion_limpia = limpiar_texto(descripcion)
    vector_descripcion = vectorizador.transform([descripcion_limpia])
    similitudes = cosine_similarity(vector_descripcion, vectores).flatten()
    indices_similares = similitudes.argsort()[-top_n:][::-1]
    libros_recomendados = libros_df.iloc[indices_similares]
    return libros_recomendados.to_dict('records')


def recomendar_por_estado_animo(estado_animo):
    estados_animo_generos = {
        "feliz": ["comedia", "aventura", "fantasía"],
        "triste": ["drama", "romance", "superación personal"],
        "emocionado": ["thriller", "acción", "misterio"],
        "relajado": ["poesía", "ensayo", "naturaleza"]
    }
    
    generos_relacionados = estados_animo_generos.get(estado_animo.lower(), [])
    if not generos_relacionados:
        return []  
    
    libros = Libro.objects.filter(genero__iregex='|'.join(generos_relacionados))
    return list(libros.values('id', 'titulo', 'autor', 'genero'))


def comparar_libros(libro_ids):
    libros = Libro.objects.filter(id__in=libro_ids).values('id', 'titulo', 'genero', 'descripcion')
    libros_df = pd.DataFrame(list(libros))
    libros_df['contenido'] = libros_df['titulo'] + ' ' + libros_df['genero'] + ' ' + libros_df['descripcion']
    libros_df['contenido'] = libros_df['contenido'].apply(limpiar_texto)
    
    vectorizador = TfidfVectorizer()
    vectores = vectorizador.fit_transform(libros_df['contenido'])
    similitudes = cosine_similarity(vectores)
    
    comparacion = pd.DataFrame(similitudes, index=libros_df['id'], columns=libros_df['id'])
    return comparacion
