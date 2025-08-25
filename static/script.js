const micBtn = document.getElementById("micBtn");
const statusDiv = document.getElementById("status");

const finalTranscriptDiv = document.getElementById("finalTranscript");
const transcriptionsDiv = document.getElementById("transcriptions");

// Helper to add a chat bubble
function addChatBubble(text, isUser = false, bubbleId = null) {
  const bubble = document.createElement("div");
  bubble.className = "chat-bubble" + (isUser ? " user" : "");
  bubble.textContent = text;
  if (bubbleId) bubble.dataset.bubbleId = bubbleId;
  transcriptionsDiv.appendChild(bubble);
  transcriptionsDiv.scrollTop = transcriptionsDiv.scrollHeight;
  return bubble;
}

function removeBubbleById(bubbleId) {
  const bubble = transcriptionsDiv.querySelector(
    `[data-bubble-id='${bubbleId}']`
  );
  if (bubble) bubble.remove();
}

let ws;
let audioContext, recorderNode, source, stream;
let isRecording = false;
let audioChunks = []; // Array to accumulate base64 audio chunks
let currentPersona = "Teacher"; // Default persona

micBtn.addEventListener("click", () => {
  if (isRecording) stopRecording();
  else startRecording();
});

async function startRecording() {
    // Only create new WebSocket if it doesn't exist or is closed
    if (!ws || ws.readyState === WebSocket.CLOSED) {
        // Get selected persona
        const personaSelect = document.getElementById("personaSelect");
        currentPersona = personaSelect.value;
        
        ws = new WebSocket(`ws://localhost:8000/ws/transcribe?persona=${currentPersona}`);
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
        // Show user transcript as a right-aligned chat bubble
        addChatBubble(msg.text, true);
        // Show 'Echo is thinking...' bubble (left)
        addChatBubble("Echo is thinking...", false, "thinking");
        finalTranscriptDiv.innerText +=
          (finalTranscriptDiv.innerText ? "\n" : "") + msg.text;
        statusDiv.textContent = "⏸️ Turn ended, you can continue speaking...";
        console.log("Final Transcript:", msg.text);
      } else if (msg.type === "session_end") {
        statusDiv.textContent = "✅ Session ended.";
        stopRecording();
      } else if (msg.type === "session_start") {
        statusDiv.textContent = "🟢 Session started.";
      } else if (msg.type === "ai_text") {
        // Remove 'Echo is thinking...' bubble and show AI response
        removeBubbleById("thinking");
        addChatBubble(msg.text, false);
      } else if (msg.type === "audio_chunk") {
        // Handle incoming base64 audio chunks
        console.log(
          "Acknowledgement: Audio chunk received, base64 data length:",
          msg.data.length
        );
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
  if (!audioContext || audioContext.state === "closed") {
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
let audioContextPlayback = null;
let audioBufferSource = null;

function initializeAudioPlayback() {
  audioQueue = [];
  isPlaying = false;
  if (currentAudio) {
    currentAudio.pause();
    currentAudio = null;
  }
  if (audioBufferSource) {
    audioBufferSource.stop();
    audioBufferSource = null;
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

async function processAudioQueue() {
  if (audioQueue.length === 0) {
    isPlaying = false;
    currentAudio = null;
    audioBufferSource = null;
    return;
  }

  isPlaying = true;
  const base64Data = audioQueue.shift();

  try {
    // Debug: Check if base64 data looks valid
    console.log("Processing audio chunk, base64 length:", base64Data.length);

    // Skip very small chunks that are likely invalid/incomplete MP3 data
    if (base64Data.length < 1000) {
      console.log(
        "Skipping small/invalid audio chunk (length:",
        base64Data.length,
        ")"
      );
      // Continue with next chunk with minimal delay
      setTimeout(processAudioQueue, 10);
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
    const blob = new Blob([bytes], { type: "audio/mp3" });
    const url = URL.createObjectURL(blob);

    // Use Web Audio API for smoother playback
    if (!audioContextPlayback) {
      audioContextPlayback = new (window.AudioContext || window.webkitAudioContext)();
    }

    // Fetch and decode the audio data
    const response = await fetch(url);
    const arrayBuffer = await response.arrayBuffer();
    
    try {
      const audioBuffer = await audioContextPlayback.decodeAudioData(arrayBuffer);
      
      // Create and configure audio source
      audioBufferSource = audioContextPlayback.createBufferSource();
      audioBufferSource.buffer = audioBuffer;
      audioBufferSource.connect(audioContextPlayback.destination);
      
      audioBufferSource.onended = () => {
        console.log("Audio chunk playback completed");
        // Clean up the object URL
        URL.revokeObjectURL(url);
        // When this chunk finishes, play the next one immediately
        processAudioQueue();
      };
      
      audioBufferSource.start();
      
    } catch (decodeError) {
      console.error("Error decoding audio data:", decodeError);
      // Fallback to HTML5 Audio if Web Audio API fails
      fallbackToHTML5Audio(url);
    }

  } catch (error) {
    console.error("Error processing audio chunk:", error);
    // Continue with next chunk even if this one fails
    setTimeout(processAudioQueue, 10);
  }
}

function fallbackToHTML5Audio(url) {
  // Fallback to HTML5 Audio element
  currentAudio = new Audio(url);

  currentAudio.onended = () => {
    console.log("Audio chunk playback completed (fallback)");
    // Clean up the object URL
    URL.revokeObjectURL(url);
    // When this chunk finishes, play the next one with minimal delay
    setTimeout(processAudioQueue, 10);
  };

  currentAudio.onerror = (error) => {
    console.error("Error playing audio chunk (fallback):", error, "URL:", url);
    // Clean up the object URL
    URL.revokeObjectURL(url);
    // Continue with next chunk even if this one fails
    setTimeout(processAudioQueue, 10);
  };

  currentAudio.play().catch((error) => {
    console.error("Error starting audio playback (fallback):", error, "URL:", url);
    // Clean up the object URL
    URL.revokeObjectURL(url);
    setTimeout(processAudioQueue, 10);
  });
}

// Function to stop all audio playback
function stopAudioPlayback() {
  audioQueue = [];
  isPlaying = false;
  
  if (currentAudio) {
    currentAudio.pause();
    currentAudio = null;
  }
  
  if (audioBufferSource) {
    audioBufferSource.stop();
    audioBufferSource = null;
  }
  
  if (audioContextPlayback) {
    audioContextPlayback.close();
    audioContextPlayback = null;
  }
}
