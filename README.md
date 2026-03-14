# Synthia - AI Assistant (Django + RAG + Tools)

Synthia is an intelligent agent built with **Django** and **OpenAI**. Unlike simple chatbots, Synthia utilizes a RAG (Retrieval-Augmented Generation) architecture to access a custom knowledge base and can perform real-world actions using external tools (e.g., managing tasks in Todoist).

## 🚀 Key Features

* **🧠 Long-Term Memory (RAG):** Uses `pgvector` and OpenAI Embeddings. The system allows the administrator to "teach" the AI new facts, which are stored in a vector database and retrieved during conversations.
* **🛠️ Agentic Capabilities & Tool Loop:** Equipped with a dynamic **Tool Registry** and robust error handling. The AI autonomously decides when to use tools, fetches missing parameters, and handles multi-step reasoning.
* **✅ Full Task Management (Todoist CRUD):** The agent doesn't just create tasks; it can read, filter, update, close, and delete tasks directly from the conversation using Todoist API v1.
* **💬 Telegram Interface:** Fully asynchronous integration via Telegram Bot API, enhanced with:
  * **Voice Integration:** Uses **OpenAI Whisper** for seamless voice message transcription and processing.
  * **Smart Messaging:** Features a custom **Smart Message Splitter** to intelligently bypass the 4096-character limit without breaking words or formatting.
* **🎭 Dynamic Persona Architecture:** A fully configurable personality system managed via the Django Admin panel. Build unique "Agent Modes" by combining modular identity blocks (`IdentityModules`) and adjusting specific behavioral sliders.
* **🐳 Dockerized:** Production-ready setup with Django, PostgreSQL, and Redis in containers.

## 🛠️ Tech Stack

* **Backend:** Python 3.11, Django 5.x
* **Database:** PostgreSQL + `pgvector` extension
* **AI Engine:** OpenAI API (GPT-4o / GPT-3.5-turbo)
* **Integrations:** Telegram Bot API (Async), Todoist API v1
* **Testing:** Pytest, pytest-django
* **DevOps:** Docker, Docker Compose

## ⚙️ Setup & Installation

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/Rzejson/Synthia-AI-Assistant.git](https://github.com/Rzejson/Synthia-AI-Assistant.git)
    cd Synthia-AI-Assistant
    ```

2.  **Environment Variables:**
    Create a `.env` file based on the example:
    ```bash
    cp .env.example .env
    ```
    *Fill in your `OPENAI_API_KEY`, `TELEGRAM_BOT_TOKEN`, and `TODOIST_API_KEY`.*

3.  **Run with Docker:**
    ```bash
    docker compose up -d --build
    ```

4.  **Apply Migrations:**
    ```bash
    docker compose exec web python manage.py migrate
    ```

5.  **Create Admin User:**
    ```bash
    docker compose exec web python manage.py createsuperuser
    ```

## 🧠 Usage Examples

* **Chat:** Talk to the bot on Telegram.
* **Task Management (CRUD):** * *Create:* "Remind me to buy milk tomorrow."
  * *Update/Delete:* "Actually, change that milk task to next week and mark it as highest priority. Also, delete the task about fixing the bike." -> The bot will query the database for IDs, update the first task, and delete the second.
* **Voice Interactions:** Send a voice note on Telegram, and the bot will transcribe it, understand the context, and execute the requested actions.
* **Knowledge Injection (Learning):**
    To add new facts to the vector database, use the custom management command:
    ```bash
    docker compose exec web python manage.py learn "The author of this project lives in Gdynia."
    ```
    *The bot will now answer correctly when asked "Where does the author live?"*
* **Persona Configuration (Admin Panel):**
    To change how Synthia behaves, log in to the Django Admin panel (`/admin/`).
    1. Define text blocks in **Identity Modules**.
    2. Define sliders in **Personality Traits** (e.g., Sarcasm, Formality).
    3. Create an **Agent Mode**, assign modules, set trait values (0-10), and check the `Is default` flag to activate it instantly.

---
*Created by Andrzej Jacyno.*