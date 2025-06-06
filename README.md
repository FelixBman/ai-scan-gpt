# AI Scan with GPT Integration

This project provides a Flask-based web interface for scanning URLs, prompts, or user questions using the Palo Alto AI Security API. If the request is classified as **allow**, the content is forwarded to **ChatGPT** for additional analysis or summarization.

## 🛠️ Features

- Free-form input (URLs, questions, text prompts)
- Palo Alto AI Security API scanning
- Color-coded risk categorization (green/yellow/red)
- Optional ChatGPT analysis for safe content
- Configurable example prompts via `config.json`
- Network-accessible web interface

## 🚀 Quick Start Docker

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/ai-scan-gpt.git
cd ai-scan-gpt
```

### 2. Configure API Keys

- Get your API Key and Profile Name  from Strata Cloud Manager
- Get your OpenAI Key

```bash
nano docker-compose.yaml
```

### 3. Deploy

```bash
sudo docker compose build
sudo docker compose up -d
```

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/ai-scan-gpt.git
cd ai-scan-gpt
```

### 2. Set Up the Environment

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Configure API Keys

1. Copy the example configuration:

```bash
cp config.example.json config.json
```

2. Edit `config.json` and replace:

- `\"your-pan-token-here\"` with your **Palo Alto AI Security API token**
- `\"your-openai-api-key-here\"` with your **OpenAI API key**

### 4. Run the Application

```bash
python app.py --host=0.0.0.0 --port=5000
```

Access the app via `http://<your-server-ip>:5000` in your browser.

---

## ⚙️ Systemd Auto-Start (Optional)

To run the application as a background service on Linux:

1. Create the service file:

```bash
sudo nano /etc/systemd/system/ai-scan-gpt.service
```

2. Example content:

```ini
[Unit]
Description=AI Scan with GPT Flask App
After=network.target

[Service]
User=your-linux-username
WorkingDirectory=/path/to/ai-scan-gpt
Environment=\"PATH=/path/to/ai-scan-gpt/venv/bin\"
ExecStart=/path/to/ai-scan-gpt/venv/bin/python app.py --host=0.0.0.0 --port=5000

Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

3. Reload and start:

```bash
sudo systemctl daemon-reload
sudo systemctl enable ai-scan-gpt.service
sudo systemctl start ai-scan-gpt.service
```

Check the status with:

```bash
sudo systemctl status ai-scan-gpt.service
```

---

## 📝 License

This project is intended for internal or demonstration purposes.  
**Do not publish API keys or sensitive data.**

---

## 🔒 Disclaimer

This tool interacts with Palo Alto Networks' and OpenAI's APIs.  
Make sure you comply with their **terms of service** and **data privacy regulations**.
