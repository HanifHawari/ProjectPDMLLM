"""
FitMind AI — Base Agent
Kelas dasar yang diwarisi oleh semua agent spesialis.
Setiap agent memiliki:
  - nama dan deskripsi
  - system_prompt khusus domain
  - kemampuan memanggil LLM (Groq atau Gemini)
"""
import json
import logging
from typing import AsyncGenerator

import httpx
from google import genai
from google.genai import types

from config import GEMINI_API_KEY, GEMINI_MODEL, GROQ_API_KEY, GROQ_MODEL

logger = logging.getLogger(__name__)

# ==============================================================
# Inisialisasi LLM Client (shared untuk semua agent)
# ==============================================================
if GEMINI_API_KEY and GEMINI_API_KEY != "ISI_API_KEY_KAMU_DISINI":
    _gemini_client = genai.Client(api_key=GEMINI_API_KEY)
else:
    _gemini_client = None
    logger.warning("GEMINI_API_KEY belum diset!")


class BaseAgent:
    """
    Kelas dasar untuk semua agent FitMind AI.

    Setiap subclass WAJIB mendefinisikan:
      - name (str): Nama agent, contoh "FitnessAgent"
      - description (str): Deskripsi singkat tugasnya
      - system_prompt (str): Instruksi/persona agent ini ke LLM
    """

    name: str = "BaseAgent"
    description: str = "Agent dasar"
    system_prompt: str = "Kamu adalah asisten AI."

    def _build_groq_messages(
        self,
        message: str,
        chat_history: list[dict],
        context: str = ""
    ) -> list[dict]:
        """Susun daftar pesan untuk Groq API (OpenAI-compatible format)."""
        messages = [{"role": "system", "content": self.system_prompt}]

        # Tambahkan riwayat percakapan (maksimal 10 pesan terakhir)
        for msg in chat_history[-10:]:
            role = "user" if msg.get("role") == "user" else "assistant"
            messages.append({"role": role, "content": msg.get("content", "")})

        # Augment pesan user dengan konteks data jika ada
        final_message = message
        if context:
            final_message = (
                f"{message}\n\n---\n"
                f"[KONTEKS DATA RELEVAN - Gunakan ini untuk menjawab]\n"
                f"{context}\n---"
            )

        messages.append({"role": "user", "content": final_message})
        return messages

    def _build_gemini_contents(
        self,
        message: str,
        chat_history: list[dict],
        context: str = ""
    ) -> list:
        """Susun daftar contents untuk Gemini API."""
        contents = []

        for msg in chat_history[-10:]:
            role = "user" if msg.get("role") == "user" else "model"
            contents.append(
                types.Content(
                    role=role,
                    parts=[types.Part(text=msg.get("content", ""))]
                )
            )

        final_message = message
        if context:
            final_message = (
                f"{message}\n\n---\n"
                f"[KONTEKS DATA RELEVAN - Gunakan ini untuk menjawab]\n"
                f"{context}\n---"
            )

        contents.append(
            types.Content(
                role="user",
                parts=[types.Part(text=final_message)]
            )
        )
        return contents

    async def stream(
        self,
        message: str,
        chat_history: list[dict],
        context: str = ""
    ) -> AsyncGenerator[str, None]:
        """
        Stream respons dari LLM menggunakan system_prompt agent ini.

        Args:
            message: Pesan user
            chat_history: Riwayat percakapan
            context: Konteks data relevan dari RAG (opsional)

        Yields:
            Potongan teks dari LLM
        """
        if not GROQ_API_KEY and _gemini_client is None:
            yield f"[{self.name}] ERROR: Tidak ada API key yang valid."
            return

        try:
            if GROQ_API_KEY:
                # --- Groq API ---
                messages = self._build_groq_messages(message, chat_history, context)
                async with httpx.AsyncClient() as http_client:
                    async with http_client.stream(
                        "POST",
                        "https://api.groq.com/openai/v1/chat/completions",
                        json={
                            "model": GROQ_MODEL,
                            "messages": messages,
                            "temperature": 0.7,
                            "stream": True
                        },
                        headers={
                            "Authorization": f"Bearer {GROQ_API_KEY}",
                            "Content-Type": "application/json"
                        },
                        timeout=60.0
                    ) as response:
                        if response.status_code != 200:
                            error_body = await response.aread()
                            yield f"\n\nError dari Groq API: {error_body.decode('utf-8')}"
                            return

                        async for line in response.aiter_lines():
                            if line.startswith("data: "):
                                data_str = line[6:].strip()
                                if data_str == "[DONE]":
                                    break
                                try:
                                    data = json.loads(data_str)
                                    content = data["choices"][0]["delta"].get("content", "")
                                    if content:
                                        yield content
                                except Exception:
                                    pass
            else:
                # --- Gemini API ---
                contents = self._build_gemini_contents(message, chat_history, context)
                response = await _gemini_client.aio.models.generate_content_stream(
                    model=GEMINI_MODEL,
                    contents=contents,
                    config=types.GenerateContentConfig(
                        system_instruction=self.system_prompt,
                        temperature=0.7,
                        top_p=0.95,
                        max_output_tokens=2048,
                    ),
                )
                async for chunk in response:
                    if chunk.text:
                        yield chunk.text

        except Exception as e:
            logger.error(f"[{self.name}] LLM error: {e}")
            yield f"\n\nMaaf, terjadi error pada {self.name}: {str(e)}"

    async def run(
        self,
        message: str,
        chat_history: list[dict],
        context: str = ""
    ) -> str:
        """Non-streaming version dari stream()."""
        full = ""
        async for chunk in self.stream(message, chat_history, context):
            full += chunk
        return full
