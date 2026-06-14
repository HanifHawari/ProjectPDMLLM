"""
FitMind AI - Pydantic Models (Request & Response Schemas)
"""
from pydantic import BaseModel, Field
from typing import Optional, List


# ==============================================================
# Chat Models
# ==============================================================

class ChatMessage(BaseModel):
    role: str = Field(..., description="'user' atau 'assistant'")
    content: str = Field(..., description="Isi pesan")


class UserProfile(BaseModel):
    """Profil user yang disimpan di localStorage frontend."""
    name: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    weight_kg: Optional[float] = None
    height_m: Optional[float] = None
    bmi: Optional[float] = None
    goal: Optional[str] = None  # weight_loss | muscle_gain | maintenance | endurance
    experience_level: Optional[str] = None  # beginner | intermediate | advanced
    workout_frequency: Optional[int] = None  # hari/minggu
    session_duration: Optional[float] = None  # jam/sesi
    workout_type: Optional[str] = None  # HIIT | Cardio | Strength | Yoga | Mixed
    equipment: Optional[str] = None
    # Alergen
    no_gluten: Optional[bool] = False
    no_dairy: Optional[bool] = False
    no_nuts: Optional[bool] = False
    no_soy: Optional[bool] = False
    no_eggs: Optional[bool] = False
    no_fish: Optional[bool] = False
    # Diet
    diet_type: Optional[str] = None  # vegan | vegetarian | keto | paleo | none


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)
    history: List[ChatMessage] = Field(default_factory=list)
    user_profile: Optional[UserProfile] = None


class ChatResponse(BaseModel):
    response: str
    intent: Optional[str] = None


# ==============================================================
# Workout Models
# ==============================================================

class WorkoutSearchRequest(BaseModel):
    body_part: Optional[str] = None
    muscle: Optional[str] = None


class WorkoutItem(BaseModel):
    body_part: Optional[str] = None
    type_of_muscle: Optional[str] = None
    workout: Optional[str] = None
    sets: Optional[str] = None
    reps_per_set: Optional[str] = None


# ==============================================================
# Nutrition Models
# ==============================================================

class FoodSearchRequest(BaseModel):
    query: Optional[str] = None
    max_calories: Optional[float] = None
    min_health_score: Optional[float] = None
    food_type: Optional[str] = None
    # Alergen filters
    no_gluten: bool = False
    no_dairy: bool = False
    no_nuts: bool = False
    no_soy: bool = False
    no_eggs: bool = False
    no_fish: bool = False
    limit: int = Field(default=20, le=100)


# ==============================================================
# Program Models
# ==============================================================

class ProgramSearchRequest(BaseModel):
    query: Optional[str] = None
    level: Optional[str] = None
    goal: Optional[str] = None
    equipment: Optional[str] = None
    max_weeks: Optional[int] = None
    limit: int = Field(default=20, le=100)


class ProgramDetailRequest(BaseModel):
    title: str
    week: Optional[int] = None
    day: Optional[int] = None


# ==============================================================
# Dashboard Models
# ==============================================================

class DashboardStats(BaseModel):
    """Statistik referensi dari dataset (bukan data personal user)."""
    total_members: Optional[int] = None
    avg_bmi: Optional[float] = None
    avg_calories_burned: Optional[float] = None
    avg_session_duration: Optional[float] = None
    workout_types: Optional[dict] = None
    experience_distribution: Optional[dict] = None


# ==============================================================
# Generic Response
# ==============================================================

class APIResponse(BaseModel):
    success: bool = True
    data: Optional[object] = None
    message: Optional[str] = None
    total: Optional[int] = None


# ==============================================================
# User & Session Schemas (untuk DB)
# ==============================================================

class UserCreate(BaseModel):
    """Request body untuk membuat / mengidentifikasi user berdasarkan username."""
    username: str = Field(..., min_length=2, max_length=30,
                          pattern=r"^[a-zA-Z0-9_.-]+$",
                          description="Nama unik user (hanya huruf, angka, dot, strip, underscore. Tanpa spasi.)")


class UserProfileUpdate(BaseModel):
    """Request body untuk menyimpan / update profil kebugaran user."""
    age:               Optional[int]   = None
    gender:            Optional[str]   = None   # male / female
    weight_kg:         Optional[float] = None
    height_m:          Optional[float] = None
    goal:              Optional[str]   = None   # weight_loss | muscle_gain | maintenance | endurance
    experience_level:  Optional[str]   = None   # beginner | intermediate | advanced
    workout_frequency: Optional[int]   = None
    session_duration:  Optional[float] = None
    workout_type:      Optional[str]   = None
    equipment:         Optional[str]   = None
    diet_type:         Optional[str]   = None
    no_gluten:         Optional[bool]  = False
    no_dairy:          Optional[bool]  = False
    no_nuts:           Optional[bool]  = False
    no_soy:            Optional[bool]  = False
    no_eggs:           Optional[bool]  = False
    no_fish:           Optional[bool]  = False


class UserResponse(BaseModel):
    """Response setelah get-or-create user."""
    id:         int
    username:   str
    is_new:     bool  # True jika baru dibuat, False jika sudah ada
    has_profile: bool

    class Config:
        from_attributes = True


class SessionResponse(BaseModel):
    """Satu sesi chat dalam daftar riwayat."""
    id:            int
    title:         Optional[str]
    last_intent:   Optional[str]
    message_count: int
    created_at:    str

    class Config:
        from_attributes = True


class MessageResponse(BaseModel):
    """Satu pesan dalam riwayat sesi."""
    id:         int
    role:       str
    content:    str
    intent:     Optional[str]
    created_at: str

    class Config:
        from_attributes = True


# Extend ChatRequest untuk mendukung session_id (opsional)
class ChatRequestDB(BaseModel):
    """Chat request yang menyimpan pesan ke database."""
    message:    str             = Field(..., min_length=1, max_length=2000)
    username:   str             = Field(..., min_length=2, max_length=30,
                                        pattern=r"^[a-zA-Z0-9_.-]+$",
                                        description="Username untuk identifikasi user (tanpa spasi)")
    session_id: Optional[int]   = Field(None, description="ID sesi (None = buat sesi baru)")
    history:    List[ChatMessage] = Field(default_factory=list)
    user_profile: Optional[UserProfile] = None
