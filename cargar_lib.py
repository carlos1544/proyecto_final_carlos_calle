from libros.models import Libro
import pandas as pd

libros_queryset = Libro.objects.all().values('id', 'titulo', 'autor', 'genero', 'descripcion','portada')
libros_df = pd.DataFrame(libros_queryset)
