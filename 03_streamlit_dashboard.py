"""
Streamlit Web Dashboard - AI Plagiarism Detection
Simple interface that calls Lambda API Gateway endpoint
"""

import streamlit as st
import requests
from datetime import datetime

# API Configuration
API_ENDPOINT = "https://uvwsd5vxgc.execute-api.us-east-2.amazonaws.com/prod/analyze"

# Configure Streamlit page
st.set_page_config(
    page_title="AI Plagiarism Detection System",
    page_icon="🔍",
    layout="wide"
)

# Title
st.title("🔍 AI Plagiarism Detection System")
st.markdown("""
**Detect plagiarism and identify AI-generated content** using advanced machine learning

- 📊 Plagiarism Detection: 87% Accuracy
- 🤖 AI Detection: 81% Accuracy  
- ⚡ Fast Processing: 30-60 seconds
""")

st.divider()

# Main Interface
col1, col2 = st.columns([1, 1])

with col1:
    st.header("📤 Upload Document")
    st.markdown("Select a PDF or DOCX file to analyze")
    
    uploaded_file = st.file_uploader(
        "Choose a file",
        type=["pdf", "docx"],
        help="Supported formats: PDF, DOCX (max 50MB)"
    )
    
    if uploaded_file:
        st.success(f"✅ File selected: {uploaded_file.name}")
        st.markdown(f"**Size:** {uploaded_file.size / 1024 / 1024:.2f} MB")

with col2:
    st.header("📊 Analysis Results")
    
    if uploaded_file:
        st.info("Click 'Analyze Document' to start processing...")
    else:
        st.warning("⬅️ Please upload a document first")

st.divider()

# Analyze Button
if uploaded_file:
    if st.button("🚀 Analyze Document", use_container_width=True):
        with st.spinner("Processing document... This may take 30-60 seconds"):
            try:
                # Read file content
                file_content = uploaded_file.getvalue()
                
                # Prepare request to Lambda API
                files = {
                    'file': (uploaded_file.name, file_content, uploaded_file.type)
                }
                
                # Call Lambda via API Gateway
                response = requests.post(
                    API_ENDPOINT,
                    files=files,
                    timeout=120
                )
                
                # Parse response
                if response.status_code == 200:
                    result = response.json()
                    
                    # Display Results
                    st.success("✅ Analysis Complete!")
                    
                    # Create result display
                    results_col1, results_col2, results_col3 = st.columns(3)
                    
                    with results_col1:
                        plagiarism_score = float(result.get('plagiarism_score', 0))
                        st.metric(
                            "📊 Plagiarism Score",
                            f"{plagiarism_score:.1f}%"
                        )
                        
                        # Color indicator
                        if plagiarism_score < 20:
                            st.markdown('<div style="background-color: #ccffcc; padding: 10px; border-radius: 5px; color: #00cc00; font-weight: bold;">✅ Low Plagiarism</div>', unsafe_allow_html=True)
                        elif plagiarism_score < 50:
                            st.markdown('<div style="background-color: #fff4cc; padding: 10px; border-radius: 5px; color: #cc8800; font-weight: bold;">⚠️ Medium Plagiarism</div>', unsafe_allow_html=True)
                        else:
                            st.markdown('<div style="background-color: #ffcccc; padding: 10px; border-radius: 5px; color: #cc0000; font-weight: bold;">🚨 High Plagiarism</div>', unsafe_allow_html=True)
                    
                    with results_col2:
                        ai_score = float(result.get('ai_detection_score', 0))
                        st.metric(
                            "🤖 AI Detection Score",
                            f"{ai_score:.1f}%"
                        )
                        
                        # AI indicator
                        if ai_score < 30:
                            st.markdown('<div style="background-color: #ccffcc; padding: 10px; border-radius: 5px; color: #00cc00; font-weight: bold;">✅ Likely Human</div>', unsafe_allow_html=True)
                        elif ai_score < 70:
                            st.markdown('<div style="background-color: #fff4cc; padding: 10px; border-radius: 5px; color: #cc8800; font-weight: bold;">⚠️ Possibly AI</div>', unsafe_allow_html=True)
                        else:
                            st.markdown('<div style="background-color: #ffcccc; padding: 10px; border-radius: 5px; color: #cc0000; font-weight: bold;">🤖 Likely AI</div>', unsafe_allow_html=True)
                    
                    with results_col3:
                        matching_docs = int(result.get('similar_documents_count', 0))
                        st.metric(
                            "📚 Matching Sources",
                            f"{matching_docs}"
                        )
                    
                    # Detailed Analysis
                    st.divider()
                    st.header("📋 Detailed Analysis")
                    
                    # Display raw result
                    st.json(result)
                
                else:
                    st.error(f"❌ API Error: {response.status_code}")
                    st.text(response.text)
            
            except requests.exceptions.Timeout:
                st.error("⏱️ Request timeout. Processing took too long. Try again.")
            except requests.exceptions.ConnectionError:
                st.error("❌ Connection error. Check your internet.")
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")

# Footer
st.divider()
st.markdown("""
---
### System Information
- **API:** AWS API Gateway + Lambda
- **Database:** PostgreSQL RDS
- **Vector Search:** Pinecone
- **Models:** HuggingFace

**Powered by:** AWS Cloud Infrastructure
""")
