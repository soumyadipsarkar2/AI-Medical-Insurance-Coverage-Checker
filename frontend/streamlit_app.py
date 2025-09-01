import streamlit as st
import requests
import os
import time
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()

# Configuration
# For local Docker Compose: use port 8001, for Render: use port 8000
DEFAULT_BASE_URL = "http://localhost:8001" if os.getenv("RENDER") != "true" else "http://localhost:8000"
BASE_URL = os.getenv("BASE_URL", DEFAULT_BASE_URL)

# Page configuration
st.set_page_config(
    page_title="AI Medical Insurance Coverage Checker",
    page_icon="🏥",
    layout="wide"
)

# Title and description
st.title("🏥 AI Medical Insurance Coverage Checker")
st.markdown("Upload your insurance policy PDF and ask questions about coverage, copays, and benefits.")

# Check backend status
backend_status = "unknown"
max_retries = 3
retry_delay = 2

for attempt in range(max_retries):
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=10)
        if response.status_code == 200:
            st.success("✅ Backend is connected and ready")
            backend_status = "connected"
            break
        else:
            st.warning("⚠️ Backend is responding but may have issues")
            backend_status = "warning"
            break
    except requests.exceptions.ConnectionError as e:
        if attempt < max_retries - 1:
            st.warning(f"⚠️ Backend not ready (attempt {attempt + 1}/{max_retries}). Retrying in {retry_delay} seconds...")
            time.sleep(retry_delay)
        else:
            st.error(f"❌ Cannot connect to backend after {max_retries} attempts: {str(e)}")
            st.info(f"Backend URL: {BASE_URL}")
            st.info("🔄 The backend may still be starting up. Please wait a moment and refresh the page.")
            backend_status = "error"
    except Exception as e:
        st.error(f"❌ Error connecting to backend: {str(e)}")
        backend_status = "error"
        break

# Initialize session state
if 'uploaded_file' not in st.session_state:
    st.session_state.uploaded_file = None
if 'document_info' not in st.session_state:
    st.session_state.document_info = None

# Section A: PDF Upload
st.header("📄 Upload Insurance Policy PDF")
st.markdown("Upload your insurance policy document to get started.")

uploaded_file = st.file_uploader(
    "Choose a PDF file",
    type=['pdf'],
    help="Only PDF files are supported"
)

if uploaded_file is not None:
    st.session_state.uploaded_file = uploaded_file
    
    if st.button("📤 Process PDF", type="primary"):
        with st.spinner("Processing PDF..."):
            try:
                # Prepare file for upload
                files = {'file': (uploaded_file.name, uploaded_file.getvalue(), 'application/pdf')}
                
                # Try to connect to backend with retries
                max_retries = 3
                for attempt in range(max_retries):
                    try:
                        # Call backend ingest endpoint
                        response = requests.post(f"{BASE_URL}/ingest", files=files, timeout=30)
                        
                        if response.status_code == 200:
                            result = response.json()
                            st.session_state.document_info = result
                            
                            st.success(f"✅ PDF processed successfully! ({result['pages']} pages, {result['chunks']} sections)")
                            break
                        else:
                            st.error(f"❌ Error processing PDF: {response.text}")
                            break
                            
                    except requests.exceptions.ConnectionError as e:
                        if attempt < max_retries - 1:
                            st.warning(f"⚠️ Backend not ready (attempt {attempt + 1}/{max_retries}). Retrying...")
                            time.sleep(2)
                        else:
                            st.error(f"❌ Cannot connect to backend after {max_retries} attempts: {str(e)}")
                            st.info("Please wait a moment and try again, or refresh the page.")
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")
                        break
                    
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")

# Section B: Ask Questions
st.header("❓ Ask Questions About Your Coverage")

