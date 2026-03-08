import requests
import urllib.parse
from typing import List, Dict, Any

def search_books(keywords: List[str], max_results: int = 3) -> List[Dict[str, Any]]:
    """
    Search Google Books API using a set of keywords.
    Returns a list of parsed book dictionaries.
    """
    query = "+".join([urllib.parse.quote(kw) for kw in keywords])
    url = f"https://www.googleapis.com/books/v1/volumes?q={query}&maxResults={max_results}&langRestrict=en"
    
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()
    
    books = []
    for item in data.get("items", []):
        volume_info = item.get("volumeInfo", {})
        book = {
            "id": item.get("id"),
            "title": volume_info.get("title", "Unknown Title"),
            "authors": volume_info.get("authors", []),
            "description": volume_info.get("description", "No description available."),
            "published_date": volume_info.get("publishedDate", ""),
            "page_count": volume_info.get("pageCount", 0),
            "categories": volume_info.get("categories", []),
            "thumbnail": volume_info.get("imageLinks", {}).get("thumbnail", ""),
            "info_link": volume_info.get("infoLink", "")
        }
        books.append(book)
        
    return books
