"""
FitMind AI — Planner Agent
Spesialis: Membuat program latihan / meal plan TERSTRUKTUR (JSON).
Menggunakan Gemini JSON Mode agar output selalu valid JSON.
"""
from agents.base_agent import BaseAgent
from data_loader import search_workout, search_programs, search_foods


class PlannerAgent(BaseAgent):
    """
    Agent khusus generate structured plan (workout / meal).
    Output berupa JSON terstruktur, BUKAN teks markdown.
    """

    name = "PlannerAgent"
    description = "Generate workout plan atau meal plan terstruktur (JSON)."

    # ── Prompt khusus untuk generate plan ──
    workout_prompt = """Kamu adalah AI Personal Trainer FitMind yang membuat program latihan terstruktur dalam format JSON.

ATURAN WAJIB:
1. Buat program latihan yang LENGKAP dan REALISTIS.
2. Setiap latihan harus punya: nama, sets, reps, rest time, dan target otot.
3. Sesuaikan dengan level, goal, equipment, dan jumlah hari yang diminta.
4. Jika ada [KONTEKS DATA RELEVAN], gunakan gerakan dari situ.
5. Berikan 2-3 tips praktis di akhir.
6. Jawab dalam Bahasa Indonesia.
7. JANGAN menyebutkan "konteks" atau "database".
8. Output HARUS berupa JSON valid.

CONTOH STRUKTUR JSON YANG DIHARAPKAN:
```json
{
  "title": "Program Pemula",
  "plan_type": "workout",
  "level": "beginner",
  "goal": "muscle_gain",
  "days_per_week": 3,
  "schedule": [
    {
      "day": "Senin",
      "focus": "Upper Body",
      "exercises": [
        {
          "name": "Bench Press",
          "sets": 3,
          "reps": "10-12",
          "rest_seconds": 90,
          "muscle_group": "Chest",
          "notes": "Jaga tempo"
        }
      ]
    }
  ],
  "tips": ["Tip 1", "Tip 2"]
}
```"""

    meal_prompt = """Kamu adalah AI Ahli Gizi FitMind yang membuat meal plan terstruktur dalam format JSON.

ATURAN WAJIB:
1. Buat meal plan HARIAN yang LENGKAP (sarapan, snack, makan siang, snack, makan malam).
2. Setiap makanan harus punya: nama, porsi, kalori, protein, karbo, lemak.
3. Sesuaikan total kalori dengan goal pengguna.
4. Pertimbangkan alergen dan preferensi diet.
5. Jika ada [KONTEKS DATA RELEVAN], gunakan makanan dari situ.
6. Berikan 2-3 tips nutrisi di akhir.
7. Jawab dalam Bahasa Indonesia.
8. JANGAN menyebutkan "konteks" atau "database".
9. Output HARUS berupa JSON valid.

CONTOH STRUKTUR JSON YANG DIHARAPKAN:
```json
{
  "title": "Meal Plan Pemula",
  "plan_type": "meal",
  "daily_calories": 2000,
  "daily_protein_g": 150,
  "daily_carbs_g": 200,
  "daily_fat_g": 60,
  "meals": [
    {
      "meal_name": "Sarapan",
      "time": "08:00",
      "foods": [
        {
          "name": "Oatmeal",
          "portion": "100g",
          "calories": 350,
          "protein_g": 10,
          "carbs_g": 60,
          "fat_g": 5
        }
      ]
    }
  ],
  "tips": ["Tip 1", "Tip 2"]
}
```"""

    # ── JSON Schemas ──
    WORKOUT_SCHEMA = {
        "type": "OBJECT",
        "properties": {
            "title": {"type": "STRING"},
            "plan_type": {"type": "STRING"},
            "level": {"type": "STRING"},
            "goal": {"type": "STRING"},
            "days_per_week": {"type": "INTEGER"},
            "schedule": {
                "type": "ARRAY",
                "items": {
                    "type": "OBJECT",
                    "properties": {
                        "day": {"type": "STRING"},
                        "focus": {"type": "STRING"},
                        "exercises": {
                            "type": "ARRAY",
                            "items": {
                                "type": "OBJECT",
                                "properties": {
                                    "name": {"type": "STRING"},
                                    "sets": {"type": "INTEGER"},
                                    "reps": {"type": "STRING"},
                                    "rest_seconds": {"type": "INTEGER"},
                                    "muscle_group": {"type": "STRING"},
                                    "notes": {"type": "STRING"},
                                },
                                "required": ["name", "sets", "reps"],
                            },
                        },
                    },
                    "required": ["day", "focus", "exercises"],
                },
            },
            "tips": {"type": "ARRAY", "items": {"type": "STRING"}},
        },
        "required": ["title", "plan_type", "schedule"],
    }

    MEAL_SCHEMA = {
        "type": "OBJECT",
        "properties": {
            "title": {"type": "STRING"},
            "plan_type": {"type": "STRING"},
            "daily_calories": {"type": "INTEGER"},
            "daily_protein_g": {"type": "INTEGER"},
            "daily_carbs_g": {"type": "INTEGER"},
            "daily_fat_g": {"type": "INTEGER"},
            "meals": {
                "type": "ARRAY",
                "items": {
                    "type": "OBJECT",
                    "properties": {
                        "meal_name": {"type": "STRING"},
                        "time": {"type": "STRING"},
                        "foods": {
                            "type": "ARRAY",
                            "items": {
                                "type": "OBJECT",
                                "properties": {
                                    "name": {"type": "STRING"},
                                    "portion": {"type": "STRING"},
                                    "calories": {"type": "INTEGER"},
                                    "protein_g": {"type": "NUMBER"},
                                    "carbs_g": {"type": "NUMBER"},
                                    "fat_g": {"type": "NUMBER"},
                                },
                                "required": ["name", "portion", "calories"],
                            },
                        },
                    },
                    "required": ["meal_name", "foods"],
                },
            },
            "tips": {"type": "ARRAY", "items": {"type": "STRING"}},
        },
        "required": ["title", "plan_type", "meals"],
    }

    def get_schema(self, plan_type: str) -> dict:
        return self.MEAL_SCHEMA if plan_type == "meal" else self.WORKOUT_SCHEMA

    def get_prompt(self, plan_type: str) -> str:
        return self.meal_prompt if plan_type == "meal" else self.workout_prompt

    def build_context(self, message: str, user_profile: dict = None) -> str:
        """Ambil data relevan dari dataset sebagai konteks RAG."""
        parts = []

        if user_profile:
            parts.append(
                "[PROFIL PENGGUNA]\n"
                + "\n".join(f"- {k}: {v}" for k, v in user_profile.items() if v)
            )

        # Cari workout berdasarkan keyword
        keywords = [
            "dada", "chest", "punggung", "back", "kaki", "legs",
            "bahu", "shoulders", "perut", "abs", "bicep", "tricep",
            "lengan", "arms", "core",
        ]
        msg = message.lower()
        found = [kw for kw in keywords if kw in msg]
        if found:
            workouts = search_workout(body_part=found[0])
            if workouts:
                lines = ["[DATA GERAKAN TERSEDIA]"]
                for w in workouts[:8]:
                    row = " | ".join(f"{k}: {v}" for k, v in w.items() if v)
                    lines.append(f"- {row}")
                parts.append("\n".join(lines))

        # Cari program referensi
        level = user_profile.get("experience_level", "") if user_profile else ""
        programs = search_programs(level=level, limit=3)
        if programs:
            lines = ["[REFERENSI PROGRAM]"]
            for p in programs[:3]:
                cols = ["title", "level", "goal", "program_length"]
                row = " | ".join(f"{c}: {p.get(c, '')}" for c in cols if p.get(c))
                lines.append(f"- {row}")
            parts.append("\n".join(lines))

        # Cari makanan jika meal plan
        if "meal" in msg or "makan" in msg or "nutrisi" in msg or "diet" in msg:
            foods = search_foods(query="chicken", limit=5)
            if foods:
                lines = ["[DATA MAKANAN TERSEDIA]"]
                for f in foods[:5]:
                    cols = ["food_name", "calories", "protein_g", "fat_g", "carbs_g"]
                    row = " | ".join(f"{c}: {f.get(c, '')}" for c in cols if f.get(c))
                    lines.append(f"- {row}")
                parts.append("\n".join(lines))

        return "\n\n".join(filter(None, parts))
