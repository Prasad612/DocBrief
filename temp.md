from flask import Flask, request, send_from_directory
from google import genai

client = genai.Client(api_key="AQ.Ab8RN6Jb9neC7MVYr006cHVDsMyEfNqHO7KN0tku7wGyQkWikw123")

app = Flask(__name__)

@app.route("/")
def home():
    return send_from_directory(".", "index.html")



from pypdf import PdfReader
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
        
    return gemini_response(filecontent)

app.run(debug=True)

