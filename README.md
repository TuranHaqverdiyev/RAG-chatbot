# RAG Chatbot (FastAPI + Streamlit)

This project is a Retrieval-Augmented Generation (RAG) AI chatbot using Amazon Bedrock LLM and Knowledge Base. It features a FastAPI backend and a Streamlit frontend, both containerized and orchestrated with Docker Compose. The system is ready for deployment on AWS EC2.

## Features
- **Backend (FastAPI):**
	- Communicates with Amazon Bedrock LLM API
	- Retrieves context from Bedrock Knowledge Base
	- Streams responses to the frontend
	- Input guardrails for prompt injection/malicious input
- **Frontend (Streamlit):**
	- Modern chat UI with live streaming
	- "Thinking..." spinner for user feedback
- **Containerized:**
	- Separate Dockerfiles for backend and frontend
	- Managed with `docker-compose.yml`
- **Deployment-ready:**
	- Designed for AWS EC2 deployment

## Project Structure

```
├── backend/
│   ├── main.py           # FastAPI app
│   ├── core/            # LLM and retriever logic
│   ├── schemas/         # Pydantic schemas
│   ├── config.py        # Loads AWS/Bedrock config from .env
│   ├── requirements.txt # Backend dependencies
│   └── Dockerfile       # Backend Dockerfile
├── frontend/
│   ├── app.py           # Streamlit app
│   ├── requirements.txt # Frontend dependencies
│   └── Dockerfile       # Frontend Dockerfile
├── assets/
│   ├── backend/         # Backend screenshots
│   └── frontend/        # Frontend screenshots
├── docker-compose.yml   # Orchestration for both services
├── .env                 # AWS credentials/config (DO NOT COMMIT)
└── README.md            # Project documentation
```

## Setup Instructions

### 1. Clone the Repository
```
git clone <your-repo-url>
cd <your-repo>
```

### 2. Configure AWS Credentials
Create a `.env` file in the project root (never commit this file):
```
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_REGION=us-east-1
BEDROCK_KB_ID=your-bedrock-kb-id
BEDROCK_MODEL_ID=your-bedrock-model-id
```

### 3. Build and Run Locally (Docker Compose)
```
docker compose up --build
```
- Backend: http://localhost:8000
- Frontend: http://localhost:8501

### 4. Deploy on AWS EC2
1. Launch an EC2 instance (Ubuntu recommended).
2. Install Docker and Docker Compose.
3. Clone your repo and add your `.env` file.
4. Run `docker compose up --build`.
5. Open the EC2 public IP at port 8501 in your browser.

## Example Usage

**Query:**
> What are Azercell's core values?

**Response:**
> (The bot will answer using only the context from the Bedrock Knowledge Base.)

## Screenshots
- Place screenshots of backend and frontend running in `assets/backend/` and `assets/frontend/`.

## CI/CD (Optional)
- Add a GitHub Actions workflow to build, lint, and deploy to EC2 (see homework instructions).

## Troubleshooting
- Ensure your `.env` is correct and not committed to GitHub.
- AWS credentials must have Bedrock and Knowledge Base access.
- If you see 500 errors, check backend logs for AWS permission/config issues.

## License
MIT (or as required by your course)
