from fastapi import FastAPI, HTTPException
import os
from llm_providers import get_llm_provider
from models.GenAIRequest import GenAIRequest
from models.GenAIResponse import GenAIResponse
import logging

app = FastAPI()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)



@app.post("/generate", response_model=GenAIResponse)
def generate_text(request: GenAIRequest):
    provider_name = request.provider or os.getenv("GENAI_DEFAULT_PROVIDER", "openai")
    llm = get_llm_provider(provider_name)
    if not llm:
        raise HTTPException(status_code=400, detail=f"Provider {provider_name} not supported.")
    try:
        response = llm.generate(
            prompt=request.prompt,
            system_prompt=request.system_prompt,
            model=request.model
        )
        return GenAIResponse(response=response)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
def health_check():
    logger.info("Health check requested")
    return {"status": "healthy", "service": "balance-api"}


