Visa AI Assistant: Full-Stack Prompt Engineering Platform
    A robust, containerized AI application designed to provide visa consultancy via Google's Gemini LLM. The project features a real-time "Admin Instruction Injector" that allows non-technical administrators to improve the AI's logic on the fly using a Supabase backend.

HOW TO LAUNCH: 
1. Prerequisites
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed.
- A `.env` file in the root directory 

2. The Quick Start (Docker)
The easiest way to get both the Frontend and Backend running simultaneously:

```powershell
# Build and start the containers
docker-compose up --build

3. Manual Startup:
- Backend (Python/Flask):
    cd backend
    python -m venv venv
    .\venv\Scripts\activate
    pip install -r requirements.txt
    python app.py

- Frontend (Next.js):
    cd frontend
    npm install
    npm run dev

⚠️ WARNING!!!:
This project currently uses the Gemini Free Tier API. 
- Rate Limits: 
    If you receive a `429 Error` or a message stating `error: data has no reply key` in the chatroom, it is likely due to the daily/per-minute rate limits of the free LLM quota.
- Resolution: 
    If this occurs, please wait until the limit resets before trying the request again, or switch to a Gemini Pro API key with higher throughput.

Architecture & Tech Stack:   
    Frontend:
        Next.js (React)
        Tailwind CSS: "Live Monitor" admin dashboard & chat styling
        State Management: React Hooks (useState, useEffect) for real-time UI updates

    Backend:
        Python Flask: server handling of AI orchestration and database logic
        Google Gemini 2.5 Flash Lite: The "brain" of the app, generating context-aware responses
        [Server] Supabase (PostgreSQL): primary database to store & retrieve system prompts in real-time

Infrastructure:
    Docker & Docker Compose: 
        - entire app is containerized. 
        - ensures that frontend, backend, environment variables work perfectly on any machine 

Development Journey (Prototype --> Production):
My development process evolved as the project complexity grew:

    Phase 1: Google AI Studio & Postman: I initially tested the Gemini "Anti-gravity" (AI) logic using Google’s sandbox. I used Postman to manually trigger API calls to ensure the AI could return the specific JSON format required for the frontend.

    Phase 2: VS Code & Flask: Once the logic was proven, I shifted to VS Code to build a custom Flask API. This allowed me to create specialized endpoints like /generate-reply and /improve-ai-manually and visualize it better.

    Phase 3: Solving the Supabase "Yellow Line" & Internal Issues: During integration, I faced "Internal 500 Errors" caused by mismatched Python environments. I resolved this by shifting my database calls from the standard Supabase library to direct REST API calls using the requests library, which proved significantly more stable within a Dockerized Linux environment. I learnt the importance of number results (200 meant it was well, 500 meant internal error, etc.)

Functionality:
    - Client Chat Interface
    - Users can engage in a natural conversation about visa requirements.

Optimistic UI: 
    - Messages appear instantly while the AI generates a response in the background.

Admin Dashboard (Secret Editing):
    - Access Control: The admin panel is protected. 
    - Users must click the "Admin" gear and enter the password: "issacompassadmin"

Live Monitor: 
    - real-time feed of all client-AI interactions

Instruction Injector:
    - Admins can write natural language commands (e.g., "Focus more on retirement visas").

Real-Time Sync: 
    - Clicking "Push Update" immediately updates the Supabase database. 
    - The AI logic is updated for the very next message without needing to restart the server


