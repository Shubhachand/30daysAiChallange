let mediaRecorder;
let recordedChunks = [];
let audioContext, analyser, dataArray, animationId;

function getOrCreateSessionId() {
  const urlParams = new URLSearchParams(window.location.search);
  let sessionId = urlParams.get("session_id");

  if (!sessionId) {
    sessionId = Math.random().toString(36).substring(2, 10);
    urlParams.set("session_id", sessionId);
    window.history.replaceState({}, "", `${window.location.pathname}?${urlParams}`);
  }
  return sessionId;
}

const SESSION_ID = getOrCreateSessionId();

document.addEventListener("DOMContentLoaded", () => {
  const llmPlayer = document.getElementById("llmPlayer");

  llmPlayer.addEventListener("ended", () => {
    // For llmPlayer, we don't auto-restart recording; echo flow handles restart logic
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
  }
};

const playAudio = (url, autoRestart = true) => {
  const player = document.getElementById("echoPlayer") || document.createElement("audio");
  player.id = "echoPlayer";
  player.autoplay = true;
  player.src = url;
  document.body.appendChild(player);

  player.onended = () => {
    if (autoRestart) {
      console.log("Audio finished — restarting recording...");
      startRecording();
    } else {
      console.log("Audio finished — not restarting due to fallback/error.");
    }
  };

  player.play().catch(err => console.error("Audio playback failed:", err));
};

const handleEchoFlow = async (blob) => {
  const uploadStatus = document.getElementById("uploadStatus");
  const transcriptionStatus = document.getElementById("transcriptionStatus");

  uploadStatus.textContent = "Processing... 🎤";
  transcriptionStatus.textContent = "";

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

    if (!res.ok) throw new Error("Chat flow failed");

    const data = await res.json();

    if (data.transcription) {
      transcriptionStatus.textContent = `📝 ${data.transcription}`;
    }

    if (data.response) {
      transcriptionStatus.textContent += `\n🤖 ${data.response}`;
    }

    // Auto restart only if normal audio
    if (data.audioUrl) {
      playAudio(data.audioUrl, true);
    } else {
      playAudio("/static/fallback.mp3", false);
    }

    uploadStatus.textContent = "✅ Done";

  } catch (err) {
    console.error(err);
    uploadStatus.textContent = "❌ Processing failed — fallback playing";
    transcriptionStatus.textContent = "🤖 I'm having trouble connecting right now.";
    playAudio("/static/fallback.mp3", false); // No restart
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
    playAudio(data.audioUrl, false); // TTS flow doesn't auto-restart recording
  } else {
    alert("Failed to generate audio");
  }
};
