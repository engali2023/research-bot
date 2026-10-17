import os
from dotenv import load_dotenv
from google import genai
from google.genai import types
import markdown
import datetime
from fpdf import FPDF
from arabic_reshaper import reshape
from bidi.algorithm import get_display

load_dotenv()

MODEL = "gemini-3.8-flash"

SYSTEM_INSTRUCTION = """You are an expert research assistant. Your tasks:
1. Understand the user's question accurately
2. Search for reliable information from multiple sources
3. Detect the language of the user's question and respond in the SAME language:
   - If the question is in Arabic → respond in Arabic
   - If the question is in English → respond in English
   - If the question is in another language → respond in that language
4. Provide a clear, organized summary including:
   - A brief introduction
   - Key points (bullet points)
   - Comparison of different viewpoints if applicable
   - Suggestions for further reading
5. Cite the sources used
6. If information is contradictory, clearly explain this to the user"""


def process_arabic_text(text):
    try:
        reshaped = reshape(text)
        return get_display(reshaped)
    except Exception:
        return text


def serve_static_file(filepath):
    full_path = os.path.join(os.path.dirname(__file__), "..", filepath)
    if os.path.exists(full_path):
        content_type_map = {
            ".html": "text/html; charset=utf-8",
            ".css": "text/css; charset=utf-8",
            ".js": "application/javascript",
            ".ttf": "font/ttf",
        }
        ext = os.path.splitext(filepath)[1]
        content_type = content_type_map.get(ext, "application/octet-stream")
        with open(full_path, "rb") as f:
            content = f.read()
        return content, {"Content-Type": content_type}
    return None, {}


def handle_chat(request_body):
    data = request_body.get("message", "")
    provided_key = request_body.get("api_key")
    api_key = provided_key if provided_key else os.getenv("GOOGLE_API_KEY")

    if not api_key:
        return {"error": "No API key provided. Please set your API key in Settings."}, 401

    try:
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model=MODEL,
            contents=data,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_INSTRUCTION,
            ),
        )
        return {"reply": response.text}, 200
    except Exception as e:
        return {"error": str(e)}, 500


def handle_export_markdown(content):
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"research_{timestamp}.md"
    exports_dir = os.path.join(os.path.dirname(__file__), "..", "exports")
    os.makedirs(exports_dir, exist_ok=True)
    filepath = os.path.join(exports_dir, filename)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

    with open(filepath, "rb") as f:
        content_bytes = f.read()
    return content_bytes, {
        "Content-Type": "text/markdown",
        "Content-Disposition": f'attachment; filename="{filename}"',
    }


def handle_export_pdf(content):
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    pdf_filename = f"research_{timestamp}.pdf"
    exports_dir = os.path.join(os.path.dirname(__file__), "..", "exports")
    os.makedirs(exports_dir, exist_ok=True)
    pdf_filepath = os.path.join(exports_dir, pdf_filename)

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    font_path = os.path.join(os.path.dirname(__file__), "..", "fonts", "arial.ttf")
    if os.path.exists(font_path):
        pdf.add_font("Arial", "", font_path, uni=True)
        bold_path = font_path.replace(".ttf", "bd.ttf")
        if os.path.exists(bold_path):
            pdf.add_font("Arial", "B", bold_path, uni=True)
        else:
            pdf.add_font("Arial", "B", font_path, uni=True)
        pdf.set_font("Arial", size=11)
    else:
        pdf.set_font("Helvetica", size=11)

    lines = content.split("\n")
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("## "):
            pdf.set_font("Arial", style="B", size=14)
            text = stripped.replace("## ", "")
            processed_text = process_arabic_text(text)
            pdf.cell(0, 10, processed_text, new_x="LMARGIN", new_y="NEXT")
            pdf.ln(3)
        elif stripped.startswith("- ") or stripped.startswith("* "):
            pdf.set_font("Arial", size=11)
            text = stripped[2:]
            processed_text = process_arabic_text(text)
            pdf.multi_cell(0, 7, chr(8226) + " " + processed_text)
            pdf.ln(1)
        elif stripped == "---":
            pdf.set_draw_color(200, 200, 200)
            pdf.line(10, pdf.get_y(), 200, pdf.get_y())
            pdf.ln(5)
        elif not stripped:
            pdf.ln(3)
        else:
            pdf.set_font("Arial", size=11)
            processed_text = process_arabic_text(stripped)
            pdf.multi_cell(0, 7, processed_text)
            pdf.ln(2)

    pdf.output(pdf_filepath)

    with open(pdf_filepath, "rb") as f:
        content_bytes = f.read()
    return content_bytes, {
        "Content-Type": "application/pdf",
        "Content-Disposition": f'attachment; filename="{pdf_filename}"',
    }


def handler(request):
    path = request.get("path", "/")
    method = request.get("method", "GET")

    # Serve index.html for root path
    if path == "/" or path == "":
        html_path = os.path.join("..", "templates", "index.html")
        full_path = os.path.join(os.path.dirname(__file__), html_path)
        if os.path.exists(full_path):
            with open(full_path, "r", encoding="utf-8") as f:
                return f.read(), {"Content-Type": "text/html; charset=utf-8"}

    # Serve static files
    if path.startswith("/static/"):
        filepath = path.lstrip("/")
        content, headers = serve_static_file(filepath)
        if content:
            return content, headers

    # Chat endpoint
    if path == "/chat" and method == "POST":
        body = request.get("body", {})
        result, status = handle_chat(body)
        return result, {"Content-Type": "application/json"}, status

    # Export Markdown
    if path == "/export/markdown" and method == "POST":
        body = request.get("body", {})
        content = body.get("content", "")
        result, headers = handle_export_markdown(content)
        return result, headers

    # Export PDF
    if path == "/export/pdf" and method == "POST":
        body = request.get("body", {})
        content = body.get("content", "")
        result, headers = handle_export_pdf(content)
        return result, headers

    # Default: serve index.html
    html_path = os.path.join("..", "templates", "index.html")
    full_path = os.path.join(os.path.dirname(__file__), html_path)
    if os.path.exists(full_path):
        with open(full_path, "r", encoding="utf-8") as f:
            return f.read(), {"Content-Type": "text/html; charset=utf-8"}

    return "Not Found", {"Content-Type": "text/plain"}, 404
