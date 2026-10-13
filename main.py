from flask import Flask, request, send_from_directory
from google import genai
import chromadb
from pypdf import PdfReader


#client = genai.Client(api_key="AQ.Ab8RN6Jb9neC7MVYr006cHVDsMyEfNqHO7KN0tku7wGyQkWikw1278")
client = genai.Client()

app = Flask(__name__)

@app.route("/")
def home():
    return send_from_directory(".", "index.html")



def pdf_to_txt(pdf_path):
    reader = PdfReader(pdf_path)
    text = ""
    
    for page in reader.pages:
        # Check if text exists on the page before adding
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"
        
    return text
    
def gemini_response(filecontent):
    response = client.models.generate_content(
        model='gemini-3.8-flash',
        contents=f'Give five bullet point summary on: {filecontent}',
    )
    content=response.text
    return content

def chromadb_response(filecontent, question):
    chroma_client = chromadb.PersistentClient(path="./chroma_db")
    collection = chroma_client.get_or_create_collection(name="project_collection")
    
    chunks = [chunk.strip() for chunk in filecontent.split("\n") if chunk.strip()]
    ids = [f"id_{i}" for i in range(len(chunks))]
    metadatas = [{"source": "test1"} for _ in chunks]


    collection.add(
        documents=chunks,
        metadatas=metadatas,
        ids=ids
    )
    content = collection.query(
    query_texts=[question],
    n_results=2
    )

    return content

@app.route("/upload", methods=["POST"])
def upload():
    file = request.files["document"]
    if file.filename.endswith(".txt"):
        print("Text file uploaded.")
        filecontent = file.read().decode("utf-8")
    elif file.filename.endswith(".pdf"):
        print("PDF file uploaded.")
        filecontent=pdf_to_txt(file)
    else:
        print("Unsupported file type.")
        
    #return gemini_response(filecontent)
    return chromadb_response(filecontent, "what is platform_deployment.yaml")

app.run(debug=False, use_reloader=False, host='0.0.0.0', port=5000)
