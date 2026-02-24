from __future__ import annotations

import json
import logging
from typing import Optional

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_groq import ChatGroq

from .config import GROQ_API_KEY, GROQ_MODEL


logger = logging.getLogger(__name__)


class LLMClient:
    """
    Thin wrapper around Groq via LangChain (`langchain_groq.ChatGroq`).

    Usage:
        llm = LLMClient()
        result = llm.complete(
            system_prompt="You are a PMO assistant...",
            user_content="Find 2 Power BI engineers in Mumbai...",
        )
    """

    def __init__(self, model: Optional[str] = None) -> None:
        if GROQ_API_KEY is None:
            raise RuntimeError(
                "GROQ_API_KEY is not set. "
                "Set it in your environment or .env file before running the app."
            )
        self.model = model or GROQ_MODEL
        # ChatGroq reads GROQ_API_KEY from env; we validate above for clearer errors.

    def complete(
        self,
        system_prompt: str,
        user_content: str,
        temperature: float = 0.2,
        max_tokens: Optional[int] = None,
        response_format: Optional[str] = None,
    ) -> str:
        """
        Basic text completion helper.

        If `response_format == 'json'`, the method will try to coerce the
        response into a JSON string with a single top-level object.
        """
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_content),
        ]

        llm = ChatGroq(
            model=self.model,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        response = llm.invoke(messages)
        content = getattr(response, "content", "") or ""

        if response_format == "json":
            # Try to extract JSON object if the model added extra text.
            try:
                # Find first and last curly brace region and parse it.
                first = content.find("{")
                last = content.rfind("}")
                if first != -1 and last != -1 and last > first:
                    json_str = content[first : last + 1]
                    # Validate JSON
                    json.loads(json_str)
                    return json_str
            except Exception as exc:
                logger.warning("Failed to parse JSON from LLM response: %s", exc)
                # Fall through and return raw content
        return content


_GLOBAL_LLM: Optional[LLMClient] = None


def get_llm() -> LLMClient:
    """
    Singleton-style accessor for a shared LLM client.
    """
    global _GLOBAL_LLM
    if _GLOBAL_LLM is None:
        _GLOBAL_LLM = LLMClient()
    return _GLOBAL_LLM

