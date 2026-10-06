"""What a notebook needs to know about where it is and which model to call.

Tier 1: stdlib + python-dotenv only. Nothing here may import litellm, numpy, or
anything else heavy — every notebook imports this, including the ones running in a
minimal sandbox.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class Config:
    """Paths and model settings, resolved once per notebook."""

    root: Path          # repo root — the directory holding pyproject.toml
    data: Path          # our instructional corpus
    use_case: Path      # the student's own work; the through-line

    llm_model: str
    api_base: str | None
    api_key: str | None
    embed_model: str
    embed_api_base: str | None
    embed_api_key: str | None
    vlm_model: str | None
    vlm_api_base: str | None
    vlm_api_key: str | None
    # Adversarial work -- prompt injection, attack search, red-teaming your own
    # app. Separate from `llm_model` on purpose, and with no fallback to it: see
    # `injection_kwargs()`.
    injection_model: str | None = None
    injection_api_base: str | None = None
    injection_api_key: str | None = None
    headers: dict[str, str] = field(default_factory=dict)  # LLM_EXTRA_HEADERS
    # Headers only follow calls to the same host; embed/vlm on their own base
    # URL don't get them.
    embed_shares_host: bool = True
    vlm_shares_host: bool = True

    def kwargs(self) -> dict:
        """LiteLLM kwargs for this config. Spread into completion(**cfg.kwargs())."""
        out = {"model": self.llm_model}
        if self.api_base:
            out["api_base"] = self.api_base
        if self.headers:
            out["extra_headers"] = dict(self.headers)
        return out

    @property
    def has_injection_endpoint(self) -> bool:
        """Is an endpoint explicitly configured for adversarial work?

        The rule is mechanical: an *endpoint you point at*, not a provider reached
        by model name alone. `http://localhost:11434` passes; so does your firm's
        gateway. A bare `LLM_MODEL=gpt-4.1-mini` does not, and that is the point.
        """
        return bool(self.injection_model and self.injection_api_base)

    def injection_kwargs(self) -> dict:
        """LiteLLM kwargs for anything that sends attack-shaped prompts.

        Why this is not `kwargs()` with a different name: the hosted providers'
        usage policies prohibit "circumventing safeguards", "unsolicited safety
        testing" and -- in Anthropic's, verbatim -- "prompt injection", with no
        carve-out for testing your own application. Their enforcement is
        automated pattern-matching that cannot see that the system prompt being
        attacked is yours; Azure's Prompt Shields flag exactly this content by
        default and feed abuse monitoring that can suspend the *subscription*.
        A student who runs the injection notebook through their employer's
        tenant on course instructions is the outcome this guard exists to
        prevent. So: no fallback to `llm_model`, ever. Set INJECTION_MODEL and
        INJECTION_API_BASE in .env -- a local server or a gateway your firm has
        approved for this -- and the notebook runs; leave them unset and it
        halts at Setup with this message rather than at the first attack.
        """
        if not self.has_injection_endpoint:
            raise RuntimeError(
                "No endpoint is configured for adversarial work. Set both\n"
                "    INJECTION_MODEL=ollama_chat/qwen2.5:7b\n"
                "    INJECTION_API_BASE=http://localhost:11434\n"
                "in .env (a local server, or a gateway your firm has approved for "
                "prompt-injection testing). This deliberately does not fall back to "
                "LLM_MODEL: attack-shaped prompts must never reach a public API by "
                "model name alone. See .env.template."
            )
        out = {"model": self.injection_model, "api_base": self.injection_api_base}
        if self.injection_api_key:
            out["api_key"] = self.injection_api_key
        return out

    def embed_kwargs(self) -> dict:
        """LiteLLM kwargs for embeddings.

        Separate from `kwargs()` because the embedding endpoint is often a
        different host from the chat one — a firm may serve embeddings locally
        while chat goes through a gateway, or the reverse.
        """
        out = {"model": self.embed_model}
        if self.embed_api_base:
            out["api_base"] = self.embed_api_base
        # Separate credential, because a separate host usually means a separate
        # credential. Falls back to the ambient OPENAI_API_KEY when unset.
        if self.embed_api_key:
            out["api_key"] = self.embed_api_key
        if self.headers and self.embed_shares_host:
            out["extra_headers"] = dict(self.headers)
        return out

    @property
    def has_vlm(self) -> bool:
        """Is a vision model configured? Notebooks branch on this rather than
        assuming — a text model will happily accept an image payload and then
        answer about nothing."""
        return bool(self.vlm_model)

    def vlm_kwargs(self) -> dict:
        """LiteLLM kwargs for a vision-capable chat model.

        Deliberately not defaulted to `llm_model`. Most chat models cannot see,
        and a silent fallback would produce confident answers about an image the
        model never received — which is far worse than an error.
        """
        if not self.vlm_model:
            raise RuntimeError(
                "No vision model is configured. Set VLM_MODEL in .env (and "
                "VLM_API_BASE if it lives somewhere other than LLM_API_BASE). "
                "See .env.template."
            )
        out = {"model": self.vlm_model}
        if self.vlm_api_base:
            out["api_base"] = self.vlm_api_base
        if self.vlm_api_key:
            out["api_key"] = self.vlm_api_key
        if self.headers and self.vlm_shares_host:
            out["extra_headers"] = dict(self.headers)
        return out

    def __str__(self) -> str:
        where = f" @ {self.api_base}" if self.api_base else ""
        return f"{self.llm_model}{where}"


def from_env(root: Path) -> Config:
    return Config(
        root=root,
        data=root / "data",
        use_case=root / "use_case",
        llm_model=os.getenv("LLM_MODEL", "gpt-4.1-mini"),
        api_base=os.getenv("LLM_API_BASE"),
        # Exposed so a notebook can hand credentials to a library that builds
        # its own client rather than going through LiteLLM.
        api_key=os.getenv("OPENAI_API_KEY"),
        embed_model=os.getenv("EMBED_MODEL", "text-embedding-3-small"),
        # Falls back to the chat endpoint, which is right for hosted providers
        # and for most single-gateway setups.
        embed_api_base=os.getenv("EMBED_API_BASE") or os.getenv("LLM_API_BASE"),
        embed_api_key=os.getenv("EMBED_API_KEY"),
        # No default. A model that cannot see must not be guessed at.
        vlm_model=os.getenv("VLM_MODEL"),
        vlm_api_base=os.getenv("VLM_API_BASE") or os.getenv("LLM_API_BASE"),
        vlm_api_key=os.getenv("VLM_API_KEY"),
        # No fallback to LLM_MODEL / LLM_API_BASE. See `injection_kwargs()`.
        injection_model=os.getenv("INJECTION_MODEL"),
        injection_api_base=os.getenv("INJECTION_API_BASE"),
        injection_api_key=os.getenv("INJECTION_API_KEY"),
        headers=json.loads(os.getenv("LLM_EXTRA_HEADERS") or "{}"),
        embed_shares_host=not os.getenv("EMBED_API_BASE"),
        vlm_shares_host=not os.getenv("VLM_API_BASE"),
    )
