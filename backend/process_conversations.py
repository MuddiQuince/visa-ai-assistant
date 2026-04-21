import json #library for Data Structure conversion (String <--> List/Dictionary)
import os #interface for OS level String retrieval (env Variables) 
import sys #system-level parameters and IO reconfiguration
import requests #library for HTTP Data Dtructure transport (JSON over the wire) 
from dotenv import load_dotenv #utility to populate the os.environ (Dictionary) 
import google.generativeai as genai

#Data Structure: IO Stream: ensures terminal handles UTF-8 (multibyte symbol) 
# characters without crashing
sys.stdout.reconfigure(encoding='utf-8')

#DS: internal Dictionary 
#reads .env file and updates os.environ mapping
load_dotenv()

def get_system_prompt_in_db():
    #DS: String 
    #acesses values from os.environ Dictionary [O(1) lookup time]
    url = os.environ.get("SUPABASE_URL", "").strip()
    key = os.environ.get("SUPABASE_KEY", "").strip()
    
    if not url or not key:
        return "You are an AI assistant."
        
    # PostgREST headers for Supabase API access
    try:
        #DS: Dictionary 
        #used to store HTTP Metadata, key-value pairs for authentication 
        headers = {
            "apikey": key,
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json"
        }

        # Query 'Settings' table where key --> 'system_prompt'
        #DS: Dynamic String 
        #build URL endpoint 
        safe_url = url.rstrip('/')
        endpoint = f"{safe_url}/rest/v1/Settings?key=eq.system_prompt&select=value"
        
        # Use PATCH to update only the 'value' column for the 'system_prompt' row
        response = requests.get(endpoint, headers=headers)
        
        if response.status_code == 200:
            #DS: List of Dictionaries 
            #Supabase returns JSON, parsed into Python DS
            data = response.json()
            #length check on List [O(1)]
            #Dictionary look-up [O(1)]
            if data and len(data) > 0:
                return data[0].get('value', "You are an AI assistant.")
    except Exception as e:
        print(f"Error fetching system prompt: {e}")
    
    return "You are an AI assistant."

def update_system_prompt_in_db(new_prompt_text):
    #DS: Dictionary 
    #specific headers required for REST PATCH operations 
    url = os.environ.get("SUPABASE_URL", "").strip()
    key = os.environ.get("SUPABASE_KEY", "").strip()
    
    headers = {
        "apikey": key,
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
        "Prefer": "return=minimal"
    }
    
    # This is where the patch happens!
    safe_url = url.rstrip('/')
    endpoint = f"{safe_url}/rest/v1/Settings?key=eq.system_prompt"
    
    try:
        #DS: Dictionary 
        #'json=' param turns python Dictionary --> JSON string 
        # new_prompt_text is DEFINED here because it's in the (parentheses) above
        response = requests.patch(endpoint, headers=headers, json={"value": new_prompt_text})
        
        if response.status_code in [200, 204]:
            print("✅ Supabase Update Success!")
            return True
        else:
            print(f"❌ Supabase Update Failed: {response.text}")
            return False
    except Exception as e:
        print(f"🚨 Update Error: {e}")
        return False


def process_conversations(filepath):
    #opens files stream in File IO 
    with open(filepath, 'r', encoding='utf-8') as f:
        #DS: List 
        #loads entire JSON array into memory of O(N) space complexity 
        data = json.load(f)

    #DS: List
    #store "Result Set" of interaction objects 
    all_interactions = []

    #iteration (visiting each conversation dictionary) O(N) time 
    for conv in data:
        contact_id = conv.get('contact_id')
        scenario = conv.get('scenario')
        messages = conv.get('conversation', [])
        #DS: list of message Dictionaries 

        #DS: Stack-like List 
        #grows as we move through the convo 
        history = []
        i = 0
        #Linear scan O(M) (M = messages in 1 convo)
        while i < len(messages):
            msg = messages[i]

            #branching based on msg 'direction' key 
            if msg.get('direction') == 'in':
                #DS: List 
                #temporary buffer for contiguous client messages 
                # Start of a client sequence
                client_sequence = []
                #nested while groups in messages, i still moves forward O(M) time 
                while i < len(messages) and messages[i].get('direction') == 'in':
                    client_sequence.append(messages[i])
                    i += 1

                #DS: List 
                #temporary buffer for consultant reply 
                # Following consultant sequence reply
                consultant_sequence = []
                while i < len(messages) and messages[i].get('direction') == 'out':
                    consultant_sequence.append(messages[i])
                    i += 1

                #DS: Dictionary 
                # Append to our list of interactions
                interaction = {
                    'contact_id': contact_id,
                    'scenario': scenario,
                    #DS: List copy 
                    #creates snapshot (shallow copy) of history so no crash O(K) time 
                    'history': list(history),
                    'client_sequence': client_sequence,
                    'consultant_sequence': consultant_sequence
                }
                #append to result list O(1) time 
                all_interactions.append(interaction)
                
                # Add these sequences to history for the next iteration O(K) 
                history.extend(client_sequence)
                history.extend(consultant_sequence)
            else:
                # If there's an unexpected 'out' message before any 'in' message, just add to history
                history.append(msg)
                i += 1

    return all_interactions

