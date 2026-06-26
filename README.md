# 🩺 CURA — AI Healthcare Assistant

<div align="center">

![CURA AI Banner](https://img.shields.io/badge/CURA-AI%20Healthcare%20Assistant-0a84ff?style=for-the-badge&logo=heart&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-2.x-000000?style=for-the-badge&logo=flask&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-3-003B57?style=for-the-badge&logo=sqlite&logoColor=white)
![LLaMA 3](https://img.shields.io/badge/LLaMA%203.3-70B-8A2BE2?style=for-the-badge&logo=meta&logoColor=white)
![Three.js](https://img.shields.io/badge/Three.js-r128-black?style=for-the-badge&logo=three.js&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-22c55e?style=for-the-badge)

**A futuristic, 3D-animated AI Healthcare Chatbot powered by LLaMA 3.3 70B via Groq API.**  
*Delivering intelligent symptom assessment, medicine lookups, health tips, and emergency protocols — all in a premium glassmorphism UI.*

</div>

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [Tech Stack](#-tech-stack)
- [Project Structure](#-project-structure)
- [Architecture](#-architecture)
- [API Endpoints](#-api-endpoints)
- [Database Schema](#-database-schema)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Running the Application](#-running-the-application)
- [Usage Guide](#-usage-guide)
- [Medical Disclaimer](#%EF%B8%8F-medical-disclaimer)
- [License](#-license)

---

## 🌟 Overview

**CURA** (Clinical Understanding & Response Assistant) is a full-stack AI healthcare chatbot that combines the power of **Meta's LLaMA 3.3 70B** large language model (served via **Groq API**) with a rich, interactive frontend to provide a healthcare companion experience. 

CURA is designed to:
- Assist users in understanding symptoms and general health conditions
- Provide detailed medicine information for common Indian and global drugs
- Surface curated health tips across diet, exercise, hydration, and sleep
- Respond to emergencies with immediate protocol activation
- Maintain a persistent consultation history using SQLite

> ⚠️ **CURA is an informational assistant only.** It does NOT replace professional medical advice, diagnosis, or treatment.

---

## ✨ Features

### 🤖 Intelligent AI Chat
- Powered by **LLaMA 3.3 70B Versatile** model via Groq's ultra-fast inference API
- Persistent **conversation memory** — last 5 chat exchanges are passed as context for coherent multi-turn dialogue
- Smart **intent detection** (greeting, symptom check, diet/exercise/sleep tips, medicine queries, emergency)
- Dynamic **avatar expression** heuristics (wave, nod, concern) based on message intent
- **Typing indicator** with animated dots while the AI processes the query

### 🩻 Symptom Checker
- Keyword-based symptom analysis engine with **regex word-boundary matching**
- Covers 9 symptom categories: chest pain, breathing difficulty, severe bleeding, stroke, fever, headache, cough, fatigue, and nausea/vomiting
- Tri-level **severity classification**: `Mild` → `Moderate` → `Emergency`
- Returns matched **possible conditions** and **actionable first-aid advice**
- Emergency conditions trigger **automatic UI protocol activation**

### 💊 Medicine Information Lookup
- **20+ medicines** in an embedded database (Indian brands + global generics)
- Rich profiles including: generic name, category, uses, mechanism of action, dosage, side effects, precautions, drug interactions, pregnancy/breastfeeding safety, and storage
- **Fuzzy autocomplete** — live suggestions as you type (powered by `difflib`)
- Covers popular Indian brands: Dolo 650, Crocin, Combiflam, Saridon, Azithral, Pan-D, Pantocid, Montair-LC, Liv.52, Metrogyl, Limcee, Electral, and more

### 📊 Health Dashboard (Sidebar)
- **Consultation Logs** — Persistent history of all conversations stored in SQLite, displayed in the sidebar
- **Bookmarked Tips** — Save health tips during chat sessions for quick reference
- **Drug Index** — Searchable medicine reference panel with autocomplete
- **BMI Calculator** — Instant Body Mass Index calculation with classification (Underweight / Normal / Overweight / Obese)
- **Emergency Helpline Panel** — Quick access to emergency numbers (911, 108 India, 112 EU, 988 Crisis Lifeline, Poison Control)

### 🚨 Emergency Protocol System
- Automatic detection of high-risk keywords: `chest pain`, `stroke symptoms`, `breathing difficulty`, `severe bleeding`, `heart attack`
- Triggers a **CRITICAL EMERGENCY PROTOCOL** banner with:
  - One-tap call buttons for **911 (US/CA)**, **108 (India)**, **112 (EU)**
  - **Nearest Hospital** finder
  - Basic first-aid directives while waiting for EMS
- Emergency response cascades from both user messages AND AI responses

### 🎙️ Voice Features
- **Voice Input** — Web Speech API–based microphone dictation for hands-free symptom description
- **Text-to-Speech** — Configurable speech synthesis to read AI responses aloud
- **Voice Settings Modal** — Select voice profile, control speech velocity (0.5x–2.0x), toggle auto-speak

### 🎨 Premium UI / UX
- **Dark/Light Mode** toggle with persistent theme preference
- **Glassmorphism** design with glowing neon accents (cyan, purple, red)
- **3D Animated Avatar** rendered with Three.js + GSAP (wave, nod, concern animations)
- **Lottie Loading Screen** with progress bar and percentage counter
- **AOS (Animate on Scroll)** for smooth message entrance animations
- **Emoji Picker** with healthcare-themed emoji set
- **File Attachment** support (images/PDFs) in the chat input
- **User Profile Modal** — Editable name and email, synced to the SQLite Users table
- Google Fonts: **Inter**, **Orbitron**, **Outfit**

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| **AI / LLM** | LLaMA 3.3 70B Versatile via [Groq API](https://console.groq.com/) |
| **Backend** | Python 3.10+, Flask 2.x |
| **Database** | SQLite 3 (via Python `sqlite3`) |
| **Frontend** | HTML5, Vanilla CSS (Glassmorphism), Vanilla JavaScript |
| **3D Graphics** | Three.js r128 + GSAP 3.12 |
| **Animations** | Lottie Web (bodymovin), AOS 2.3, Typed.js |
| **Icons** | Font Awesome 6.4 |
| **Fonts** | Google Fonts (Inter, Orbitron, Outfit) |
| **Medicine Fuzzy Match** | Python `difflib` |
| **Env Management** | Custom `.env` file parser (no `python-dotenv` dependency) |

---

## 📁 Project Structure

```
AI HEALTHCARE CHATBOT/
│
├── .env                        # Environment variables (GROQ_API_KEY)
├── README.md                   # This file
│
├── backend/                    # Python Flask application
│   ├── app.py                  # Flask app factory, route definitions
│   ├── chatbot.py              # LLM integration, intent detection, chat history
│   ├── database.py             # SQLite schema, initialization, data seeding
│   ├── medicine_info.py        # Medicine database, lookup, autocomplete logic
│   └── symptom_checker.py      # Symptom rule engine, severity classification
│
├── database/
│   └── healthcare.db           # SQLite database file (auto-created on first run)
│
├── static/
│   ├── css/
│   │   └── style.css           # All styles — glassmorphism, dark/light themes, animations
│   └── js/
│       ├── app.js              # Application entry point / bootstrap
│       ├── chat.js             # Chat UI, API calls, voice I/O, history, profile
│       ├── animation.js        # GSAP avatar animations, loading screen logic
│       └── threeScene.js       # Three.js 3D avatar scene setup and rendering
│
└── templates/
    └── index.html              # Single-page application (Jinja2 template)
```

---

## 🏗️ Architecture

```
┌──────────────────────────────────────────────────────────┐
│                     Browser (Client)                     │
│                                                          │
│  ┌────────────┐  ┌──────────────┐  ┌────────────────┐  │
│  │ Three.js   │  │   chat.js    │  │  animation.js  │  │
│  │ 3D Avatar  │  │ (Core Logic) │  │ (GSAP/Lottie)  │  │
│  └────────────┘  └──────┬───────┘  └────────────────┘  │
│                         │ REST (JSON)                    │
└─────────────────────────┼──────────────────────────────-┘
                          │
                ┌─────────▼──────────┐
                │   Flask Backend    │
                │     (app.py)       │
                │                   │
                │  /chat            │
                │  /symptom-check   │
                │  /medicine        │
                │  /medicine/suggest│
                │  /health-tips     │
                │  /history         │
                │  /history/clear   │
                │  /profile         │
                └──┬──────────┬─────┘
                   │          │
        ┌──────────▼──┐   ┌───▼──────────┐
        │  Groq API   │   │   SQLite DB  │
        │ LLaMA 3.3   │   │ (healthcare  │
        │   70B       │   │    .db)      │
        └─────────────┘   └─────────────┘
```

---

## 🌐 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Serves the main SPA (`index.html`) |
| `POST` | `/chat` | Send a message to the AI chatbot |
| `POST` | `/symptom-check` | Analyze symptoms and return severity + advice |
| `GET` | `/medicine?name=<name>` | Lookup detailed medicine information |
| `GET` | `/medicine/suggest?query=<q>` | Get autocomplete suggestions for medicine names |
| `GET` | `/health-tips` | Retrieve all health tips grouped by category |
| `GET` | `/history?user_id=<id>` | Retrieve last 50 consultation records for a user |
| `POST` | `/history/clear` | Delete all consultation history for a user |
| `POST` | `/profile` | Create or update a user profile (name, email) |

### Request / Response Examples

**POST `/chat`**
```json
// Request
{ "message": "I have a severe headache and fever", "user_id": 1 }

// Response
{
  "response": "I'm sorry to hear you're experiencing...",
  "intent": "symptom_check",
  "animation": "nod",
  "emergency": false
}
```

**POST `/symptom-check`**
```json
// Request
{ "symptoms": "chest pain and breathing difficulty" }

// Response
{
  "severity": "Emergency",
  "conditions": ["Angina", "Myocardial Infarction (Heart Attack)", "Pulmonary Embolism"],
  "advice": ["This could be a life-threatening medical emergency.", "Call emergency services immediately.", ...],
  "is_emergency": true
}
```

**GET `/medicine?name=Paracetamol`**
```json
{
  "name": "Paracetamol",
  "generic_name": "Paracetamol (Acetaminophen)",
  "category": "Analgesic & Antipyretic",
  "uses": "Temporary relief of mild to moderate pain...",
  "dosage": "Adults: 500mg to 1000mg every 4-6 hours...",
  "common_side_effects": "Mild stomach upset, nausea...",
  "precautions": "Avoid alcohol. Do not take with other paracetamol products...",
  ...
}
```

---

## 🗄️ Database Schema

The SQLite database (`database/healthcare.db`) contains 4 tables:

```sql
-- Registered users / patient profiles
CREATE TABLE Users (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    name       TEXT NOT NULL,
    email      TEXT UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- All AI chat exchanges (user + bot messages)
CREATE TABLE ChatHistory (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id   INTEGER,
    message   TEXT NOT NULL,
    response  TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(user_id) REFERENCES Users(id)
);

-- Curated health tips (diet, exercise, water, sleep)
CREATE TABLE HealthTips (
    id       INTEGER PRIMARY KEY AUTOINCREMENT,
    title    TEXT NOT NULL,
    content  TEXT NOT NULL,
    category TEXT NOT NULL    -- 'diet' | 'exercise' | 'water' | 'sleep'
);

-- Medicine reference database
CREATE TABLE Medicines (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    name         TEXT UNIQUE NOT NULL,
    usage        TEXT NOT NULL,
    side_effects TEXT NOT NULL,
    precautions  TEXT NOT NULL
);
```

> The database is **auto-initialized and seeded** on first run with a default Guest User, 12 health tips, and 19 pre-loaded medicine records.

---

## ⚙️ Installation

### Prerequisites

| Requirement | Version |
|-------------|---------|
| Python | 3.10 or higher |
| pip | Latest |
| Git | Any |
| A Groq API Key | Free at [console.groq.com](https://console.groq.com/) |

### Step 1 — Clone the Repository

```bash
git clone https://github.com/your-username/cura-ai-healthcare-chatbot.git
cd "cura-ai-healthcare-chatbot"
```

### Step 2 — Create a Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 3 — Install Dependencies

```bash
pip install flask
```

> **No additional packages required.** The project uses Python's built-in `sqlite3`, `urllib`, `json`, `re`, `os`, and `difflib` modules. No external AI SDK is needed — the Groq API is called directly over HTTP.

---

## 🔧 Configuration

Create a `.env` file in the **root project directory** (same level as the `backend/` folder):

```env
# Get your free API key at: https://console.groq.com/
GROQ_API_KEY=your_groq_api_key_here
```

> **Security Note:** Never commit your `.env` file to version control. Add it to `.gitignore`.

```bash
echo ".env" >> .gitignore
```

---

## 🚀 Running the Application

```bash
# From the project root directory
python -m backend.app
```

The server starts on **http://localhost:5000**

```
 * Running on http://0.0.0.0:5000
 * Database initialized successfully at: .../database/healthcare.db
 * Debug mode: on
```

Open your browser and navigate to **[http://localhost:5000](http://localhost:5000)**

---

## 📖 Usage Guide

### 💬 Chatting with CURA
1. Type your health query in the chat input box (e.g., *"I have a fever and body aches"*)
2. Press **Enter** or click the **Send** button (paper plane icon)
3. CURA will respond with empathetic, context-aware advice using the LLaMA 3.3 70B model
4. Previous messages are remembered for a natural, flowing conversation

### 🎙️ Voice Input
- Click the **microphone** icon to speak your symptoms hands-free
- The transcribed text auto-fills the input field
- Configure voice settings via the **speaker** icon in the header

### 🔍 Medicine Lookup
- Open the sidebar **Drug Index** panel
- Type any medicine name (e.g., *"Dolo"*, *"Ibuprofen"*, *"Metformin"*)
- Autocomplete suggestions appear as you type
- Click a suggestion or press the search button for full drug information

### 🩺 Symptom Checker
- Type your symptoms directly in the chat (e.g., *"chest pain and shortness of breath"*)
- The backend's symptom checker classifies severity and returns targeted advice
- Emergency symptoms trigger the **CRITICAL EMERGENCY PROTOCOL** UI automatically

### ⚖️ BMI Calculator
- Open the sidebar **BMI Calculator** panel
- Enter your **weight (kg)** and **height (cm)**
- Click **Calculate BMI** for an instant result with classification

### 🗑️ Clear History
- Click the **trash** icon in the **Consultation Logs** sidebar section
- Confirm in the dialog to permanently delete all chat records for the current user

---

## ⚕️ Medical Disclaimer

> **IMPORTANT:** CURA is an **AI-powered informational tool only**. It is **NOT** a licensed medical device and does **NOT** provide medical diagnoses, prescriptions, or professional medical opinions.
>
> - Always consult a **qualified healthcare professional** for medical advice, diagnosis, and treatment.
> - In case of a **life-threatening emergency**, call your local emergency number immediately:
>   - 🇺🇸 USA / Canada: **911**
>   - 🇮🇳 India: **108** (Ambulance) | **112** (General Emergency)
>   - 🇪🇺 Europe: **112**
>   - 🧠 Mental Health Crisis: **988** (US)
>   - ☠️ Poison Control: **1-800-222-1222** (US)

---

## 📄 License

This project is licensed under the **MIT License**.

```
MIT License

Copyright (c) 2026 AVII — CURA Health Systems

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
```

---

<div align="center">

Made with ❤️ by **AVII**  
Powered by **LLaMA 3.3 · Groq · Flask · Three.js**

</div>
