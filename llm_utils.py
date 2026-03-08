import os
from pydantic import BaseModel, Field
from google import genai
from typing import List, Optional

# Initialize the Gemini client
client = genai.Client()

class ThemeList(BaseModel):
    themes: List[str] = Field(description="A list of 3-5 distinct learning themes extracted from the user's goal")

class KeywordSets(BaseModel):
    keyword_sets: List[List[str]] = Field(description="A list of keyword sets. Each set is a list of strings representing a search query for Google Books. The total number of words across all strings in a single set MUST be 6 or fewer.")

class BookEvaluation(BaseModel):
    is_relevant: bool = Field(description="Whether the book is highly relevant to the goal and theme")
    reasoning: str = Field(description="Explanation of why the book is relevant and how it helps the user achieve their goal")

def extract_themes(goal: str) -> List[str]:
    """Extract distinct learning themes from a user's goal."""
    prompt = f"Analyze the following user learning goal and extract 3 to 5 core themes or topics that need to be learned to achieve this goal. \n\nUser Goal: {goal}"
    
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt,
        config=genai.types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=ThemeList,
            temperature=0.2
        )
    )
    return response.parsed.themes if response.parsed else []

def generate_keywords(theme: str) -> List[List[str]]:
    """Generate different sets of search keywords for a specific learning theme."""
    prompt = f"For the learning theme '{theme}', generate 3 different sets of search keywords. Each set should contain 2-4 keywords that can be used to query a book database, but the TOTAL number of words in a set MUST NOT exceed 6 words. Make the sets diverse (e.g., one theoretical, one practical, one beginner-focused)."
    
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt,
        config=genai.types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=KeywordSets,
            temperature=0.7
        )
    )
    return response.parsed.keyword_sets if response.parsed else []

def evaluate_book(goal: str, theme: str, book_title: str, book_description: str, authors: List[str]) -> ThemeList:
    """Evaluate if a book is relevant to the user's goal and specific theme."""
    prompt = f"""
    Evaluate the following book's relevance to the user's goal and specific theme.
    
    User Goal: {goal}
    Learning Theme: {theme}
    
    Book Title: {book_title}
    Authors: {', '.join(authors) if authors else 'Unknown'}
    Description: {book_description}
    
    Determine if this book is highly relevant and would be a good recommendation for this specific theme. If it is relevant, explain why and how it helps tackle the learning theme in the context of the user's overarching goal.
    """
    
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt,
        config=genai.types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=BookEvaluation,
            temperature=0.2
        )
    )
    return response.parsed if response.parsed else None
