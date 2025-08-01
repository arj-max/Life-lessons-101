let currentCharacter = null;

function selectCharacter(charName) {
  currentCharacter = charName;
  document.getElementById('interaction').style.display = 'block';
}

function getResponse() {
  const input = document.getElementById("userInput").value.toLowerCase();
  const absurdWords = ["breathe", "blink", "smile", "stand", "drink", "walk"];
  const isAbsurd = absurdWords.some(word => input.includes(word));
  let response = "";

  if (!currentCharacter) {
    response = "Pick a character first!";
  } else if (isAbsurd) {
    // Funny responses for absurd questions
    response = getAbsurdReply(currentCharacter);
  } else {
    // Funny responses for serious questions
    response = getSeriousReply(currentCharacter);
  }

  document.getElementById("response").innerText = response;
}

function getAbsurdReply(character) {
  const replies = {
    commander: "You breathe like a recruit! Inhale like you're storming a battlefield!",
    granny: "Oh dear, just pinch your nose and think of cookies. That's how I breathe!",
    support: "Please restart your lungs and try again.",
    flirty: "Blink? Baby, I only blink when I see *you*.",
    depressed: "Blinking... yeah, that's about the only thing I’m good at.",
    philosopher: "Blinking is but the universe reminding you that perception is temporary.",
    enthusiastic: "OMG YES!!! Blink LIKE A LEGEND!!! YOU GOT THIS!!!",
    yogi: "Close your eyes. Now open them. You have blinked. Welcome to the now."
  };
  return replies[character];
}

function getSeriousReply(character) {
  const replies = {
    commander: "I'm here for war strategies, not kitchen gossip! OUT!",
    granny: "You don’t even tie your own shoelaces and now you want biryani?",
    support: "Thank you for contacting us. Unfortunately, we do not support cooking ambitions.",
    flirty: "You want biryani? Let’s spice things up, babe.",
    depressed: "Cooking? That’s rich. I barely microwave sadness.",
    philosopher: "To make biryani is to embrace both chaos and spice.",
    enthusiastic: "YESSSS!!! COOK THAT BIRYANI!!! Add ALL THE SPICES!!! WOOO!!!",
    yogi: "To cook is to destroy the raw to create peace. Are you ready?"
  };
  return replies[character];
}
