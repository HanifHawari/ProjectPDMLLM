"""
FitMind AI — Supervisor Agent (Router / Orchestrator)

Ini adalah otak dari sistem multi-agent.
Tugasnya:
  1. Menerima pesan dari user.
  2. Mengklasifikasikan intent menggunakan LLM (bukan hanya Regex).
  3. Mendelegasikan pesan ke agent spesialis yang tepat.
  4. Mengembalikan respons dari agent terpilih ke user.

Pola: Supervisor-Worker (1 supervisor → N worker agents)
"""
import json
import logging
from typing import AsyncGenerator

import httpx
from google import genai
from google.genai import types

from config import GEMINI_API_KEY, GEMINI_MODEL, GROQ_API_KEY, GROQ_MODEL
from agents.fitness_agent import FitnessAgent
from agents.nutrition_agent import NutritionAgent
from agents.health_agent import HealthAgent

logger = logging.getLogger(__name__)

# ==============================================================
# Inisialisasi agent spesialis (singleton)
# ==============================================================
_fitness_agent = FitnessAgent()
_nutrition_agent = NutritionAgent()
_health_agent = HealthAgent()

# Mapping nama agent ke instance-nya
AGENT_REGISTRY: dict[str, object] = {
    "fitness": _fitness_agent,
    "nutrition": _nutrition_agent,
    "health": _health_agent,
}

# ==============================================================
# LLM Client untuk Supervisor (sama seperti agent lain)
# ==============================================================
if GEMINI_API_KEY and GEMINI_API_KEY != "ISI_API_KEY_KAMU_DISINI":
    _gemini_client = genai.Client(api_key=GEMINI_API_KEY)
else:
    _gemini_client = None

# ==============================================================
# Prompt Supervisor — untuk klasifikasi intent
# ==============================================================
_SUPERVISOR_PROMPT = """Kamu adalah Supervisor AI di sistem FitMind.
Tugasmu HANYA mengklasifikasikan pertanyaan pengguna ke salah satu agent:

- "fitness"   → pertanyaan tentang: latihan, gerakan gym, program workout, otot, jadwal latihan
- "nutrition" → pertanyaan tentang: kalori, gizi, nutrisi makanan, alergen, diet, makanan sehat
- "health"    → pertanyaan tentang: BMI, berat badan ideal, estimasi kalori terbakar, TDEE, analisis kesehatan

ATURAN:
1. Jawab HANYA dengan satu kata JSON: {"agent": "fitness"} atau {"agent": "nutrition"} atau {"agent": "health"}
2. Jika pertanyaan mencakup dua domain, pilih yang paling dominan.
3. Jika tidak ada yang cocok, jawab {"agent": "fitness"} sebagai default.
4. JANGAN menulis penjelasan apapun. HANYA JSON."""


async def _classify_intent(message: str) -> str:
    """
    Gunakan LLM untuk mengklasifikasikan pesan ke agent yang tepat.
    Returns: salah satu dari "fitness", "nutrition", "health"
    """
    try:
        if GROQ_API_KEY:
            async with httpx.AsyncClient() as http_client:
                resp = await http_client.post(
                    "https://api.groq.com/openai/v1/chat/completions",
                    json={
                        "model": GROQ_MODEL,
                        "messages": [
                            {"role": "system", "content": _SUPERVISOR_PROMPT},
                            {"role": "user", "content": message}
                        ],
                        "temperature": 0.0,  # Deterministic
                        "max_tokens": 30,
                        "stream": False
                    },
                    headers={
                        "Authorization": f"Bearer {GROQ_API_KEY}",
                        "Content-Type": "application/json"
                    },
                    timeout=10.0
                )
                if resp.status_code == 200:
                    data = resp.json()
                    raw = data["choices"][0]["message"]["content"].strip()
                    parsed = json.loads(raw)
                    agent_name = parsed.get("agent", "fitness")
                    if agent_name in AGENT_REGISTRY:
                        return agent_name

        elif _gemini_client:
            response = await _gemini_client.aio.models.generate_content(
                model=GEMINI_MODEL,
                contents=[types.Content(
                    role="user",
                    parts=[types.Part(text=message)]
                )],
                config=types.GenerateContentConfig(
                    system_instruction=_SUPERVISOR_PROMPT,
                    temperature=0.0,
                    max_output_tokens=30,
                ),
            )
            raw = response.text.strip()
            parsed = json.loads(raw)
            agent_name = parsed.get("agent", "fitness")
            if agent_name in AGENT_REGISTRY:
                return agent_name

    except Exception as e:
        logger.warning(f"[Supervisor] Klasifikasi LLM gagal ({e}), pakai fallback Regex.")

    # --- Fallback: Regex sederhana jika LLM gagal ---
    return _classify_by_regex(message)


