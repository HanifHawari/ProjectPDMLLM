"""
FitMind AI - LLM Service (Gemini API via google-genai SDK terbaru)
Handles: prompt building, intent detection, streaming chat, context injection.
"""
import json
import logging
import re
from typing import AsyncGenerator

from google import genai
from google.genai import types

from config import GEMINI_API_KEY, GEMINI_MODEL
from data_loader import (
    ds, search_workout, search_foods, search_foods_allergen_free,
    search_programs, get_user_stats_summary
)

logger = logging.getLogger(__name__)

# ==============================================================
# Init Gemini Client
# ==============================================================
if not GEMINI_API_KEY or GEMINI_API_KEY == "ISI_API_KEY_KAMU_DISINI":
    logger.warning("GEMINI_API_KEY belum diset! Chat akan gagal.")
    client = None
else:
    client = genai.Client(api_key=GEMINI_API_KEY)


# ==============================================================
# Intent Detection
# ==============================================================

INTENT_PATTERNS = {
    "workout_by_body_part": [
        # Bahasa Indonesia
        r"latihan\s+(untuk\s+)?(?P<part>dada|punggung|kaki|lengan|bahu|perut|bicep|tricep|paha|bokong|betis|bawah)",
        r"gerakan\s+(untuk\s+)?(?P<part>[\w\s]+)",
        r"(otot|muscle)\s+(?P<part>[\w\s]+)",
        r"(cara|how)\s+(melatih|train)\s+(?P<part>[\w\s]+)",
        # Bahasa Inggris
        r"exercise\s+(for\s+)?(?P<part>chest|back|legs|arms|shoulders|abs|bicep|tricep|hamstring|quad|glute|forearm|core)",
        r"workout\s+(for\s+)?(?P<part>chest|back|legs|arms|shoulders|abs|bicep|tricep|hamstring|quad|glute|forearm|core)",
    ],
    "nutrition_lookup": [
        # Bahasa Indonesia
        r"kalori\s+(dalam|dari|untuk|di)\s+(?P<food>.+)",
        r"berapa\s+kalori\s+(di\s+|dalam\s+|dari\s+)?(?P<food>.+)",
        r"nutrisi\s+(dari\s+|dalam\s+)?(?P<food>.+)",
        r"gizi\s+(dalam\s+|dari\s+)?(?P<food>.+)",
        r"protein\s+(dalam\s+|dari\s+)?(?P<food>.+)",
        r"kandungan\s+(gizi|nutrisi)\s+(dari\s+|dalam\s+)?(?P<food>.+)",
        r"(makanan|food)\s+(?P<food>.+)\s+(berapa|how many|kalori|calories)",
        # Bahasa Inggris
        r"(calories|nutrition|nutrients|macros)\s+(in|of|for)\s+(?P<food>.+)",
        r"how\s+(many|much)\s+(calories|protein|carbs|fat)\s+(in|does)\s+(?P<food>.+)",
        r"nutritional\s+value\s+of\s+(?P<food>.+)",
    ],
    "allergen_check": [
        r"(mengandung|contain|apakah|does|ada)\s+.*(gluten|dairy|susu|kacang|nuts|soy|kedelai|egg|telur|fish|ikan|seafood)",
        r"(bebas|free|tanpa)\s+(gluten|dairy|susu|kacang|nuts|soy|kedelai|egg|telur|fish|ikan)",
        r"alergen|allergen|alergi",
        r"safe for (vegan|vegetarian|celiac|lactose|diabetic)",
        r"(aman|cocok)\s+(untuk|buat)\s+(alergi|penderita|yang)",
        r"tidak\s+(boleh|bisa)\s+(makan|konsumsi)",
    ],
    "program_recommend": [
        r"program\s+(latihan|gym|fitness|workout|olahraga)",
        r"rencana\s+(latihan|gym|fitness|olahraga)",
        r"jadwal\s+(latihan|gym|olahraga)",
        r"(\d+)\s+(week|minggu)\s+program",
        r"program\s+(untuk\s+)?(pemula|beginner|intermediate|advanced|mahir)",
        r"(recommend|rekomendasikan|sarankan).*program",
        r"(mulai|start)\s+(gym|fitness|latihan|olahraga)",
    ],
    "calorie_estimate": [
        r"berapa\s+kalori\s+(yang\s+)?(saya\s+)?(bakar|terbakar)",
        r"estimasi\s+(kalori|kalori yang terbakar)",
        r"calories?\s+burned?",
        r"burn.*(calorie|kalori)",
        r"(pembakaran|membakar)\s+kalori",
    ],
    "bmi_analysis": [
        r"bmi\s*(saya|ku|aku|mu|ku)?",
        r"(berat\s+badan|body\s+weight)\s+(ideal|normal|sehat)",
        r"apakah\s+(saya\s+|berat\s+badan\s+saya\s+)?(normal|ideal|sehat|obesitas|kurus)",
        r"body\s+mass\s+index",
        r"indeks\s+massa\s+tubuh",
        r"(kelebihan|kekurangan)\s+berat\s+badan",
        r"(overweight|underweight|obese)",
    ],
    "diet_check": [
        r"(makanan|food)\s+(untuk\s+)?(vegan|vegetarian|keto|paleo|halal|diet|sehat)",
        r"diet\s+(restriction|pembatasan|sehat|plan|program)",
        r"(rekomendasi|recommend|saran)\s+(makanan|food|makan)",
        r"(apa\s+)?(yang\s+)?(boleh|bisa|aman)\s+(dimakan|dikonsumsi|saya makan)",
    ],
    "general_fitness": [
        r"tips?\s+(gym|fitness|olahraga|latihan|sehat)",
        r"cara\s+(menurunkan|menaikkan|membentuk|mengecilkan|membesarkan)\s+(berat|badan|otot|perut)",
        r"how\s+to\s+(lose|gain|build|tone|burn)\s+(weight|muscle|fat|belly|body)",
        r"(motivasi|motivation)\s+(gym|latihan|olahraga)",
        r"(manfaat|benefit)\s+(olahraga|gym|latihan|fitness)",
    ],
}


