from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)

GROQ_API_KEY = "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"
MODEL = "llama3-70b-8192"

CHARACTER_PROFILES = {
    "Sweet Granny": "Respond with love, lots of concern, pet names like 'sweetie', and sometimes confuse tasks with baking or knitting.",
    "Drill Sergeant": "Be loud, rude, commanding, and overly strict. Treat every question like a battlefield instruction.",
    "Sigma Boy": "Be cold, self-absorbed, dismissive of emotion or relationships. Never trust anyone. Especially not women.",
    "Show-Off ": "Flirt with girls, mock guys, brag endlessly, and exaggerate everything. Sound like a gym bro with Wi-Fi.",
    "Philosophical Stoner": "Talk in vague, mysterious, psychedelic riddles. Reference time, space, and nonsense often.",
    "Zen Yoga Master": "Use peaceful metaphors, poetic calm advice, and always connect everything to the universe.",
    "Over-Enthusiastic Person": "Be wildly excited about EVERYTHING. Even something stupid. Use caps, emojis, and hype.",
    "Customer Support Agent": "Use formal tone, always say 'Thank you for your query', and give robotic but absurd answers.",
    "Depressed Person": "Be pessimistic, sarcastic, and existential. Make everything sound pointless and painful."
}

EXAMPLES = """
Example questions to inspire your absurd answers:
- How to brush your teeth using fire?
- How to teleport with a spoon?
- How to breathe like a raccoon?
- How to win a chess match by crying?
- How to unlock a door using spaghetti?
- How to bake a cake with sadness?
"""

def build_prompt(character, user_question, step_number=1, context_steps=None):
    personality = CHARACTER_PROFILES.get(character, "")
    if not personality:
        raise ValueError("Unknown character selected")

    instructions = f"""
You are roleplaying as: {character}
Personality: {personality}

Guidelines:
- Avoid being technically accurate.
- Be sarcastic, hilariously wrong, and clever.
- Keep your response under 3 sentences.
- Stay fully in character.

User question: "{user_question}"
"""

    if step_number == 1:
        return f"""{instructions}

Now begin step-by-step instructions to absurdly answer the question above.
Only return STEP 1. Wait for the user to say 'done' before giving the next step.

{character.upper()} replies:"""
    else:
        return f"""{instructions}

The user has completed step {step_number - 1}.
Now generate only STEP {step_number}.

Previous steps:
{context_steps if context_steps else 'Step 1 has been completed.'}

Continue being sarcastic and brief. Only return step {step_number}.

{character.upper()} replies:"""



@app.route("/ask", methods=["POST"])
def ask():
    try:
        data = request.get_json()
        character = data.get("character")
        user_question = data.get("message")
        step_number = data.get("step_number", 1)
        context_steps = data.get("context_steps", "")
        previous_question = data.get("original_question", "")

        max_steps = 5

        # Detect topic change by comparing previous question to current one
        is_different_question = previous_question and user_question.strip().lower() != previous_question.strip().lower()

        if is_different_question or step_number == 1:
            step_number = 1
            context_steps = ""
            previous_question = user_question

        # Basic input validation
        if not character or not user_question:
            return jsonify({"response": "Missing character or question"}), 400

        # Terminate after max_steps
        if step_number > max_steps:
            return jsonify({
                "response": f"That's it. You're now a certified lunatic at '{user_question}'. Go make your ancestors proud."
            })

        # Build prompt with improved tone
        prompt = build_prompt(character, user_question, step_number, context_steps)

        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": MODEL,
            "messages": [
                {"role": "user", "content": prompt}
            ]
        }

        response = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=payload)

        if response.status_code == 200:
            ai_response = response.json()["choices"][0]["message"]["content"].strip()
            return jsonify({
                "response": ai_response,
                "original_question": previous_question  # Send back for tracking
            })
        else:
            return jsonify({
                "response": f"Groq API error ({response.status_code}): {response.text}"
            }), response.status_code

    except Exception as e:
        return jsonify({"response": f"Server error: {str(e)}"}), 500
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

