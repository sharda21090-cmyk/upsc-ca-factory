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
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for professional design
st.markdown("""
<style>
    /* Main theme colors */
    :root {
        --primary: #4F46E5;
        --primary-dark: #4338CA;
        --secondary: #10B981;
        --accent: #F59E0B;
        --danger: #EF4444;
        --bg-light: #F9FAFB;
        --bg-card: #FFFFFF;
        --text-primary: #111827;
        --text-secondary: #6B7280;
        --border: #E5E7EB;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Main container styling */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1400px;
    }
    
    /* Header gradient */
    .gradient-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2.5rem 2rem;
        border-radius: 16px;
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.2);
    }
    
    .gradient-header h1 {
        color: white;
        font-size: 2.5rem;
        font-weight: 700;
        margin: 0;
        text-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }
    
    .gradient-header p {
        color: rgba(255,255,255,0.9);
        font-size: 1.1rem;
        margin-top: 0.5rem;
    }
    
    /* Card styling */
    .custom-card {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        border: 1px solid var(--border);
        margin-bottom: 1.5rem;
    }
    
    .custom-card h3 {
        color: var(--text-primary);
        font-size: 1.25rem;
        font-weight: 600;
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    /* Stats card */
    .stat-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 12px;
        text-align: center;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }
    
    .stat-card h2 {
        font-size: 2.5rem;
        font-weight: 700;
        margin: 0;
    }
    
    .stat-card p {
        margin: 0.5rem 0 0 0;
        opacity: 0.9;
        font-size: 0.9rem;
    }
    
    /* Queue item styling */
    .queue-item {
        background: var(--bg-light);
        border-left: 4px solid var(--primary);
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 0.75rem;
    }
    
    .queue-item h4 {
        margin: 0 0 0.5rem 0;
        color: var(--text-primary);
        font-size: 1rem;
    }
    
    .queue-item .meta {
        display: flex;
        gap: 1rem;
        font-size: 0.85rem;
        color: var(--text-secondary);
    }
    
    /* Badge styling */
    .badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 999px;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.025em;
    }
    
    .badge-prelims {
        background: #FEF3C7;
        color: #92400E;
    }
    
    .badge-mains {
        background: #DBEAFE;
        color: #1E40AF;
    }
    
    .badge-success {
        background: #D1FAE5;
        color: #065F46;
    }
    
    /* Process button styling */
    .stButton > button {
        background: linear-gradient(135deg, #10B981 0%, #059669 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        font-size: 1rem;
        box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(16, 185, 129, 0.4);
    }
    
    /* Empty state */
    .empty-state {
        text-align: center;
        padding: 3rem 2rem;
        color: var(--text-secondary);
    }
    
    .empty-state svg {
        width: 80px;
        height: 80px;
        margin-bottom: 1rem;
        opacity: 0.3;
    }
    
    /* Progress steps */
    .progress-steps {
        display: flex;
        justify-content: space-between;
        margin: 2rem 0;
        padding: 0;
    }
    
    .step {
        flex: 1;
        text-align: center;
        position: relative;
    }
    
    .step-number {
        width: 40px;
        height: 40px;
        background: var(--bg-light);
        border: 2px solid var(--border);
        border-radius: 50%;
        display:flex;
        align-items: center;
        justify-content: center;
        margin: 0 auto 0.5rem;
        font-weight: 600;
        color: var(--text-secondary);
    }
    
    .step.active .step-number {
        background: var(--primary);
        border-color: var(--primary);
        color: white;
    }
    
    .step.complete .step-number {
        background: var(--secondary);
        border-color: var(--secondary);
        color: white;
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.5rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: var(--bg-light);
        border-radius: 8px 8px 0 0;
        padding: 0.75rem 1.5rem;
        font-weight: 500;
    }
    
    .stTabs [aria-selected="true"] {
        background: white;
        border-bottom: 2px solid var(--primary);
    }
    
    /* Download section */
    .download-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 1rem;
        margin-top: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'articles' not in st.session_state:
    st.session_state.articles = []
if 'result' not in st.session_state:
    st.session_state.result = None
if 'selected_css_theme' not in st.session_state:
    st.session_state.selected_css_theme = "Modern Clean"
if 'current_step' not in st.session_state:
    st.session_state.current_step = 1

# Load webhook URL
try:
    N8N_WEBHOOK_URL = st.secrets["N8N_WEBHOOK_URL"]
    API_KEY = st.secrets.get("API_KEY", "")
except Exception as e:
    st.error("⚠️ Please configure N8N_WEBHOOK_URL in Streamlit secrets")
    st.stop()

# Load CSS themes function (keep existing function)
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
ul {
    margin-left: 25px;
}
li {
    margin-bottom: 8px;
}
p {
    margin-bottom: 14px;
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
                with open(css_path, 'r', encoding='utf-8') as f:
                    themes[theme_name] = f.read()
            else:
                if theme_name == "Modern Clean":
                    themes[theme_name] = default_theme
        except Exception as e:
            if theme_name == "Modern Clean":
                themes[theme_name] = default_theme
    
    if not themes:
        themes["Modern Clean"] = default_theme
    
    return themes

CSS_THEMES = load_css_themes()

def process_html_for_A4(html_content):
    """Keep existing function"""
    try:
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html_content, 'html.parser')
        # ... existing processing logic ...
        return str(soup)
    except:
        return html_content

# ===========================================
# HEADER
# ===========================================
st.markdown("""
<div class="gradient-header">
    <h1>📚 UPSC Content Factory</h1>
    <p>Transform news articles into exam-ready study material in seconds</p>
</div>
""", unsafe_allow_html=True)

# ===========================================
# PROGRESS STEPS
# ===========================================
step_classes = ["complete" if st.session_state.current_step > i else ("active" if st.session_state.current_step == i else "") 
                for i in range(1, 4)]

st.markdown(f"""
<div class="progress-steps">
    <div class="step {step_classes[0]}">
        <div class="step-number">1</div>
        <div>Add Articles</div>
    </div>
    <div class="step {step_classes[1]}">
        <div class="step-number">2</div>
        <div>Process</div>
    </div>
    <div class="step {step_classes[2]}">
        <div class="step-number">3</div>
        <div>Download</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ===========================================
# MAIN CONTENT
# ===========================================

if not st.session_state.result:
    # STEP 1 & 2: Add Articles and Process
    col_left, col_right = st.columns([2, 1])
    
    with col_left:
        st.markdown('<div class="custom-card">', unsafe_allow_html=True)
        st.markdown("### 📝 Add New Article")
        
        with st.form(key='article_form', clear_on_submit=True):
            article_title = st.text_input("Article Title*", placeholder="Enter a descriptive title")
            
            input_method = st.radio(
                "Input Method:",
                ["🔗 URL", "📄 Raw Text", "📸 Image"],
                horizontal=True
            )
            
            article_url = ""
            raw_text = ""
            image_data = ""
            
            if input_method == "🔗 URL":
                article_url = st.text_input("Article URL", placeholder="https://example.com/article")
            elif input_method == "📄 Raw Text":
                raw_text = st.text_area("Paste Article Content", height=150, 
                                       placeholder="Paste your article text here...")
            else:
                uploaded_file = st.file_uploader("Upload Image", type=['png', 'jpg', 'jpeg'])
                if uploaded_file:
                    image = Image.open(uploaded_file)
                    st.image(image, caption="Preview", use_column_width=True)
                    buffered = io.BytesIO()
                    image.save(buffered, format="JPEG")
                    image_data = base64.b64encode(buffered.getvalue()).decode()
            
            col1, col2 = st.columns(2)
            with col1:
                exam_type = st.selectbox("Exam Type*", ["Prelims", "Mains"])
            with col2:
                subject = st.text_input("Subject", placeholder="e.g., Polity, Economy")
            
            focus_keyword = st.text_input("Focus Keyword (optional)", 
                                         placeholder="Main concept to emphasize")
            
            submit_col1, submit_col2, submit_col3 = st.columns([2, 1, 1])
            with submit_col1:
                submit_button = st.form_submit_button("➕ Add to Queue", 
                                                      use_container_width=True,
                                                      type="primary")
            
            if submit_button:
                if not article_title:
                    st.error("Please enter an article title")
                elif input_method == "🔗 URL" and not article_url:
                    st.error("Please enter a URL")
                elif input_method == "📄 Raw Text" and not raw_text:
                    st.error("Please paste article text")
                elif input_method == "📸 Image" and not image_data:
                    st.error("Please upload an image")
                else:
                    article = {
                        "title": article_title,
                        "url": article_url if input_method == "🔗 URL" else "",
                        "raw_text": raw_text if input_method == "📄 Raw Text" else "",
                        "image_data": image_data if input_method == "📸 Image" else "",
                        "exam_type": exam_type,
                        "subject": subject or "General",
                        "focus_keyword": focus_keyword or article_title
                    }
                    st.session_state.articles.append(article)
                    st.success(f"✅ Added: {article_title}")
                    st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col_right:
        # Queue Card
        st.markdown('<div class="custom-card">', unsafe_allow_html=True)
        st.markdown(f"### 📋 Queue ({len(st.session_state.articles)})")
        
        if st.session_state.articles:
            for idx, article in enumerate(st.session_state.articles):
                badge_class = "badge-prelims" if article['exam_type'] == "Prelims" else "badge-mains"
                input_type = "URL" if article['url'] else ("Text" if article['raw_text'] else "Image")
                
                st.markdown(f"""
                <div class="queue-item">
                    <h4>{idx + 1}. {article['title'][:40]}...</h4>
                    <div class="meta">
                        <span class="badge {badge_class}">{article['exam_type']}</span>
                        <span>📚 {article['subject']}</span>
                        <span>📌 {input_type}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                if st.button("🗑️ Remove", key=f"remove_{idx}", use_container_width=True):
                    st.session_state.articles.pop(idx)
                    st.rerun()
                
                st.markdown("<br>", unsafe_allow_html=True)
            
            if st.button("🧹 Clear All", type="secondary", use_container_width=True):
                st.session_state.articles = []
                st.rerun()
        else:
            st.markdown("""
            <div class="empty-state">
                <div style="font-size: 3rem; margin-bottom: 1rem;">📝</div>
                <p>No articles in queue</p>
                <p style="font-size: 0.85rem;">Add an article to get started</p>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Stats Card
        if len(st.session_state.articles) > 0:
            st.markdown(f"""
            <div class="stat-card">
                <h2>{len(st.session_state.articles)}</h2>
                <p>Articles Ready to Process</p>
            </div>
            """, unsafe_allow_html=True)
    
    # Process Button
    st.markdown("<br>", unsafe_allow_html=True)
    if len(st.session_state.articles) > 0:
        if st.button(f"🚀 Process {len(st.session_state.articles)} Article(s)", 
                     type="primary", use_container_width=True):
            with st.spinner("⏳ Processing articles... This may take a few minutes..."):
                try:
                    payload = {"articles": st.session_state.articles}
                    headers = {"Content-Type": "application/json"}
                    if API_KEY:
                        headers["x-api-key"] = API_KEY
                    
                    response = requests.post(N8N_WEBHOOK_URL, json=payload, 
                                           headers=headers, timeout=600)
                    
                    if response.status_code == 200:
                        st.session_state.result = response.json()
                        st.session_state.current_step = 3
                        st.success("✅ Processing complete!")
                        st.rerun()
                    else:
                        st.error(f"❌ Error: {response.status_code}")
                        with st.expander("Error Details"):
                            st.code(response.text)
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")

else:
    # STEP 3: Results and Downloads
    result = st.session_state.result
    doc_url = result.get('url') or result.get('document_url')
    
    # Success Banner
    st.success("🎉 **Study Material Generation Complete!**")
    
    col_link, col_stats = st.columns([3, 1])
    
    with col_link:
        if doc_url:
            st.markdown(f"### [📄 Open Google Doc]({doc_url})")
        else:
            st.warning("Document URL not available")
    
    with col_stats:
        total = result.get('total_processed', len(result.get('articles', [])))
        st.markdown(f"""
        <div class="stat-card">
            <h2>{total}</h2>
            <p>Articles Processed</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Tabs for Preview and Downloads
    tab1, tab2, tab3 = st.tabs(["📄 Google Doc", "🌐 HTML Preview", "📥 Downloads"])
    
    with tab1:
        if doc_url:
            embed_url = doc_url.replace('/edit', '/preview')
            st.components.v1.iframe(embed_url, height=700, scrolling=True)
        else:
            st.info("No document URL available")
    
    with tab2:
        articles_list = result.get('articles', [])
        if articles_list:
            col_sel1, col_sel2 = st.columns(2)
            
            with col_sel1:
                selected_theme = st.selectbox(
                    "🎨 CSS Theme:",
                    options=list(CSS_THEMES.keys()),
                    index=0
                )
            
            with col_sel2:
                article_titles = [f"{i+1}. {a.get('title', 'Untitled')}" 
                                 for i, a in enumerate(articles_list)]
                selected_article_idx = st.selectbox(
                    "📄 Select Article:", 
                    range(len(articles_list)), 
                    format_func=lambda i: article_titles[i]
                )
            
            article = articles_list[selected_article_idx]
            html_content = article.get('html', '')
            
            if html_content:
                if selected_theme == "A4 Standard":
                    html_content = process_html_for_A4(html_content)
                    wrapped_html = f'<div class="page"><article class="book"><div class="prose">{html_content}</div></article></div>'
                elif selected_theme == "Poster Style":
                    wrapped_html = f'''<section class="poster">
  <div class="print-header"></div>
  <div class="poster-content">
    {html_content}
  </div>
</section>'''
                else:
                    wrapped_html = html_content
                
                styled_html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>{CSS_THEMES[selected_theme]}</style>
</head>
<body>{wrapped_html}</body>
</html>"""
                
                st.components.v1.html(styled_html, height=700, scrolling=True)
            else:
                st.warning("No HTML content available")
    
    with tab3:
        articles_list = result.get('articles', [])
        if articles_list:
            for idx, article in enumerate(articles_list):
                st.markdown(f"### 📄 {article.get('title', 'Untitled')}")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.download_button(
                        "📄 Markdown",
                        data=article.get('markdown', ''),
                        file_name=f"article_{idx+1}.md",
                        mime="text/markdown",
                        use_container_width=True,
                        key=f"md_{idx}"
                    )
                
                with col2:
                    st.download_button(
                        "🌐 Raw HTML",
                        data=article.get('html', ''),
                        file_name=f"article_{idx+1}.html",
                        mime="text/html",
                        use_container_width=True,
                        key=f"html_{idx}"
                    )
                
                with col3:
                    st.write("**Styled HTML:**")
                
                # Themed downloads
                theme_cols = st.columns(3)
                for theme_idx, (theme_name, theme_css) in enumerate(CSS_THEMES.items()):
                    with theme_cols[theme_idx]:
                        raw_html = article.get('html', '')
                        
                        if theme_name == "A4 Standard":
                            raw_html = process_html_for_A4(raw_html)
                            body_html = f'<div class="page"><article class="book"><div class="prose">{raw_html}</div></article></div>'
                        elif theme_name == "Poster Style":
                            body_html = f'''<section class="poster">
  <div class="print-header"></div>
  <div class="poster-content">
    {raw_html}
  </div>
</section>'''
                        else:
                            body_html = raw_html
                        
                        styled_html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{article.get('title', 'UPSC Study Material')}</title>
    <style>{theme_css}</style>
</head>
<body>{body_html}</body>
</html>"""
                        
                        st.download_button(
                            f"🎨 {theme_name.split()[0]}",
                            data=styled_html,
                            file_name=f"article_{idx+1}_{theme_name.replace(' ', '_').lower()}.html",
                            mime="text/html",
                            use_container_width=True,
                            key=f"download_{idx}_{theme_name}"
                        )
                
                st.markdown("---")
    
    # Reset Button
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🔄 Start New Batch", type="primary", use_container_width=True):
        st.session_state.articles = []
        st.session_state.result = None
        st.session_state.current_step = 1
        st.rerun()

# Footer
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("""
<div style='text-align: center; color: #9CA3AF; font-size: 0.9rem; padding: 2rem 0;'>
    <p>Built with ❤️ for UPSC Aspirants | Powered by n8n & Gemini AI</p>
    <p style='font-size: 0.8rem; margin-top: 0.5rem;'>© 2026 UPSC Content Factory. All rights reserved.</p>
</div>
""", unsafe_allow_html=True)
