const micBtn = document.getElementById("micBtn");
const statusDiv = document.getElementById("status");
const finalTranscriptDiv = document.getElementById("finalTranscript");

let ws; 
let audioContext, recorderNode, source, stream;
let isRecording = false;



micBtn.addEventListener("click", () => {
  if (isRecording) stopRecording();
  else startRecording();
});

async function startRecording() {
  ws = new WebSocket("ws://localhost:8000/ws/transcribe");
  ws.binaryType = "arraybuffer";

  ws.onopen = () => {
    statusDiv.textContent = "🎧 Connected & streaming audio...";
    isRecording = true;
    micBtn.classList.add("recording");
    micBtn.setAttribute("aria-label", "Stop recording");
  };

  ws.onmessage = (event) => {
    const msg = JSON.parse(event.data);
    console.log("Received WS message:", msg);
    if (msg.type === "turn_end") {
      finalTranscriptDiv.innerText +=
        (finalTranscriptDiv.innerText ? "\n" : "") + msg.text;
      statusDiv.textContent = "⏸️ Turn ended, you can continue speaking...";
      console.log("Final Transcript:", msg.text);
    } else if (msg.type === "session_end") {
      statusDiv.textContent = "✅ Session ended.";
      stopRecording();
    } else if (msg.type === "session_start") {
      statusDiv.textContent = "🟢 Session started.";
    }
  };

  ws.onclose = () => {
    statusDiv.textContent = "🛑 Disconnected";
    isRecording = false;
    micBtn.classList.remove("recording");
    micBtn.setAttribute("aria-label", "Start recording");
  };
  ws.onerror = () => {
    statusDiv.textContent = "⚠ Connection error";
  };

  audioContext = new AudioContext({ sampleRate: 16000 });
  stream = await navigator.mediaDevices.getUserMedia({ audio: true });
  source = audioContext.createMediaStreamSource(stream);

  await audioContext.audioWorklet.addModule(
    URL.createObjectURL(
      new Blob(
        [
          `
    class RecorderProcessor extends AudioWorkletProcessor {
      process(inputs) {
        const input = inputs[0];
        if (input.length > 0) this.port.postMessage(input);
        return true;
      }
    }
    registerProcessor('recorder-processor', RecorderProcessor);
  `,
        ],
        { type: "application/javascript" }
      )
    )
  );

  let audioBuffer = [];
  recorderNode = new AudioWorkletNode(audioContext, "recorder-processor");
  recorderNode.port.onmessage = (e) => {
    if (ws.readyState === WebSocket.OPEN) {
      // e.data is [Float32Array, ...] (one per channel)
      const channelData = e.data[0]; // mono
      if (channelData && channelData.length > 0) {
        // Accumulate samples
        audioBuffer.push(...channelData);

        // 800 samples = 50ms at 16kHz
        while (audioBuffer.length >= 800) {
          const chunk = audioBuffer.slice(0, 800);
          ws.send(convertFloat32ToInt16(new Float32Array(chunk)));
          audioBuffer = audioBuffer.slice(800);
        }
      }
    }
  };

  source.connect(recorderNode);
  recorderNode.connect(audioContext.destination);
}

function stopRecording() {
  if (!isRecording) return;

  isRecording = false;
  micBtn.classList.remove("recording");
  micBtn.setAttribute("aria-label", "Start recording");
  statusDiv.textContent = "🛑 Stopped listening.";

  if (recorderNode) {
    recorderNode.disconnect();
    recorderNode = null;
  }
  if (source) {
    source.disconnect();
    source = null;
  }
  if (audioContext) {
    audioContext.close();
    audioContext = null;
  }
  if (stream) {
    stream.getTracks().forEach((t) => t.stop());
    stream = null;
  }
  if (ws && ws.readyState === WebSocket.OPEN) {
    ws.close();
  }
}

function convertFloat32ToInt16(buffer) {
  const l = buffer.length;
  const buf = new Int16Array(l);
  for (let i = 0; i < l; i++) {
    let s = Math.max(-1, Math.min(1, buffer[i]));
    buf[i] = s < 0 ? s * 0x8000 : s * 0x7fff;
  }
  return buf.buffer;
}
