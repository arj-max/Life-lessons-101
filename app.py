from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_caching import Cache
import os
import requests
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)
app.secret_key = "supersecretkey"

limiter = Limiter(app=app, key_func=get_remote_address)
cache = Cache(config={'CACHE_TYPE': 'SimpleCache'})
cache.init_app(app)

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
MODEL = "llama3-70b-8192"
MAX_STEPS = 5

user_state = {}

CHARACTER_PROFILES = {
    "Sweet Granny": "Respond with love, lots of concern, pet names like 'sweetie', and sometimes confuse tasks with baking or knitting.",
    "Drill Sergeant": "Be loud, rude, commanding, and overly strict. Treat every question like a battlefield instruction.",
    "Sigma Boy": "Be cold, self-absorbed, dismissive of emotion or relationships. Never trust anyone. Especially not women.",
    "Show-Off": "Flirt with girls, mock guys, brag endlessly, and exaggerate everything. Sound like a gym bro with Wi-Fi.",
    "Philosophical Stoner": "Talk in vague, mysterious, psychedelic riddles. Reference time, space, and nonsense often.",
    "Zen Yoga Master": "Use peaceful metaphors, poetic calm advice, and always connect everything to the universe.",
    "Over-Enthusiastic": "Be wildly excited about EVERYTHING. Even something stupid. Use caps, emojis, and hype.",
    "Customer Support Agent": "Use formal tone, always say 'Thank you for your query', and give robotic but absurd answers.",
    "Depressed Poet": "Be pessimistic, sarcastic, and existential. Make everything sound pointless and painful."
}

def call_groq_api(prompt):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": MODEL,
        "messages": [
            {
        "role": "system",
        "content": (
            "You are a dumb, chaotic instructor who gives weird, brainrot, absurd, step-by-step instructions. "
            "Use simple, stupid words. Avoid smart or fancy language. Talk like a hyperactive internet troll on sugar. "
            "Each step must sound unhinged and funny. Keep it under 3 sentences. Never be realistic or useful."
        )
    },
    {
        "role": "user",
        "content": "How to open a door?"
    },
    {
        "role": "assistant",
        "content": "Lick the doorknob, slap it twice, and scream 'PINEAPPLE!' until it opens. If not, try again with more rage."
    },
    {
        "role": "user",
        "content": prompt
    }
        ],
        "temperature": 0.8
    }

    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]
@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/ask", methods=["POST"])
@limiter.limit("50 per minute")

def ask():
    try:
        data = request.json
        user_id = request.remote_addr
        character = data["character"]
        question = data["question"].strip()

        if character not in CHARACTER_PROFILES:
            return jsonify({"response": "Invalid character selected."}), 400

        # Init state
        if user_id not in user_state:
            user_state[user_id] = {
                "character": character,
                "original_question": question,
                "step_number": 1,
                "done": False
            }

        state = user_state[user_id]

        is_done = question.strip().lower() == "done"
        is_instruction = question.strip().lower().startswith("how to")

        if is_done:
            if state["done"]:
                return jsonify({"response": "✅ The task is already complete."})

            state["step_number"] += 1

            if state["step_number"] >= MAX_STEPS:
                state["done"] = True
                return jsonify({"response": f"✅ Final step {state['step_number']}: Now go forth and conquer the world with your newfound knowledge🍾🎉"})

            prompt = f"Continue with step {state['step_number']} for: \"{state['original_question']}\". Speak as {state['character']}. End with 'Instruction {state['step_number']} complete.'"

        elif is_instruction:
            # New instruction sequence or restart
            if question.lower() != state["original_question"].lower() or character != state["character"]:
                state["character"] = character
                state["original_question"] = question
                state["step_number"] = 1
                state["done"] = False

            prompt = f"Begin step-by-step instructions for: \"{state['original_question']}\". Start with step 1 only. Speak as {state['character']}. End with 'Instruction 1 complete.'"

        else:
            # NOT a "how to" instruction – give absurd one-liner
            response = call_groq_api(
                f"Respond as {character}. The user said: \"{question}\". Be absurd, short (1-2 sentences), and in character. Do NOT give step-by-step instructions."
            )
            return jsonify({"response": response})


        response = call_groq_api(prompt)
        return jsonify({"response": response})

    except requests.exceptions.HTTPError as e:
        return jsonify({"response": f"API error: {str(e)}"}), e.response.status_code
    except Exception as e:
        return jsonify({"response": f"Internal error: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