if st.session_state.document_info:
    st.success("📋 Document loaded! You can now ask questions about your insurance coverage.")
    
    # Simple question input
    question = st.text_input(
        "Ask a question about your insurance coverage:",
        value=st.session_state.get('example_question', ''),
        placeholder="e.g., Is MRI covered? What's the copay for emergency room visits?",
        help="Ask specific questions about coverage, copays, deductibles, etc."
    )
    
    # Simple ask button
    if st.button("🔍 Ask Question", type="primary") and question:
        with st.spinner("Searching for answer..."):
            try:
                # Call backend ask endpoint with default settings
                payload = {
                    "question": question,
                    "k": 4  # Default value
                }
                
                response = requests.post(f"{BASE_URL}/ask", json=payload)
                
                if response.status_code == 200:
                    result = response.json()
                    
                    # Display answer in a clean format
                    st.subheader("💡 Answer")
                    st.write(result['answer'])
                    
                    # Display sources in a simple format
                    if result['sources']:
                        st.caption(f"📚 Sources: {len(result['sources'])} pages referenced")
                    
                else:
                    st.error(f"❌ Error getting answer: {response.text}")
                    
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
    
    # Example questions in a cleaner layout
    st.subheader("💡 Example Questions")
    st.markdown("Click any question below to get started:")
    
    example_questions = [
        "Is MRI covered under this policy?",
        "What's the copay for emergency room visits?",
        "What's the annual deductible?",
        "Are prescription drugs covered?",
        "What's the out-of-pocket maximum?",
        "Is physical therapy covered?",
        "What's the copay for specialist visits?",
        "Are mental health services covered?"
    ]
    
    # Display example questions in a grid
    cols = st.columns(2)
    for i, example in enumerate(example_questions):
        col_idx = i % 2
        with cols[col_idx]:
            if st.button(example, key=f"example_{i}", use_container_width=True):
                st.session_state.example_question = example
                st.rerun()
    
    # Clear example question
    if st.session_state.get('example_question'):
        if st.button("🗑️ Clear Question", key="clear_example", use_container_width=True):
            st.session_state.example_question = ""
            st.rerun()

else:
    st.info("📋 Please upload a PDF document first to start asking questions.")

# Advanced Settings Section (collapsed by default)
with st.expander("⚙️ Advanced Settings"):
    st.markdown("**For advanced users only**")
    
    if st.session_state.document_info:
        # Number of chunks to retrieve
        k_chunks = st.slider("Number of relevant text chunks to consider:", min_value=1, max_value=10, value=4)
        
        # Display document details
        st.subheader("📄 Document Details")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Document ID", st.session_state.document_info['document_id'][:8] + "...")
        with col2:
            st.metric("Pages", st.session_state.document_info['pages'])
        with col3:
            st.metric("Text Chunks", st.session_state.document_info['chunks'])
        
        # Advanced question asking
        st.subheader("🔧 Advanced Question")
        advanced_question = st.text_input("Advanced question with custom settings:", key="advanced_question")
        
        if st.button("🔍 Ask with Custom Settings", key="advanced_ask") and advanced_question:
            with st.spinner("Searching with custom settings..."):
                try:
                    payload = {
                        "question": advanced_question,
                        "k": k_chunks
                    }
                    
                    response = requests.post(f"{BASE_URL}/ask", json=payload)
                    
                    if response.status_code == 200:
                        result = response.json()
                        
                        st.subheader("💡 Advanced Answer")
                        st.write(result['answer'])
                        
                        # Display detailed metrics
                        col1, col2 = st.columns(2)
                        with col1:
                            st.metric("Response Time", f"{result['latency_ms']:.1f} ms")
                        with col2:
                            st.metric("Sources Used", len(result['sources']))
                        
                        # Display detailed sources
                        if result['sources']:
                            st.subheader("📚 Detailed Sources")
                            for i, source in enumerate(result['sources']):
                                st.info(f"**Source {i+1}:** {source['source']} - Page {source['page']}")
                        
                    else:
                        st.error(f"❌ Error: {response.text}")
                        
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
    else:
        st.info("Upload a document to access advanced settings.")

# Footer
st.markdown("---")
st.markdown("**AI Medical Insurance Coverage Checker** - Powered by LangChain, OpenAI, and Pinecone")
st.markdown("Upload your insurance policy and get instant answers about coverage, copays, and benefits.")
