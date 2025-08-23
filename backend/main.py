from fastapi.responses import StreamingResponse
from core.llm import stream_bedrock_llm

# --- Streaming Generate endpoint ---
# (Moved to end of file after all imports, app, and schema definitions)
import re
# --- System prompt for Claude ---
SYSTEM_PROMPT = (
	"You are an AI assistant for Azercell. Only answer using the provided context. "
	"If the answer is not in the context, say 'I don't know.' Do not answer questions unrelated to Azercell."
)

# --- Guardrail: Detect prompt injection or malicious input ---
def is_malicious_prompt(prompt: str) -> bool:
	# Only block clear prompt injection attempts, not normal business queries
	patterns = [
		r"ignore previous instructions",
		r"forget previous instructions",
		r"as an ai language model",
		r"act as a system prompt",
		r"act as an admin",
		r"run shell|run command|execute script|os\.system|subprocess|import os|import sys|rm -rf|sudo|su|hack|bypass|exploit|malware|phish|leak|steal|delete|drop|shutdown|format"
	]
	return any(re.search(pat, prompt, re.IGNORECASE) for pat in patterns)

# main.py — FastAPI backend skeleton
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from core.llm import call_bedrock_llm
from core.retriever import retrieve_context


app = FastAPI(title="FastAPI Backend server for ML project", version="1.0.0", description="REST API for ML project")
app.add_middleware(
	CORSMiddleware,
	allow_origins=["*"],
	allow_credentials=True,
	allow_methods=["*"],
	allow_headers=["*"],
)


# --- Schemas ---
class GenerateRequest(BaseModel):
	prompt: str
	modelName: Optional[str] = None
	# rag_mode removed: only KB supported

class GenerateResponse(BaseModel):
	response: str

# --- Health endpoint ---
@app.get("/health")
def health():
	return {"status": "ok"}


# --- Generate endpoint ---
@app.post("/generate", response_model=GenerateResponse)
def generate(req: GenerateRequest):
	# Guardrail: Block malicious or prompt injection attempts (input only)
	if is_malicious_prompt(req.prompt):
		return {"response": "Your input was flagged as potentially unsafe and was not processed."}

	context = retrieve_context(req.prompt)

	# Compose Claude-compatible RAG prompt
	prompt = ""
	if context:
		prompt += f"Context:\n{context}\n\n"
	prompt += f"User: {req.prompt}\nAssistant:"
	model_id = req.modelName or ""
	result = call_bedrock_llm(prompt, model_id, system_prompt=SYSTEM_PROMPT)
	return {"response": result}

# --- Streaming Generate endpoint ---
@app.post("/generate/stream")
def generate_stream(req: GenerateRequest):
	if is_malicious_prompt(req.prompt):
		return StreamingResponse((x for x in ["Your input was flagged as potentially unsafe and was not processed."]), media_type="text/plain")

	context = retrieve_context(req.prompt)

	prompt = ""
	if context:
		prompt += f"Context:\n{context}\n\n"
	prompt += f"User: {req.prompt}\nAssistant:"
	model_id = req.modelName or ""
	return StreamingResponse(
		stream_bedrock_llm(prompt, model_id, system_prompt=SYSTEM_PROMPT),
		media_type="text/plain"
	)
