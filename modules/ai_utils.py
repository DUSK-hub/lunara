import os
import openai

openai.api_key = os.getenv("OPENAI_API_KEY")
openai.api_base = os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1")

openai.default_headers = {
    "HTTP-Referer": "http://localhost:5000",
    "X-Title": "College AI Platform"
}

def generate_ai_output(text):
    prompt = f"""
    Analyze the following educational content and provide:
    1. A concise summary (3-5 sentences)
    2. An interactive quiz with:
       - 3 multiple-choice questions (with 4 options each)
       - 2 true/false questions
       - 1 fill-in-the-blank question
    
    Format the quiz in clean HTML with proper structure.
    
    Content:
    {text[:3000]}
    """

    try:
        response = openai.ChatCompletion.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )

        ai_output = response.choices[0].message["content"]

    except Exception as e:
        ai_output = f"Error calling AI model: {e}\n\nPlease check your API key and connection."

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Summary & Quiz</title>
        <style>
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                padding: 30px;
                max-width: 900px;
                margin: 0 auto;
                background: #f5f5f5;
            }}
            .content {{
                background: white;
                padding: 30px;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }}
            h1 {{
                color: #2c3e50;
                border-bottom: 3px solid #3498db;
                padding-bottom: 10px;
            }}
            pre {{
                background: #f8f9fa;
                padding: 20px;
                border-radius: 5px;
                white-space: pre-wrap;
                line-height: 1.6;
            }}
        </style>
    </head>
    <body>
        <div class="content">
            <h1>Summary & Quiz Results</h1>
            <pre>{ai_output}</pre>
        </div>
    </body>
    </html>
    """

    return ai_output, html