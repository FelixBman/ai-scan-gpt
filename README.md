# AI Scan with GPT Integration

This project provides a Flask-based web interface for scanning URLs, prompts, or user questions using the Palo Alto AI Security API. If the request is classified as **allow**, the content is forwarded to **ChatGPT** for additional analysis or summarization.

## 🛠️ Features

- Free-form input (URLs, questions, text prompts)
- Palo Alto AI Security API scanning
- Color-coded risk categorization (green/yellow/red)
- Optional ChatGPT analysis for safe content
- Configurable example prompts via `config.json`
- Network-accessible web interface

---

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

---

## 📝 License

This project is intended for internal or demonstration purposes.  
**Do not publish API keys or sensitive data.**

---

## 🔒 Disclaimer

This tool interacts with Palo Alto Networks' and OpenAI's APIs.  
Make sure you comply with their **terms of service** and **data privacy regulations**.
