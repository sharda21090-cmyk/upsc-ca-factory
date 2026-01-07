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

# Load webhook URL from Streamlit secrets
try:
    N8N_WEBHOOK_URL = st.secrets["N8N_WEBHOOK_URL"]
    API_KEY = st.secrets.get("API_KEY", "")
except Exception as e:
    st.error("⚠️ Configuration Error: Please add N8N_WEBHOOK_URL in Streamlit Cloud secrets")
    st.stop()

st.title("📚 UPSC Content Factory")
st.markdown("Generate high-quality study material for UPSC preparation")

# Sidebar for configuration
with st.sidebar:
    st.header("⚙️ Settings")
    st.info(f"🔗 Connected to: {N8N_WEBHOOK_URL[:50]}...")
    
    default_css = st.text_area(
        "Custom CSS (optional)",
        value="""
body {
    font-family: 'Georgia', serif;
    line-height: 1.8;
    color: #333;
    max-width: 900px;
    margin: 0 auto;
    padding: 20px;
}
h1 {
    color: #2c3e50;
    border-bottom: 3px solid #3498db;
    padding-bottom: 10px;
    margin-top: 30px;
}
h3 {
    color: #34495e;
    margin-top: 25px;
    margin-bottom: 10px;
}
strong {
    color: #e74c3c;
    font-weight: 600;
}
ul {
    margin-left: 25px;
    margin-top: 10px;
}
li {
    margin-bottom: 8px;
}
        """,
        height=200
    )

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
                # Convert to base64
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
            # Validation
            if not article_title:
                st.error("Please enter an article title")
            elif input_method == "URL" and not article_url:
                st.error("Please enter a URL")
            elif input_method == "Raw Text" and not raw_text:
                st.error("Please paste article text")
            elif input_method == "Image Upload" and not image_data:
                st.error("Please upload an image")
            else:
                # Add to session state
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

# Process button
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

# Process articles
if process_button:
    with st.spinner("🔄 Processing articles... This may take a few minutes..."):
        try:
            # Prepare payload
            payload = {
                "articles": st.session_state.articles,
                "options": {
                    "css": default_css
                }
            }
            
            # Prepare headers
            headers = {"Content-Type": "application/json"}
            if API_KEY:
                headers["x-api-key"] = API_KEY
            
            # Send to n8n webhook
            response = requests.post(
                N8N_WEBHOOK_URL,
                json=payload,
                headers=headers,
                timeout=300
            )
            
            if response.status_code == 200:
                st.session_state.result = response.json()
                st.success("✅ Processing complete!")
                st.rerun()
            else:
                st.error(f"❌ Error: {response.status_code}")
                with st.expander("See error details"):
                    st.code(response.text)
        except requests.exceptions.Timeout:
            st.error("⏱️ Request timed out. Try processing fewer articles or check your n8n server.")
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")

# Display results
if st.session_state.result:
    st.markdown("---")
    st.header("✨ Results")
    
    result = st.session_state.result
    
    # Google Doc link
    st.success(f"📄 **Study Material Created!**")
   # Use .get() to avoid crashing if the key is missing
doc_url = result.get('url') or result.get('document_url')
if doc_url:
    st.markdown(f"### [🔗 Open Google Doc]({doc_url})")
else:
    st.error("Document URL not found in response.")
    
    col_info1, col_info2 = st.columns(2)
    with col_info1:
        st.metric("Articles Processed", result['total_processed'])
    with col_info2:
        st.metric("Document ID", result['document_id'][:15] + "...")
    
    st.caption(f"Created at: {result['timestamp']}")
    
    # Download options
    st.markdown("---")
    st.subheader("📥 Downloads")
    
    tabs = st.tabs([f"Article {i+1}" for i in range(len(result['articles']))])
    
    for idx, (tab, article) in enumerate(zip(tabs, result['articles'])):
        with tab:
            st.markdown(f"### {article['title']}")
            st.markdown(f"**Type:** {article['exam_type']}")
            
            col_md, col_html, col_styled = st.columns(3)
            
            with col_md:
                # Download Markdown
                st.download_button(
                    label="📄 Download Markdown",
                    data=article['markdown'],
                    file_name=f"article_{idx+1}.md",
                    mime="text/markdown",
                    use_container_width=True
                )
            
            with col_html:
                # Download Raw HTML
                st.download_button(
                    label="🌐 Download HTML",
                    data=article['html'],
                    file_name=f"article_{idx+1}.html",
                    mime="text/html",
                    use_container_width=True
                )
            
            with col_styled:
                # Download Styled HTML
                styled_html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{article['title']}</title>
    <style>
        {default_css}
    </style>
</head>
<body>
    {article['html']}
</body>
</html>"""
                st.download_button(
                    label="🎨 Download Styled HTML",
                    data=styled_html,
                    file_name=f"article_{idx+1}_styled.html",
                    mime="text/html",
                    use_container_width=True
                )
            
            # Preview
            with st.expander("👁️ Preview HTML"):
                st.components.v1.html(article['html'], height=400, scrolling=True)
    
    # New batch button
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
