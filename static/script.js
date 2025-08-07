let mediaRecorder;
let recordedChunks = [];
let audioContext, analyser, dataArray, animationId;

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
      const audioURL = URL.createObjectURL(blob);
      document.getElementById("echoPlayer").src = audioURL;

      cancelAnimationFrame(animationId);
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      stream.getTracks().forEach(track => track.stop());

      handleUploadAndTranscription(blob);
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

const handleUploadAndTranscription = async (blob) => {
  const uploadStatus = document.getElementById("uploadStatus");
  const transcriptionStatus = document.getElementById("transcriptionStatus");

  uploadStatus.textContent = "Uploading...";
  transcriptionStatus.textContent = "";

  const formData = new FormData();
  formData.append("file", blob, "recorded-audio.webm");

  try {
    const uploadRes = await fetch("/upload-audio", {
      method: "POST",
      body: formData,
    });

    if (!uploadRes.ok) throw new Error("Upload failed");
    const uploadResult = await uploadRes.json();
    uploadStatus.textContent = `✅ Uploaded: ${uploadResult.filename} (${uploadResult.size_in_kb} KB)`;

    const transcribeRes = await fetch("/transcribe/file", {
      method: "POST",
      body: formData,
    });

    if (!transcribeRes.ok) throw new Error("Transcription failed");
    const transcribeResult = await transcribeRes.json();
    transcriptionStatus.textContent = `📝 Transcription: ${transcribeResult.text}`;

  } catch (err) {
    console.error(err);
    uploadStatus.textContent = "❌ Upload failed";
    transcriptionStatus.textContent = "❌ Transcription failed";
  }
};

const sendText = async () => {
  const text = document.getElementById("textInput").value;
  if (!text.trim()) return alert("Please enter some text.");

  const response = await fetch("/generate", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text }),
  });

  if (response.ok) {
    const data = await response.json();
    document.getElementById("player").src = data.audioUrl;
  } else {
    alert("Failed to generate audio");
  }
};
