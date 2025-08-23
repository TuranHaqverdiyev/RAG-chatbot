# llm.py — Bedrock LLM interface

from typing import Optional
from tools import get_bedrock_client
from ..config import BEDROCK_MODEL_ID
import json


def stream_bedrock_llm(
    prompt: str, model_id: str = "", system_prompt: Optional[str] = None
):
    """
    Stream Claude 3 response from Bedrock using invoke_model_with_response_stream.
    Yields text chunks as they arrive.
    """
    client = get_bedrock_client()
    model = model_id if model_id else BEDROCK_MODEL_ID
    model = model or ""
    if "claude-3" in model.lower():
        body_dict = {
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 64128,
            "anthropic_version": "bedrock-2023-05-31",
        }
        if system_prompt:
            body_dict["system"] = system_prompt
        body = json.dumps(body_dict)
        stream = client.invoke_model_with_response_stream(
            modelId=model,
            body=body,
            accept="application/json",
            contentType="application/json",
        )
        stream_body = stream.get("body")
        for event in stream_body:
            stream_chunk = event.get("chunk")
            if not stream_chunk:
                continue
            decoded = json.loads(stream_chunk.get("bytes").decode("utf-8"))
            delta = decoded.get("delta", {})
            text = delta.get("text", "")
            if text:
                yield text
    else:
        # fallback to non-streaming call if not Claude 3
        yield call_bedrock_llm(prompt, model_id, system_prompt)


def call_bedrock_llm(
    prompt: str, model_id: str = "", system_prompt: Optional[str] = None
) -> str:
    """
    Call Bedrock LLM with the given prompt and return the response as a string.
    """
    client = get_bedrock_client()
    model = model_id if model_id else BEDROCK_MODEL_ID
    model = model or ""
    # Claude 3 models require the Messages API format
    if "claude-3" in model.lower():
        body_dict = {
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 512,
            "anthropic_version": "bedrock-2023-05-31",
        }
        if system_prompt:
            body_dict["system"] = system_prompt
        body = json.dumps(body_dict)
    else:
        body = json.dumps({"prompt": prompt, "max_tokens_to_sample": 512})
    response = client.invoke_model(
        modelId=model,
        body=body,
        accept="application/json",
        contentType="application/json",
    )
    result = response["body"].read().decode()
    try:
        result_json = json.loads(result)
        # Claude 3 returns {"content": ...} in the Messages API
        if "claude-3" in model.lower():
            # Claude 3 returns {"content": ...} or {"content": [{"type": "text", "text": ...}]}
            content = result_json.get("content")
            if (
                isinstance(content, list)
                and content
                and isinstance(content[0], dict)
                and "text" in content[0]
            ):
                return content[0]["text"]
            elif isinstance(content, str):
                return content
            return str(result_json)
        return (
            result_json.get("completion")
            or result_json.get("output")
            or str(result_json)
        )
    except Exception:
        return result
