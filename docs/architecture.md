# Synthia AI Assistant - Architecture Overview

## 1. Introduction
This document outlines the software architecture for the **Synthia AI Assistant**. The primary goal of this architecture is to create a modular, scalable, and extensible system that allows for easy addition of new functionalities, communication channels, and AI models.

The system is built using **Python 3.x**, leveraging the **Django** framework and **Django REST Framework (DRF)** to provide a robust web-based API.

---

## 2. Core Principles
The architecture is guided by the following principles:

* **Modularity:** Components are designed to be independent and interchangeable.
* **Extensibility:** Adding new features (tools, communication channels, AI providers) has minimal impact on existing components.
* **Separation of Concerns:** Each layer (API, Service, Data) has clearly defined responsibilities.

---

## 3. High-Level Architecture Diagram
*(Placeholder for a future Mermaid or visual diagram)*

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

### 4.2. API Layer (Views & Serializers)
This layer follows the Django REST Framework conventions and acts as the entry point for all communications:

* **Serializers:** Handle the transformation between JSON payloads and Django Model instances (e.g., `MessageSerializer`, `ConversationSerializer`).
* **Views:** Manage the Request-Response cycle. They perform initial validation, handle authentication, and delegate business logic to the **Orchestrator**.

---

## 5. Data Flow
The typical lifecycle of a message in Synthia followsi these steps:

1.  **User Request:** The user sends a `POST` request with the message body to the `/api/messages/` endpoint.
2.  **Validation:** The `MessageViewSet` receives the request and uses the `MessageSerializer` to validate the input.
3.  **Forwarding:** The view initializes a `ConversationOrchestrator` instance and forwards the validated message content.
4.  **Classification:** The orchestrator invokes the LLM service to determine the user's intent (e.g., general chat or tool usage).
5.  **Execution:** Based on the intent, the orchestrator either invokes a specific **Tool** or generates a direct response using the conversation history.
6.  **Persistence:** The final AI response is saved to the database as a `Message` object linked to the conversation.
7.  **Response:** The view returns the newly created message data to the user as a JSON response.