import streamlit as st
import requests
import base64
from PIL import Image
import io
import json
from pathlib import Path

# Page configuration
st.set_page_config(
    page_title="UPSC Content Factory",
    page_icon="📚",
    layout="wide"
)

# Simplified, clean CSS
st.markdown("""
<style>
    /* Hide Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Main container */
    .main .block-container {
        padding-top: 1rem;
        max-width: 1200px;
    }
    
    /* Header */
    .app-header {
        background: linear-gradient(90deg, #1e3a8a 0%, #3b82f6 100%);
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        text-align: center;
    }
    
    .app-header h1 {
        color: white;
        margin: 0;
        font-size: 2rem;
    }
    
    .app-header p {
        color: rgba(255,255,255,0.9);
        margin: 0.5rem 0 0 0;
    }
    
    /* Section headers */
    .section-header {
        background: #f8fafc;
        padding: 1rem 1.5rem;
        border-left: 4px solid #3b82f6;
        margin: 2rem 0 1rem 0;
        border-radius: 4px;
    }
    
    .section-header h3 {
        margin: 0;
        color: #1e293b;
    }
    
    /* Queue items */
    .queue-item {
        background: white;
        border: 1px solid #e2e8f0;
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 0.75rem;
    }
    
    .queue-item:hover {
        border-color: #3b82f6;
        box-shadow: 0 2px 8px rgba(59, 130, 246, 0.1);
    }
    
    /* Badges */
    .badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 999px;
        font-size: 0.75rem;
        font-weight: 600;
        margin-right: 0.5rem;
    }
    
    .badge-prelims {
        background: #fef3c7;
        color: #92400e;
    }
    
    .badge-mains {
        background: #dbeafe;
        color: #1e40af;
    }
    
    /* Success message */
    .success-banner {
        background: #d1fae5;
        border-left: 4px solid #10b981;
        padding: 1rem 1.5rem;
        border-radius: 4px;
        margin: 1rem 0;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.5rem;
        border-bottom: 2px solid #e5e7eb;
    }
    
    .stTabs [data-baseweb="tab"] {
        padding: 0.75rem 1.5rem;
        border-radius: 6px 6px 0 0;
    }
    
    .stTabs [aria-selected="true"] {
        background: white;
        border-bottom: 3px solid #3b82f6;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'articles' not in st.session_state:
    st.session_state.articles = []
if 'result' not in st.session_state:
    st.session_state.result = None

# Load configuration
try:
    N8N_WEBHOOK_URL = st.secrets["N8N_WEBHOOK_URL"]
    API_KEY = st.secrets.get("API_KEY", "")
except Exception as e:
    st.error("⚠️ Please configure N8N_WEBHOOK_URL in Streamlit secrets")
    st.stop()

# Load CSS themes
def load_css_themes():
    themes = {}
    styles_dir = Path(__file__).parent / "styles"
    
    default_theme = """
body {
    font-family: 'Inter', 'Segoe UI', sans-serif;
    line-height: 1.7;
    color: #1a1a1a;
    max-width: 850px;
    margin: 0 auto;
    padding: 40px 25px;
    background: #ffffff;
}
h1 {
    color: #0f172a;
    font-weight: 700;
    margin-top: 40px;
    margin-bottom: 20px;
    font-size: 2.5em;
}
h2 {
    color: #334155;
    font-weight: 600;
    margin-top: 32px;
    font-size: 1.75em;
}
h3 {
    color: #475569;
    font-weight: 600;
    margin-top: 24px;
    font-size: 1.35em;
}
strong {
    color: #dc2626;
    font-weight: 600;
    background: #fef2f2;
    padding: 2px 6px;
    border-radius: 3px;
}
    """
    
    css_files = {
        "A4 Standard": "A4_standard.css",
        "Poster Style": "poster_style.css",
        "Modern Clean": "modern_clean.css"
    }
    
    for theme_name, filename in css_files.items():
        css_path = styles_dir / filename
        try:
            if css_path.exists():
                themes[theme_name] = css_path.read_text(encoding='utf-8')
            elif theme_name == "Modern Clean":
                themes[theme_name] = default_theme
        except:
            if theme_name == "Modern Clean":
                themes[theme_name] = default_theme
    
    if not themes:
        themes["Modern Clean"] = default_theme
    
    return themes

CSS_THEMES = load_css_themes()

def process_html_for_A4(html_content):
    try:
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html_content, 'html.parser')
        return str(soup)
    except:
        return html_content

# ===========================================
# HEADER
# ===========================================
st.markdown("""
<div class="app-header">
    <h1>📚 UPSC Content Factory</h1>
    <p>Transform news into exam-ready study material</p>
</div>
""", unsafe_allow_html=True)

# ===========================================
# MAIN CONTENT
# ===========================================

# Always show Article Input and Queue (removed if/else Result toggle)
st.markdown('<div class="section-header"><h3>📝 Add Articles</h3></div>', unsafe_allow_html=True)

col1, col2 = st.columns([2, 1])

with col1:
    # Input Method Selection (Outside Form for Instant Updates)
    input_method = st.radio("Input Method:", ["URL", "Text", "Image"], horizontal=True)
    
    with st.form(key='article_form', clear_on_submit=False): # Changed to False to persist data
        article_title = st.text_input("📌 Article Title", placeholder="Enter title...")
        
        article_url = ""
        raw_text = ""
        image_data = ""
        
        # Inputs based on selection
        if input_method == "URL":
            article_url = st.text_input("🔗 URL", placeholder="https://...")
        elif input_method == "Text":
            raw_text = st.text_area("📄 Content", height=150, placeholder="Paste article text...")
        else:
            uploaded_file = st.file_uploader("📸 Upload Image", type=['png', 'jpg', 'jpeg'])
            if uploaded_file:
                image = Image.open(uploaded_file)
                st.image(image, width=300)
                buffered = io.BytesIO()
                image.save(buffered, format="JPEG")
                image_data = base64.b64encode(buffered.getvalue()).decode()
        
        col_a, col_b = st.columns(2)
        with col_a:
            exam_type = st.selectbox("📖 Exam", ["Prelims", "Mains"])
        with col_b:
            subject = st.text_input("📚 Subject", placeholder="e.g., Polity")
        
        focus_keyword = st.text_input("🎯 Focus Keyword (Optional)", placeholder="Main topic or concept to emphasize...")
        
        submitted = st.form_submit_button("➕ Add to Queue", type="primary", use_container_width=True)
        
        if submitted:
            if not article_title:
                st.error("Please enter a title")
            elif input_method == "URL" and not article_url:
                st.error("Please enter a URL")
            elif input_method == "Text" and not raw_text:
                st.error("Please paste text")
            elif input_method == "Image" and not image_data:
                st.error("Please upload an image")
            else:
                st.session_state.articles.append({
                    "title": article_title,
                    "url": article_url if input_method == "URL" else "",
                    "raw_text": raw_text if input_method == "Text" else "",
                    "image_data": image_data if input_method == "Image" else "",
                    "exam_type": exam_type,
                    "subject": subject or "General",
                    "focus_keyword": focus_keyword or article_title
                })
                st.success(f"✅ Added: {article_title}")
                st.rerun()

with col2:
    st.markdown(f"**📋 Queue ({len(st.session_state.articles)})**")
    
    if st.session_state.articles:
        for idx, article in enumerate(st.session_state.articles):
            badge = "badge-prelims" if article['exam_type'] == "Prelims" else "badge-mains"
            input_type = "URL" if article['url'] else ("Text" if article['raw_text'] else "Image")
            
            st.markdown(f"""
            <div class="queue-item">
                <div><strong>{idx + 1}. {article['title'][:35]}...</strong></div>
                <div style="margin-top: 0.5rem;">
                    <span class="badge {badge}">{article['exam_type']}</span>
                    <span style="font-size: 0.85rem; color: #64748b;">{article['subject']} • {input_type}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("🗑️", key=f"del_{idx}"):
                st.session_state.articles.pop(idx)
                st.rerun()
        
        if st.button("🧹 Clear All", type="secondary", use_container_width=True):
            st.session_state.articles = []
            st.rerun()
    else:
        st.info("No articles added yet")

# Process button
st.markdown("---")

if st.session_state.articles:
    if st.button(f"🚀 Process {len(st.session_state.articles)} Article(s)", type="primary", use_container_width=True):
        with st.spinner("⏳ Processing..."):
            try:
                response = requests.post(
                    N8N_WEBHOOK_URL,
                    json={"articles": st.session_state.articles},
                    headers={"Content-Type": "application/json", "x-api-key": API_KEY} if API_KEY else {"Content-Type": "application/json"},
                    timeout=600
                )
                
                if response.status_code == 200:
                    st.session_state.result = response.json()
                    st.success("✅ Complete!")
                    st.rerun()
                else:
                    st.error(f"❌ Error {response.status_code}")
            except Exception as e:
                st.error(f"❌ {str(e)}")
else:
    st.info("Add articles to get started")

# Results section (Always rendered if results exist)
if st.session_state.result:
    st.markdown("---")
    st.markdown('<div class="section-header"><h3>✨ Processing Results</h3></div>', unsafe_allow_html=True)
    
    result = st.session_state.result
    doc_url = result.get('url') or result.get('document_url')
    
    st.markdown("""
    <div class="success-banner">
        <strong>🎉 Study Material Generated Successfully!</strong>
    </div>
    """, unsafe_allow_html=True)
    
    if doc_url:
        st.markdown(f"### [📄 Open Google Doc]({doc_url})")
    
    st.markdown("---")
    
    # Tabs
    tab1, tab2, tab3 = st.tabs(["📄 Google Doc", "🌐 HTML Preview", "📥 Downloads"])
    
    with tab1:
        if doc_url:
            embed_url = doc_url.replace('/edit', '/preview')
            st.components.v1.iframe(embed_url, height=600, scrolling=True)
        else:
            st.info("No document available")
    
    with tab2:
        articles_list = result.get('articles', [])
        if articles_list:
            col_a, col_b = st.columns(2)
            
            with col_a:
                selected_theme = st.selectbox("🎨 Theme:", list(CSS_THEMES.keys()))
            
            with col_b:
                article_titles = [f"{i+1}. {a.get('title', 'Untitled')}" for i, a in enumerate(articles_list)]
                selected_idx = st.selectbox("📄 Article:", range(len(articles_list)), format_func=lambda i: article_titles[i])
            
            article = articles_list[selected_idx]
            html_content = article.get('html', '')
            
            if html_content:
                if selected_theme == "A4 Standard":
                    html_content = process_html_for_A4(html_content)
                    wrapped_html = f'<div class="page"><article class="book"><div class="prose">{html_content}</div></article></div>'
                elif selected_theme == "Poster Style":
                    wrapped_html = f'<section class="poster"><div class="print-header"></div><div class="poster-content">{html_content}</div></section>'
                else:
                    wrapped_html = html_content
                
                styled_html = f'<!DOCTYPE html><html><head><meta charset="UTF-8"><style>{CSS_THEMES[selected_theme]}</style></head><body>{wrapped_html}</body></html>'
                st.components.v1.html(styled_html, height=600, scrolling=True)
            else:
                st.warning("No HTML content")
    
    with tab3:
        articles_list = result.get('articles', [])
        if articles_list:
            for idx, article in enumerate(articles_list):
                st.markdown(f"**{idx+1}. {article.get('title', 'Untitled')}**")
                
                col1, col2, col3, col4, col5 = st.columns(5)
                
                with col1:
                    st.download_button(
                        "📄 MD",
                        article.get('markdown', ''),
                        f"article_{idx+1}.md",
                        "text/markdown",
                        key=f"md_{idx}"
                    )
                
                with col2:
                    st.download_button(
                        "🌐 HTML",
                        article.get('html', ''),
                        f"article_{idx+1}.html",
                        "text/html",
                        key=f"html_{idx}"
                    )
                
                # Styled downloads
                for tidx, (theme_name, theme_css) in enumerate(CSS_THEMES.items()):
                    with [col3, col4, col5][tidx]:
                        raw_html = article.get('html', '')
                        
                        if theme_name == "A4 Standard":
                            raw_html = process_html_for_A4(raw_html)
                            body_html = f'<div class="page"><article class="book"><div class="prose">{raw_html}</div></article></div>'
                        elif theme_name == "Poster Style":
                            body_html = f'<section class="poster"><div class="print-header"></div><div class="poster-content">{raw_html}</div></section>'
                        else:
                            body_html = raw_html
                        
                        styled = f'<!DOCTYPE html><html><head><meta charset="UTF-8"><title>{article.get("title", "")}</title><style>{theme_css}</style></head><body>{body_html}</body></html>'
                        
                        st.download_button(
                            f"🎨 {theme_name.split()[0]}",
                            styled,
                            f"article_{idx+1}_{theme_name.replace(' ', '_').lower()}.html",
                            "text/html",
                            key=f"dl_{idx}_{tidx}"
                        )
                
                if idx < len(articles_list) - 1:
                    st.markdown("---")
    
    # Reset
    st.markdown("---")
    if st.button("🔄 New Batch (Clear Results)", type="primary", use_container_width=True):
        st.session_state.articles = []
        st.session_state.result = None
        st.rerun()

# Footer
st.markdown("---")
st.markdown("<p style='text-align: center; color: #94a3b8; font-size: 0.875rem;'>Built for UPSC Aspirants | Powered by n8n & Gemini AI</p>", unsafe_allow_html=True)
