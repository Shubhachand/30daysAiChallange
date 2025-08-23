const micBtn = document.getElementById("micBtn");
const statusDiv = document.getElementById("status");
const finalTranscriptDiv = document.getElementById("finalTranscript");

let ws; 
let audioContext, recorderNode, source, stream;
let isRecording = false;
let audioChunks = []; // Array to accumulate base64 audio chunks



micBtn.addEventListener("click", () => {
  if (isRecording) stopRecording();
  else startRecording();
});

async function startRecording() {
  // Only create new WebSocket if it doesn't exist or is closed
  if (!ws || ws.readyState === WebSocket.CLOSED) {
    ws = new WebSocket("ws://localhost:8000/ws/transcribe");
    ws.binaryType = "arraybuffer";

    ws.onopen = () => {
      statusDiv.textContent = "🎧 Connected & streaming audio...";
      isRecording = true;
      micBtn.classList.add("recording");
      micBtn.setAttribute("aria-label", "Stop recording");
      audioChunks = []; // Reset audio chunks array for new session
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
      } else if (msg.type === "audio_chunk") {
        // Handle incoming base64 audio chunks
        console.log("Acknowledgement: Audio chunk received, base64 data length:", msg.data.length);
      // Play the audio chunk immediately
      playAudioChunk(msg.data);
      // Accumulate the chunks in an array
      audioChunks.push(msg.data);
      } else if (msg.type === "audio_start") {
        console.log("Audio playback started");
        // Initialize audio playback
        initializeAudioPlayback();
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
  } else if (ws.readyState === WebSocket.OPEN) {
    // WebSocket is already open, just update the UI
    statusDiv.textContent = "🎧 Connected & streaming audio...";
    isRecording = true;
    micBtn.classList.add("recording");
    micBtn.setAttribute("aria-label", "Stop recording");
    audioChunks = []; // Reset audio chunks array for new session
  }

  // Only create new AudioContext if it doesn't exist or is closed
  if (!audioContext || audioContext.state === 'closed') {
    audioContext = new AudioContext({ sampleRate: 16000 });
  }
  
  // Only get user media if not already available
  if (!stream) {
    stream = await navigator.mediaDevices.getUserMedia({ audio: true });
  }
  
  // Only create source if not already available
  if (!source) {
    source = audioContext.createMediaStreamSource(stream);
  }

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

  // Stop all audio playback
  stopAudioPlayback();

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

// Audio playback functions
let audioQueue = [];
let isPlaying = false;
let currentAudio = null;

function initializeAudioPlayback() {
  audioQueue = [];
  isPlaying = false;
  if (currentAudio) {
    currentAudio.pause();
    currentAudio = null;
  }
  console.log("Audio playback initialized");
}

function playAudioChunk(base64Data) {
  // Add the chunk to the queue
  audioQueue.push(base64Data);
  
  // If not currently playing, start playback
  if (!isPlaying && audioQueue.length > 0) {
    console.log("Starting playback of audio chunk");
    processAudioQueue();
  } else {
    console.log("Audio chunk added to queue, waiting for playback");
  }
}

function processAudioQueue() {
  if (audioQueue.length === 0) {
    isPlaying = false;
    currentAudio = null;
    return;
  }
  
  isPlaying = true;
  const base64Data = audioQueue.shift();
  
  try {
    // Debug: Check if base64 data looks valid
    console.log("Processing audio chunk, base64 length:", base64Data.length);
    
    // Skip very small chunks that are likely invalid/incomplete MP3 data
    if (base64Data.length < 1000) {
      console.log("Skipping small/invalid audio chunk (length:", base64Data.length, ")");
      // Continue with next chunk
      setTimeout(processAudioQueue, 50);
      return;
    }
    
    // Decode base64 to binary data
    const binaryData = atob(base64Data);
    console.log("Binary data length:", binaryData.length);
    
    const bytes = new Uint8Array(binaryData.length);
    for (let i = 0; i < binaryData.length; i++) {
      bytes[i] = binaryData.charCodeAt(i);
    }
    
    // Create blob with proper MIME type
    const blob = new Blob([bytes], { type: 'audio/mp3' });
    const url = URL.createObjectURL(blob);
    
    // Create audio element and play the chunk
    currentAudio = new Audio(url);
    
    currentAudio.onended = () => {
      console.log("Audio chunk playback completed");
      // Clean up the object URL
      URL.revokeObjectURL(url);
      // When this chunk finishes, play the next one
      setTimeout(processAudioQueue, 50); // Small delay to ensure smooth transition
    };
    
    currentAudio.onerror = (error) => {
      console.error("Error playing audio chunk:", error, "URL:", url);
      // Clean up the object URL
      URL.revokeObjectURL(url);
      // Continue with next chunk even if this one fails
      setTimeout(processAudioQueue, 50);
    };
    
    currentAudio.play().catch(error => {
      console.error("Error starting audio playback:", error, "URL:", url);
      // Clean up the object URL
      URL.revokeObjectURL(url);
      setTimeout(processAudioQueue, 50);
    });
  } catch (error) {
    console.error("Error processing audio chunk:", error);
    // Continue with next chunk even if this one fails
    setTimeout(processAudioQueue, 50);
  }
}

// Function to stop all audio playback
function stopAudioPlayback() {
  audioQueue = [];
  isPlaying = false;
  if (currentAudio) {
    currentAudio.pause();
    currentAudio = null;
  }
}
