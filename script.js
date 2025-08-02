let stepNumber = 1;
let contextSteps = "";
let currentQuestion = "";
let waitingForDone = false;

// Unified message append function
function appendMessage(message, isUser) {
  const chatBox = document.getElementById("chatBox");
  const messageElement = document.createElement("div");
  messageElement.className = isUser ? "user-message" : "bot-message";
  chatBox.appendChild(messageElement);

  let index = 0;
  function typeWriter() {
    if (index < message.length) {
      messageElement.textContent += message.charAt(index);
      index++;
      setTimeout(typeWriter, 20);
      chatBox.scrollTop = chatBox.scrollHeight;
    }
  }

  typeWriter();
}

async function sendMessage() {
  const userInput = document.getElementById("userInput");
  const character = document.getElementById("characterSelect").value;
  const message = userInput.value.trim();

  if (!message || !character) return;

  appendMessage(message, true);
  userInput.value = "";
  waitingForDone = true;
  document.getElementById("doneButton").style.display = "inline-block";

  if (stepNumber === 1) {
    currentQuestion = message;
  }

  try {
    const response = await fetch("http://localhost:5000/ask", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        character,
        message,
        step_number: stepNumber,
        context_steps: contextSteps,
        original_question: currentQuestion
      })
    });

    const data = await response.json();
    appendMessage(data.response, false);

    contextSteps += `\nStep ${stepNumber}: ${data.response}`;
    stepNumber++;
  } catch (err) {
    appendMessage("Error: " + err.message, false);
  }
}

function sendDone() {
  const character = document.getElementById("characterSelect").value;

  if (!character || !currentQuestion) {
    appendMessage("Please select a character and send a message first.", false);
    return;
  }

  fetch("http://localhost:5000/ask", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      character,
      message: currentQuestion,
      step_number: stepNumber,
      context_steps: contextSteps,
      original_question: currentQuestion
    })
  })
    .then(res => res.json())
    .then(data => {
      appendMessage(data.response, false);

      contextSteps += `\nStep ${stepNumber}: ${data.response}`;
      stepNumber++;

      // End condition: hide button when task is finished
      if (stepNumber > 5 || data.response.toLowerCase().includes("certified lunatic")) {
        document.getElementById("doneButton").style.display = "none";
        waitingForDone = false;
      }
    })
    .catch(err => {
      appendMessage("Error: " + err.message, false);
      document.getElementById("doneButton").style.display = "none";
    });
}
