import os
import openai

# Load environment settings
openai.api_key = os.getenv("OPENAI_API_KEY")
openai.api_base = os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1")

# Optional: identify your app for OpenRouter analytics
openai.default_headers = {
    "HTTP-Referer": "http://localhost:5000",
    "X-Title": "Lunara AI Summary Generator"
}

def generate_ai_output(text):
    prompt = f"""
    Summarize the following lecture notes and generate a quiz with:
    - 3 multiple-choice questions
    - 2 true/false questions
    - 1 fill-in-the-blank question

    Text:
    {text}
    """

    try:
        # ✅ Use DeepSeek model through OpenRouter
        response = openai.ChatCompletion.create(
            model="deepseek/deepseek-chat",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )

        ai_output = response.choices[0].message["content"]

    except Exception as e:
        ai_output = f"Error calling AI model: {e}"

    html = f"""
    <html>
    <head><title>Summary & Quiz</title></head>
    <body style="font-family:sans-serif; padding:20px;">
        <h1>Summary & Quiz</h1>
        <pre>{ai_output}</pre>
    </body>
    </html>
    """

    return ai_output, html