def detect_intent(message: str) -> tuple[str, dict]:
    """
    Deteksi intent dari pesan user.
    Returns: (intent_name, extracted_entities)
    """
    msg = message.lower().strip()
    for intent, patterns in INTENT_PATTERNS.items():
        for pattern in patterns:
            match = re.search(pattern, msg, re.IGNORECASE)
            if match:
                try:
                    entities = match.groupdict()
                except Exception:
                    entities = {}
                return intent, {k: v for k, v in entities.items() if v}
    return "general", {}


# ==============================================================
# Context Builder (RAG-lite: CSV query -> string context)
# ==============================================================

def _format_workout_context(workouts: list[dict]) -> str:
    if not workouts:
        return ""
    lines = ["[DATA LATIHAN TERSEDIA]"]
    for w in workouts[:10]:
        row_str = " | ".join(f"{k}: {v}" for k, v in w.items() if v)
        lines.append(f"- {row_str}")
    return "\n".join(lines)


def _format_food_context(foods: list[dict]) -> str:
    if not foods:
        return ""
    # Catatan satuan per 100g disertakan agar LLM tidak salah interpretasi
    lines = ["[DATA NUTRISI TERSEDIA — semua nilai makronutrisi adalah per 100 gram]"]
    key_cols = ["food_name", "calories", "protein_g", "fat_g",
                "carbs_g", "fiber_g", "sugar_g", "sodium_mg",
                "health_score", "food_type",
                "contains_gluten", "contains_dairy", "contains_nuts",
                "contains_soy", "contains_eggs", "contains_fish"]
    for f in foods[:8]:
        parts = []
        for col in key_cols:
            val = f.get(col, "")
            # Truncate nilai teks yang terlalu panjang (misal: ingredients)
            if isinstance(val, str) and len(val) > 80:
                val = val[:77] + "..."
            if val != "" and val is not None:
                parts.append(f"{col}: {val}")
        if parts:
            lines.append("- " + " | ".join(parts))
    return "\n".join(lines)


