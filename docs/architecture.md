# Synthia AI Assistant - Architecture Overview

## 1. Introduction
This document outlines the software architecture for the **Synthia AI Assistant**. The primary goal of this architecture is to create a modular, scalable, and extensible system that allows for easy addition of new functionalities, communication channels, and AI models.

The system is built using **Python 3.x** and the **Django** framework. While it can support web APIs, its primary interface is a fully asynchronous **Telegram Bot**. At its core, Synthia operates as an autonomous AI Agent, utilizing a RAG (Retrieval-Augmented Generation) memory system and a dynamic Tool Loop to interact with external services.

---

## 2. Core Principles
The architecture is guided by the following principles:

* **Modularity:** Components are designed to be independent and interchangeable.
* **Extensibility:** Adding new features (tools, communication channels, AI providers) has minimal impact on existing components.
* **Separation of Concerns:** Each layer (API, Service, Data) has clearly defined responsibilities.

---

## 3. High-Level Architecture Diagram
*(Placeholder for a future Mermaid or visual diagram)*

**Core Flow:**
`Telegram API` <-> `run_bot.py (Handlers)` <-> `ConversationOrchestrator` <-> `LLMFactory (OpenAI)` <-> `Tool Registry (Todoist, RAG, etc.)`

---

## 4. Key Components
The system is composed of several key layers and components:

### 4.1. Orchestrator (Service Layer)
The **Orchestrator** is the "brain" of the application. It acts as a Service Layer that encapsulates the complex business logic, keeping the views clean. Its responsibilities include:

* **Input Management:** Receiving and processing user input forwarded from the API layer.
* **Context Handling:** Managing conversation context (short-term memory) by retrieving history from the database.
* **AI Coordination:** Interacting with the configured LLM (Large Language Model) via the `LLMFactory`.
* **Intent Analysis:** Interpreting LLM responses to decide between a direct reply or tool usage.
* **Tool Execution:** Invoking external tools (e.g., Todoist, Home Assistant) and processing their results.
* **Response Generation:** Formatting and generating the final content to be sent to the user.
* **Memory Management:** Accessing and updating long-term memory and reflections.

### 4.2. Telegram Interface (`run_bot.py`)
This layer acts as the primary entry point for user interactions using the asynchronous `python-telegram-bot` library.
* **Handlers:** Catch incoming text and voice messages (`handle_message`, `handle_voice`), perform user authorization, and handle audio transcription via OpenAI Whisper.
* **Smart Message Splitter:** Ensures that large AI responses are intelligently chunked to bypass Telegram's 4096-character limit without breaking the content.

### 4.3. Tool Registry & RAG
The system extends the LLM's capabilities through discrete, manageable tools:
* **BaseTool Interface:** A standardized class ensuring all tools define their name, description, parameters, and an `execute` method.
* **Todoist Integration:** A suite of tools (`CreateTask`, `DeleteTask`, etc.) providing full CRUD capabilities over external tasks.
* **RAG Memory:** Utilizes `pgvector` to search and retrieve long-term knowledge injected into the system via custom Django management commands (e.g., `learn.py`).

---

## 5. Data Flow
The typical lifecycle of a message in Synthia follows these steps:

1.  **User Input:** The user sends a text or voice message to the Telegram bot.
2.  **Preprocessing:** If it's a voice message, `run_bot.py` downloads it to memory and uses Whisper for transcription. Text messages proceed directly.
3.  **Orchestration:** The text is passed to the `ConversationOrchestrator`, which logs the user message to the database and gathers conversation history.
4.  **Tool Loop (Agentic Flow):** The Orchestrator sends the context to the LLM. If the LLM requests a tool (e.g., `DeleteTask`), the Orchestrator executes the tool locally, appends the result to the context, and queries the LLM again. This loop continues until a final response is generated.
5.  **Persistence:** The final AI response is saved to the database.
6.  **Smart Delivery:** The final response is passed through the `message_splitter` to ensure it meets Telegram's constraints, and then sent back to the user chunk by chunk.