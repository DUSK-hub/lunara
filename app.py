from flask import Flask, render_template, request, redirect, url_for, flash, session, send_from_directory
import os
from modules.pdf_utils import extract_text_from_pdf
from modules.ai_utils import generate_ai_output
from modules.db_utils import init_db, save_quiz_score, get_user_scores
from modules.auth import register_user, login_user, logout_user, login_required
from dotenv import load_dotenv
from werkzeug.utils import secure_filename
import uuid
from datetime import datetime

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "default_secret_key")
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['OUTPUT_FOLDER'] = 'outputs'
app.config['GENERATED_FOLDER'] = 'generated'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)
os.makedirs(app.config['GENERATED_FOLDER'], exist_ok=True)

init_db()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if login_user(username, password):
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid credentials', 'error')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        if register_user(username, email, password):
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('login'))
        else:
            flash('Username already exists', 'error')
    return render_template('login.html')

@app.route('/logout')
def logout():
    logout_user()
    flash('Logged out successfully', 'success')
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    scores = get_user_scores(session['user_id'])
    return render_template('dashboard.html', scores=scores)

@app.route('/subjects/<subject_name>')
@login_required
def subject(subject_name):
    template_map = {
        'data_structure': 'subjects/data_structure.html',
        'discrete_math': 'subjects/discrete_math.html',
        'micro_assembly': 'subjects/micro_assembly.html',
        'operations_research': 'subjects/operations_research.html',
        'systems_analysis': 'subjects/systems_analysis.html',
        'web_programming': 'subjects/web_programming.html'
    }
    template = template_map.get(subject_name)
    if template:
        return render_template(template, subject=subject_name)
    return redirect(url_for('dashboard'))

@app.route('/ai_tool/upload')
@login_required
def ai_tool():
    return render_template('ai_tool/upload.html')

@app.route('/process', methods=['POST'])
@login_required
def process():
    user_text = request.form.get('user_text')
    pdf_file = request.files.get('pdf_file')
    
    if not user_text and not pdf_file:
        flash("Please upload a file or enter text.", 'error')
        return redirect(url_for('ai_tool'))
    
    if pdf_file and pdf_file.filename:
        filename = secure_filename(pdf_file.filename)
        pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        pdf_file.save(pdf_path)
        user_text = extract_text_from_pdf(pdf_path)
    
    # Generate HTML from AI
    html_output = generate_ai_output(user_text)
    
    # Create unique filename with timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    unique_id = str(uuid.uuid4())[:8]
    filename = f"study_page_{timestamp}_{unique_id}.html"
    
    # Save to generated folder
    output_path = os.path.join(app.config['GENERATED_FOLDER'], filename)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_output)
    
    # Redirect to view the generated HTML
    return redirect(url_for('view_generated', filename=filename))

@app.route('/generated/<filename>')
@login_required
def view_generated(filename):
    """Serve generated HTML files inline in the browser."""
    return send_from_directory(
        app.config['GENERATED_FOLDER'],
        filename,
        mimetype='text/html',
        as_attachment=False
    )

@app.route('/submit_quiz', methods=['POST'])
@login_required
def submit_quiz():
    score = request.form.get('score', 0)
    subject = request.form.get('subject', 'general')
    save_quiz_score(session['user_id'], subject, int(score))
    flash(f'Quiz submitted! Score: {score}', 'success')
    return redirect(url_for('dashboard'))

@app.errorhandler(404)
def not_found(e):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(e):
    return render_template('errors/500.html'), 500

if __name__ == '__main__':
    app.run(debug=True)