import llm_utils
import books_api
from typing import Dict, List, Any

def process_learning_goal(goal: str, progress_callback=None) -> Dict[str, Any]:
    """
    End-to-end workflow to generate a learning pathway.
    
    1. Extract Themes
    2. Generate Keywords per Theme
    3. Search Books per Keyword Set
    4. Evaluate and Synthesize Results
    """
    
    if progress_callback:
        progress_callback("Extracting themes from your goal...", 10)
        
    themes = llm_utils.extract_themes(goal)
    
    if not themes:
        return {"error": "Could not extract themes from the goal."}
        
    if progress_callback:
        progress_callback(f"Identified {len(themes)} themes. Generating search keywords...", 20)
        
    pathway = []
    
    total_themes = len(themes)
    for i, theme in enumerate(themes):
        if progress_callback:
            progress_callback(f"Processing Theme {i+1}/{total_themes}: {theme}", 20 + int(70 * (i / total_themes)))
            
        keyword_sets = llm_utils.generate_keywords(theme)
        theme_books = []
        seen_book_ids = set()
        
        for k_set in keyword_sets:
            books = books_api.search_books(k_set, max_results=2)
            for book in books:
                if book["id"] not in seen_book_ids:
                    seen_book_ids.add(book["id"])
                    
                    try:
                        # Evaluate relevance
                        evaluation = llm_utils.evaluate_book(
                            goal=goal,
                            theme=theme,
                            book_title=book["title"],
                            book_description=book["description"],
                            authors=book["authors"]
                        )
                        
                        if evaluation and evaluation.is_relevant:
                            theme_books.append({
                                "book_info": book,
                                "reasoning": evaluation.reasoning,
                                "keywords_used": k_set
                            })
                    except Exception as eval_err:
                        print(f"Error evaluating book {book['title']}: {eval_err}")
                        return {"error": f"Error during Gemini evaluation of book '{book['title']}': {str(eval_err)}"}
                        
                    # Once we find 2 good books for a theme, we can move on to the next theme
                        if len(theme_books) >= 2:
                            break
            if len(theme_books) >= 2:
                break
                
        pathway.append({
            "theme": theme,
            "keyword_sets_tried": keyword_sets,
            "recommended_books": theme_books
        })
        
    if progress_callback:
        progress_callback("Finalizing learning pathway...", 100)
        
    return {
        "original_goal": goal,
        "pathway": pathway
    }