def format_history(history_messages):
    #DS: List of Strings 
    #gathering strings before joining 
    formatted = []
    for msg in history_messages:
        role = "(CLIENT)" if msg['direction'] == 'in' else "(CONSULTANT)"
        formatted.append(f"{role} {msg['text']}")
    #DS: String 
    #.join is O(N) (N = total character count) 
    #'.join' better than '+=' since O(N) better than O(N^2)
    return "\n".join(formatted)

def format_client_message(client_sequence):
    formatted = []
    for msg in client_sequence:
        formatted.append(msg['text'])
    return "\n".join(formatted)

def generate_ai_reply(client_history_str, client_message_str, system_prompt_template=None):
    #DS: String 
    #building prompt through string interpolation 
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("Error: GEMINI_API_KEY is missing")
        return {"reply": "Error: API Key not configured."}
        
    genai.configure(api_key=api_key)

    # Use a safe fallback for history
    history_val = client_history_str if client_history_str else "(No previous history)"

    #DS: Multiline String (instruction set for LLM)
    # Building detailed prompt for Gemini
    # Force strict JSON instructions
    prompt = f"""{system_prompt_template if system_prompt_template else "You are a helpful visa assistant."}

**Context:**
{history_val}

**Client Message:**
{client_message_str}

IMPORTANT: You must respond ONLY with a valid JSON object in this format:
{{"reply": "your message here"}}"""

    try:
        model = genai.GenerativeModel(
            model_name='gemini-2.5-flash-lite',
            system_instruction="You are a JSON-only response bot. Always return {'reply': '...'}"
        )
        response = model.generate_content(prompt)
        
        # Check if response actually has text
        if not response or not response.text:
            return {"reply": "The AI could not generate a response."}

        #DS: String Manipulation 
        #strips whitespace & markdown characters 
        reply_text = response.text.strip()
        
        # Clean up Markdown (Gemini often wraps JSON in ```json blocks)
        if "```" in reply_text:
            #string split O(N) 
            #acess index[1] of resulting list 
            reply_text = reply_text.split("```")[1]
            # Convert string response into a Python Dictionary
            if reply_text.startswith("json"):
                reply_text = reply_text[4:]
        
        # Try to parse the JSON
        try:
            #convert AI string -> Python Dictionary DS 
            parsed = json.loads(reply_text.strip())
            # Ensure the 'reply' key exists
            if "reply" in parsed:
                return parsed
            else:
                # If AI sent {"message": "hi"}, convert it to {"reply": "hi"}
                return {"reply": str(next(iter(parsed.values())))}
        except json.JSONDecodeError:
            #DS: Dictionary
            #fallback to ensure ensure API consistency 
            # If parsing fails, just wrap the raw text to avoid the 500 error
            return {"reply": reply_text}

    except Exception as e:
        print(f"🚨 CRITICAL GENERATION ERROR: {e}")
        # Returning a dictionary ensures app.py doesn't crash
        return {"reply": f"Sorry, I encountered an internal error: {str(e)}"}

