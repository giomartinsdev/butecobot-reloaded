from typing import Optional
import os
import openai
import google.generativeai as genai

class LLMProvider:
    def generate(self, prompt: str, system_prompt: Optional[str] = None, model: Optional[str] = None) -> str:
        """
        Generate a response from the LLM provider.
        :param prompt: The user prompt/question.
        :param system_prompt: Optional system/business prompt for fine-tuning.
        :param model: Optional model name.
        :return: The generated response as a string.
        """
        raise NotImplementedError("Subclasses must implement this method.")

class OpenAIProvider(LLMProvider):
    def __init__(self):
        openai.api_key = os.getenv("OPENAI_API_KEY")
    def generate(self, prompt: str, system_prompt: Optional[str] = None, model: Optional[str] = None) -> str:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        try:
            response = openai.ChatCompletion.create(
                model=model or "gpt-3.5-turbo",
                messages=messages
            )
            return response.choices[0].message.content
        except Exception as e:
            raise RuntimeError(f"OpenAIProvider error: {e}")

class GeminiProvider(LLMProvider):
    def __init__(self):
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    def generate(self, prompt: str, system_prompt: Optional[str] = None, model: Optional[str] = None) -> str:
        full_prompt = f"{system_prompt}\n{prompt}" if system_prompt else prompt
        model_name = model or "gemini-1.5-flash"
        try:
            gemini_model = genai.GenerativeModel(model_name)
            response = gemini_model.generate_content(full_prompt)
            return response.text if hasattr(response, 'text') else str(response)
        except Exception as e:
            raise RuntimeError(f"GeminiProvider error: {e}")

def get_llm_provider(name: str) -> Optional[LLMProvider]:
    name = name.lower()
    if name == "openai":
        return OpenAIProvider()
    elif name == "gemini":
        return GeminiProvider()
    return None
