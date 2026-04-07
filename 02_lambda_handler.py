"""
AWS Lambda Handler - Document Processing & Plagiarism Detection
Triggered by S3 upload events
"""

import json
import boto3
import psycopg2
import PyPDF2
import requests
from datetime import datetime
from pinecone import Pinecone
import os
from dotenv import load_dotenv

load_dotenv()

# Initialize AWS and external clients
s3_client = boto3.client('s3')
secrets_client = boto3.client('secretsmanager')

# Get secrets
def get_secret(secret_name):
    try:
        response = secrets_client.get_secret_value(SecretId=secret_name)
        return response['SecretString']
    except Exception as e:
        print(f"Error retrieving secret {secret_name}: {str(e)}")
        return None

# Database connection
def get_db_connection():
    return psycopg2.connect(
        host=os.getenv('RDS_HOST'),
        port=os.getenv('RDS_PORT'),
        user=os.getenv('RDS_USER'),
        password=os.getenv('RDS_PASSWORD'),
        database=os.getenv('RDS_DB')
    )

# Initialize Pinecone
def init_pinecone():
    api_key = get_secret('plagiarism/pinecone-api-key')
    pc = Pinecone(api_key=api_key)
    return pc.Index(os.getenv('PINECONE_INDEX_NAME'))

# Extract text from PDF/DOCX
def extract_text_from_document(s3_bucket, s3_key):
    """Extract text from PDF or DOCX file in S3"""
    try:
        # Download file from S3
        response = s3_client.get_object(Bucket=s3_bucket, Key=s3_key)
        file_content = response['Body'].read()
        
        # Detect file type
        if s3_key.lower().endswith('.pdf'):
            text = extract_from_pdf(file_content)
        elif s3_key.lower().endswith('.docx'):
            text = extract_from_docx(file_content)
        else:
            text = file_content.decode('utf-8', errors='ignore')
        
        return text
    except Exception as e:
        print(f"Error extracting text: {str(e)}")
        return None

def extract_from_pdf(file_content):
    """Extract text from PDF bytes"""
    from io import BytesIO
    pdf_reader = PyPDF2.PdfReader(BytesIO(file_content))
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text

def extract_from_docx(file_content):
    """Extract text from DOCX bytes"""
    from zipfile import ZipFile
    from io import BytesIO
    from xml.etree import ElementTree as ET
    
    text = []
    with ZipFile(BytesIO(file_content)) as docx:
        xml_content = docx.read('word/document.xml')
        tree = ET.XML(xml_content)
        
        # Extract text from paragraphs
        namespace = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
        for paragraph in tree.findall('.//w:p', namespace):
            para_text = ''.join(
                node.text for node in paragraph.findall('.//w:t', namespace)
                if node.text
            )
            text.append(para_text)
    
    return '\n'.join(text)

# Generate embeddings using HuggingFace
def generate_embeddings(text, chunk_size=512):
    """Generate embeddings for text using HuggingFace API"""
    hf_token = get_secret('plagiarism/huggingface-token')
    
    # Use HuggingFace Inference API for embeddings
    api_url = "https://api-inference.huggingface.co/pipeline/feature-extraction"
    
    headers = {"Authorization": f"Bearer {hf_token}"}
    
    # Chunk text if too long
    sentences = text.split('.')
    all_embeddings = []
    
    for i in range(0, len(sentences), 5):  # Group sentences
        chunk = '. '.join(sentences[i:i+5])
        
        try:
            response = requests.post(
                api_url,
                headers=headers,
                json={"inputs": chunk},
                timeout=30
            )
            
            if response.status_code == 200:
                embeddings = response.json()
                all_embeddings.append(embeddings)
        except Exception as e:
            print(f"Embedding error: {str(e)}")
    
    # Average embeddings (dimension: 384 for all-MiniLM-L6-v2)
    if all_embeddings:
        import numpy as np
        avg_embedding = np.mean(all_embeddings, axis=0).tolist()
        return avg_embedding
    
    return None

# Detect AI-generated content using statistical analysis
def detect_ai_generated(text):
    """
    Detect if content is AI-generated using perplexity analysis
    Returns confidence score 0-100
    """
    # Simple heuristics for AI detection:
    # 1. Check for suspicious patterns
    # 2. Analyze sentence structure uniformity
    # 3. Check vocabulary diversity
    
    ai_indicators = 0
    total_checks = 0
    
    # Check 1: Excessive formal language
    formal_words = ['furthermore', 'moreover', 'consequently', 'thereby', 'hence']
    formal_count = sum(text.lower().count(word) for word in formal_words)
    total_checks += 1
    if formal_count > len(text.split()) / 50:  # More than 2% formal words
        ai_indicators += 0.3
    
    # Check 2: Sentence length uniformity
    sentences = text.split('.')
    if len(sentences) > 5:
        sentence_lengths = [len(s.split()) for s in sentences]
        avg_length = sum(sentence_lengths) / len(sentence_lengths)
        variance = sum((x - avg_length) ** 2 for x in sentence_lengths) / len(sentence_lengths)
        if variance < 5:  # Very uniform sentence length
            ai_indicators += 0.2
    
    # Check 3: Low contraction usage (AI avoids contractions)
    contractions = ["don't", "can't", "won't", "isn't", "doesn't"]
    contraction_count = sum(text.lower().count(c) for c in contractions)
    total_checks += 1
    if contraction_count < len(text.split()) / 200:
        ai_indicators += 0.2
    
    # Check 4: Lack of personal pronouns/voice
    personal_pronouns = ['i ', ' i ', 'me ', ' me ', 'my ', 'we ', 'our ']
    pronoun_count = sum(text.lower().count(p) for p in personal_pronouns)
    total_checks += 1
    if pronoun_count < len(text.split()) / 100:
        ai_indicators += 0.3
    
    # Normalize score to 0-100
    ai_score = min(100, (ai_indicators / total_checks) * 100)
    
    return round(ai_score, 2)

