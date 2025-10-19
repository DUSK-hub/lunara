import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
DEEPSEEK_API_BASE = os.getenv("DEEPSEEK_API_BASE", "https://api.deepseek.com")

def generate_ai_output(text):
    """
    Ask DeepSeek for a full HTML document. If the model misbehaves,
    extract the HTML block if present, or wrap the text in a safe HTML shell.
    Returns a string containing a complete HTML document.
    """
    if not DEEPSEEK_API_KEY:
        return _generate_error_html("DeepSeek API key is not configured. Please set DEEPSEEK_API_KEY in your .env file.")

    # Keep input small to reduce drift
    truncated_text = (text or "")[:3000]

    prompt = f"""
YOU MUST RETURN VALID HTML ONLY.

ABSOLUTE RULES (if you break them the output is INVALID):
- Output MUST start with <!DOCTYPE html>
- Output MUST end with </html>
- NO markdown fences (no ``` anywhere)
- NO markdown headings or prose outside HTML
- The answer IS a full HTML document, nothing else

TASK:
Create a full standalone HTML study page with inline CSS and JS based on the content below.
Include:
1) A styled summary section (3–5 sentences)
2) A quiz section:
   - 3 MCQs with 4 options
   - 2 True/False
   - 1 Fill-in-the-blank
3) JS to check answers and show score

CONTENT TO ANALYZE:
{truncated_text}

REMINDER: RETURN ONLY RAW HTML CODE FROM <!DOCTYPE html> TO </html>
"""

    try:
        url = f"{DEEPSEEK_API_BASE}/chat/completions"
        headers = {
            "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "deepseek-chat",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.4
        }
        r = requests.post(url, headers=headers, json=payload, timeout=60)

        if r.status_code == 401:
            return _generate_error_html("Invalid DeepSeek API key.")
        if r.status_code == 402:
            return _generate_error_html("Payment required on DeepSeek API. Add credits or use another model/provider.")
        if r.status_code == 429:
            return _generate_error_html("Rate limit exceeded. Please try again later.")
        if r.status_code >= 500:
            return _generate_error_html("DeepSeek API server error. Please try again later.")

        r.raise_for_status()
        data = r.json()
        content = (data.get("choices", [{}])[0].get("message", {}).get("content") or "").strip()

        # Strip any accidental code fences
        for fence in ("```html", "```HTML", "```", "“““", "”””"):
            if content.startswith(fence):
                content = content[len(fence):].strip()
        if content.endswith("```"):
            content = content[:-3].strip()

        # Try to extract the HTML block if present
        lower = content.lower()
        start_idx = lower.find("<!doctype html")
        if start_idx == -1:
            start_idx = lower.find("<! doctype html")  # in case of weird spacing

        end_idx = lower.rfind("</html>")
        if start_idx != -1 and end_idx != -1:
            html = content[start_idx:end_idx + len("</html>")]
            return html.strip()

        # If we reach here, the model did not return a full HTML doc.
        # Wrap whatever came back in a minimal HTML shell so the user still gets a page.
        escaped = content.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        fallback_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Generated Study Page (Recovered)</title>
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <style>
    body{{font-family:system-ui, -apple-system, Segoe UI, Roboto, Arial; margin:2rem; line-height:1.6;}}
    .warn{{background:#fff3cd; color:#664d03; border:1px solid #ffecb5; padding:12px 16px; border-radius:8px; margin-bottom:1rem;}}
    pre{{background:#111; color:#eee; padding:16px; border-radius:10px; overflow:auto;}}
  </style>
</head>
<body>
  <div class="warn"><strong>Note:</strong> The AI did not return a valid HTML document.
  Showing raw output below. You can regenerate or continue.</div>
  <pre>{escaped}</pre>
</body>
</html>"""
        return fallback_html

    except requests.exceptions.Timeout:
        return _generate_error_html("Request timed out. Please try again.")
    except requests.exceptions.ConnectionError:
        return _generate_error_html("Connection error. Check your internet connection.")
    except requests.exceptions.RequestException as e:
        return _generate_error_html(f"Error calling DeepSeek API: {e}")
    except Exception as e:
        return _generate_error_html(f"Unexpected error: {e}")



    try:
        # Make API request to DeepSeek
        url = f"{DEEPSEEK_API_BASE}/chat/completions"
        headers = {
            "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "deepseek-chat",
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.7
        }
        
        response = requests.post(url, headers=headers, json=payload, timeout=60)
        
        # Check for HTTP errors
        if response.status_code == 401:
            error_msg = "Invalid DeepSeek API key. Please check your DEEPSEEK_API_KEY in .env file."
            return _generate_error_html(error_msg)
        elif response.status_code == 429:
            error_msg = "Rate limit exceeded. Please try again later."
            return _generate_error_html(error_msg)
        elif response.status_code >= 500:
            error_msg = "DeepSeek API server error. Please try again later."
            return _generate_error_html(error_msg)
        
        response.raise_for_status()
        
        # Parse response
        response_data = response.json()
        
        if "choices" not in response_data or len(response_data["choices"]) == 0:
            error_msg = "Unexpected response format from DeepSeek API."
            return _generate_error_html(error_msg)
        
        html_output = response_data["choices"][0]["message"]["content"].strip()
        
        # Clean up any markdown code fences if they appear
        if html_output.startswith("```html"):
            html_output = html_output[7:]
        if html_output.startswith("```"):
            html_output = html_output[3:]
        if html_output.endswith("```"):
            html_output = html_output[:-3]
        
        html_output = html_output.strip()
        
        # Validate that it's HTML
        if not html_output.lower().startswith("<!doctype html>") and not html_output.lower().startswith("<html"):
            error_msg = "AI did not return valid HTML. Please try again."
            return _generate_error_html(error_msg)
        
        return html_output

    except requests.exceptions.Timeout:
        error_msg = "Request timed out. The DeepSeek API is taking too long to respond. Please try again."
        return _generate_error_html(error_msg)
    
    except requests.exceptions.ConnectionError:
        error_msg = "Connection error. Unable to reach DeepSeek API. Please check your internet connection."
        return _generate_error_html(error_msg)
    
    except requests.exceptions.RequestException as e:
        error_msg = f"Error calling DeepSeek API: {str(e)}"
        return _generate_error_html(error_msg)
    
    except json.JSONDecodeError:
        error_msg = "Invalid JSON response from DeepSeek API."
        return _generate_error_html(error_msg)
    
    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        return _generate_error_html(error_msg)


def _generate_error_html(error_message):
    """Generate HTML for error messages."""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Error - College AI Platform</title>
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
        .error {{
            background: #f8d7da;
            color: #721c24;
            padding: 20px;
            border-radius: 5px;
            border-left: 4px solid #f5c6cb;
        }}
        h1 {{
            color: #e74c3c;
            margin-bottom: 20px;
        }}
        .help-text {{
            margin-top: 20px;
            color: #7f8c8d;
            font-size: 0.9rem;
        }}
        .back-btn {{
            display: inline-block;
            margin-top: 20px;
            padding: 10px 20px;
            background: #3498db;
            color: white;
            text-decoration: none;
            border-radius: 5px;
        }}
        .back-btn:hover {{
            background: #2980b9;
        }}
    </style>
</head>
<body>
    <div class="content">
        <h1>⚠️ Error</h1>
        <div class="error">
            <strong>Error:</strong> {error_message}
        </div>
        <div class="help-text">
            <p>Troubleshooting tips:</p>
            <ul>
                <li>Verify your DEEPSEEK_API_KEY is set correctly in the .env file</li>
                <li>Check your internet connection</li>
                <li>Ensure you have sufficient API credits</li>
                <li>Try again in a few moments</li>
            </ul>
        </div>
        <a href="/ai_tool/upload" class="back-btn">← Back to Upload</a>
    </div>
</body>
</html>
"""