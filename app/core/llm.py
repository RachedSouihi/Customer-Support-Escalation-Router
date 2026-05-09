from __future__ import annotations

import logging
import httpx
from typing import Any

from groq import Groq

from app.core.config import settings

logger = logging.getLogger(__name__)


def generate_support_reply(prompt: str) -> str:
    logger.info("Generating support reply with prompt: %s", prompt)
    # Ensure at least one provider key is present
    if settings.llm_provider.lower() == "groq" and not settings.groq_api_key:
        logger.warning("GROQ provider selected but GROQ_API_KEY is empty")
        return ""
    if settings.llm_provider.lower() != "groq" and not settings.llm_api_key:
        logger.warning("OpenRouter provider selected but LLM API key is empty")
        return ""

    try:
        if settings.llm_provider.lower() == "groq":
            # Use Groq SDK
            logger.info("Using GROQ SDK for model: %s", settings.llm_model)
            client = Groq(api_key=settings.groq_api_key) if settings.groq_api_key else Groq()

            # Create completion (non-streaming by default)
            logger.debug("Calling Groq chat.completions.create (stream=False)")
            completion = client.chat.completions.create(
                model=settings.llm_model,
                messages=[
                    {"role": "system", "content": "You are a concise customer support assistant."},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.2,
                max_completion_tokens=2048,
                top_p=1,
                stream=True,
            )

            # Groq SDK may return an iterator when stream=True or a completed object when stream=False
            logger.debug("Groq response type: %s", type(completion))
            # If iterable (streaming), accumulate
            #if hasattr(completion, "__iter__") and not isinstance(completion, (str, bytes, dict)):
            logger.info("Streaming GROQ response")
            parts = []
            for chunk in completion:
                    try:
                        text = chunk.choices[0].delta.content or ""
                    except Exception:
                        # Fallback shapes
                        text = getattr(chunk, "text", None) or getattr(chunk, "content", "")
                    logger.debug("GROQ chunk received: %s", text)
                    parts.append(text)
            response =  "".join(parts)
            logger.info("Completed streaming GROQ response")
            logger.debug("Full GROQ response: %s", response)
            return response

            # Non-streaming response handling
            # Try common fields
        if isinstance(completion, dict):
                if "output" in completion:
                    out = completion["output"]
                    if isinstance(out, list):
                        return "".join(map(str, out)) or ""
                    return str(out) or ""
                if "choices" in completion and completion["choices"]:
                    first = completion["choices"][0]
                    if isinstance(first, dict):
                        for k in ("text", "message", "content"):
                            if k in first:
                                val = first.get(k)
                                if isinstance(val, dict) and "content" in val:
                                    return val["content"] or ""
                                return val or ""
            # If SDK returns an object with attributes
        try:
                # some SDKs provide .choices[0].message.content
                return completion.choices[0].message.content or ""
        except Exception:
                logger.debug("Unable to parse GROQ completion object, returning stringified response")
                return str(completion)

        # Fallback: OpenRouter / OpenAI-compatible client
        '''
        from openai import OpenAI

        client = OpenAI(
            base_url=settings.llm_base_url,
            api_key=settings.llm_api_key,
        )

        extra_headers = {}
        if settings.llm_site_url:
            extra_headers["HTTP-Referer"] = settings.llm_site_url
        if settings.llm_title:
            extra_headers["X-OpenRouter-Title"] = settings.llm_title

        logger.info("Sending request to LLM via OpenRouter model %s", settings.llm_model)
        completion = client.chat.completions.create(
            model=settings.llm_model,
            messages=[
                {"role": "system", "content": "You are a concise customer support assistant."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.2,
            extra_headers=extra_headers or None,
        )
        return completion.choices[0].message.content or ""
        '''
    except Exception:
        logger.exception("LLM request failed")
        raise