def _format_program_context(programs: list[dict]) -> str:
    if not programs:
        return ""
    lines = ["[DATA PROGRAM LATIHAN TERSEDIA]"]
    key_cols = ["title", "level", "goal", "equipment", "program_length",
                "time_per_workout", "total_exercises", "description"]
    for p in programs[:5]:
        parts = []
        for col in key_cols:
            val = p.get(col, "")
            # Truncate deskripsi panjang agar tidak overflow token LLM
            if col == "description" and isinstance(val, str) and len(val) > 200:
                val = val[:197] + "..."
            if val != "" and val is not None:
                parts.append(f"{col}: {val}")
        if parts:
            lines.append("- " + " | ".join(parts))
    return "\n".join(lines)


def build_context(intent: str, entities: dict, user_profile: dict = None) -> str:
    """Ambil data relevan dari CSV berdasarkan intent dan bangun context string untuk LLM."""
    context_parts = []

    if user_profile:
        profile_str = "[PROFIL PENGGUNA]\n" + "\n".join(
            f"- {k}: {v}" for k, v in user_profile.items() if v
        )
        context_parts.append(profile_str)

    if intent == "workout_by_body_part":
        body_part = entities.get("part", "")
        workouts = search_workout(body_part=body_part)
        if not workouts:
            workouts = search_workout()
        context_parts.append(_format_workout_context(workouts))

    elif intent == "nutrition_lookup":
        food_query = entities.get("food", "")
        foods = search_foods(query=food_query, limit=8)
        context_parts.append(_format_food_context(foods))

    elif intent == "allergen_check":
        foods = search_foods_allergen_free(limit=10)
        context_parts.append(_format_food_context(foods))

    elif intent == "program_recommend":
        level = user_profile.get("experience_level", "") if user_profile else ""
        programs = search_programs(level=level, limit=5)
        context_parts.append(_format_program_context(programs))

    elif intent == "diet_check":
        foods = search_foods(min_health_score=60, limit=10)
        context_parts.append(_format_food_context(foods))

    elif intent in ("calorie_estimate", "bmi_analysis"):
        stats = get_user_stats_summary()
        if stats:
            stats_str = "[STATISTIK REFERENSI GYM MEMBERS]\n" + "\n".join(
                f"- {k}: {v}" for k, v in stats.items()
            )
            context_parts.append(stats_str)

    elif intent == "general_fitness":
        workouts = search_workout()
        programs = search_programs(limit=3)
        context_parts.append(_format_workout_context(workouts[:5]))
        context_parts.append(_format_program_context(programs))

    return "\n\n".join(filter(None, context_parts))


# ==============================================================
# System Prompt
# ==============================================================

