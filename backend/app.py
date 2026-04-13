from flask import Flask, request, jsonify
from flask_cors import CORS
# importing custom logic for database & AI generation 
from process_conversations import (
    get_system_prompt_in_db,
    update_system_prompt_in_db,
    generate_ai_reply,
    update_ai_prompt
)

import os
from dotenv import load_dotenv
from supabase import create_client, Client
import google.generativeai as genai

# load environment variables from env. file
load_dotenv()

# Get credentials from .env file --> initialize supabase
url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")

supabase: Client = create_client(url, key)

app = Flask(__name__)
# global var to store session chat logs for Admin Live Monitor
chat_history = []
# resource sharing so frontend can talk to API
CORS(app, resources={r"/*": {"origins": "*"}})

@app.route('/')
def home():
    return "AI Agent Server is LIVE! The endpoints are ready for requests."

def parse_chat_history(chat_history):
    """Converts the JSON array chat history into the flat string format `process_conversations` expects."""
    formatted = []
    for msg in chat_history:
        role = "(CLIENT)" if msg.get("role") == "client" else "(CONSULTANT)"
        formatted.append(f"{role} {msg.get('message', '')}")
    return "\n".join(formatted)

@app.route('/generate-reply', methods=['POST'])
def generate_reply_endpoint():
    data = request.json
    if not data:
        return jsonify({"error": "Missing JSON payload"}), 400
        
    client_sequence = data.get("clientSequence", "")
    chat_history_arr = data.get("chatHistory", [])
    
    # Convert incoming JSON history into clean string for AI to read
    chat_history_str = parse_chat_history(chat_history_arr)
    
    # load the system prompt from Supabase
    system_prompt = get_system_prompt_in_db()
    
    # Send history, new message, and rules to Google Gemini
    ai_response = generate_ai_reply(
        client_history_str=chat_history_str,
        client_message_str=client_sequence,
        system_prompt_template=system_prompt
    )
    
    if "error" in ai_response:
        return jsonify({"reply": ai_response}), 500
    
    # Extract text from AI's JSON response
    ai_text = ai_response.get("reply", str(ai_response))

    # Save to global history so Admin Dashboard can see the conversation live
    global chat_history
    chat_history.append({"role": "user", "text": client_sequence})
    chat_history.append({"role": "ai", "text": ai_text})
        
    return jsonify({
        "aiReply": ai_text
    })

@app.route('/improve-ai', methods=['POST'])
def improve_ai_endpoint():
    data = request.json
    if not data:
        return jsonify({"error": "Missing JSON payload"}), 400
        
    client_sequence = data.get("clientSequence", "")
    chat_history_arr = data.get("chatHistory", [])
    consultant_reply = data.get("consultantReply", "")
    
    chat_history_str = parse_chat_history(chat_history_arr)
    existing_prompt = get_system_prompt_in_db()
    
    # First, generate the hypothetical predicted AI reply as baseline
    # Only send the last 6 messages to the AI to keep the "envelope" small for free tier LLM API
    shortened_history = chat_history_arr[-6:]
    ai_response = generate_ai_reply(
        client_history_str=parse_chat_history(shortened_history),
        client_message_str=client_sequence,
        system_prompt_template=existing_prompt
    )
    predicted_reply = ai_response.get("reply", str(ai_response))
    
    # Pass all variables to Editor
    nuevo_prompt = update_ai_prompt(
        existing_prompt=existing_prompt,
        client_sequence=client_sequence,
        chat_history=chat_history_str,
        real_reply=consultant_reply,
        predicted_reply=predicted_reply
    )
    
    if nuevo_prompt and nuevo_prompt != existing_prompt:
        update_system_prompt_in_db(nuevo_prompt)
        
    return jsonify({
        "predictedReply": predicted_reply,
        "updatedPrompt": nuevo_prompt
    })

@app.route('/improve-ai-manually', methods=['POST'])
def improve_ai_manually_endpoint():
    data = request.json
    new_instructions = data.get("instructions") or data.get("instruction") or ""
    
    if not new_instructions:
        return jsonify({"error": "Instructions are empty"}), 400

    try:
        # 1. Fetch current
        existing_prompt = get_system_prompt_in_db()
        
        # 2. Combine
        updated_combined_prompt = f"{existing_prompt}\n{new_instructions}"
        
        # 3. USE THE HELPER FUNCTION (Instead of the supabase object)
        # use the 'requests' logic (more stable in Docker)
        success = update_system_prompt_in_db(updated_combined_prompt)
        
        if success:
            return jsonify({"success": True, "updatedPrompt": updated_combined_prompt})
        else:
            return jsonify({"error": "Supabase refused the update"}), 500
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/get-logs', methods=['GET'])
def get_logs():
    # Return chat history variable 
    return jsonify({"history": chat_history})

if __name__ == '__main__':
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)

