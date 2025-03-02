# frontend/app.py
import streamlit as st
import plotly.graph_objects as go
import requests
import json
import openai
from utils import create_mindmap_figure
import platform
import getpass
import os

def create_directory_from_mindmap(graph_data, base_path):
    if not os.path.exists(base_path):
        os.makedirs(base_path)
    
    # Create a mapping of node IDs to their full paths
    node_paths = {}
    nodes = {node['id']: node['label'] for node in graph_data['nodes']}
    
    # First, handle the root node
    root_node = next(node for node in graph_data['nodes'] if node['id'] == 'root')
    root_path = os.path.join(base_path, root_node['label'])
    node_paths['root'] = root_path
    os.makedirs(root_path, exist_ok=True)
    
    # Process all edges to create directory structure
    for edge in graph_data['edges']:
        from_node = edge['from']
        to_node = edge['to']
        
        # If parent path is known
        if from_node in node_paths:
            parent_path = node_paths[from_node]
            child_name = nodes[to_node]
            child_path = os.path.join(parent_path, child_name)
            node_paths[to_node] = child_path
            os.makedirs(child_path, exist_ok=True)
    
    return root_path


# Configure OpenAI API key
openai.api_key = st.secrets["OPENAI_API_KEY"]

# Page configuration
st.set_page_config(
    page_title="LightningRoute - AI-Powered Mind Mapping 🧠",
    page_icon="⚡",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    /* Base Theme */
    :root {
        --primary: #FF6B6B;
        --secondary: #4ECDC4;
        --accent: #45B7D1;
        --background: #f8f9fa;
        --text: #2d3436;
    }

    /* Reset container margins */
    .element-container {
        margin: 0 !important;
        padding: 0.5rem 0 !important;
    }

    /* Main container styling */
    .stApp {
        background: linear-gradient(135deg, #FF6B6B 0%, #4ECDC4 50%, #45B7D1 100%);
        background-attachment: fixed;
    }

    /* Content containers */
    .stTextInput, .stTextArea, .stButton, 
    div[data-testid="stFileUploader"], .stRadio {
        background: rgba(255, 255, 255, 0.95);
        border-radius: 12px;
        padding: 0.7rem;
        margin: 1rem 0;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
        backdrop-filter: blur(8px);
    }

    /* Button styling */
    .stButton > button {
        width: auto;
        background: linear-gradient(45deg, var(--primary), var(--secondary));
        color: white;
        border: none;
        padding: 0.75rem 2rem;
        border-radius: 50px;
        font-weight: 600;
        transition: all 0.3s ease;
        margin: 1rem 0;
        padding-top: 10px !important;
        padding-bottom: 10px !important;
    }

    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
    }

    /* Headings */
    h1, h2, h3 {
        color: white;
        text-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
        padding: 1rem 0;
        margin: 0;
        line-height: 1.4;
    }

    /* Plotly chart container */
    [data-testid="stPlotlyChart"] {
        background: white;
        border-radius: 12px;
        padding: 1rem;
        margin: 1rem 0;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
    }

    /* Sidebar */
    .css-1d391kg {
        background: rgba(255, 255, 255, 0.95);
        padding: 2rem 1rem;
    }

    /* File uploader */
    .uploadedFile {
        background: linear-gradient(45deg, var(--secondary), var(--accent));
        border-radius: 8px;
        padding: 0.75rem;
        color: white;
        margin: 0.5rem 0;
    }

    /* Radio buttons */
    .stRadio > div {
        background: white;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
    }

    /* Debug sections */
    .stTextArea[aria-label="Raw Text Input"],
    .element-container:has(pre) {
        background: rgba(255, 255, 255, 0.95);
        border-radius: 12px;
        padding: 1rem;
        margin: 1rem 0;
        font-family: monospace;
    }

    /* Responsive adjustments */
    @media (max-width: 768px) {
        .stButton > button {
            width: 100%;
            padding: 0.5rem;
        }
        
        .element-container,
        .stTextInput, .stTextArea,
        div[data-testid="stFileUploader"],
        .stRadio {
            padding: 1rem;
            margin: 0.5rem 0;
        }
    }
</style>
""", unsafe_allow_html=True)
# Main title
st.title("⚡︎ LightningRoute: AI-Powered **Mind Mapping** ⚡︎")

# File upload and text input section
st.subheader("Input Options")
input_type = st.radio("Choose input type:", ["Text Input", "File Upload"])

# Directory creation options
st.subheader("Directory Creation Options")
create_dir = st.radio("Create directory structure from mind map?", ["No", "Yes"])

if create_dir == "Yes":
    # Set default path based on OS
    default_path = "~/" if platform.system() == "Darwin" else f"C:\\Users\\{getpass.getuser()}\\Documents"
    dir_path = st.text_input("Directory path for mind map structure", value=default_path,
                            help="Enter the base directory path where the mind map structure will be created")

text_input = ""

if input_type == "Text Input":
    text_input = st.text_area(
        "Enter your text (e.g., study notes, article, etc.)",
        height=200,
        help="Paste your text here to generate a mind map"
    )
else:
    uploaded_file = st.file_uploader("Choose a file", type=["txt", "docx", "doc", "pdf", "png", "jpg", "jpeg"])
    if uploaded_file is not None:
        try:
            if uploaded_file.type == "text/plain":
                text_input = uploaded_file.getvalue().decode()
            elif uploaded_file.type == "application/pdf":
                import PyPDF2
                import io
                pdf_reader = PyPDF2.PdfReader(io.BytesIO(uploaded_file.getvalue()))
                text_input = ""
                for page in pdf_reader.pages:
                    text_input += page.extract_text()
            elif "word" in uploaded_file.type:
                import docx
                doc = docx.Document(io.BytesIO(uploaded_file.getvalue()))
                text_input = "\n".join([paragraph.text for paragraph in doc.paragraphs])
            elif uploaded_file.type.startswith("image/"):
                import pytesseract
                from PIL import Image
                import io
                pytesseract.pytesseract.tesseract_cmd = "C:\\Program Files\\Tesseract-OCR\\tesseract.exe"
                image = Image.open(io.BytesIO(uploaded_file.getvalue()))
                text_input = pytesseract.image_to_string(image)
        except Exception as e:
            st.error(f"Error reading file: {str(e)}")

col1, col2 = st.columns([2,10])
# Process button
# Flask API 服务器地址
FLASK_API_URL = "https://lightningroute.onrender.com"

st.title("⚡ LightningRoute: AI-Powered Mind Mapping ⚡")

# 选择输入方式
input_type = st.radio("Choose input type:", ["Text Input", "File Upload"])

text_input = ""

if input_type == "Text Input":
    text_input = st.text_area("Enter your text to generate a mind map:")
else:
    uploaded_file = st.file_uploader("Choose a text file", type=["txt"])
    if uploaded_file is not None:
        text_input = uploaded_file.getvalue().decode()

if st.button("Generate Mind Map"):
    if text_input:
        with st.spinner("Generating mind map..."):
            # 发送请求到 Flask 后端
            response = requests.post(f"{FLASK_API_URL}/api/generate-map", json={"text": text_input})

            if response.status_code == 200:
                graph_data = response.json()

                # 显示思维导图
                st.subheader("Mind Map Visualization")
                fig = create_mindmap_figure(graph_data)
                st.plotly_chart(fig, use_container_width=True)

                # 下载按钮
                st.download_button("Download Mind Map", 
                                   data=json.dumps(graph_data), 
                                   file_name="mindmap.json", 
                                   mime="application/json")
            else:
                st.error("Failed to generate mind map. Please try again.")
    else:
        st.warning("Please enter text or upload a file.")

# Add instructions in sidebar
with st.sidebar:
    st.header("How to use LightningRoute⚡")
    st.markdown("""
    1. Paste your text in the input area / Upload a file (PDF, DOCX, TXT)
    2. Click 'Generate Mind Map'
    3. Interact with the mind map:
        - Zoom in/out
    4. Download the mind map (as JSON) for later use
    5. OUR ROADMAP 🛣️:
        - OCR (Done! ✅)
        - Mindmap to directory tree (Done! ✅)
        - Accept video input (.mp4) or video links
    """)
