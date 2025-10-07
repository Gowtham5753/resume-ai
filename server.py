from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import google.generativeai as genai
import os
from io import BytesIO
import pypdf as pdf_parser 
from dotenv import load_dotenv

# Import PDF libraries within the function to avoid circular imports, 
# but define them here for reference.
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT


# Load environment variables for secure key handling
load_dotenv() 

app = Flask(__name__)
CORS(app)

# Key configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") 
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
else:
    print("FATAL ERROR: GEMINI_API_KEY not found. Check .env file.")


# --- Helper: Convert PDF File to Text (Used for Review Upload) ---
def pdf_to_text(uploaded_file):
    try:
        reader = pdf_parser.PdfReader(uploaded_file)
        text = ''
        for page in reader.pages:
            text += str(page.extract_text())
        return text
    except Exception as e:
        # If PDF parsing fails, return None or an empty string
        return None

# --- Helper: Create PDF (ULTRA-ROBUST VERSION) ---
def create_pdf(text_content):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter,
                            leftMargin=72, rightMargin=72, topMargin=72, bottomMargin=72)
    styles = getSampleStyleSheet()
    
    # Define custom styles
    styles.add(ParagraphStyle(name='HeadingCentered', alignment=TA_CENTER, 
                             fontSize=16, spaceAfter=8, fontName='Helvetica-Bold'))
    styles.add(ParagraphStyle(name='SubHeading', fontSize=12, spaceAfter=8, fontName='Helvetica-Bold'))
    styles.add(ParagraphStyle(name='BodyTextCustom', fontSize=10, spaceAfter=4, alignment=TA_LEFT))
    styles.add(ParagraphStyle(name='ListItem', fontSize=10, leftIndent=18, bulletIndent=0, spaceAfter=2))
    
    story = []
    
    for line in text_content.split('\n'):
        line = line.strip()
        
        # 1. FINAL CLEANUP: Remove common Markdown/HTML artifacts and ensure clean encoding
        line = line.replace('**', '').replace('__', '').replace('---', '—')
        line = line.replace('\xa0', ' ').replace('\u2022', '*').strip()
        
        # 2. ESCAPE HTML/XML characters (like '&', '<', '>')
        line = line.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        
        # 3. Final encoding check for stability
        line = line.encode('ascii', 'xmlcharrefreplace').decode()

        if not line:
            story.append(Spacer(1, 6))
            continue
            
        # 4. Heuristic for headings (ALL CAPS)
        if line.isupper() and len(line) < 50:
            style = styles['SubHeading']
            story.append(Paragraph(line, style))
        
        # 5. Handle list items (bullets)
        elif line.startswith('*') or line.startswith('•'):
            p = Paragraph(line.lstrip('*•').strip(), styles['ListItem'])
            story.append(p)
        
        # 6. Handle centered titles (Name/Contact info)
        elif len(story) < 3 and len(line) < 50 and ('@' in line or 'Phone' in line):
            story.append(Paragraph(line, styles['BodyTextCustom']))
        
        # 7. Everything else is body text
        else:
            p = Paragraph(line, styles['BodyTextCustom'])
            story.append(p)
            
    doc.build(story)
    buffer.seek(0)
    return buffer
# --- End Helper Functions ---


# --- API Route for Content Generation (Form 1) ---
@app.route("/generate", methods=["POST"])
def generate_content_and_review():
    data = request.json
    prompt = data.get("prompt", "")
    
    model = genai.GenerativeModel(model_name="gemini-2.5-flash")

    try:
        response = model.generate_content(
            contents=[{"role": "user", "parts": [{"text": prompt}]}]
        )
        text = response.text
        return jsonify({"text": text})

    except Exception as e:
        print(f"Gemini API Error: {e}")
        return jsonify({"text": f"Error generating content: {e}. Check server logs."}), 500

# --- API Route for ATS Review (Form 2) ---
@app.route("/review_upload", methods=["POST"])
def review_uploaded_file():
    if 'resumeFile' not in request.files:
        return jsonify({"text": "No file uploaded."}), 400
    
    file = request.files['resumeFile']
    job_description = request.form.get('reviewJobDescription', '')

    if file.filename == '' or not file.filename.lower().endswith('.pdf'):
        return jsonify({"text": "Invalid file. Please upload a PDF."}), 400

    resume_text = pdf_to_text(file)
    
    if not resume_text or len(resume_text.strip()) < 50:
        return jsonify({"text": "Could not read text from PDF. Ensure the PDF is not an image scan."}), 500

    review_prompt = f"""
        ACT AS A SENIOR ATS SPECIALIST WITH 10 YEARS OF RECRUITMENT EXPERIENCE. Your task is to provide a detailed, ATS-focused review for the resume provided below against the target job description.
        
        Resume Text for Review: {resume_text}
        
        Target Job Description: {job_description}
        
        Output ONLY a single block of text with the following mandatory sections:
        
        --- DEDICATED ATS COMPATIBILITY REPORT ---
        1. JD Match Score (Rate 0-100%):
        2. Key Mistakes & Gaps: (List specific mistakes in formatting, grammar, or missing experience relative to the JD)
        3. ATS Template & Formatting Check: (Critique the format for ATS compatibility, noting strengths or weaknesses)
        4. Suggestions for Improvement: (List 3 specific, actionable changes to boost the score and make content more impactful)
    """
    
    model = genai.GenerativeModel(model_name="gemini-2.5-flash")
    try:
        response = model.generate_content(
            contents=[{"role": "user", "parts": [{"text": review_prompt}]}]
        )
        return jsonify({"text": response.text})
    except Exception as e:
        print(f"Gemini API Error: {e}")
        return jsonify({"text": f"Error during review: {e}. Make sure the job description is long enough."}), 500

# --- API Route for PDF Download (POST) ---
@app.route("/download_pdf", methods=["POST"])
def download_pdf():
    data = request.json
    text_content = data.get("content", "")
    filename = data.get("filename", "resume.pdf")
    
    if not text_content:
        return jsonify({"error": "No content provided for PDF generation."}), 400

    pdf_buffer = create_pdf(text_content)
    
    return send_file(
        pdf_buffer,
        mimetype='application/pdf',
        as_attachment=True,
        download_name=filename
    )

if __name__ == "__main__":
    @app.route("/")
    def home():
        return "AI Resume Builder API is running! Open your index.html file to use the app."
        
    app.run(port=5000)