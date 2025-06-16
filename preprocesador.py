import nltk
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd

nltk.download('stopwords')
from nltk.corpus import stopwords

STOPWORDS = stopwords.words('spanish')

def limpiar_texto(texto):
    """Limpia y normaliza el texto."""
    texto = texto.lower()  
    texto = ''.join(c for c in texto if c.isalnum() or c.isspace()) 
    palabras = texto.split()
    palabras = [palabra for palabra in palabras if palabra not in STOPWORDS]
    return ' '.join(palabras)

def vectorizar_datos(libros):
    libros['contenido'] = libros['titulo'] + ' ' + libros['genero'] + ' ' + libros['descripcion']
    libros['contenido'] = libros['contenido'].apply(limpiar_texto)
    vectorizador = TfidfVectorizer()
    vectores = vectorizador.fit_transform(libros['contenido'])
    return vectores, libros, vectorizador

def recomendar_libros(libro_id, vectores, libros, top_n=5):
    similitudes = cosine_similarity(vectores[libro_id], vectores).flatten()
    indices_similares = similitudes.argsort()[-top_n-1:-1][::-1]  
    return libros.iloc[indices_similares]
