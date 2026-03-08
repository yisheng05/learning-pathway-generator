import requests
import urllib.parse
from typing import List, Dict, Any

def search_books(keywords: List[str], max_results: int = 3) -> List[Dict[str, Any]]:
    """
    Search Open Library API using a set of keywords.
    Returns a list of parsed book dictionaries.
    """
    query = "+".join([urllib.parse.quote(kw) for kw in keywords])
    url = f"https://openlibrary.org/search.json?q={query}&limit={max_results}"
    
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()
    
    books = []
    for item in data.get("docs", []):
        # Open Library provides cover IDs. We construct the image URL.
        cover_id = item.get("cover_i")
        thumbnail = f"https://covers.openlibrary.org/b/id/{cover_id}-M.jpg" if cover_id else ""
        
        # Open Library search API doesn't return full descriptions. 
        # We rely on subtitle/subject or default text for Gemini to evaluate.
        description = item.get("first_sentence", [""])[0] if item.get("first_sentence") else ""
        if not description:
            subjects = item.get("subject", [])
            description = f"Topics covered: {', '.join(subjects[:5])}" if subjects else "No detailed description available."
            
        book = {
            "id": item.get("key", ""),
            "title": item.get("title", "Unknown Title"),
            "authors": item.get("author_name", []),
            "description": description,
            "published_date": str(item.get("first_publish_year", "")),
            "page_count": item.get("number_of_pages_median", 0),
            "categories": item.get("subject", []),
            "thumbnail": thumbnail,
            "info_link": f"https://openlibrary.org{item.get('key', '')}"
        }
        books.append(book)
        
    return books