def _classify_by_regex(message: str) -> str:
    """Fallback klasifikasi berbasis kata kunci jika LLM gagal."""
    msg = message.lower()

    nutrition_keywords = [
        "kalori", "calori", "nutrisi", "gizi", "protein", "karbohidrat", "lemak",
        "makanan", "makan", "diet", "alergi", "alergen", "gluten", "dairy", "vegan",
        "food", "calories", "nutrition", "fat", "carbs", "fiber", "sugar", "vitamin"
    ]
    health_keywords = [
        "bmi", "berat badan", "body mass", "tinggi badan", "ideal weight", "obesitas",
        "kurus", "gemuk", "overweight", "underweight", "kalori terbakar", "calories burned",
        "tdee", "bmr", "basal metabolic", "estimasi kalori"
    ]

    if any(kw in msg for kw in health_keywords):
        return "health"
    if any(kw in msg for kw in nutrition_keywords):
        return "nutrition"
    return "fitness"


class SupervisorAgent:
    """
    Supervisor Agent — Orkestrasi seluruh sistem multi-agent FitMind AI.

    Alur kerja:
    1. Terima pesan user
    2. Klasifikasi ke agent yang tepat (LLM-based + Regex fallback)
    3. Delegasikan ke agent spesialis
    4. Stream atau kembalikan respons ke user

    Atribut publik:
    - last_delegated_agent: nama agent terakhir yang dipanggil (untuk logging/debugging)
    """

    def __init__(self):
        self.last_delegated_agent: str = "fitness"

    async def route_and_stream(
        self,
        message: str,
        chat_history: list[dict],
        user_profile: dict = None
    ) -> AsyncGenerator[str, None]:
        """
        Terima pesan, pilih agent yang tepat, dan stream responsnya.

        Yields:
            Potongan teks dari agent yang dipilih.
        """
        # Langkah 1: Klasifikasikan intent
        agent_name = await _classify_intent(message)
        self.last_delegated_agent = agent_name
        logger.info(f"[Supervisor] Mendelegasikan ke: {agent_name.upper()}")

        # Langkah 2: Dapatkan agent yang dipilih
        agent = AGENT_REGISTRY[agent_name]

        # Langkah 3: Bangun konteks RAG khusus agent tersebut
        context = agent.build_context(message, user_profile)

        # Langkah 4: Stream respons dari agent
        async for chunk in agent.stream(message, chat_history, context):
            yield chunk

    async def route_and_run(
        self,
        message: str,
        chat_history: list[dict],
        user_profile: dict = None
    ) -> str:
        """Non-streaming version dari route_and_stream()."""
        full = ""
        async for chunk in self.route_and_stream(message, chat_history, user_profile):
            full += chunk
        return full

    def get_last_agent(self) -> str:
        """Kembalikan nama agent yang terakhir menangani pesan."""
        return self.last_delegated_agent

    @staticmethod
    def list_agents() -> dict[str, str]:
        """Kembalikan daftar semua agent yang terdaftar beserta deskripsinya."""
        return {name: agent.description for name, agent in AGENT_REGISTRY.items()}
