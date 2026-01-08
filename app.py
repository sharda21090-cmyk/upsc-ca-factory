import streamlit as st
import requests
import base64
from PIL import Image
import io
import json

# Page configuration
st.set_page_config(
    page_title="UPSC Content Factory",
    page_icon="📚",
    layout="wide"
)

# Initialize session state
if 'articles' not in st.session_state:
    st.session_state.articles = []
if 'result' not in st.session_state:
    st.session_state.result = None
if 'selected_css_theme' not in st.session_state:
    st.session_state.selected_css_theme = "Modern Clean"

# Load webhook URL from Streamlit secrets
try:
    N8N_WEBHOOK_URL = st.secrets["N8N_WEBHOOK_URL"]
    API_KEY = st.secrets.get("API_KEY", "")
except Exception as e:
    st.error("⚠️ Configuration Error: Please add N8N_WEBHOOK_URL in Streamlit Cloud secrets")
    st.stop()

# === CSS THEMES ===
CSS_THEMES = {
    "Classic Academic": """
body {
    font-family: 'Georgia', serif;
    line-height: 1.8;
    color: #2c3e50;
    max-width: 900px;
    margin: 0 auto;
    padding: 30px;
    background: #fafafa;
}
h1 {
    color: #1a1a1a;
    border-bottom: 3px solid #8b4513;
    padding-bottom: 12px;
    margin-top: 35px;
    font-size: 2.2em;
}
h2 {
    color: #333;
    margin-top: 28px;
    font-size: 1.6em;
    border-left: 4px solid #8b4513;
    padding-left: 15px;
}
h3 {
    color: #555;
    margin-top: 22px;
    font-size: 1.3em;
}
strong {
    color: #c0392b;
    font-weight: 600;
}
ul {
    margin-left: 30px;
    margin-top: 12px;
}
li {
    margin-bottom: 10px;
    line-height: 1.6;
}
p {
    margin-bottom: 15px;
}
    """,
    
    "Modern Clean": """
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
    letter-spacing: -0.5px;
}
h2 {
    color: #334155;
    font-weight: 600;
    margin-top: 32px;
    margin-bottom: 16px;
    font-size: 1.75em;
}
h3 {
    color: #475569;
    font-weight: 600;
    margin-top: 24px;
    margin-bottom: 12px;
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
    margin-top: 10px;
}
li {
    margin-bottom: 8px;
    padding-left: 8px;
}
p {
    margin-bottom: 14px;
}
    """,
    
    "Dark Mode Pro": """
body {
    font-family: 'SF Pro', 'Helvetica Neue', sans-serif;
    line-height: 1.75;
    color: #e2e8f0;
    max-width: 880px;
    margin: 0 auto;
    padding: 35px;
    background: #0f172a;
}
h1 {
    color: #f1f5f9;
    font-weight: 700;
    margin-top: 38px;
    margin-bottom: 18px;
    font-size: 2.4em;
    border-bottom: 2px solid #3b82f6;
    padding-bottom: 14px;
}
h2 {
    color: #cbd5e1;
    font-weight: 600;
    margin-top: 30px;
    margin-bottom: 14px;
    font-size: 1.7em;
}
h3 {
    color: #94a3b8;
    font-weight: 600;
    margin-top: 26px;
    margin-bottom: 10px;
    font-size: 1.4em;
}
strong {
    color: #fbbf24;
    font-weight: 600;
    background: rgba(251, 191, 36, 0.1);
    padding: 2px 6px;
    border-radius: 4px;
}
ul {
    margin-left: 28px;
    margin-top: 11px;
}
li {
    margin-bottom: 9px;
    color: #cbd5e1;
}
p {
    margin-bottom: 15px;
    color: #e2e8f0;
}
a {
    color: #60a5fa;
    text-decoration: none;
}
a:hover {
    text-decoration: underline;
}
    """
}

st.title("📚 UPSC Content Factory")
st.markdown("Generate high-quality study material for UPSC preparation")

# Sidebar
with st.sidebar:
    st.header("⚙️ Settings")
    st.info(f"🔗 Connected to n8n workflow")
    st.markdown("---")
    st.caption("💡 CSS themes are pre-configured. Select your theme in the results section after processing.")

# Main content area
col1, col2 = st.columns([2, 1])

