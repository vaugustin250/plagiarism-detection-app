"""
Streamlit Web Dashboard - Plagiarism Detection Results Visualization
Deployed on Streamlit Cloud or Cloud Run
"""

import streamlit as st
API_ENDPOINT = "https://uvwsd5vxgc.execute-api.us-east-2.amazonaws.com/prod/analyze"
import psycopg2
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
import boto3

load_dotenv()

# Configure Streamlit page
st.set_page_config(
    page_title="AI Plagiarism Detection System",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
    }
    .high-plagiarism {
        background-color: #ffcccc;
        color: #cc0000;
    }
    .medium-plagiarism {
        background-color: #fff4cc;
        color: #cc8800;
    }
    .low-plagiarism {
        background-color: #ccffcc;
        color: #00cc00;
    }
</style>
""", unsafe_allow_html=True)

# Database connection
@st.cache_resource
def get_db_connection():
    conn = psycopg2.connect(
        host=os.getenv('RDS_HOST'),
        port=os.getenv('RDS_PORT'),
        user=os.getenv('RDS_USER'),
        password=os.getenv('RDS_PASSWORD'),
        database=os.getenv('RDS_DB')
    )
    return conn

# S3 client for document downloads
@st.cache_resource
def get_s3_client():
    return boto3.client('s3')

# Query functions
def get_all_documents():
    """Fetch all documents with latest plagiarism reports"""
    conn = get_db_connection()
    query = """
    SELECT 
        d.id,
        d.filename,
        d.upload_time,
        d.status,
        pr.overall_plagiarism_score,
        pr.ai_detection_score,
        pr.total_similar_documents,
        pr.created_at as report_time
    FROM documents d
    LEFT JOIN plagiarism_reports pr ON d.id = pr.document_id
    ORDER BY d.upload_time DESC
    LIMIT 100
    """
    df = pd.read_sql(query, conn)
    conn.close()
    return df

def get_document_details(document_id):
    """Fetch detailed report for a specific document"""
    conn = get_db_connection()
    
    # Get document info
    doc_query = "SELECT * FROM documents WHERE id = %s"
    doc_df = pd.read_sql(doc_query, conn, params=[document_id])
    
    # Get plagiarism report
    report_query = """
    SELECT pr.* FROM plagiarism_reports pr
    WHERE pr.document_id = %s
    ORDER BY pr.created_at DESC LIMIT 1
    """
    report_df = pd.read_sql(report_query, conn, params=[document_id])
    
    # Get similar documents
    similar_query = """
    SELECT 
        sm.similarity_score,
        d.filename,
        d.upload_time
    FROM similarity_matches sm
    JOIN plagiarism_reports pr ON sm.report_id = pr.id
    JOIN documents d ON sm.matched_document_id = d.id
    WHERE pr.document_id = %s
    ORDER BY sm.similarity_score DESC
    """
    similar_df = pd.read_sql(similar_query, conn, params=[document_id])
    
    conn.close()
    
    return doc_df, report_df, similar_df

def get_statistics():
    """Get aggregate statistics"""
    conn = get_db_connection()
    query = """
    SELECT 
        COUNT(DISTINCT d.id) as total_documents,
        COUNT(DISTINCT pr.id) as total_reports,
        ROUND(AVG(pr.overall_plagiarism_score), 2) as avg_plagiarism,
        ROUND(AVG(pr.ai_detection_score), 2) as avg_ai_score,
        SUM(CASE WHEN pr.overall_plagiarism_score > 30 THEN 1 ELSE 0 END) as high_plagiarism_count
    FROM documents d
    LEFT JOIN plagiarism_reports pr ON d.id = pr.document_id
    """
    result = pd.read_sql(query, conn)
    conn.close()
    return result

def upload_document_to_s3(uploaded_file):
    """Upload file to S3 (triggers Lambda)"""
    s3 = get_s3_client()
    bucket = os.getenv('S3_BUCKET')
    
    try:
        key = f"submissions/{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uploaded_file.name}"
        s3.upload_fileobj(uploaded_file, bucket, key)
        return key
    except Exception as e:
        st.error(f"Upload failed: {str(e)}")
        return None

def get_plagiarism_color(score):
    """Return color based on plagiarism score"""
    if score > 50:
        return '#ff6b6b'  # Red
    elif score > 20:
        return '#ffd43b'  # Yellow
    else:
        return '#51cf66'  # Green

# ============================================================================
# PAGE: Dashboard
# ============================================================================

def page_dashboard():
    st.title("🔍 AI Plagiarism Detection System")
    st.markdown("Real-time academic integrity analysis powered by cloud AI")
    
    # Key Statistics
    stats = get_statistics()
    if not stats.empty:
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.metric("Total Documents", int(stats['total_documents'].iloc[0]))
        
        with col2:
            st.metric("Reports Generated", int(stats['total_reports'].iloc[0]))
        
        with col3:
            st.metric("Avg Plagiarism %", f"{stats['avg_plagiarism'].iloc[0]:.1f}%")
        
        with col4:
            st.metric("Avg AI Score", f"{stats['avg_ai_score'].iloc[0]:.1f}%")
        
        with col5:
            st.metric("High Plagiarism Cases", int(stats['high_plagiarism_count'].iloc[0]))
    
    st.divider()
    
    # Recent Documents Table
    st.subheader("📋 Recent Document Analysis")
    
    df = get_all_documents()
    if not df.empty:
        # Format for display
        df_display = df.copy()
        df_display['Status'] = df_display['status'].str.upper()
        df_display['Plagiarism %'] = df_display['overall_plagiarism_score'].fillna(0).apply(lambda x: f"{x:.1f}%")
        df_display['AI Score %'] = df_display['ai_detection_score'].fillna(0).apply(lambda x: f"{x:.1f}%")
        df_display['Similar Docs'] = df_display['total_similar_documents'].fillna(0).astype(int)
        df_display['Upload Time'] = pd.to_datetime(df_display['upload_time']).dt.strftime('%Y-%m-%d %H:%M')
        
        # Select columns to display
        display_cols = ['id', 'filename', 'Upload Time', 'Status', 'Plagiarism %', 'AI Score %', 'Similar Docs']
        st.dataframe(df_display[display_cols], use_container_width=True)
    else:
        st.info("No documents analyzed yet. Upload your first document!")
    
    # Charts
    st.divider()
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Plagiarism Score Distribution")
        if not df.empty:
            plagiarism_data = df[df['overall_plagiarism_score'].notna()]['overall_plagiarism_score']
            if not plagiarism_data.empty:
                fig = go.Figure(data=[go.Histogram(x=plagiarism_data, nbinsx=20)])
                fig.update_layout(
                    xaxis_title="Plagiarism Score (%)",
                    yaxis_title="Number of Documents",
                    showlegend=False,
                    height=400
                )
                st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("🤖 AI Detection Distribution")
        if not df.empty:
            ai_data = df[df['ai_detection_score'].notna()]['ai_detection_score']
            if not ai_data.empty:
                fig = go.Figure(data=[go.Histogram(x=ai_data, nbinsx=20)])
                fig.update_layout(
                    xaxis_title="AI Detection Score (%)",
                    yaxis_title="Number of Documents",
                    showlegend=False,
                    height=400
                )
                st.plotly_chart(fig, use_container_width=True)

# ============================================================================
# PAGE: Upload & Analyze
# ============================================================================

def page_upload():
    st.title("📤 Upload Document for Analysis")
    
    st.markdown("""
    Upload your assignment, research paper, or document to analyze:
    - Plagiarism detection
    - AI-generated content detection
    - Similarity matching with existing documents
    """)
    
    uploaded_file = st.file_uploader(
        "Choose a PDF or DOCX file",
        type=['pdf', 'docx'],
        help="Supported formats: PDF, DOCX"
    )
    
    if uploaded_file:
        st.success(f"✅ File selected: {uploaded_file.name}")
        
        col1, col2 = st.columns([1, 3])
        with col1:
            if st.button("🚀 Analyze Now", use_container_width=True):
                with st.spinner("Processing document..."):
                    # Upload to S3
                    s3_key = upload_document_to_s3(uploaded_file)
                    
                    if s3_key:
                        st.success("✅ Document uploaded successfully!")
                        st.info("Analysis is processing. Lambda function has been triggered. Check results in 30-60 seconds.")
                        
                        # Show expected results preview
                        st.markdown("### 📋 What You'll Get:")
                        st.markdown("""
                        - **Plagiarism Score**: Overall similarity percentage
                        - **AI Detection Score**: Confidence that content is AI-generated
                        - **Similar Documents**: List of matching documents with scores
                        - **Detailed Report**: Exportable plagiarism report
                        """)

# ============================================================================
# PAGE: Detailed Report
# ============================================================================

def page_detailed_report():
    st.title("📄 Detailed Plagiarism Report")
    
    # Select document
    df = get_all_documents()
    if df.empty:
        st.warning("No documents available. Please upload a document first.")
        return
    
    # Filter completed reports only
    df_completed = df[df['status'] == 'completed']
    if df_completed.empty:
        st.warning("No completed reports available yet.")
        return
    
    selected_doc = st.selectbox(
        "Select Document",
        options=df_completed['id'].tolist(),
        format_func=lambda x: f"{df_completed[df_completed['id']==x]['filename'].values[0]} (ID: {x})"
    )
    
    if selected_doc:
        doc_df, report_df, similar_df = get_document_details(selected_doc)
        
        if report_df.empty:
            st.warning("No report generated for this document yet.")
            return
        
        # Header with scores
        col1, col2, col3 = st.columns(3)
        
        plagiarism_score = report_df['overall_plagiarism_score'].iloc[0]
        ai_score = report_df['ai_detection_score'].iloc[0]
        
        with col1:
            # Plagiarism gauge
            fig_plag = go.Figure(go.Indicator(
                mode="gauge+number",
                value=plagiarism_score,
                title={'text': "Plagiarism Score"},
                domain={'x': [0, 1], 'y': [0, 1]},
                gauge={
                    'axis': {'range': [0, 100]},
                    'bar': {'color': get_plagiarism_color(plagiarism_score)},
                    'steps': [
                        {'range': [0, 20], 'color': "#e8f5e9"},
                        {'range': [20, 50], 'color': "#fff3e0"},
                        {'range': [50, 100], 'color': "#ffebee"}
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': 30
                    }
                }
            ))
            fig_plag.update_layout(height=350)
            st.plotly_chart(fig_plag, use_container_width=True)
        
        with col2:
            # AI Detection gauge
            fig_ai = go.Figure(go.Indicator(
                mode="gauge+number",
                value=ai_score,
                title={'text': "AI Detection Score"},
                domain={'x': [0, 1], 'y': [0, 1]},
                gauge={
                    'axis': {'range': [0, 100]},
                    'bar': {'color': get_plagiarism_color(ai_score)},
                    'steps': [
                        {'range': [0, 20], 'color': "#e8f5e9"},
                        {'range': [20, 50], 'color': "#fff3e0"},
                        {'range': [50, 100], 'color': "#ffebee"}
                    ]
                }
            ))
            fig_ai.update_layout(height=350)
            st.plotly_chart(fig_ai, use_container_width=True)
        
        with col3:
            st.markdown("### 📊 Report Summary")
            st.metric("Similar Documents Found", int(report_df['total_similar_documents'].iloc[0]))
            st.metric("Report Generated", report_df['created_at'].iloc[0].strftime('%Y-%m-%d %H:%M:%S'))
        
        st.divider()
        
        # Similar Documents
        st.subheader("🔗 Similar Documents")
        if not similar_df.empty:
            similar_display = similar_df.copy()
            similar_display['Similarity'] = (similar_display['similarity_score'] * 100).apply(lambda x: f"{x:.1f}%")
            similar_display['Upload Time'] = pd.to_datetime(similar_display['upload_time']).dt.strftime('%Y-%m-%d %H:%M')
            
            st.dataframe(
                similar_display[['filename', 'Similarity', 'Upload Time']],
                use_container_width=True
            )
        else:
            st.info("No similar documents found.")
        
        st.divider()
        
        # Verdict
        st.subheader("⚖️ Integrity Verdict")
        
        if plagiarism_score > 50:
            status = "🚨 HIGH PLAGIARISM RISK"
            recommendation = "Manual review recommended. Investigate similar documents."
        elif plagiarism_score > 20:
            status = "⚠️ MODERATE PLAGIARISM RISK"
            recommendation = "Review similar documents to ensure proper citation."
        else:
            status = "✅ LOW PLAGIARISM RISK"
            recommendation = "Document appears to be original work."
        
        if ai_score > 50:
            ai_status = "🤖 LIKELY AI-GENERATED"
        elif ai_score > 20:
            ai_status = "⚠️ POSSIBLE AI ASSISTANCE"
        else:
            ai_status = "✅ LIKELY HUMAN-WRITTEN"
        
        st.markdown(f"**Plagiarism Status:** {status}")
        st.markdown(f"**AI Detection:** {ai_status}")
        st.markdown(f"**Recommendation:** {recommendation}")

# ============================================================================
# PAGE: Analytics
# ============================================================================

def page_analytics():
    st.title("📈 System Analytics")
    
    df = get_all_documents()
    if df.empty:
        st.warning("No data available yet.")
        return
    
    # Filter only completed reports
    df = df[df['status'] == 'completed'].copy()
    if df.empty:
        st.warning("No completed reports available.")
        return
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Plagiarism by Time")
        df['date'] = pd.to_datetime(df['upload_time']).dt.date
        daily_plagiarism = df.groupby('date')['overall_plagiarism_score'].mean()
        
        fig = px.line(daily_plagiarism.reset_index(), x='date', y='overall_plagiarism_score')
        fig.update_layout(
            title="Average Plagiarism Score Over Time",
            xaxis_title="Date",
            yaxis_title="Average Plagiarism %",
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Risk Distribution")
        risk_counts = pd.cut(df['overall_plagiarism_score'], 
                            bins=[0, 20, 50, 100], 
                            labels=['Low', 'Medium', 'High']).value_counts()
        
        fig = px.pie(
            values=risk_counts.values,
            names=risk_counts.index,
            color_discrete_map={'Low': '#51cf66', 'Medium': '#ffd43b', 'High': '#ff6b6b'}
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)

# ============================================================================
# Main App
# ============================================================================

def main():
    # Sidebar navigation
    st.sidebar.title("🎯 Navigation")
    page = st.sidebar.radio(
        "Select Page",
        ["Dashboard", "Upload & Analyze", "Detailed Report", "Analytics"],
        icons=["📊", "📤", "📄", "📈"]
    )
    
    st.sidebar.divider()
    st.sidebar.markdown("### ℹ️ About")
    st.sidebar.markdown("""
    **AI Plagiarism Detection System**
    
    A cloud-native platform for academic integrity verification.
    
    **Technology Stack:**
    - AWS Lambda (Processing)
    - Pinecone (Vector DB)
    - PostgreSQL RDS (Storage)
    - Streamlit (Dashboard)
    """)
    
    # Route to selected page
    if page == "Dashboard":
        page_dashboard()
    elif page == "Upload & Analyze":
        page_upload()
    elif page == "Detailed Report":
        page_detailed_report()
    elif page == "Analytics":
        page_analytics()

if __name__ == "__main__":
    main()
# Auto-rebuild trigger
