let recordedChunks = [];
let audioContext, analyser, dataArray, animationId;
let isRecording = false;
let isSessionEnded = false; // NEW FLAG
const SESSION_ID = Math.random().toString(36).substring(2, 10);

document.addEventListener("DOMContentLoaded", () => {
  const recordBtn = document.getElementById("recordBtn");
  const endSessionBtn = document.getElementById("endSessionBtn"); // NEW BUTTON

  recordBtn.addEventListener("click", () => {
    if (isRecording) {
      stopRecording();
    } else {
      isSessionEnded = false; // reset if starting again
      startRecording();
    }
  });

  // End session button handler
  endSessionBtn.addEventListener("click", () => {
    isSessionEnded = true;
    setStatus("🛑 Session ended.");
  });
});

const startRecording = async () => {
  recordedChunks = [];
  isRecording = true;
  updateUI();

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
      cancelAnimationFrame(animationId);
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      stream.getTracks().forEach(track => track.stop());
      handleEchoFlow(new Blob(recordedChunks, { type: "audio/webm" }));
    };

    mediaRecorder.start();
    setStatus("Listening...");
  } catch (err) {
    alert("Microphone access is required.");
    console.error(err);
    isRecording = false;
    updateUI();
  }
};

const stopRecording = () => {
  if (mediaRecorder && mediaRecorder.state !== "inactive") {
    mediaRecorder.stop();
    isRecording = false;
    updateUI();
    setStatus("Processing...");
  }
};

const handleEchoFlow = async (blob) => {
  try {
    const res = await fetch(`/agent/chat/${SESSION_ID}`, {
      method: "POST",
      body: (() => {
        const formData = new FormData();
        formData.append("file", blob, "recorded-audio.webm");
        formData.append("session_id", SESSION_ID);
        return formData;
      })()
    });

    if (!res.ok) throw new Error("Chat request failed");

    const data = await res.json();
    if (data.response) setStatus(`🤖 ${data.response}`);

    const player = document.getElementById("echoPlayer");
    player.src = data.audioUrl || "/static/fallback.mp3";
    await player.play();

    // Auto-restart ONLY if session not ended
    player.onended = () => {
      if (data.audioUrl && !isSessionEnded) startRecording();
    };

  } catch (err) {
    console.error(err);
    setStatus("❌ Connection issue. Try again.");
  }
};

const updateUI = () => {
  const btn = document.getElementById("recordBtn");
  if (isRecording) {
    btn.textContent = "⏹️ Stop Talking";
    btn.classList.add("recording");
  } else {
    btn.textContent = "🎤 Start Talking";
    btn.classList.remove("recording");
  }
};

const setStatus = (msg) => {
  document.getElementById("statusText").textContent = msg;
};
