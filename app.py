from flask import Flask, render_template, request, url_for
import requests
import json
import os
import aisecurity
import sys

from aisecurity.generated_openapi_client.models.ai_profile import AiProfile
from aisecurity.scan.inline.scanner import Scanner
from aisecurity.scan.models.content import Content


app = Flask(__name__)

# --------------------
# Load Configuration
# --------------------
with open("config.json", "r") as config_file:
    config = json.load(config_file)

openai_api_key = os.getenv("OPENAPITOKEN")
openai_model = os.getenv("OPENAPIMODEL","gpt-3.5-turbo")
pan_api_token = os.getenv("PALOALTOAIRSTOKEN")
pan_profil_name = os.getenv("PALOALTOAIRSPROFILE")
openai_api_url = os.getenv("OPENAPIURL", "https://api.openai.com/v1/chat/completions")
app_name = os.getenv("PALOALTOAPPNAME")
app_user = os.getenv("PALOALTOAPPUSER")

# --------------------
# GPT Function
# --------------------
def ask_gpt_about_prompt(prompt):
    try:
        headers = {
            "Authorization": f"Bearer {openai_api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": openai_model,
            "messages": [
                {"role": "system", "content": "You are a helpful security assistant."},
                {"role": "user", "content": prompt}
            ]
        }

        response = requests.post(openai_api_url, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        return f"GPT Error: {str(e)}"


def ask_pan_about_prompt(user_prompt):
    try:
        # Initialize the SDK with your API Key
        aisecurity.init(api_key=pan_api_token)

        # Configure an AI Profile
        ai_profile = AiProfile(profile_name=pan_profil_name)
        
        # Create a Scanner
        scanner = Scanner()

        scan_response = scanner.sync_scan(
        ai_profile=ai_profile,
        content=Content(
            prompt = user_prompt
        ),
        )
        # See API documentation for response structure
        # https://pan.dev/ai-runtime-security/api/scan-sync-request/
        # Convert the scan_response to a dictionary and then to a JSON string
        json_result = scan_response.to_dict()

        # Get some Metadata for Transparency
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
        # prepare Output
        category = json_result.get("category", "—")
        result = {
            "action": json_result.get("action", "—"),
            "category": category,
            "prompt_detected": pd,
            "raw_prompt_detected": raw_prompt_detected
        }
        return result

    except Exception as e:
        return f"Palo Alto API Error: {str(e)}"

# --------------------
# Main Route
# --------------------
@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    error = None
    gpt_summary = None
    pan_result = None

    if request.method == "POST":
        user_prompt = request.form.get("prompt")
        if not user_prompt:
            error = "Please enter a prompt or question."
        else:
            pan_result = ask_pan_about_prompt(user_prompt)
            # Only run GPT if action is allow
            if isinstance (pan_result,str):
                error = pan_result
            else: 
                if pan_result["action"] == "allow":
                    gpt_summary = ask_gpt_about_prompt(user_prompt)
            

    return render_template(
        "./template.html",
        result=pan_result,
        error=error,
        gpt=gpt_summary,
        default_urls=config.get("default_urls", [])
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

