"""Unified LLM Service with free provider support and override.

Priority (automatic) order:
1. Groq (if GROQ_API_KEY provided) - free tier available
2. Hugging Face local transformers (if installed) - fully free
3. OpenAI (if key provided) - optional paid
4. Mock provider (deterministic, rule-based) - always available fallback

Env override: LLM_PROVIDER can force one of: groq | hf | huggingface | openai | mock

Each provider implements: generate(prompt: str) -> str
"""

from __future__ import annotations

import os
import logging
from typing import Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)


class BaseProvider:
	name: str = "base"

	def is_available(self) -> bool:  # pragma: no cover - trivial
		return False

	def generate(self, prompt: str) -> str:  # pragma: no cover - interface
		raise NotImplementedError

class GroqProvider(BaseProvider):
    name = "groq"

    SYSTEM_PROMPT = """You are an expert AI recruiting assistant specializing in tech hiring. 
You excel at:
- Understanding hiring requirements from client messages
- Extracting specific job roles, locations, and industries  
- Providing professional, actionable recruitment advice
- Generating concise, relevant responses for business contexts
- Maintaining conversation flow and context awareness
- Making logical recommendations based on client needs

CRITICAL INSTRUCTIONS:
- Only respond based on information the client has ACTUALLY provided
- Do not assume or hallucinate details not mentioned
- Ask clarifying questions when information is missing
- Be professional, concise, and helpful
- Progress conversations logically through stages
- Avoid repetitive responses

Focus on being professional, specific, and helpful."""

    def __init__(self, max_history=10):
        self._available = False
        self.history = []  # Stores prior messages for context
        self.max_history = max_history  # Limit to avoid hitting token cap

        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            return
        try:
            from groq import Groq  # type: ignore
            self.client = Groq(api_key=api_key)
            self.model = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
            self._available = True
        except Exception as e:
            logger.warning("Groq provider unavailable: %s", e)

    def is_available(self) -> bool:
        return self._available

    def generate(self, prompt: str) -> str:
        try:
            # Add system prompt if starting fresh
            if not any(msg["role"] == "system" for msg in self.history):
            	self.history.insert(0, {"role": "system", "content": self.SYSTEM_PROMPT})

            # Append user message
            self.history.append({"role": "user", "content": prompt})

            # # Keep only last N exchanges (excluding system message)
            # system_msgs = [m for m in self.history if m["role"] == "system"]
            # other_msgs = [m for m in self.history if m["role"] != "system"]
            # self.history = system_msgs + other_msgs[-self.max_history:]
			
            # Send to Groq
            resp = self.client.chat.completions.create(
                model=self.model,
                messages=self.history,
                temperature=0.3,
                max_tokens=1500,
                top_p=0.9,
                frequency_penalty=0.2,
                presence_penalty=0.3
            )

            # Extract text safely
            reply = resp.choices[0].message.content.strip() if resp.choices else "No response from model."

            # Save assistant reply to history
            self.history.append({"role": "assistant", "content": reply})

            return reply

        except Exception as e:
            logger.error("Groq generation failed: %s", e)
            return "I'm having a temporary issue generating a response. Could you rephrase or try again?"

class HFProvider(BaseProvider):
	name = "huggingface"

	def __init__(self):
		self._available = False
		try:
			from transformers import pipeline  # type: ignore
			import torch  # type: ignore

			model = os.getenv("HF_MODEL", "microsoft/DialoGPT-small")
			device = 0 if torch.cuda.is_available() else -1
			self.pipe = pipeline(
				"text-generation",
				model=model,
				device=device,
				max_new_tokens=220,
				do_sample=True,
				temperature=0.7,
			)
			self._available = True
		except Exception as e:  # pragma: no cover - optional dependency
			logger.info("HF provider not available: %s", e)

	def is_available(self) -> bool:
		return self._available

	def generate(self, prompt: str) -> str:
		try:
			base = f"User: {prompt}\nAssistant:"  # simple conversation framing
			out = self.pipe(base)[0]["generated_text"]
			# take text after last marker
			return out.split("Assistant:")[-1].strip()[:1000]
		except Exception as e:  # pragma: no cover
			logger.error("HF generation failed: %s", e)
			return "(local model error) Please try again."


