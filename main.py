from fastapi import FastAPI, HTTPException
import requests

app = FastAPI()

OPEN_LIBRARY_BASE_URL = "https://openlibrary.org"

@app.get("/books/search")
def search_books(q: str):
    response = requests.get(f"{OPEN_LIBRARY_BASE_URL}/search.json", params={"q": q})
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Error fetching data from Open Library")
    return response.json()

@app.get("/books/{isbn}")
def get_book_by_isbn(isbn: str):
    response = requests.get(f"{OPEN_LIBRARY_BASE_URL}/api/books", params={"bibkeys": f"ISBN:{isbn}", "format": "json", "jscmd": "data"})
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Error fetching book details")
    data = response.json()
    return data.get(f"ISBN:{isbn}", {})

@app.get("/books/authors/{author_id}")
def get_books_by_author(author_id: str):
    response = requests.get(f"{OPEN_LIBRARY_BASE_URL}/authors/{author_id}/works.json")
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Error fetching author's books")
    return response.json()
