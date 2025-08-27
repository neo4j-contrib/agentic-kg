from enum import Enum

import logging

from google.adk.models.lite_llm import LiteLlm
import litellm

from .config import get_settings

logger = logging.getLogger(__name__)

litellm.log_raw_request_response = False
litellm.suppress_debug_info = True
litellm.turn_off_message_logging=True
litellm.logging = False
litellm._logging._disable_debugging()

MODEL_GEMINI_2_0_FLASH = "gemini/gemini-2.0-flash"
MODEL_GPT_4O = "openai/gpt-4o"
MODEL_CLAUDE_SONNET = "anthropic/claude-3-sonnet-20240229"
MODEL_OPENAI_CHAT = "openai/gpt-4o"
MODEL_GPT_4O_MINI = "openai/gpt-4o-mini"
MODEL_GPT_5_MINI = "openai/gpt-5-mini"

LM_STUDIO_QWEN = "hosted_vllm/qwen2.5-7b-instruct"
LM_STUDIO_GPT_OSS = "hosted_vllm/openai/gpt-oss-20b"
LM_STUDIO_BASE_URL = "http://localhost:1234/v1"

OLLAMA_MODEL = "openai/qwen3:4b"
OLLAMA_BASE_URL = "http://localhost:11434/v1"


class LlmKind(str, Enum):
    reasoning = 'reasoning'
    conversational = 'conversational'


_llm_instance: LiteLlm | None = None


def get_llm(kind: LlmKind = LlmKind.reasoning) -> LiteLlm:
    """Lazily construct and return a kind of LiteLlm instance.

    Args:
        kind: The kind of LiteLlm to construct.
    """
    global _llm_instance
    if _llm_instance is None:
        settings = get_settings()
        logger.info(f"llm_model: {settings.llm_model}")
        _llm_instance = LiteLlm(
            model=MODEL_GPT_4O_MINI,
            # api_base=OLLAMA_BASE_URL,
        )
        # _llm_instance = LiteLlm(
        #     model=LM_STUDIO_GPT_OSS,
        #     api_base=LM_STUDIO_BASE_URL,
        # )
    return _llm_instance