class MockProvider(BaseProvider):
	name = "mock"

	def is_available(self) -> bool:
		return True

	def generate(self, prompt: str) -> str:
		low = prompt.lower()
		
		# Handle entity extraction prompts (JSON responses)
		if "extract" in low and "json" in low and "urgency" in low:
			if "urgent" in low or "asap" in low:
				return '{"company_name": null, "industry": "technology", "location": null, "roles": ["developer"], "urgency": "urgent", "budget_range": null, "experience_level": null, "additional_requirements": null}'
			elif "developer" in low or "engineer" in low:
				return '{"company_name": null, "industry": "technology", "location": null, "roles": ["backend engineer"], "urgency": "medium", "budget_range": null, "experience_level": null, "additional_requirements": null}'
			else:
				return '{"company_name": null, "industry": null, "location": null, "roles": [], "urgency": "medium", "budget_range": null, "experience_level": null, "additional_requirements": null}'
		
		# Handle greeting prompts
		if any(k in low for k in ["greeting", "hello", "hi", "hey"]):
			return "Hello! I'm your recruiting assistant. What positions are you looking to fill?"
		
		# Handle hiring needs
		if "developer" in low or "engineer" in low:
			return "Perfect! I understand you need technical talent. Could you share the specific tech stack, number of positions, and your timeline?"
		
		# Handle proposal requests
		if "proposal" in low or "quote" in low:
			return "I'd be happy to prepare a tailored proposal for you! Based on your needs, I recommend our Tech Startup Package with 2-4 week timeline and 92% success rate. Shall I prepare the detailed proposal?"
		
		# Handle affirmative responses
		if "yes" in low or "sure" in low:
			return "Excellent! I'll prepare a comprehensive hiring package with timeline, pricing, and next steps. This will be perfect for your needs."
			
		# Default response
		return "I'd love to help you with your recruiting needs! Could you tell me about the roles you need to fill, including quantities and timeline?"


class GeminiProvider(BaseProvider):
	name = "gemini"

	def __init__(self):
		self._available = False
		api_key = os.getenv("GOOGLE_API_KEY")
		if not api_key:
			return
		try:
			import google.generativeai as genai  # type: ignore
			genai.configure(api_key=api_key)
			self.model = genai.GenerativeModel(os.getenv("GEMINI_MODEL", "gemini-1.5-flash"))
			self._available = True
		except Exception as e:  # pragma: no cover
			logger.warning("Gemini provider unavailable: %s", e)

	def is_available(self) -> bool:
		return self._available

	def generate(self, prompt: str) -> str:
		try:
			response = self.model.generate_content(
				prompt,
				generation_config={
					"temperature": 0.3,
					"max_output_tokens": 800,
					"top_p": 0.9,
				}
			)
			return response.text.strip()
		except Exception as e:  # pragma: no cover
			logger.error("Gemini generation failed: %s", e)
			return "I'm having a temporary issue generating a response. Could you rephrase or try again?"


class ClaudeProvider(BaseProvider):
	name = "claude"

	def __init__(self):
		self._available = False
		api_key = os.getenv("ANTHROPIC_API_KEY")
		if not api_key:
			return
		try:
			import anthropic  # type: ignore
			self.client = anthropic.Anthropic(api_key=api_key)
			self.model = os.getenv("CLAUDE_MODEL", "claude-3-5-sonnet-20240620")
			self._available = True
		except Exception as e:  # pragma: no cover
			logger.warning("Claude provider unavailable: %s", e)

	def is_available(self) -> bool:
		return self._available

	def generate(self, prompt: str) -> str:
		try:
			response = self.client.messages.create(
				model=self.model,
				max_tokens=800,
				temperature=0.3,
				messages=[{"role": "user", "content": prompt}]
			)
			return response.content[0].text.strip()
		except Exception as e:  # pragma: no cover
			logger.error("Claude generation failed: %s", e)
			return "I'm having a temporary issue generating a response. Could you rephrase or try again?"


