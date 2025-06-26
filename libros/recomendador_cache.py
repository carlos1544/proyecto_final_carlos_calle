# recomendador_cache.py
from .recomendador import vectorizar_datos

_vectores = None
_libros_df = None
_vectorizador = None

def vectorizar_datos_cacheado():
    global _vectores, _libros_df, _vectorizador
    if _vectores is None or _libros_df is None or _vectorizador is None:
        _vectores, _libros_df, _vectorizador = vectorizar_datos()
    return _vectores, _libros_df, _vectorizador