with col1:
    st.header("📝 Add Articles")
    
    # Article input form
    with st.form(key='article_form', clear_on_submit=True):
        article_title = st.text_input("Article Title*", placeholder="Enter a descriptive title")
        
        # Input method selection
        input_method = st.radio(
            "Choose Input Method:",
            ["URL", "Raw Text", "Image Upload"],
            horizontal=True
        )
        
        article_url = ""
        raw_text = ""
        image_data = ""
        
        if input_method == "URL":
            article_url = st.text_input("Article URL*", placeholder="https://example.com/article")
        elif input_method == "Raw Text":
            raw_text = st.text_area("Paste Article Text*", height=200, placeholder="Paste your article content here...")
        else:
            uploaded_file = st.file_uploader("Upload Article Image", type=['png', 'jpg', 'jpeg'])
            if uploaded_file:
                image = Image.open(uploaded_file)
                st.image(image, caption="Uploaded Image", use_column_width=True)
                buffered = io.BytesIO()
                image.save(buffered, format="JPEG")
                image_data = base64.b64encode(buffered.getvalue()).decode()
        
        col_exam, col_subject = st.columns(2)
        with col_exam:
            exam_type = st.selectbox("Exam Type*", ["Prelims", "Mains"])
        with col_subject:
            subject = st.text_input("Subject", placeholder="e.g., Polity, Economy")
        
        focus_keyword = st.text_input("Focus Keyword (optional)", placeholder="Main concept to focus on")
        
        submit_button = st.form_submit_button("➕ Add Article", use_container_width=True)
        
        if submit_button:
            if not article_title:
                st.error("Please enter an article title")
            elif input_method == "URL" and not article_url:
                st.error("Please enter a URL")
            elif input_method == "Raw Text" and not raw_text:
                st.error("Please paste article text")
            elif input_method == "Image Upload" and not image_data:
                st.error("Please upload an image")
            else:
                article = {
                    "title": article_title,
                    "url": article_url if input_method == "URL" else "",
                    "raw_text": raw_text if input_method == "Raw Text" else "",
                    "image_data": image_data if input_method == "Image Upload" else "",
                    "exam_type": exam_type,
                    "subject": subject or "General",
                    "focus_keyword": focus_keyword or article_title
                }
                st.session_state.articles.append(article)
                st.success(f"✅ Added: {article_title}")
                st.rerun()

with col2:
    st.header("📋 Queue")
    st.markdown(f"**Total Articles:** {len(st.session_state.articles)}")
    
    if st.session_state.articles:
        for idx, article in enumerate(st.session_state.articles):
            with st.expander(f"{idx + 1}. {article['title'][:30]}..."):
                st.write(f"**Type:** {article['exam_type']}")
                st.write(f"**Subject:** {article['subject']}")
                input_type = "URL" if article['url'] else ("Text" if article['raw_text'] else "Image")
                st.write(f"**Input:** {input_type}")
                if st.button(f"🗑️ Remove", key=f"remove_{idx}"):
                    st.session_state.articles.pop(idx)
                    st.rerun()
    else:
        st.info("No articles added yet")
    
    if st.button("🧹 Clear All", type="secondary", use_container_width=True):
        st.session_state.articles = []
        st.rerun()

st.markdown("---")
col_process, col_status = st.columns([1, 3])

with col_process:
    process_button = st.button(
        "🚀 Process Articles",
        type="primary",
        disabled=len(st.session_state.articles) == 0,
        use_container_width=True
    )

with col_status:
    if len(st.session_state.articles) > 0:
        st.info(f"Ready to process {len(st.session_state.articles)} article(s)")
    else:
        st.warning("Add articles to get started")

if process_button:
    with st.spinner("🔄 Processing articles... This may take a few minutes..."):
        try:
            payload = {"articles": st.session_state.articles}
            headers = {"Content-Type": "application/json"}
            if API_KEY:
                headers["x-api-key"] = API_KEY
            
            response = requests.post(
                N8N_WEBHOOK_URL,
                json=payload,
                headers=headers,
                timeout=600
            )
            
            if response.status_code == 200:
                st.session_state.result = response.json()
                st.success("✅ Processing complete!")
                st.rerun()
            else:
                st.error(f"❌ Error: {response.status_code}")
                with st.expander("See error details"):
                    st.code(response.text)
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")

