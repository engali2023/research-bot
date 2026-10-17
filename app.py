import os
from dotenv import load_dotenv
from flask import Flask, render_template, request, jsonify, send_file
from google import genai
from google.genai import types
import markdown
import datetime
from fpdf import FPDF
from arabic_reshaper import reshape
from bidi.algorithm import get_display

load_dotenv()

app = Flask(__name__)

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
    """Process Arabic text for correct RTL rendering in PDF"""
    try:
        reshaped = reshape(text)
        return get_display(reshaped)
    except Exception:
        return text


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_message = data.get("message", "")

    # Use API key from request (user-provided) or fallback to environment variable
    provided_key = data.get("api_key")
    api_key = provided_key if provided_key else os.getenv("GOOGLE_API_KEY")

    if not api_key:
        return jsonify({"error": "No API key provided. Please set your API key in Settings."}), 401

    try:
        temp_client = genai.Client(api_key=api_key)
        response = temp_client.models.generate_content(
            model=MODEL,
            contents=user_message,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_INSTRUCTION,
            ),
        )
        return jsonify({"reply": response.text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/export/markdown", methods=["POST"])
def export_markdown():
    data = request.get_json()
    content = data.get("content", "")
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"research_{timestamp}.md"
    filepath = os.path.join("exports", filename)

    os.makedirs("exports", exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

    return send_file(filepath, as_attachment=True, download_name=filename)


@app.route("/export/pdf", methods=["POST"])
def export_pdf():
    data = request.get_json()
    content = data.get("content", "")
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    pdf_filename = f"research_{timestamp}.pdf"
    pdf_filepath = os.path.join("exports", pdf_filename)

    os.makedirs("exports", exist_ok=True)

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # Register Arabic-supporting font
    font_path = os.path.join("fonts", "arial.ttf")
    if not os.path.exists(font_path):
        alt_paths = [
            r"C:\Windows\Fonts\arial.ttf",
            os.path.join("fonts", "dejavusans.ttf"),
        ]
        for path in alt_paths:
            if os.path.exists(path):
                font_path = path
                break

    if os.path.exists(font_path):
        pdf.add_font("Arial", "", font_path, uni=True)
        bold_path = font_path.replace(".ttf", "bd.ttf") if "arial.ttf" in font_path else font_path
        if os.path.exists(bold_path):
            pdf.add_font("Arial", "B", bold_path, uni=True)
        else:
            pdf.add_font("Arial", "B", font_path, uni=True)
    else:
        pdf.add_font("Helvetica", "", size=11)

    try:
        pdf.set_font("Arial", size=11)
    except Exception:
        pdf.set_font("Helvetica", size=11)

    lines = content.split("\n")
    for line in lines:
        stripped = line.strip()

        if stripped.startswith("## "):
            try:
                pdf.set_font("Arial", style="B", size=14)
            except Exception:
                pdf.set_font("Helvetica", style="B", size=14)
            text = stripped.replace("## ", "")
            processed_text = process_arabic_text(text)
            pdf.cell(0, 10, processed_text, new_x="LMARGIN", new_y="NEXT")
            pdf.ln(3)

        elif stripped.startswith("- ") or stripped.startswith("* "):
            try:
                pdf.set_font("Arial", size=11)
            except Exception:
                pdf.set_font("Helvetica", size=11)
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
            try:
                pdf.set_font("Arial", size=11)
            except Exception:
                pdf.set_font("Helvetica", size=11)
            processed_text = process_arabic_text(stripped)
            pdf.multi_cell(0, 7, processed_text)
            pdf.ln(2)

    pdf.output(pdf_filepath)
    return send_file(pdf_filepath, as_attachment=True, download_name=pdf_filename)


if __name__ == "__main__":
    print("=" * 50)
    print("Research Bot - Web Interface")
    print("=" * 50)
    print("Opening browser at http://localhost:5000\n")
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=False, host="0.0.0.0", port=port)