import time
from typing import Any, Dict, List, Optional, Tuple
import httpx
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.errors import AppException
from app.core.logging import logger
from app.models.llm import LLMProviderConfig

PROVIDER_ENDPOINTS = {
    "nvidia_nim": "https://integrate.api.nvidia.com/v1/chat/completions",
    "groq": "https://api.groq.com/openai/v1/chat/completions",
    "ollama": "http://localhost:11434/v1/chat/completions",
    "openrouter": "https://openrouter.ai/api/v1/chat/completions",
    "gemini": "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions",
}


def mask_api_key(key: Optional[str]) -> Optional[str]:
    if not key:
        return None
    cleaned = key.strip()
    if len(cleaned) <= 8:
        return "***"
    return f"{cleaned[:3]}***{cleaned[-4:]}"


class LLMGateway:
    def _resolve_url(self, provider: str, custom_base_url: Optional[str] = None) -> str:
        if custom_base_url and custom_base_url.strip():
            url = custom_base_url.strip().rstrip("/")
            if not url.endswith("/chat/completions"):
                url = f"{url}/chat/completions"
            return url
        if provider == "ollama" and settings.OLLAMA_BASE_URL:
            base = settings.OLLAMA_BASE_URL.strip().rstrip("/")
            if not base.endswith("/chat/completions"):
                base = f"{base}/v1/chat/completions" if not base.endswith("/v1") else f"{base}/chat/completions"
            return base
        return PROVIDER_ENDPOINTS.get(provider, PROVIDER_ENDPOINTS["openrouter"])

    def _resolve_headers(self, provider: str, api_key: Optional[str]) -> Dict[str, str]:
        headers = {"Content-Type": "application/json"}
        key = api_key.strip() if api_key else ""
        if provider == "openrouter":
            headers["Authorization"] = f"Bearer {key}"
            headers["HTTP-Referer"] = "http://localhost:8000"
            headers["X-Title"] = "AI Placement Coach"
        elif provider == "ollama":
            headers["Authorization"] = f"Bearer {key or 'ollama'}"
        else:
            headers["Authorization"] = f"Bearer {key}"
        return headers

    def call_provider(
        self,
        provider: str,
        model: str,
        api_key: Optional[str],
        base_url: Optional[str],
        messages: List[Dict[str, str]],
        json_mode: bool = False,
        timeout: float = 45.0,
    ) -> str:
        endpoint = self._resolve_url(provider, base_url)
        headers = self._resolve_headers(provider, api_key)

        payload: Dict[str, Any] = {
            "model": model,
            "messages": messages,
            "temperature": 0.2,
        }
        if json_mode:
            payload["response_format"] = {"type": "json_object"}

        with httpx.Client(timeout=timeout) as client:
            resp = client.post(endpoint, headers=headers, json=payload)
            if resp.status_code != 200:
                raise RuntimeError(
                    f"[{provider}] API error {resp.status_code}: {resp.text[:200]}"
                )
            data = resp.json()
            choices = data.get("choices", [])
            if not choices:
                raise RuntimeError(f"[{provider}] Returned empty choices array")
            return choices[0]["message"]["content"]

    def test_connection(
        self,
        provider: str,
        model: str,
        api_key: Optional[str],
        base_url: Optional[str],
    ) -> Tuple[bool, float, Optional[str], Optional[str]]:
        start = time.perf_counter()
        messages = [
            {"role": "system", "content": "You are a test ping responder."},
            {"role": "user", "content": "Respond with 'pong'."},
        ]
        try:
            content = self.call_provider(
                provider=provider,
                model=model,
                api_key=api_key,
                base_url=base_url,
                messages=messages,
                json_mode=False,
                timeout=15.0,
            )
            duration_ms = (time.perf_counter() - start) * 1000
            return True, duration_ms, content.strip(), None
        except Exception as exc:
            duration_ms = (time.perf_counter() - start) * 1000
            return False, duration_ms, None, str(exc)

    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        json_mode: bool = False,
        user_id: Optional[str] = None,
        db: Optional[Session] = None,
    ) -> str:
        config: Optional[LLMProviderConfig] = None
        if user_id and db:
            config = db.query(LLMProviderConfig).filter(LLMProviderConfig.user_id == user_id).first()

        messages: List[Dict[str, str]] = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        # Resolve primary
        primary_provider = config.primary_provider if config else "openrouter"
        primary_model = config.primary_model if config else "meta-llama/llama-3.3-70b-instruct"
        primary_key = (config.primary_api_key if config and config.primary_api_key else settings.OPENAI_KEY) or ""
        primary_url = config.primary_base_url if config else None

        # Resolve backup
        backup_provider = config.backup_provider if config else None
        backup_model = config.backup_model if config else None
        backup_key = config.backup_api_key if config else None
        backup_url = config.backup_base_url if config else None

        # 1. Try Primary
        try:
            logger.info(f"Attempting LLM generation via Primary Provider [{primary_provider}] model [{primary_model}]")
            return self.call_provider(
                provider=primary_provider,
                model=primary_model,
                api_key=primary_key,
                base_url=primary_url,
                messages=messages,
                json_mode=json_mode,
            )
        except Exception as primary_err:
            logger.warning(
                f"Primary LLM provider [{primary_provider}] failed: {primary_err}. Checking backup provider..."
            )

        # 2. Try Backup if configured
        if backup_provider and backup_model:
            try:
                logger.info(
                    f"Failing over to Backup Provider [{backup_provider}] model [{backup_model}]"
                )
                return self.call_provider(
                    provider=backup_provider,
                    model=backup_model,
                    api_key=backup_key,
                    base_url=backup_url,
                    messages=messages,
                    json_mode=json_mode,
                )
            except Exception as backup_err:
                logger.error(f"Backup LLM provider [{backup_provider}] also failed: {backup_err}")
                raise AppException(
                    message=f"Both primary ({primary_provider}) and backup ({backup_provider}) LLM providers failed.",
                    code="LLM_FAILOVER_EXHAUSTED",
                    details={
                        "primary_error": str(primary_err),
                        "backup_error": str(backup_err),
                    },
                )

        raise AppException(
            message=f"Primary LLM provider [{primary_provider}] failed and no backup provider was configured.",
            code="LLM_GENERATION_FAILED",
            details={"error": str(primary_err)},
        )


llm_gateway = LLMGateway()
