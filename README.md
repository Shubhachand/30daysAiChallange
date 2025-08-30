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
| ✅ 13 | Create README.md documentation              | ✅ Done |
| ✅ 14 | Refactor code and upload to GitHub          | ✅ Done |
| ✅ 15 | Implement a basic WebSocket echo server     | ✅ Done |
| ✅ 16 | Stream audio from client to server          | ✅ Done |
| ✅ 17 | Transcribe streaming audio with AssemblyAI  | ✅ Done |
| ✅ 18 | Implement AssemblyAI turn detection         | ✅ Done |
| ✅ 19 | Get streaming LLM responses                 | ✅ Done |
| ✅ 20 | Stream text to Murf for TTS via WebSockets  | ✅ Done |
| ✅ 21 | Stream TTS audio from server to client      | ✅ Done |
| ✅ 22 | Play streaming audio on the client          | ✅ Done |
| ✅ 23 | Integrate all parts into a voice agent      | ✅ Done |
| ✅ 24 | Add a persona to the agent                  | ✅ Done |
| ✅ 25 | Add a special skill (e.g., web search)      | ✅ Done |
| ✅ 26 | Add a second special skill                  | ✅ Done |
| ✅ 27 | UI revamp and allow user API keys           | ✅ Done |
| ✅ 28 | Deploy the agent                            | ✅ Done |
| ✅ 29 | Update final documentation/README.md        | ✅ Done |

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

### ✅ Day 13 – Documentation with README.md 📄
- Created a comprehensive `README.md` in the project root
- Documented project purpose, features, architecture, and tech stack
- Added step-by-step setup, dependency installation, and API key instructions

---

### ✅ Day 14 – Code Refactoring & GitHub Upload 🛠️
- Refactored codebase for clarity and maintainability
- Moved third-party service logic (STT, TTS) to `/services` folder
- Introduced Pydantic models for API schemas
- Removed unused code and cleaned up imports
- Uploaded the project to a public GitHub repository

---

### ✅ Day 15 – Basic WebSocket Implementation 🌐
- Added `/ws` endpoint to FastAPI for WebSocket connections
- Implemented simple echo functionality (server returns received messages)
- Tested WebSocket with Postman and browser client

---

### ✅ Day 16 – Streaming Audio from Client to Server 🎙️
- Updated client to stream audio chunks to server via WebSocket in real-time
- Modified server to receive/process binary audio data
- Saved streamed audio as a file on the server

---

### ✅ Day 17 – Real-time Transcription with AssemblyAI 📝
- Integrated AssemblyAI SDK into WebSocket handler
- Streamed incoming audio directly to AssemblyAI’s real-time transcription
- Printed live transcription results to server console

---

### ✅ Day 18 – Implementing Turn Detection 🔄
- Used AssemblyAI’s turn detection to identify when user stops speaking
- Sent final transcript back to client at end of each turn
- Displayed transcript in UI for seamless conversation flow

---

### ✅ Day 19 – Streaming Responses from LLM 🤖
- Sent user transcript to Google Gemini LLM for response
- Configured LLM API for streaming text responses
- Accumulated and logged response chunks on server

---

### ✅ Day 20 – Streaming Text-to-Speech with Murf 🔊
- Established WebSocket connection to Murf TTS API
- Streamed LLM response text to Murf in chunks
- Received and logged base64-encoded audio stream from Murf

---

### ✅ Day 21 – Streaming Audio Back to the Client 🔁
- Relayed audio chunks from Murf to client via WebSocket
- Client accumulated incoming audio data for playback
- Verified data transfer with browser console logs

---

### ✅ Day 22 – Real-time Audio Playback 🎧
- Implemented client-side streaming audio playback
- Used Web Audio API to queue and play audio chunks as they arrived
- Achieved smooth, continuous conversational experience

---

### ✅ Day 23 – Full End-to-End Integration 🚀
- Connected all components for a complete conversational voice agent
- Flow: real-time transcription → LLM response → TTS → streaming playback
- Added chat history saving for session review

---

### ✅ Day 24 – Adding an Agent Persona 🦸
- Customized system prompt for LLM to define agent persona (e.g., pirate, robot)
- Ensured responses matched chosen persona’s tone and style

---

### ✅ Day 25 – Adding a Special Skill (Function Calling) 🛠️
- Integrated LLM function-calling for special skills (e.g., web search via Tavily API)
- Enabled agent to answer questions using external tools

---

### ✅ Day 26 – Adding a Second Special Skill 🧩
- Expanded agent with an additional skill (e.g., weather lookup)
- Broadened agent’s ability to handle complex, multi-domain queries

---

### ✅ Day 27 – UI Revamp and Configuration ⚙️
- Improved UI with a configuration section for user API keys
- Allowed users to enter their own Murf, AssemblyAI, and Gemini keys
- Enhanced flexibility and user control

---

### ✅ Day 28 – Deploying the Agent 🌍
- Finalized dependencies and production configs
- Deployed FastAPI backend and frontend to Render
- Shared public URL for live demo

---

### ✅ Day 29 – Final Documentation Update 📝
- Thoroughly updated `README.md` with all new features and instructions
- Documented persona, special skills, and user-configurable API keys
- Polished setup and deployment steps for end users

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
> - **Tavily (Web Search Skill)**: Register for a free API key at [tavily.com](https://www.tavily.com)

#### 5️⃣ Start the FastAPI Server
```bash
```bash
uvicorn app.main:app --reload
```
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
git clone https://github.com/Shubhachand/30daysAiChallange.git && cd 30daysAiChallange && python -m venv venv && venv\Scripts\activate && pip install -r requirements.txt

# All-in-one commands for Mac/Linux
git clone https://github.com/Shubhachand/30daysAiChallange.git && cd 30daysAiChallange && python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt
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
🎓 Final year student | Full-stack & AI enthusiast  
🔗 [LinkedIn](https://www.linkedin.com/in/shubhachand/) 

---

)

---

## 📢 Stay Tuned

> More updates daily...  
Follow along as I turn this into a fully functional **Voice Assistant App**!  
Made with ❤️ and curiosity.

---