SYSTEM_PROMPT = """Kamu adalah FitMind AI, asisten kebugaran dan nutrisi berbasis AI yang cerdas, ramah, dan berpengetahuan luas.

KEPRIBADIAN:
- Antusias, memotivasi, dan supportif
- Berbicara dengan gaya natural (campuran Bahasa Indonesia dan English adalah OK)
- Berikan jawaban yang terstruktur, mudah dibaca
- Gunakan emoji secara bijak untuk membuat respons lebih menarik

KEMAMPUAN UTAMA:
1. Rekomendasi latihan (dari database gerakan berdasarkan body part/muscle group)
2. Informasi nutrisi lengkap (dari database 35.000+ makanan gabungan USDA & OpenFoodFacts)
3. Filter makanan berdasarkan alergen (gluten, dairy, nuts, soy, eggs, fish)
4. Rekomendasi program latihan (dari ribuan program)
5. Analisis BMI dan estimasi kalori terbakar
6. Panduan diet (vegan, vegetarian, keto, paleo, halal, dll)

ATURAN PENTING — WAJIB DIIKUTI:
1. DATA NUTRISI: Semua nilai makronutrisi (kalori, protein, lemak, karbo) dalam konteks yang
   diberikan adalah PER 100 GRAM, kecuali ada keterangan satuan lain secara eksplisit.
   JANGAN mengasumsikan nilai per porsi atau per sajian jika tidak disebutkan.
2. DATA KONTEKS: Jika ada data dari dataset di bagian [KONTEKS DATA RELEVAN], WAJIB gunakan
   data tersebut sebagai acuan utama. Jangan mengarang angka atau nama makanan/latihan.
3. KETIDAKTERSEDIAAN DATA: Jika data tidak tersedia, nyatakan dengan jelas dan berikan
   panduan umum yang valid secara ilmiah.
4. FORMAT RESPONS:
   - Gunakan markdown: **bold**, bullet points (•), dan heading (###)
   - Untuk workout: sertakan nama gerakan, otot target, sets × reps
   - Untuk nutrisi: sertakan kalori, protein, karbohidrat, lemak (semua per 100g)
   - Untuk program: sertakan level, tujuan, durasi program, dan waktu per sesi
5. KESELAMATAN: Selalu sarankan konsultasi dokter/ahli gizi untuk kondisi medis khusus.

KONTEKS yang diberikan adalah data NYATA dari dataset — percayai dan gunakan sebagai fakta!"""


# ==============================================================
# Chat with Gemini (Streaming)
# ==============================================================

async def chat_stream(
    message: str,
    chat_history: list[dict],
    user_profile: dict = None
) -> AsyncGenerator[str, None]:
    """
    Stream respons dari Gemini API menggunakan google-genai SDK terbaru.

    Args:
        message: Pesan user terbaru
        chat_history: List of {"role": "user"/"assistant", "content": "..."}
        user_profile: Dict profil user dari localStorage (optional)

    Yields:
        String chunks dari LLM response
    """
    if client is None:
        yield "ERROR: GEMINI_API_KEY belum diset. Silakan isi file .env dengan API key dari https://aistudio.google.com/app/apikey"
        return

    try:
        # 1. Detect intent & build context
        intent, entities = detect_intent(message)
        logger.info(f"Intent: {intent} | Entities: {entities}")
        context = build_context(intent, entities, user_profile)

        # 2. Augment message dengan context
        augmented_message = message
        if context:
            augmented_message = (
                f"{message}\n\n"
                f"---\n"
                f"[KONTEKS DATA RELEVAN - Gunakan ini untuk menjawab]\n"
                f"{context}\n"
                f"---"
            )

        # 3. Build conversation history untuk google-genai format
        history = []
        for msg in chat_history[-10:]:
            role = "user" if msg.get("role") == "user" else "model"
            history.append(
                types.Content(
                    role=role,
                    parts=[types.Part(text=msg.get("content", ""))]
                )
            )

        # 4. Stream response
        response = await client.aio.models.generate_content_stream(
            model=GEMINI_MODEL,
            contents=history + [
                types.Content(
                    role="user",
                    parts=[types.Part(text=augmented_message)]
                )
            ],
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                temperature=0.7,
                top_p=0.95,
                max_output_tokens=2048,
            ),
        )
        async for chunk in response:
            if chunk.text:
                yield chunk.text

    except Exception as e:
        logger.error(f"Gemini API error: {e}")
        yield f"\n\nMaaf, terjadi error: {str(e)}. Silakan coba lagi."


async def chat_simple(
    message: str,
    chat_history: list[dict],
    user_profile: dict = None
) -> str:
    """Non-streaming version untuk endpoint biasa."""
    full_response = ""
    async for chunk in chat_stream(message, chat_history, user_profile):
        full_response += chunk
    return full_response
