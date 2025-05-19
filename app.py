from flask import Flask, render_template_string, request, url_for
import requests
import json

app = Flask(__name__)

# --------------------
# Konfiguration laden
# --------------------
with open("config.json", "r") as config_file:
    config = json.load(config_file)

# --------------------
# GPT-Funktion
# --------------------
def ask_gpt_about_prompt(prompt):
    try:
        headers = {
            "Authorization": f"Bearer {config['openai_api_key']}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "gpt-3.5-turbo",
            "messages": [
                {"role": "system", "content": "Du bist ein hilfreicher Sicherheitsassistent."},
                {"role": "user", "content": prompt}
            ]
        }
        response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        return f"Fehler bei GPT: {str(e)}"

# --------------------
# HTML-Template
# --------------------
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>AI Scan & GPT</title>
    <link href="https://fonts.googleapis.com/css2?family=Open+Sans&display=swap" rel="stylesheet">
    <style>
        body { font-family: 'Open Sans', sans-serif; background-color: #1B1F3B; color: #f0f0f0; padding: 40px; }
        .container { background-color: #2C3059; max-width: 600px; margin: auto; padding: 30px; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.3); }
        .logo { text-align: center; margin-bottom: 20px; }
        .logo img { max-width: 200px; }
        h1 { text-align: center; color: #FF6F00; margin-bottom: 10px; }
        form { margin-top: 20px; }
        select, input[type="text"] { width: 100%; padding: 12px; border: none; border-radius: 6px; margin-bottom: 15px; font-size: 16px; }
        input[type="submit"] { width: 100%; background-color: #FF6F00; border: none; color: white; padding: 12px; font-size: 16px; border-radius: 6px; cursor: pointer; transition: background-color 0.2s ease-in-out; }
        input[type="submit"]:hover { background-color: #e65c00; }
        .result, .gpt { background-color: #1B1F3B; padding: 20px; border-radius: 8px; margin-top: 30px; border-left: 4px solid #FF6F00; }
        .field { margin-bottom: 10px; }
        .label { font-weight: bold; color: #FF6F00; }
        .category-safe { color: #00e676; font-weight: bold; }
        .category-warning { color: #ffeb3b; font-weight: bold; }
        .category-danger { color: #ff1744; font-weight: bold; }
        .error { margin-top: 20px; background-color: #ff4c4c; padding: 15px; border-radius: 6px; color: white; }
        .footer { margin-top: 40px; text-align: center; font-size: 0.9em; color: #aaa; }
        pre { white-space: pre-wrap; word-break: break-word; color: #ccc; }
    </style>
</head>
<body>
    <div class="container">
        <div class="logo">
            <img src="{{ url_for('static', filename='logo.svg') }}" alt="Palo Alto Networks Logo">
        </div>
        <h1>AI Scan mit GPT-Erweiterung</h1>
        <form method="post">
            <label for="prompt">Wähle eine Beispiel-Frage oder gib eine eigene ein:</label><br>
            <select onchange="document.getElementById('prompt').value = this.value">
                <option value="">-- vordefinierte Beispiele --</option>
                {% for item in default_urls %}
                <option value="{{ item.url }}">{{ item.label }}</option>
                {% endfor %}
            </select>
            <input type="text" id="prompt" name="prompt" placeholder="z. B. Wie sicher ist facebook.com?" required>
            <input type="submit" value="Scannen & Auswerten">
        </form>

        {% if result %}
        <div class="result">
            <h2>Scan-Ergebnis</h2>
            <div class="field"><span class="label">Aktion:</span> {{ result.action }}</div>
            <div class="field"><span class="label">Kategorie:</span> 
                <span class="
                    {% if result.category.lower() == 'malicious' %}category-danger
                    {% elif result.category.lower() in ['suspicious', 'phishing', 'proxy-avoidance'] %}category-warning
                    {% else %}category-safe{% endif %}">
                    {{ result.category }}
                </span>
            </div>
            <div class="field"><span class="label">Erkannter Prompt:</span> {{ result.prompt_detected }}</div>
            <div class="field"><span class="label">Rohwert aus API:</span> <pre>{{ result.raw_prompt_detected }}</pre></div>
        </div>
        {% endif %}

        {% if gpt %}
        <div class="gpt">
            <h2>ChatGPT-Auswertung</h2>
            <pre>{{ gpt }}</pre>
        </div>
        {% endif %}

        {% if error %}
        <div class="error"><strong>Fehler:</strong> {{ error }}</div>
        {% endif %}

        <div class="footer">
            Powered by Prisma Access & GPT
        </div>
    </div>
</body>
</html>
"""

# --------------------
# Haupt-Route
# --------------------
@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    error = None
    gpt_summary = None

    if request.method == "POST":
        user_prompt = request.form.get("prompt")
        if not user_prompt:
            error = "Bitte gib einen Text oder eine Frage ein."
        else:
            try:
                url = 'https://service.api.aisecurity.paloaltonetworks.com/v1/scan/sync/request'
                headers = {
                    'Content-Type': 'application/json',
                    'x-pan-token': config["x_pan_token"]
                }
                data = {
                    "metadata": {
                        "ai_model": config["ai_model"],
                        "app_name": config["app_name"],
                        "app_user": config["app_user"]
                    },
                    "contents": [{"prompt": user_prompt}],
                    "tr_id": "1234",
                    "ai_profile": {"profile_name": "felix_test_profile"}
                }

                response = requests.post(url, headers=headers, json=data)
                response.raise_for_status()
                json_result = response.json()

                pd_raw = json_result.get("prompt_detected", "")
                raw_prompt_detected = pd_raw

                if isinstance(pd_raw, str):
                    pd = pd_raw.strip()
                elif isinstance(pd_raw, dict):
                    pd = pd_raw.get("text", "").strip()
                else:
                    pd = ""

                if pd.lower() == "url" or not pd:
                    pd = user_prompt

                category = json_result.get("category", "—")
                result = {
                    "action": json_result.get("action", "—"),
                    "category": category,
                    "prompt_detected": pd,
                    "raw_prompt_detected": raw_prompt_detected
                }

                # GPT nur, wenn Kategorie nicht kritisch ist
                blocked_categories = ["malicious", "suspicious", "phishing"]
                if result["action"] == "allow" and category.lower() not in blocked_categories:
                    gpt_summary = ask_gpt_about_prompt(user_prompt)

            except Exception as e:
                error = str(e)

    return render_template_string(
        HTML_TEMPLATE,
        result=result,
        error=error,
        gpt=gpt_summary,
        default_urls=config.get("default_urls", [])
    )

if __name__ == "__main__":
        app.run(host="0.0.0.0", port=5000, debug=True)