def update_ai_prompt(existing_prompt, client_sequence, chat_history, real_reply, predicted_reply):
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("Error: GEMINI_API_KEY environment variable not set.")
        return existing_prompt
        
    genai.configure(api_key=api_key)

    # provide the 'real' consultant answer vs the 'AI' answer so Gemini can see the gap
    editor_prompt = f"""You are an AI prompt engineer analyzing and improving an AI chatbot prompt.
Your goal is to adjust the existing prompt so that the AI's predicted reply more closely matches the real consultant's reply.

**Existing Prompt:**
{existing_prompt if existing_prompt else "You are an AI assistant."}

**Client Message / Sequence:**
{client_sequence}

**Chat History:**
{chat_history}

**Real Consultant Reply:**
{real_reply}

**Predicted AI Reply:**
{predicted_reply}

Please analyze the differences between the real reply and the predicted reply. Then, update the existing prompt to better instruct the AI for future interactions.
Return ONLY valid JSON in the following format:
{{"prompt": "new updated prompt text..."}}
"""

    try:
        model = genai.GenerativeModel(
            model_name='gemini-2.5-flash-lite',
            system_instruction="You are a prompt editor. Return your response ONLY as valid JSON."
        )
        response = model.generate_content(editor_prompt)
        # Parse the improvement and return it for database storage
        reply_text = response.text
        
        # Strip potential markdown formatting if Gemini wrapped the JSON
        if "```" in reply_text:
            reply_text = reply_text.split("```")[1]
            if reply_text.startswith("json"):
                reply_text = reply_text[4:]
            
        parsed_json = json.loads(reply_text.strip())
        new_prompt = parsed_json.get("prompt")
        
        if new_prompt:
            return new_prompt
    except Exception as e:
        print(f"Error generating updated prompt: {e}")
        
    return existing_prompt

#main execution loop 
def main():
    filepath = 'conversations.json'
    #DS: List of Dictionaries 
    #output of processing logic 
    interactions = process_conversations(filepath)
    
    print(f"Total extracted interactions: {len(interactions)}\n")
    
    system_prompt_template = get_system_prompt_in_db()
    if system_prompt_template:
        preview = system_prompt_template.replace('\n', ' ')[:50]
        print(f"Fetched prompt from database: {preview}...")
    
    if not interactions:
        return

    #DS: Slice / Selection (picking specific indices for testing 
    # samples:
    # 1. very first interaction (usually no history)
    # 2. interaction with some history to show the full context
    interaction1 = interactions[0]
    interaction2 = next((item for item in interactions if len(item['history']) > 0), interactions[1])
    
    samples = [interaction1, interaction2]
    
    for i, sample in enumerate(samples):
        print(f"=== SAMPLE {i+1} ===")
        print(f"Scenario: {sample['scenario']}\n")
        
        print("CLIENT:")
        client_text = format_client_message(sample['client_sequence'])
        print(client_text)
        
        print("\nCHAT HISTORY:")
        history_text = format_history(sample['history'])
        print(history_text if history_text else "(No previous history)")
        
        print("\nAI REPLY:")
        if os.environ.get("GEMINI_API_KEY"):
            ai_reply = generate_ai_reply(history_text, client_text, system_prompt_template)
            predicted_text = ai_reply.get("reply", str(ai_reply))
            print(json.dumps(ai_reply, indent=2, ensure_ascii=False))
            
            # integrate the Editor logic:
            # get the real consultant reply from sample['consultant_sequence']
            # run the editor, update the prompt locally and in DB.
            if sample['consultant_sequence']:
                #print to stdout 
                formatted_real_reply = format_client_message(sample['consultant_sequence'])
                
                print("\nREAL CONSULTANT REPLY:")
                print(formatted_real_reply)
                
                print("\n--- Running AI Prompt Editor ---")
                new_db_prompt = update_ai_prompt(
                    existing_prompt=system_prompt_template,
                    client_sequence=client_text,
                    chat_history=history_text,
                    real_reply=formatted_real_reply,
                    predicted_reply=predicted_text
                )
                
                if new_db_prompt and new_db_prompt != system_prompt_template:
                    print(f"Prompt updated. New length: {len(new_db_prompt)}")
                    # Save to DB
                    update_system_prompt_in_db(new_db_prompt)
                    # Update variable for next iterations
                    system_prompt_template = new_db_prompt
                else:
                    print("No significant change to prompt.")
                    
        else:
            print("GEMINI_API_KEY not found in environment. Skipping LLM generation.")
            print("To see generated replies, please set GEMINI_API_KEY in a .env file or environment variable.")
            print("\nExample expected JSON output format if key was present:")
            print('{\n  "reply": "[Predicted AI reply text goes here]"\n}')
        print("==========================\n")

if __name__ == '__main__':
    main()
