import streamlit as st
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

import workflow

st.set_page_config(
    page_title="Learning Pathway Generator",
    page_icon="📚",
    layout="wide"
)

st.title("📚 AI Learning Pathway Generator")
st.markdown("""
Welcome! Describe what you want to learn or the problem you are trying to solve. 
This tool will use AI to break down your goal into key themes, dynamically search for the best resources, and build a custom reading curriculum for you.
""")

if "pathway_result" not in st.session_state:
    st.session_state.pathway_result = None

with st.form("goal_form"):
    user_goal = st.text_area(
        "What do you want to learn?", 
        placeholder="e.g., I want to learn how to build autonomous agents using Python and LangGraph.",
        height=150
    )
    submitted = st.form_submit_button("Generate Pathway")

if submitted and user_goal:
    st.session_state.pathway_result = None  # Reset previous result
    
    if not os.environ.get("GEMINI_API_KEY") or os.environ.get("GEMINI_API_KEY") == "your_api_key_here":
        st.error("Please set your GEMINI_API_KEY in the Streamlit Cloud Secrets or local .env file before running the application.")
    else:
        with st.status("Building your learning pathway...", expanded=True) as status:
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            def update_progress(message, percent):
                status_text.text(message)
                progress_bar.progress(percent / 100.0)
                
            try:
                result = workflow.process_learning_goal(user_goal, progress_callback=update_progress)
                if "error" in result:
                    status.update(label="Failed to generate pathway", state="error", expanded=True)
                    st.error(result["error"])
                else:
                    status.update(label="Pathway generated successfully!", state="complete", expanded=False)
                    st.session_state.pathway_result = result
            except Exception as e:
                status.update(label="An error occurred", state="error", expanded=True)
                st.error(f"Error: {str(e)}")

# Display the result
if st.session_state.pathway_result and "pathway" in st.session_state.pathway_result:
    st.header("🎯 Your Custom Learning Pathway")
    st.markdown(f"**Goal:** {st.session_state.pathway_result['original_goal']}")
    
    pathway = st.session_state.pathway_result["pathway"]
    
    if not pathway:
        st.warning("No relevant books were found for your goal.")
    else:
        for index, theme_data in enumerate(pathway):
            theme = theme_data["theme"]
            books = theme_data["recommended_books"]
            
            st.subheader(f"Module {index + 1}: {theme}")
            
            if not books:
                st.info("Could not find highly relevant books for this theme using the generated keywords.")
                if "keyword_sets_tried" in theme_data:
                    st.markdown("**Search Queries Tried:**")
                    for ks in theme_data["keyword_sets_tried"]:
                        st.markdown(f"- `{' '.join(ks)}`")
            else:
                for book_data in books:
                    book = book_data["book_info"]
                    reasoning = book_data["reasoning"]
                    keywords = book_data["keywords_used"]
                    
                    with st.expander(f"📖 {book['title']} by {', '.join(book['authors']) if book['authors'] else 'Unknown Author'}"):
                        cols = st.columns([1, 4])
                        
                        with cols[0]:
                            if book.get("thumbnail"):
                                st.image(book["thumbnail"], use_container_width=True)
                            else:
                                st.markdown("*(No image)*")
                                
                        with cols[1]:
                            st.markdown(f"**Relevance to Theme:**\n{reasoning}")
                            st.markdown(f"**Description:**\n{book['description']}")
                            st.markdown(f"**Search Query Used:** `{' '.join(keywords)}`")
                            
                            if book.get("info_link"):
                                st.markdown(f"[View on Google Books]({book['info_link']})")
            
            st.divider()
