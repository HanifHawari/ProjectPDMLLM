"""
FitMind AI — Nutrition Agent
Spesialis: Kalori makanan, kandungan nutrisi, pengecekan alergen, diet.
Persona: Ahli Gizi (Nutritionist) profesional.
"""
from agents.base_agent import BaseAgent
from data_loader import search_foods, search_foods_allergen_free


class NutritionAgent(BaseAgent):
    """
    Agent spesialis nutrisi dan diet.

    Dipanggil oleh SupervisorAgent untuk pertanyaan seputar:
    - Kalori dan kandungan nutrisi suatu makanan
    - Pengecekan alergen (gluten, dairy, nuts, dll)
    - Rekomendasi makanan untuk diet tertentu
    - Informasi protein, karbohidrat, lemak dari makanan
    """

    name = "NutritionAgent"
    description = "Spesialis kalori, nutrisi makanan, alergen, dan rekomendasi diet."

    system_prompt = """Kamu adalah Dr. Nisa, Ahli Gizi bersertifikat di FitMind AI.

KEPRIBADIAN:
- Akurat, berbasis data, dan mudah dipahami.
- Hanya membahas topik nutrisi, makanan, diet, dan gizi.
- Jika ditanya di luar topik nutrisi & kesehatan, tolak dengan singkat.

KEMAMPUAN UTAMA:
1. Memberikan informasi kalori dan makronutrisi (protein, karbohidrat, lemak, serat).
2. Mengidentifikasi kandungan alergen dalam makanan.
3. Merekomendasikan makanan sesuai kebutuhan diet (vegan, keto, low-carb, dll).
4. Menjelaskan nilai gizi dan manfaat kesehatan suatu makanan.

ATURAN FORMAT RESPONS:
- Selalu sebutkan satuan: nilai nutrisi adalah PER 100 GRAM kecuali disebutkan lain.
- Gunakan **bold** untuk nama makanan dan nilai penting.
- Gunakan tabel atau bullet points untuk data nutrisi.
- Langsung ke poin, tanpa basa-basi panjang.
- Maksimal 1 emoji, atau tidak sama sekali.

ATURAN DATA:
- Jika ada [KONTEKS DATA RELEVAN], WAJIB jadikan acuan utama.
- Jangan mengarang nilai kalori atau nutrisi yang tidak ada di konteks.
- Jika data tidak ditemukan, sampaikan dengan jujur."""

    def build_context(self, message: str, user_profile: dict = None) -> str:
        """
        Ambil data nutrisi relevan dari dataset untuk dijadikan konteks RAG.
        """
        context_parts = []

        # Tambahkan profil user jika ada
        if user_profile:
            profile_str = "[PROFIL PENGGUNA]\n" + "\n".join(
                f"- {k}: {v}" for k, v in user_profile.items() if v
            )
            context_parts.append(profile_str)

        msg_lower = message.lower()

        # Cek apakah ini pertanyaan alergen
        allergen_keywords = [
            "alergi", "alergen", "allergen", "gluten", "dairy", "susu",
            "kacang", "nuts", "soy", "kedelai", "telur", "egg", "ikan", "fish",
            "bebas", "free", "tanpa", "safe", "aman"
        ]
        is_allergen_query = any(kw in msg_lower for kw in allergen_keywords)

        if is_allergen_query:
            # Deteksi alergen spesifik yang disebutkan
            foods = search_foods_allergen_free(
                exclude_gluten="gluten" in msg_lower,
                exclude_dairy=any(kw in msg_lower for kw in ["dairy", "susu", "milk"]),
                exclude_nuts=any(kw in msg_lower for kw in ["kacang", "nuts", "nut"]),
                exclude_soy=any(kw in msg_lower for kw in ["soy", "kedelai"]),
                exclude_eggs=any(kw in msg_lower for kw in ["telur", "egg"]),
                exclude_fish=any(kw in msg_lower for kw in ["ikan", "fish", "seafood"]),
                limit=10
            )
        else:
            # Cari berdasarkan nama makanan dalam pesan
            # Hapus kata-kata pertanyaan yang tidak relevan
            stop_words = [
                "berapa", "kalori", "nutrisi", "gizi", "protein", "kandungan",
                "dalam", "dari", "di", "untuk", "apakah", "apa", "how", "many",
                "much", "what", "is", "are", "the"
            ]
            words = msg_lower.split()
            food_words = [w for w in words if w not in stop_words and len(w) > 2]
            food_query = " ".join(food_words[:4])  # Ambil max 4 kata pertama

            foods = search_foods(query=food_query, limit=8)
            if not foods and food_words:
                # Fallback: coba satu kata pertama yang paling relevan
                foods = search_foods(query=food_words[0], limit=8)

        if foods:
            lines = ["[DATA NUTRISI TERSEDIA — semua nilai makronutrisi adalah per 100 gram]"]
            key_cols = [
                "food_name", "calories", "protein_g", "fat_g", "carbs_g",
                "fiber_g", "sugar_g", "sodium_mg", "health_score", "food_type",
                "contains_gluten", "contains_dairy", "contains_nuts",
                "contains_soy", "contains_eggs", "contains_fish"
            ]
            for f in foods[:8]:
                parts = []
                for col in key_cols:
                    val = f.get(col, "")
                    if isinstance(val, str) and len(val) > 80:
                        val = val[:77] + "..."
                    if val != "" and val is not None:
                        parts.append(f"{col}: {val}")
                if parts:
                    lines.append("- " + " | ".join(parts))
            context_parts.append("\n".join(lines))

        return "\n\n".join(filter(None, context_parts))
