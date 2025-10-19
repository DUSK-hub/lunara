from flask import Flask, render_template, request, send_file
import os
from modules.pdf_utils import extract_text_from_pdf
from modules.ai_utils import generate_ai_output
from dotenv import load_dotenv
from werkzeug.utils import secure_filename

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['OUTPUT_FOLDER'] = 'outputs'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/ai_tool')
def ai_tool():
    return render_template('ai_tool/upload.html')

@app.route('/process', methods=['POST'])
def process():
    user_text = request.form.get('user_text')
    pdf_file = request.files.get('pdf_file')

    # Extract text from uploaded file if provided
    if pdf_file:
        filename = secure_filename(pdf_file.filename)
        pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        pdf_file.save(pdf_path)
        user_text = extract_text_from_pdf(pdf_path)

    # Generate AI summary and quiz
    summary, html_result = generate_ai_output(user_text)

    # Save HTML result
    output_path = os.path.join(app.config['OUTPUT_FOLDER'], 'result.html')
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_result)

    return send_file(output_path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
