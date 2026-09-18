"""
Shared LLM Factory supporting Gemini, Groq, OpenAI, Ollama, and Mock/Offline execution.
Allows anyone to run the code seamlessly either with free API keys or offline in deterministic simulation mode.
"""

import os
import json
from typing import Optional, Any, Dict, List
from dotenv import load_dotenv

load_dotenv()

class MockChatModel:
    """
    A lightweight, prompt-aware mock chat model for deterministic offline testing and demonstration.
    Returns structured AIMessage-like objects with tool_calls or text content.
    """
    def __init__(self, mode: str = "clean"):
        self.mode = mode
        self.call_count = 0

    def invoke(self, messages: List[Any], **kwargs) -> Any:
        self.call_count += 1
        # Extract prompt content
        last_msg = messages[-1]
        content = getattr(last_msg, "content", str(last_msg))
        
        # Return mock message wrapper
        from langchain_core.messages import AIMessage
        return AIMessage(content=f"Mock response to: {content[:100]}...")

def get_llm(provider: Optional[str] = None, model_name: Optional[str] = None, temperature: float = 0.2, **kwargs):
    """
    Factory to return a ChatModel based on available API keys or user preference.
    Priority:
    1. Explicit provider requested
    2. GEMINI_API_KEY / GOOGLE_API_KEY (Recommended default in assignment)
    3. GROQ_API_KEY
    4. OPENAI_API_KEY
    5. Fallback to mock / offline model if no keys found
    """
    google_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    groq_key = os.getenv("GROQ_API_KEY")
    openai_key = os.getenv("OPENAI_API_KEY")

    if provider == "mock" or kwargs.get("mock", False):
        return MockChatModel()

    # 1. Google Gemini (Recommended Default)
    if (provider == "gemini" or (provider is None and google_key)) and google_key:
        from langchain_google_genai import ChatGoogleGenerativeAI
        target_model = model_name or os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
        return ChatGoogleGenerativeAI(
            model=target_model,
            google_api_key=google_key,
            temperature=temperature,
            **kwargs
        )

    # 2. Groq (Free tier, fast)
    if (provider == "groq" or (provider is None and groq_key)) and groq_key:
        from langchain_groq import ChatGroq
        target_model = model_name or os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
        return ChatGroq(
            model=target_model,
            api_key=groq_key,
            temperature=temperature,
            **kwargs
        )

    # 3. OpenAI
    if (provider == "openai" or (provider is None and openai_key)) and openai_key:
        from langchain_openai import ChatOpenAI
        target_model = model_name or os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        return ChatOpenAI(
            model=target_model,
            api_key=openai_key,
            temperature=temperature,
            **kwargs
        )

    # Fallback to None if no key configured
    return None
