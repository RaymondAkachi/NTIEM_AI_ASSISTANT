# AI-Powered Business Assistant & Operations Hub

## Project Overview

The **AI-Powered Business Assistant & Operations Hub** is a robust, enterprise-scale solution designed to revolutionize business operations through intelligent automation, advanced knowledge retrieval, and comprehensive real-time oversight. Built as a sophisticated AI assistant and bot, this system transforms how organizations manage information, interact with customers, and coordinate internal events.

## Key Features

* **Intelligent Knowledge Retrieval (RAG-Powered):**
    Leverages Retrieval Augmented Generation (RAG) to provide instant, accurate, and context-aware answers to virtually any business-related question. The bot is comprehensively fed with all organizational information, acting as a central knowledge base.
* **Seamless Appointment Management System:**
    Facilitates effortless appointment booking for customers and empowers administrators with a dedicated interface to efficiently accept, review, and cancel appointments directly through the AI assistant.
* **Automated Communication Engine:**
    Implements sophisticated protocols for proactive engagement, delivering automated email and SMS notifications to both staff and customers regarding upcoming events, appointment confirmations, and critical updates.
* **Comprehensive Business Oversight:**
    Functions as an intelligent business overseer, maintaining real-time awareness and centralized intelligence across all staff activities, ongoing events, and organizational information, significantly enhancing operational visibility and strategic decision-making.

## Technologies Utilized

This project leverages a modern, scalable, and versatile technology stack:

* **Backend:** Python (core logic, AI orchestration)
* **Langchain and Langgrpah:** AI logic and AI Orchestration
* **Vector Database:** Qdrant (for efficient similarity search and RAG implementation)
* **Relational Database:** PostgreSQL (for structured data like appointments, user management)
* **NoSQL Database:** MongoDB Atlas (User chat history management)
* **Assembly AI:"" Used for handling voiced user input

## Getting Started

Follow these steps to set up and run the AI Business Assistant on your local machine.

### Prerequisites

Before you begin, ensure you have the following installed:

* **Python 3.12+**
* **Git**
* **Docker** (Highly recommended for easily running Qdrant, PostgreSQL, and MongoDB locally)
* **Miniconda** (Project environment)
* Basic understanding of API interaction and environment variables.

### Installation

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/YourUsername/YourProjectName.git](https://github.com/RaymondAkachi/NTIEM_Bot_Backup.git)
    cd YourProjectName
    ```
2.  **Set up Miniconda Virtual Environment and install project dependencies**
    ```bash
    conda env create -f environment.yml -y
    ```

4.  **Set up Database Containers (using Docker):**
    Create a `docker-compose.yml` file or run individual Docker commands to spin up Qdrant, PostgreSQL, and MongoDB instances.

### Configuration

1.  Create a `.env` file in the root directory of the project based on a `.env.example` (you should provide this example file).

### Running the Application

1.  **Ensure databases are running** (e.g., `docker-compose up -d`).
2.  **Start the Backend Server:**
    ```bash
    uvicorn main:app --host 0.0.0.0 --port 8000 --reload
    ```

## Usage

* **AI Assistant/Bot Interface:** Access the assistant via `http://localhost:8000/docs` (for FastAPI Swagger UI)
* **Appointment Booking:** Customers can interact with the bot through the designated channel to schedule appointments.
* **Admin Dashboard:** Administrators can log into the web-based dashboard to manage appointments, oversee events, and view organizational insights.

## Architecture

*The AI assistant has access to Organisational Data which allows it to provide responses to questions through RAG, stores user data in PostreSQL
Uses MongoDB ATlas to manage user chat history to improvr user intent detection, utilizes Amazon s3 for image creation and voiced replies
Uses Assembly AI for voiced user input transcription.... and others*


## License

This project is licensed under the [MIT License]

---
