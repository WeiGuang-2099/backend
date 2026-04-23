"""
LLM service using LangChain + OpenAI with streaming support
"""
import os
from typing import AsyncGenerator, List, Dict
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage


class LLMService:
    def __init__(self):
        self._api_key = os.getenv("OPENAI_API_KEY")
        self._model_name = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")

    def _get_chat_model(self, temperature: float = 0.7, max_tokens: int = 2048) -> ChatOpenAI:
        return ChatOpenAI(
            api_key=self._api_key,
            model=self._model_name,
            temperature=temperature,
            max_tokens=max_tokens,
            streaming=True,
        )

    def build_messages(
        self,
        system_prompt: str,
        history: List[Dict[str, str]],
        user_message: str,
    ) -> List:
        """Build LangChain message list from history and current input."""
        messages = []
        if system_prompt:
            messages.append(SystemMessage(content=system_prompt))
        for msg in history:
            if msg["role"] == "user":
                messages.append(HumanMessage(content=msg["content"]))
            elif msg["role"] == "assistant":
                messages.append(AIMessage(content=msg["content"]))
        messages.append(HumanMessage(content=user_message))
        return messages

    async def stream_chat(
        self,
        system_prompt: str,
        history: List[Dict[str, str]],
        user_message: str,
        temperature: float = 0.7,
        max_tokens: int = 2048,
    ) -> AsyncGenerator[str, None]:
        """Stream chat tokens as an async generator."""
        chat_model = self._get_chat_model(temperature=temperature, max_tokens=max_tokens)
        messages = self.build_messages(system_prompt, history, user_message)

        async for chunk in chat_model.astream(messages):
            token = chunk.content
            if token:
                yield token

    async def chat(
        self,
        system_prompt: str,
        history: List[Dict[str, str]],
        user_message: str,
        temperature: float = 0.7,
        max_tokens: int = 2048,
    ) -> str:
        """Non-streaming chat, returns full response."""
        chat_model = self._get_chat_model(temperature=temperature, max_tokens=max_tokens)
        chat_model.streaming = False
        messages = self.build_messages(system_prompt, history, user_message)
        response = await chat_model.ainvoke(messages)
        return response.content


llm_service = LLMService()