# === RESULTS SECTION ===
if st.session_state.result:
    st.markdown("---")
    st.header("✨ Results")
    
    result = st.session_state.result
    
    # Document link and metrics
    st.success(f"📄 **Study Material Created!**")
    doc_url = result.get('url') or result.get('document_url')
    
    col_link, col_metrics = st.columns([2, 1])
    
    with col_link:
        if doc_url:
            st.markdown(f"### [🔗 Open Google Doc]({doc_url})")
        else:
            st.warning("Document URL not available")
    
    with col_metrics:
        st.metric("Articles Processed", result.get('total_processed', len(result.get('articles', []))))
    
    st.caption(f"Created at: {result.get('timestamp', 'Unknown')}")
    
    # === PREVIEW SECTION ===
    st.markdown("---")
    st.subheader("👁️ Preview")
    
    preview_tab1, preview_tab2 = st.tabs(["📄 Google Doc Preview", "🌐 HTML Preview"])
    
    with preview_tab1:
        if doc_url:
            # Embed Google Doc
            embed_url = doc_url.replace('/edit', '/preview')
            st.components.v1.iframe(embed_url, height=600, scrolling=True)
        else:
            st.info("No document URL available for preview")
    
    with preview_tab2:
        articles_list = result.get('articles', [])
        if articles_list and len(articles_list) > 0:
            # CSS Theme Selector
            selected_theme = st.selectbox(
                "🎨 Select CSS Theme:",
                options=list(CSS_THEMES.keys()),
                index=list(CSS_THEMES.keys()).index(st.session_state.selected_css_theme),
                key="theme_selector"
            )
            st.session_state.selected_css_theme = selected_theme
            
            # Article selector for preview
            article_titles = [f"{i+1}. {a.get('title', 'Untitled')}" for i, a in enumerate(articles_list)]
            selected_article_idx = st.selectbox("Select Article:", range(len(articles_list)), format_func=lambda i: article_titles[i])
            
            # Generate styled HTML
            article = articles_list[selected_article_idx]
            html_content = article.get('html', '<p>No HTML content available</p>')
            styled_html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <style>{CSS_THEMES[selected_theme]}</style>
            </head>
            <body>
                {html_content}
            </body>
            </html>
            """
            
            # Live Preview
            st.components.v1.html(styled_html, height=600, scrolling=True)
        else:
            st.info("No HTML content available for preview")
    
    # === DOWNLOADS SECTION ===
    st.markdown("---")
    st.subheader("📥 Downloads")
    
    articles_list = result.get('articles', [])
    if articles_list:
        for idx, article in enumerate(articles_list):
            with st.expander(f"📄 {article.get('title', 'Untitled')} ({article.get('exam_type', 'N/A')})"):
                
                # Download buttons in columns
                col_md, col_html, col_themes = st.columns([1, 1, 2])
                
                with col_md:
                    st.download_button(
                        label="📄 Markdown",
                        data=article.get('markdown', ''),
                        file_name=f"article_{idx+1}.md",
                        mime="text/markdown",
                        use_container_width=True
                    )
                
                with col_html:
                    st.download_button(
                        label="🌐 Raw HTML",
                        data=article.get('html', ''),
                        file_name=f"article_{idx+1}.html",
                        mime="text/html",
                        use_container_width=True
                    )
                
                with col_themes:
                    st.markdown("**Styled HTML:**")
                
                # Styled HTML downloads for all 3 themes
                theme_cols = st.columns(3)
                for theme_idx, (theme_name, theme_css) in enumerate(CSS_THEMES.items()):
                    with theme_cols[theme_idx]:
                        styled_html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{article.get('title', 'UPSC Study Material')}</title>
    <style>{theme_css}</style>
</head>
<body>
{article.get('html', '')}
</body>
</html>"""
                        st.download_button(
                            label=f"🎨 {theme_name.split()[0]}",
                            data=styled_html,
                            file_name=f"article_{idx+1}_{theme_name.replace(' ', '_').lower()}.html",
                            mime="text/html",
                            use_container_width=True,
                            key=f"download_{idx}_{theme_name}"
                        )

    # Reset button
    st.markdown("---")
    if st.button("🔄 Start New Batch", type="primary", use_container_width=True):
        st.session_state.articles = []
        st.session_state.result = None
        st.rerun()

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666;'>
        <p>Built with ❤️ for UPSC Aspirants | Powered by n8n & Gemini AI</p>
    </div>
    """,
    unsafe_allow_html=True
)
