import pandas as pd
from preprocesador import vectorizar_datos, recomendar_libros

data = [
    {"id": 1, "titulo": "Cien años de soledad", "autor": "Gabriel García Márquez", "genero": "Realismo mágico", "descripcion": "Historia de la familia Buendía en el pueblo de Macondo."},
    {"id": 2, "titulo": "El amor en los tiempos del cólera", "autor": "Gabriel García Márquez", "genero": "Romance", "descripcion": "Historia de amor y espera en tiempos difíciles."},
    {"id": 3, "titulo": "La casa de los espíritus", "autor": "Isabel Allende", "genero": "Realismo mágico", "descripcion": "Saga familiar con elementos sobrenaturales."},
    {"id": 4, "titulo": "Don Quijote de la Mancha", "autor": "Miguel de Cervantes", "genero": "Aventuras", "descripcion": "Las aventuras de un caballero y su fiel escudero."},
    {"id": 5, "titulo": "Pedro Páramo", "autor": "Juan Rulfo", "genero": "Realismo mágico", "descripcion": "Un hombre busca a su padre en un pueblo fantasma."},
]

libros_df = pd.DataFrame(data)
vectores, libros_df, vectorizador = vectorizar_datos(libros_df)
recomendados = recomendar_libros(0, vectores, libros_df)

print("Libros recomendados:")
print(recomendados[['titulo', 'autor']])
