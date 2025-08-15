Welcome to my journey through the **30 Days of AI Voice Agents** challenge! 🚀  
This repo tracks my progress from **Day 1 to Day 30**, building AI-powered voice apps using **FastAPI**, **AssemblyAI**, and other tools. Each day, we build something new – from simple TTS to real-time transcription bots.

---

## 📅 Progress Overview

| Day | Task Description                             | Status  |
|-----|----------------------------------------------|---------|
| ✅ 1 | Setup FastAPI server & UI                    | ✅ Done |
| ✅ 2 | Integrated Text-to-Speech (TTS) using Murf   | ✅ Done |
| ✅ 3 | UI for Echo Bot with recording               | ✅ Done |
| ✅ 4 | Visualize live audio waveform                | ✅ Done |
| ✅ 5 | Upload audio to server via endpoint          | ✅ Done |
| ✅ 6 | Transcribe audio using AssemblyAI            | ✅ Done |
| ✅ 7 | Echo Bot v2 – Record → Transcribe → AI Voice | ✅ Done |
| ✅ 9 | Full non-streaming AI conversation pipeline  | ✅ Done |
| ✅ 10| Automatic continuous conversations           | ✅ Done |
| ✅ 11| Error handling & graceful recovery           | ✅ Done |
| ✅ 12| UI revamp & conversation flow upgrade        | ✅ Done |
| ⏳ 13–29 | Coming soon...                           | Ongoing |
| 🔜 30 | Final App + LinkedIn Post + Deployment 🎉   | Pending |

---

## 🔥 What We Built So Far

### ✅ Day 1 – Project Setup & UI Bootstrapping
- Initialized FastAPI backend
- Created clean responsive UI using HTML & CSS
- Setup file structure: `static/`, `templates/`, `main.py`

---

### ✅ Day 2 – Text-to-Speech with Murf.ai
- Connected Murf API to backend
- Built `/generate` endpoint
- User enters text → Audio is generated
- Audio is playable from the UI

---

### ✅ Day 3 – Echo Bot Recording UI
- Added recording functionality using `MediaRecorder` API
- Start/Stop buttons to control audio recording
- Saved audio locally in memory (no server upload yet)

---

### ✅ Day 4 – Audio Waveform Visualizer
- Used `Canvas` to show live audio waveform
- Integrated `AnalyserNode` from Web Audio API
- Made UI futuristic with pulse animations 🎧

---

### ✅ Day 5 – Upload Audio to Server
- Built `/upload-audio` POST endpoint
- Saved uploaded audio file in `/uploads` directory
- Returned file name, type, and size from server
- Displayed upload status in frontend

---

### ✅ Day 6 – Transcribe Audio via AssemblyAI
- Used AssemblyAI Python SDK
- Created `/transcribe/file` endpoint that:
  - Accepts audio file
  - Transcribes using `transcribe(audio_data)`
  - Returns full transcript
- Displayed transcription on frontend after recording

---
### ✅  Day 7 – Echo Bot v2 🎤✨

- Record audio in the browser
- Upload to backend via /tts/echo endpoint
 - Transcribe audio using AssemblyAI
 - Generate AI voice from transcription using Murf API
 - Play back the AI-generated voice in the browser
 - It’s like talking to yourself… but in a perfect studio voice 🎙️
---
### ✅ Day 8 – LLM Integration with Google Gemini 🤖
- Added `/llm/query` endpoint in FastAPI backend  
- Connected to Google’s Gemini API for intelligent, context-aware replies  
- Successfully tested — the LLM can explain Murf AI features 📝✨  
- Prepares the bot for natural, conversational responses  

---

### ✅ Day 9 – Full Non-Streaming AI Conversation Pipeline 🎯
- Implemented **listen → think → talk back** loop:  
  1. 🎤 Record voice in browser  
  2. ✍️ Transcribe via AssemblyAI  
  3. 💡 Generate smart response via Gemini API  
  4. 🎶 Convert to natural speech using Murf AI  
  5. 🔁 Play AI’s voice back instantly  
- Now holds voice-only conversations without typing  

---

### ✅ Day 10 – Automatic Continuous Conversations 🔄
- Bot now **listens, thinks, and responds** without extra clicks  
- After speaking, it starts listening again  
- Smooth, delay-free, back-and-forth interaction

