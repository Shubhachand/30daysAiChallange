// static/script.js
async function sendText() {
  const input = document.getElementById("textInput").value;

  const response = await fetch("/generate", {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({ text: input })
  });

  const data = await response.json();

  if (response.ok && data.audioUrl) {
    document.getElementById("player").src = data.audioUrl;
  } else {
    alert("Error generating audio!");
  }
}
