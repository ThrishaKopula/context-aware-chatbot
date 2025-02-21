# Supportly

This is a context-aware mental health chatbot application that uses a backend powered by OpenAI and a frontend that communicates with the backend to provide an interactive chatbot experience.

Dataset used: https://www.kaggle.com/datasets/elvis23/mental-health-conversational-data?resource=download

## Prerequisites

Ensure you have the following installed on your local machine:

- **Docker Desktop** (with Docker Compose support)
- **Node.js** (for the frontend development, if you plan to modify or inspect the frontend)

---

## Setup Instructions

Have Docker Desktop open

### 1. Clone the Repository

Start by cloning the repository to your local machine:

```sh
git clone https://github.com/ThrishaKopula/context-aware-chatbot.git
cd context-aware-chatbot
```

### 2. Build and run the application

```sh
docker compose up --build
```

### 3. Access the application

```sh
http://localhost:3000
```


### 4. Stop running the application

```sh
docker compose down
```


