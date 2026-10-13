FROM python:3.11-slim

WORKDIR /project

RUN pip install --no-cache-dir --progress-bar off \
    flask \
    chromadb \
    google-genai \
    pypdf

COPY index.html .
COPY main.py .

CMD ["python", "main.py"]