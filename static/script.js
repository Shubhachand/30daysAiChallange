let mediaRecorder;
let recordedChunks = [];
let audioContext, analyser, dataArray, animationId;

function getOrCreateSessionId() {
  const urlParams = new URLSearchParams(window.location.search);
  let sessionId = urlParams.get("session_id");

  if (!sessionId) {
    sessionId = Math.random().toString(36).substring(2, 10);
    urlParams.set("session_id", sessionId);
    window.history.replaceState(
      {},
      "",
      `${window.location.pathname}?${urlParams}`
    );
    
  } 
  return sessionId;
}

const SESSION_ID = getOrCreateSessionId();

document.addEventListener("DOMContentLoaded", () => {
  const llmPlayer = document.getElementById("llmPlayer");

  // Attach ended listener once when DOM ready
  llmPlayer.addEventListener("ended", () => {
    
    startRecording();
  });

  llmPlayer.addEventListener("play", () => {
    
  });

  llmPlayer.addEventListener("pause", () => {
    
  });

  llmPlayer.addEventListener("error", (e) => {
    
  });
});

const startRecording = async () => {
  recordedChunks = [];
  

  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    

    audioContext = new (window.AudioContext || window.webkitAudioContext)();
    const source = audioContext.createMediaStreamSource(stream);
    analyser = audioContext.createAnalyser();
    analyser.fftSize = 256;
    dataArray = new Uint8Array(analyser.frequencyBinCount);
    source.connect(analyser);

    const canvas = document.getElementById("visualizer");
    const ctx = canvas.getContext("2d");

    const draw = () => {
      animationId = requestAnimationFrame(draw);
      analyser.getByteFrequencyData(dataArray);

      ctx.fillStyle = "#1c1c1c";
      ctx.fillRect(0, 0, canvas.width, canvas.height);

      const barWidth = (canvas.width / dataArray.length) * 1.5;
      let x = 0;

      for (let i = 0; i < dataArray.length; i++) {
        const barHeight = dataArray[i];
        ctx.fillStyle = "#00ffd5";
        ctx.fillRect(x, canvas.height - barHeight, barWidth, barHeight);
        x += barWidth + 1;
      }
    };

    draw();

    mediaRecorder = new MediaRecorder(stream);
    mediaRecorder.ondataavailable = (e) => {
      if (e.data.size > 0) recordedChunks.push(e.data);
      
    };

    mediaRecorder.onstop = () => {
      
      const blob = new Blob(recordedChunks, { type: "audio/webm" });
      cancelAnimationFrame(animationId);
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      stream.getTracks().forEach((track) => track.stop());

      handleEchoFlow(blob);
    };

    mediaRecorder.start();
    

    document.getElementById("startBtn").disabled = true;
    document.getElementById("stopBtn").disabled = false;
    document.getElementById("startBtn").classList.add("recording-active");
  } catch (err) {
    alert("Please allow microphone access.");
    console.error("Recording failed:", err);
  }
};

const stopRecording = () => {
  if (mediaRecorder && mediaRecorder.state !== "inactive") {
    
    mediaRecorder.stop();
    document.getElementById("startBtn").disabled = false;
    document.getElementById("stopBtn").disabled = true;
    document.getElementById("startBtn").classList.remove("recording-active");
  } else {
    
  }
};

const playLLMAudio = (url) => {
  
  const llmPlayer = document.getElementById("llmPlayer");
  llmPlayer.src = url;
  llmPlayer.load();

  llmPlayer
    .play()
    .catch((err) => {
      console.error("Error playing audio:", err);
    });
};

const handleEchoFlow = async (blob) => {
  
  const uploadStatus = document.getElementById("uploadStatus");
  const transcriptionStatus = document.getElementById("transcriptionStatus");

  uploadStatus.textContent = "Processing... 🎤";
  transcriptionStatus.textContent = "";

  const formData = new FormData();
  formData.append("file", blob, "recorded-audio.webm");
  formData.append("session_id", SESSION_ID);

  try {
    const res = await fetch(`/agent/chat/${SESSION_ID}`, {
      method: "POST",
      body: formData,
    });

    if (!res.ok) {
      const errorText = await res.text();
      throw new Error(`Chat flow failed: ${errorText}`);
    }

    const data = await res.json();
   

    playLLMAudio(data.audioUrl);

    uploadStatus.textContent = "✅ Voice ready";
    transcriptionStatus.textContent = data.response
      ? `📝 ${data.response}`
      : data.transcription
      ? `📝 ${data.transcription}`
      : "";
  } catch (err) {
    
    uploadStatus.textContent = "❌ Processing failed";
    transcriptionStatus.textContent = "";
  }
};

const sendText = async () => {
  const text = document.getElementById("textInput").value;
  if (!text.trim()) {
    
    return alert("Please enter some text.");
  }



  const response = await fetch(`/generate?session_id=${SESSION_ID}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text }),
  });

  if (response.ok) {
    const data = await response.json();
    
    playLLMAudio(data.audioUrl);
  } else {
    alert("Failed to generate audio");
  }
};