---

### ✅ Day 11 – Error Handling & Graceful Recovery 💪
- Handled API timeouts, connection drops, and unexpected failures  
- Bot **recovers gracefully** without freezing  
- Friendly fallback messages when something goes wrong

---

### ✅ Day 12 – UI Revamp & Conversation Flow Upgrade 🎨
- Removed old TTS/Echo Bot UI → Now **pure Conversational Agent mode** 🎯  
- Single smart **Start/Stop** button 🎤⏹️  
- Added **End Session** button 🛑  
- Clean, glowing mic button & sleeker audio visualizer  
- Instant audio playback without bulky players  
- Mobile-friendly redesign 📱  

---


## 🛠 Tech Stack

- **Frontend**: HTML5, CSS3, JavaScript (vanilla)
- **Backend**: Python, FastAPI
- **APIs**: Murf.ai (TTS), AssemblyAI (Transcription)
- **Audio**: MediaRecorder API, Web Audio API, Canvas
- **Dev Tools**: VS Code, Postman, Git

---

## ⚙️ How to Run Locally

### 🚀 Step-by-Step Guide for Beginners

#### 1️⃣ Clone the Repository
```bash
git clone https://github.com/your-username/ai-voice-agent.git
cd ai-voice-agent
```

#### 2️⃣ Create Virtual Environment
**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**Mac/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

> 💡 **Tip:** You'll see `(venv)` in your terminal when the virtual environment is active!

#### 3️⃣ Install Dependencies
```bash
pip install -r requirements.txt
```

#### 4️⃣ Set Up Environment Variables
Create a `.env` file in the root directory:
```bash
# Windows
echo. > .env

# Mac/Linux
touch .env
```

Add your API keys to the `.env` file:
```env
MURF_API_KEY=your_murf_api_key_here
ASSEMBLYAI_API_KEY=your_assemblyai_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here
```

> 🔑 **Where to get API keys:**
> - **Murf.ai**: Sign up at [murf.ai](https://murf.ai)
> - **AssemblyAI**: Create account at [assemblyai.com](https://www.assemblyai.com)
> - **Google Gemini**: Get key from [Google AI Studio](https://makersuite.google.com/app/apikey)

#### 5️⃣ Start the FastAPI Server
```bash
uvicorn main:app --reload
```

> ✅ **Success!** You should see: `Uvicorn running on http://127.0.0.1:8000`

#### 6️⃣ Open in Browser
Navigate to: [http://127.0.0.1:8000](http://127.0.0.1:8000)

---

### 🛠️ Troubleshooting Tips

**If you get "pip not found":**
- Windows: `python -m pip install --upgrade pip`
- Mac/Linux: `python3 -m pip install --upgrade pip`

**If port 8000 is busy:**
```bash
uvicorn app.main:app --reload --port 8001

```

**To deactivate virtual environment:**
```bash
deactivate
```

### 📱 Quick Start Commands (Copy & Paste)
```bash
# All-in-one commands for Windows
git clone https://github.com/your-username/ai-voice-agent.git && cd ai-voice-agent && python -m venv venv && venv\Scripts\activate && pip install -r requirements.txt

# All-in-one commands for Mac/Linux
git clone https://github.com/your-username/ai-voice-agent.git && cd ai-voice-agent && python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt
```





---

## 🚀 Final Goal (Day 30)

- 🎯 Build a **complete AI Voice Agent app**
- 🧠 Features: TTS + Echo + Transcription + Real-time streaming
- 🌐 Deploy app on Render / Vercel
- 📸 Post final demo on [LinkedIn](https://www.linkedin.com/in/shubhachand/)

---


## 📢 Stay Tuned

> More updates daily...  
Follow along as I turn this into a fully functional **Voice Assistant App**!  
Made with ❤️ and curiosity.

---

### 👨‍💻 Author

**Shubhachand Patel**  
🧑‍🎓 3rd year student | Full-stack & AI enthusiast  
🔗 [LinkedIn](https://www.linkedin.com/in/shubhachand/) 

---

)

---

## 📢 Stay Tuned

> More updates daily...  
Follow along as I turn this into a fully functional **Voice Assistant App**!  
Made with ❤️ and curiosity.

---

