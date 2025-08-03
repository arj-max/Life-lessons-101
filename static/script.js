let isSending = false;
let waitingForDone = false;
let currentQuestion = "";

const elements = {
  userInput: document.getElementById("userInput"),
  chatBox: document.getElementById("chatBox"),
  characterSelect: document.getElementById("characterSelect"),
  doneButton: document.getElementById("doneButton")
};

const sanitizeInput = (text) => DOMPurify ? DOMPurify.sanitize(text.trim()) : text.trim();

function showLoader() {
  const loader = document.createElement("div");
  loader.className = "loader";
  elements.chatBox.appendChild(loader);
}

function hideLoader() {
  const loader = document.querySelector(".loader");
  if (loader) loader.remove();
}

function appendMessage(message, isUser) {
  const messageElement = document.createElement("div");
  messageElement.className = isUser ? "user-message" : "bot-message";
  elements.chatBox.appendChild(messageElement);

  let index = 0;
  function typeWriter() {
    if (index < message.length) {
      messageElement.textContent = message.slice(0, index + 1);
      index++;
      setTimeout(typeWriter, 20);
      elements.chatBox.scrollTop = elements.chatBox.scrollHeight;
    }
  }
  typeWriter();
}

async function sendMessage() {
  if (isSending) return;

  const message = sanitizeInput(elements.userInput.value);
  const character = elements.characterSelect.value;

  if (!message || !character) {
    appendMessage("Please select a character and type a message!", false);
    return;
  }

  isSending = true;
  showLoader();
  appendMessage(message, true);
  elements.userInput.value = "";

  currentQuestion = message;
  waitingForDone = true;
  elements.doneButton.style.display = "inline-block";

  try {
    const response = await fetch("http://localhost:5000/ask", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        character,
        question: currentQuestion
      })
    });

    if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);

    const data = await response.json();
    appendMessage(data.response, false);
  } catch (err) {
    appendMessage(`Error: ${err.message}`, false);
  } finally {
    isSending = false;
    hideLoader();
  }
}

function sendDone() {
  const character = elements.characterSelect.value;

  if (!character || !currentQuestion) {
    appendMessage("Please start a conversation first!", false);
    return;
  }

  showLoader();

  fetch("http://localhost:5000/ask", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      character,
      question: "done"
    })
  })
  .then(res => {
    if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);
    return res.json();
  })
  .then(data => {
    appendMessage(data.response, false);
    if (data.response.includes("Instruction finished") || data.response.includes("✅")) {
      elements.doneButton.style.display = "none";
      waitingForDone = false;
    }
  })
  .catch(err => {
    appendMessage(`Error: ${err.message}`, false);
  })
  .finally(() => {
    hideLoader();
  });
}
