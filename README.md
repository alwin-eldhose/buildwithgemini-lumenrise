# 🌅 LumenRise — Mindful Morning AI Companion

> A warm, supportive morning companion agent that delivers personalized, multimodal briefings, uplifting affirmations, custom scenic morning artwork, and interactive daily reflections tailored to your profile and mood.

![LumenRise Demo](./demo.gif)

---

## 🌟 Overview

**LumenRise** is an AI-powered morning companion designed to start your day with mindfulness, clarity, and positivity. Whether you need a daily briefing, an inspiring quote, custom morning artwork, or a quiet space to record a journal entry, LumenRise adapts to your preferences over time while offering a beautiful, structured interface powered by **A2UI**.

---

## ✨ Key Features

- 🌅 **Personalized Daily Briefing**: Start your morning with an uplifting affirmation, weather greeting, and inspirational theme.
- 🎨 **Generative Scenic Artwork**: Request custom morning illustrations (e.g. *"misty mountain lake at sunrise"*) generated on demand using Gemini Imagen 3.
- 📝 **Mindful Journaling & Reflection**: Log gratitude, morning intentions, and reflections that persist across days.
- 💬 **Interactive Category Selection**: Tailor your affirmations to specific domains like *Literature & Philosophy*, *Sports & Athletics*, *Faith & Spirituality*, or *General Mindfulness*.
- 🖼️ **Native A2UI Display**: Rich UI cards, structured text hierarchy, and embedded media rendered directly in the chat UI.
- 🔄 **Multi-Session Continuity**: Cross-session memory allows LumenRise to remember your past preferences and journal notes.

---

## ☁️ Google Cloud & Agent Platform Tools

LumenRise leverages the full suite of **Google Cloud Agent Engine & Vertex AI** tools:

| Google Cloud Tool | Usage in LumenRise |
| :--- | :--- |
| 🧠 **Vertex AI Memory Bank** | Persists user profiles, preferences, and reflection history across multiple chat sessions. |
| 🗄️ **Google Cloud Firestore** | Stores structured journal entries, session logs, and user activity history (`roles/datastore.user`). |
| ☁️ **Google Cloud Storage (GCS)** | Hosts generated morning artwork & audio files in a public media bucket (`roles/storage.objectAdmin`). |
| 🌤️ **Live Weather API (Open-Meteo)** | Real-time live temperature, weather conditions, humidity, and wind speed lookup for any city. |
| 🎵 **Ambient Audio Chimes** | Synthesizes serene pentatonic morning audio chimes uploaded to Cloud Storage and rendered via A2UI. |
| 📚 **Vertex AI RAG Engine** | Grounded retrieval for curated literature, philosophical quotes, and mindfulness sources. |
| 🖼️ **Gemini Imagen 3** | Generates custom scenic sunrise artwork based on user mood (`gemini-3.1-flash-lite-image`). |
| 🎨 **A2UI Protocol (v0.8)** | Agent-to-User Interface JSON schema protocol streaming rich display cards and audio players directly to the web client. |


---

## 🛠️ Project Architecture

```
lumenrise/
├── app/
│   ├── agent.py            # ADK Reasoning Engine agent definition & A2UI callbacks
│   ├── a2ui_utils.py       # A2UI Schema Manager (v0.8 Basic Catalog)
│   ├── artwork_tool.py     # Generative artwork tool using Imagen 3 & Cloud Storage
│   └── journal_tool.py     # Firestore journal & memory integration tool
├── frontend/
│   ├── main.py             # FastAPI proxy bridging browser requests to Agent Engine over A2A
│   ├── static/index.html   # Responsive chat UI with built-in A2UI mini-renderer
│   └── requirements.txt    # Frontend dependencies (a2a-sdk, fastapi, uvicorn, httpx)
├── demo.gif                # Looping preview animation of the live application
└── README.md               # Project documentation
```

---

## 🚀 Running Locally

### 1. Prerequisites
Ensure you are authenticated with Google Cloud and have the required environment variables set:
```bash
gcloud auth application-default login
export GOOGLE_CLOUD_PROJECT="qwiklabs-gcp-03-c47843160c69"
export GOOGLE_CLOUD_LOCATION="us-east1"
```

### 2. Start the Frontend Application
Navigate to the `frontend/` directory and run the FastAPI server:
```bash
cd frontend
pip install -r requirements.txt
export AGENT_ENGINE_RESOURCE_NAME="projects/37061403718/locations/us-east1/reasoningEngines/6639378974092820480"
export AGENT_DIRECTORY="app"
python main.py
```

Open your browser and navigate to **[http://localhost:8081](http://localhost:8081)** to launch **LumenRise**!