class OpenAIProvider(BaseProvider):
	name = "openai"

	def __init__(self):
		self._available = False
		api_key = os.getenv("OPENAI_API_KEY")
		if not api_key:
			return
		try:
			from openai import OpenAI  # type: ignore
			self.client = OpenAI(api_key=api_key)
			self.model = os.getenv("OPENAI_MODEL", "gpt-4o")  # Updated to GPT-4
			self._available = True
		except Exception as e:  # pragma: no cover
			logger.warning("OpenAI provider unavailable: %s", e)

	def is_available(self) -> bool:
		return self._available

	def generate(self, prompt: str) -> str:
		try:
			resp = self.client.chat.completions.create(
				model=self.model,
				messages=[{"role": "user", "content": prompt}],
				temperature=0.3,  # Lower temperature for consistency
				max_tokens=800,   # Increased for better responses
				top_p=0.9,       # Focused sampling
			)
			return resp.choices[0].message.content.strip()
		except Exception as e:  # pragma: no cover
			logger.error("OpenAI generation failed: %s", e)
			return "I'm having a temporary issue generating a response. Could you rephrase or try again?"


class DeepSeekProvider(BaseProvider):
	name = "deepseek"

	def __init__(self):
		self._available = False
		api_key = os.getenv("DEEPSEEK_API_KEY")
		if not api_key:
			return
		try:
			from openai import OpenAI  # DeepSeek uses OpenAI-compatible API
			self.client = OpenAI(
				api_key=api_key,
				base_url="https://api.deepseek.com"
			)
			self.model = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
			self._available = True
		except Exception as e:  # pragma: no cover
			logger.warning("DeepSeek provider unavailable: %s", e)

	def is_available(self) -> bool:
		return self._available

	def generate(self, prompt: str) -> str:
		try:
			resp = self.client.chat.completions.create(
				model=self.model,
				messages=[{"role": "user", "content": prompt}],
				temperature=0.3,
				max_tokens=800,
				top_p=0.9,
			)
			return resp.choices[0].message.content.strip()
		except Exception as e:  # pragma: no cover
			logger.error("DeepSeek generation failed: %s", e)
			return "I'm having a temporary issue generating a response. Could you rephrase or try again?"


class LLMService:
	"""Facade selecting the best available provider with optional override."""

	def __init__(self):
		self.providers: Dict[str, BaseProvider] = {}
		# Instantiate all providers (API keys checked in constructor)
		for cls in (GroqProvider, GeminiProvider, ClaudeProvider, OpenAIProvider, DeepSeekProvider, HFProvider, MockProvider):
			inst = cls()
			self.providers[inst.name] = inst
		self.active = self._select_active()
		logger.info("LLM provider selected: %s", self.active)

	def _select_active(self) -> str:
		forced = os.getenv("LLM_PROVIDER", "").strip().lower()
		# Updated priority order: DeepSeek (free), GPT-4, Claude, Gemini, Groq, HF, Mock
		order = ["deepseek", "openai", "claude", "gemini", "groq", "huggingface", "mock"]

		def is_up(name: str) -> bool:
			prov = self.providers.get(name)
			return bool(prov and prov.is_available())

		# Forced first
		if forced:
			mapping = {
				"gpt": "openai", "gpt4": "openai", "openai": "openai",
				"claude": "claude", "anthropic": "claude",
				"gemini": "gemini", "google": "gemini",
				"groq": "groq", "llama": "groq",
				"deepseek": "deepseek", "ds": "deepseek",
				"hf": "huggingface", "huggingface": "huggingface", 
				"mock": "mock"
			}
			target = mapping.get(forced)
			if target and is_up(target):
				return target
			logger.warning("Forced provider '%s' unavailable, falling back", forced)
		# Automatic selection in priority order
		for name in order:
			if is_up(name):
				return name
		return "mock"

	def generate(self, prompt: str) -> str:
		return self.providers[self.active].generate(prompt)

	@property
	def provider(self) -> str:
		"""Get the name of the active provider"""
		return self.active

	def is_available(self) -> bool:
		"""Check if the current active provider is available"""
		return self.providers[self.active].is_available()

	def info(self) -> Dict[str, Any]:  # For diagnostics
		return {
			"active": self.active,
			"available": [n for n, p in self.providers.items() if p.is_available()],
		}


_GLOBAL_LLM: LLMService | None = None


def get_llm_service() -> LLMService:
	global _GLOBAL_LLM
	if _GLOBAL_LLM is None:
		_GLOBAL_LLM = LLMService()
	return _GLOBAL_LLM

