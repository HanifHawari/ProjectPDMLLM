"""
Exercise API Service
Menghubungkan ke ExerciseDB via RapidAPI untuk mendapatkan data latihan + GIF animasi.
"""
import httpx
from functools import lru_cache
from config import RAPIDAPI_KEY, APP_HOST, APP_PORT

from deep_translator import GoogleTranslator

BASE_URL = "https://exercisedb.p.rapidapi.com"
HEADERS = {
    "X-RapidAPI-Key": RAPIDAPI_KEY,
    "X-RapidAPI-Host": "exercisedb.p.rapidapi.com",
}

# Mapping pencarian (Lokal -> ExerciseDB)
BODY_PART_MAP = {
    "chest": "chest", "back": "back", "legs": "upper legs", "arms": "upper arms",
    "shoulders": "shoulders", "abs": "waist", "bicep": "upper arms", "tricep": "upper arms",
    "core": "waist", "cardio": "cardio", "neck": "neck",
}


# Cache translasi instruksi untuk mempercepat pencarian yang sama
_instruction_cache = {}

import asyncio

def translate_instructions(instructions: list[str]) -> list[str]:
    if not instructions:
        return []
    key = str(instructions)
    if key in _instruction_cache:
        return _instruction_cache[key]
    
    try:
        translated = GoogleTranslator(source='en', target='id').translate_batch(instructions)
        if translated:
            _instruction_cache[key] = translated
            return translated
    except Exception:
        pass
    return instructions



# Backend base URL untuk proxy GIF
# Gunakan localhost jika APP_HOST adalah 0.0.0.0 (artinya listen di semua interface)
_host = "localhost" if APP_HOST in ("0.0.0.0", "") else APP_HOST
BACKEND_BASE_URL = f"http://{_host}:{APP_PORT}"


def _make_gif_url(ex_id: str) -> str:
    """
    Buat URL proxy GIF dengan relative path agar frontend bisa mengambilnya dari domain yang sama.
    """
    if not ex_id:
        return ""
    return f"/api/workout/gif/image/{ex_id}?v=3"


async def _normalize_exercise(ex: dict) -> dict:
    """Normalisasi field dari ExerciseDB ke format yang konsisten + Translate ke Bahasa Indonesia."""
    ex_id = ex.get("id", "")
    gif_url = _make_gif_url(ex_id)
    
    # Menggunakan bahasa Inggris asli (tanpa translasi statis)
    bp = ex.get("bodyPart", "").title()
    target = ex.get("target", "").title()
    eq = ex.get("equipment", "").title()
    
    raw_sec = ex.get("secondaryMuscles", [])
    sec = [m.title() for m in raw_sec]
    
    # Translasi Dinamis (Google Translate)
    raw_instructions = ex.get("instructions", [])
    loop = asyncio.get_event_loop()
    instructions = await loop.run_in_executor(None, translate_instructions, raw_instructions)
    
    return {
        "id": ex_id,
        "name": ex.get("name", "").title(),
        "body_part": bp,
        "target": target,
        "equipment": eq,
        "gif_url": gif_url,
        "secondary_muscles": sec,
        "instructions": instructions,
        "description": ex.get("description", ""),
        "difficulty": ex.get("difficulty", ""),
        "category": ex.get("category", ""),
    }


async def search_by_name(name: str, limit: int = 12) -> list[dict]:
    """Cari exercise berdasarkan nama. Mengembalikan list dengan gif_url (proxy)."""
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            res = await client.get(
                f"{BASE_URL}/exercises/name/{name.lower().strip()}",
                headers=HEADERS,
                params={"limit": limit, "offset": 0},
            )
            if res.status_code == 200:
                tasks = [_normalize_exercise(e) for e in res.json()]
                return await asyncio.gather(*tasks)
    except Exception as e:
        print(f"[ExerciseDB] search_by_name error: {e}")
    return []


async def search_by_body_part(body_part: str, limit: int = 12) -> list[dict]:
    """Cari exercise berdasarkan body part. Mengembalikan list dengan gif_url (proxy)."""
    mapped = BODY_PART_MAP.get(body_part.lower(), body_part.lower())
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            res = await client.get(
                f"{BASE_URL}/exercises/bodyPart/{mapped}",
                headers=HEADERS,
                params={"limit": limit, "offset": 0},
            )
            if res.status_code == 200:
                tasks = [_normalize_exercise(e) for e in res.json()]
                return await asyncio.gather(*tasks)
    except Exception as e:
        print(f"[ExerciseDB] search_by_body_part error: {e}")
    return []


async def get_all_exercises_gif(limit: int = 24) -> list[dict]:
    """Ambil semua exercise. Mengembalikan list dengan gif_url (proxy)."""
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            res = await client.get(
                f"{BASE_URL}/exercises",
                headers=HEADERS,
                params={"limit": limit, "offset": 0},
            )
            if res.status_code == 200:
                tasks = [_normalize_exercise(e) for e in res.json()]
                return await asyncio.gather(*tasks)
    except Exception as e:
        print(f"[ExerciseDB] get_all_exercises_gif error: {e}")
    return []


async def get_exercise_detail(exercise_id: str) -> dict | None:
    """Ambil detail lengkap satu exercise berdasarkan ID."""
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            res = await client.get(
                f"{BASE_URL}/exercises/exercise/{exercise_id}",
                headers=HEADERS,
            )
            if res.status_code == 200:
                return await _normalize_exercise(res.json())
    except Exception as e:
        print(f"[ExerciseDB] get_exercise_detail error: {e}")
    return None


async def get_all_body_parts() -> list[str]:
    """Ambil semua body part yang tersedia di ExerciseDB."""
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            res = await client.get(f"{BASE_URL}/exercises/bodyPartList", headers=HEADERS)
            if res.status_code == 200:
                return res.json()
    except Exception as e:
        print(f"[ExerciseDB] get_all_body_parts error: {e}")
    return []


# Simple in-memory cache for GIFs (exercise_id -> bytes)
_gif_cache = {}
MAX_CACHE_SIZE = 100

async def fetch_exercise_gif(exercise_id: str) -> bytes | None:
    """
    Proxy: Ambil bytes GIF dari ExerciseDB menggunakan endpoint /image.
    ExerciseDB v2 tidak lagi menyertakan gifUrl di response JSON, melainkan
    menyediakan endpoint /image?exerciseId=<id>&resolution=<res> yang memerlukan
    RapidAPI key di header. Backend melakukan proxy agar frontend bisa menampilkan gambar.
    """
    # Cek di cache dulu agar tidak memanggil RapidAPI berulang kali
    if exercise_id in _gif_cache:
        return _gif_cache[exercise_id]

    try:
        async with httpx.AsyncClient(timeout=20, follow_redirects=True) as client:
            res = await client.get(
                f"{BASE_URL}/image",
                headers=HEADERS,
                params={"exerciseId": exercise_id, "resolution": "1080"},
            )
            if res.status_code == 200:
                ct = res.headers.get("content-type", "")
                if "image" in ct or "gif" in ct:
                    # Simpan ke cache jika batas belum tercapai (mencegah memory leak)
                    if len(_gif_cache) >= MAX_CACHE_SIZE:
                        _gif_cache.pop(next(iter(_gif_cache))) # Hapus elemen pertama
                    _gif_cache[exercise_id] = res.content
                    return res.content
            print(f"[ExerciseDB] fetch_exercise_gif status={res.status_code} for id={exercise_id}")
    except Exception as e:
        print(f"[ExerciseDB] fetch_exercise_gif error: {e}")
    return None
