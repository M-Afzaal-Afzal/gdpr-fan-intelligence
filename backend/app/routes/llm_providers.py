"""GET /api/llm-providers — list LLM backends the server can call."""

from __future__ import annotations

from fastapi import APIRouter

from app.config import settings
from app.schemas import LlmProvider, LlmProviderOption, LlmProvidersResponse
from app.services import llm_service

router = APIRouter()


@router.get("/llm-providers", response_model=LlmProvidersResponse)
def get_llm_providers() -> LlmProvidersResponse:
    default = settings.LLM_PROVIDER.lower()
    try:
        default_provider = LlmProvider(default)
    except ValueError:
        default_provider = LlmProvider.stub

    providers = [
        LlmProviderOption(
            id=LlmProvider(item["id"]),
            label=str(item["label"]),
            model=str(item["model"]),
            configured=bool(item["configured"]),
        )
        for item in llm_service.list_llm_providers()
    ]
    return LlmProvidersResponse(default=default_provider, providers=providers)
