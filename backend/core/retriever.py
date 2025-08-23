## Standard RAG: Bedrock Knowledge Base Retrieval (Matches instructor's notebook)
import boto3
from config import AWS_ACCESS_KEY_ID, AWS_REGION, AWS_SECRET_ACCESS_KEY, BEDROCK_KB_ID


def retrieve_context(query: str, top_k: int = 3) -> str:
    """
    Retrieve relevant passages from Bedrock Knowledge Base for a given query.
    Returns concatenated text of the top retrieved documents/passages.

    This is the standard/instructor approach (no local vector DB, no Titan embeddings).
    """
    try:
        client = boto3.client(
            "bedrock-agent-runtime",
            region_name=AWS_REGION,
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        )
        req = {
            "knowledgeBaseId": BEDROCK_KB_ID,
            "retrievalQuery": {"text": query},
            "retrievalConfiguration": {
                "vectorSearchConfiguration": {"numberOfResults": top_k}
            },
        }
        response = client.retrieve(**req)
        candidates = response.get("retrievalResults", [])
        vec_response = "\n\n".join(
            [
                f"Document {ind+1}: " + i.get("content", {}).get("text", "")
                for ind, i in enumerate(candidates)
            ]
        )
        return vec_response
    except Exception:
        return ""
