from flask import Flask, request, jsonify
import fitz  # PyMuPDF
import requests
from langchain.text_splitter import RecursiveCharacterTextSplitter

app = Flask(__name__)

def estimate_token_count(text):
    return max(1, len(text) // 4)

def download_pdf_from_url(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.content
    except Exception as e:
        raise Exception(f"Failed to download PDF: {str(e)}")

def extract_text_per_page(pdf_bytes):
    try:
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        page_texts = []
        for i, page in enumerate(doc):
            text = page.get_text().strip()
            if text:
                page_texts.append({"page": i + 1, "text": text})
        return page_texts
    except Exception as e:
        raise Exception(f"Failed to parse PDF: {str(e)}")

def build_page_ranges(page_texts):
    full_text = ""
    page_ranges = []
    for page_data in page_texts:
        start_index = len(full_text)
        full_text += page_data["text"] + "\n\n"
        end_index = len(full_text)
        page_ranges.append({
            "page": page_data["page"],
            "start": start_index,
            "end": end_index
        })
    return full_text.strip(), page_ranges

def find_chunk_pages(start, end, page_ranges):
    pages = set()
    for page_info in page_ranges:
        if page_info["end"] > start and page_info["start"] < end:
            pages.add(page_info["page"])
    return sorted(list(pages))

def chunk_text_with_metadata(page_texts):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=60,
        separators=["\n\n", "\n", ".", " ", ""]
    )
    full_text, page_ranges = build_page_ranges(page_texts)
    chunks = []
    split_chunks = splitter.split_text(full_text)
    global_index = 0
    for chunk in split_chunks:
        chunk = chunk.strip()
        start = full_text.find(chunk, global_index)
        if start == -1:
            start = global_index
        end = start + len(chunk)
        pages = find_chunk_pages(start, end, page_ranges)
        chunks.append({
            "pages": pages,
            "content": chunk,
            "startIndex": start,
            "endIndex": end,
            "tokenCount": estimate_token_count(chunk)
        })
        global_index = end
    return full_text, chunks

@app.route('/process-document', methods=['POST'])
def process_document():
    try:
        data = request.get_json()
        if not data or "s3Url" not in data:
            return jsonify({"error": "Missing 's3Url' in request body"}), 400

        s3_url = data["s3Url"]
        pdf_bytes = download_pdf_from_url(s3_url)
        page_texts = extract_text_per_page(pdf_bytes)
        full_text, chunks = chunk_text_with_metadata(page_texts)

        return jsonify({
            "textContent": full_text,
            "chunks": chunks
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