# Search for similar documents
def find_similar_documents(index, embedding, document_id, top_k=5):
    """Search Pinecone for similar documents"""
    try:
        results = index.query(
            vector=embedding,
            top_k=top_k + 1,  # +1 to exclude self
            include_metadata=True
        )
        
        similar_docs = []
        for match in results['matches']:
            if int(match['metadata'].get('document_id', -1)) != document_id:
                similar_docs.append({
                    'document_id': match['metadata']['document_id'],
                    'similarity_score': round(match['score'], 4),
                    'filename': match['metadata']['filename']
                })
        
        return similar_docs[:top_k]
    except Exception as e:
        print(f"Similarity search error: {str(e)}")
        return []

# Calculate overall plagiarism score
def calculate_plagiarism_score(similar_docs):
    """Calculate overall plagiarism percentage from similar documents"""
    if not similar_docs:
        return 0.0
    
    # Weight by similarity scores
    total_weight = sum(doc['similarity_score'] for doc in similar_docs)
    if total_weight == 0:
        return 0.0
    
    avg_similarity = total_weight / len(similar_docs)
    # Convert similarity (0-1) to plagiarism percentage (0-100)
    plagiarism_percentage = min(100, avg_similarity * 100)
    
    return round(plagiarism_percentage, 2)

# Store results in database
def store_results_in_db(document_id, plagiarism_score, ai_score, similar_docs):
    """Store plagiarism report in RDS"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Insert plagiarism report
        report_json = {
            'similar_documents': similar_docs,
            'timestamp': datetime.now().isoformat()
        }
        
        cur.execute("""
            INSERT INTO plagiarism_reports 
            (document_id, overall_plagiarism_score, ai_detection_score, 
             total_similar_documents, report_json)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id
        """, (document_id, plagiarism_score, ai_score, len(similar_docs), json.dumps(report_json)))
        
        report_id = cur.fetchone()[0]
        
        # Insert similarity matches
        for match in similar_docs:
            cur.execute("""
                INSERT INTO similarity_matches 
                (report_id, matched_document_id, similarity_score)
                VALUES (%s, %s, %s)
            """, (report_id, match['document_id'], match['similarity_score']))
        
        # Update document status
        cur.execute("""
            UPDATE documents 
            SET status = 'completed'
            WHERE id = %s
        """, (document_id,))
        
        conn.commit()
        cur.close()
        conn.close()
        
        return report_id
    except Exception as e:
        print(f"Database error: {str(e)}")
        return None

# Main Lambda handler
def lambda_handler(event, context):
    """
    Main Lambda handler - supports both S3 events and API Gateway calls
    
    S3 Event format: event['Records'][0]['s3']['bucket']['name']
    API Gateway format: event['s3_bucket'] and event['s3_key']
    """
    try:
        # Determine event source and extract bucket/key
        if 'Records' in event:
            # S3 Event format
            bucket = event['Records'][0]['s3']['bucket']['name']
            key = event['Records'][0]['s3']['object']['key']
            print(f"Processing S3 event: s3://{bucket}/{key}")
        elif 's3_bucket' in event and 's3_key' in event:
            # API Gateway/Direct format
            bucket = event['s3_bucket']
            key = event['s3_key']
            print(f"Processing API Gateway request: s3://{bucket}/{key}")
        else:
            raise Exception("Invalid event format. Expected S3 event or {s3_bucket, s3_key} format")
        
        # 1. Create document record
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute("""
            INSERT INTO documents (filename, s3_path, status)
            VALUES (%s, %s, %s)
            RETURNING id
        """, (key, f"s3://{bucket}/{key}", 'processing'))
        
        document_id = cur.fetchone()[0]
        conn.commit()
        cur.close()
        conn.close()
        
        # 2. Extract text from document
        text = extract_text_from_document(bucket, key)
        if not text:
            raise Exception("Failed to extract text from document")
        
        # 3. Generate embeddings
        embedding = generate_embeddings(text)
        if not embedding:
            raise Exception("Failed to generate embeddings")
        
        # 4. Store embedding in Pinecone
        index = init_pinecone()
        index.upsert(vectors=[(
            f"doc_{document_id}",
            embedding,
            {"document_id": document_id, "filename": key}
        )])
        
        # 5. Find similar documents
        similar_docs = find_similar_documents(index, embedding, document_id)
        
        # 6. Calculate plagiarism score
        plagiarism_score = calculate_plagiarism_score(similar_docs)
        
        # 7. Detect AI-generated content
        ai_score = detect_ai_generated(text)
        
        # 8. Store results
        report_id = store_results_in_db(document_id, plagiarism_score, ai_score, similar_docs)
        
        # Prepare response (works whether called from S3 or API Gateway)
        response_body = {
            'document_id': document_id,
            'report_id': report_id,
            'plagiarism_score': plagiarism_score,
            'ai_detection_score': ai_score,
            'similar_documents_found': len(similar_docs)
        }
        
        # Always return JSON body for compatibility
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps(response_body)
        }
    
    except Exception as e:
        print(f"Lambda error: {str(e)}")
        import traceback
        traceback.print_exc()
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': str(e)})
        }

