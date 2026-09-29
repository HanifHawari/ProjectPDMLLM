"""
FitMind AI - Pydantic Models (Request & Response Schemas)
"""
from pydantic import BaseModel, Field
from typing import Literal, Optional, List


# ==============================================================
# Chat Models
# ==============================================================

class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(..., max_length=2000, description="Isi pesan")


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
    history: List[ChatMessage] = Field(default_factory=list, max_length=50)
    user_profile: Optional[UserProfile] = None


class ChatResponse(BaseModel):
    response: str
    intent: Optional[str] = None


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
    """Request body untuk pendaftaran dan login."""
    username: str = Field(..., min_length=2, max_length=30,
                          pattern=r"^[a-zA-Z0-9_.-]+$",
                          description="Nama unik user (hanya huruf, angka, dot, strip, underscore. Tanpa spasi.)")
    password: str = Field(..., min_length=1, max_length=72, description="Password user")
    phone: Optional[str] = Field(None, description="Nomor WhatsApp (misal: 08123456789)")


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
    """Response setelah pendaftaran atau login."""
    id:         int
    username:   str
    phone:      Optional[str]
    is_new:     bool  # True jika baru dibuat, False jika sudah ada
    has_profile: bool
    token: Optional[str] = None

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
    history:    List[ChatMessage] = Field(default_factory=list, max_length=50)
    user_profile: Optional[UserProfile] = None


# ==============================================================
# Plan Generation Models (Structured Output)
# ==============================================================

class PlanGenerateRequest(BaseModel):
    """Request untuk generate workout / meal plan terstruktur."""
    plan_type: Optional[str] = Field("workout", description="'workout' atau 'meal'")
    goal: Optional[str] = Field(None, description="weight_loss | muscle_gain | maintenance | endurance")
    level: Optional[str] = Field(None, description="beginner | intermediate | advanced")
    days_per_week: Optional[int] = Field(3, description="Jumlah hari latihan per minggu")
    equipment: Optional[str] = Field(None, description="Full Gym | Dumbbells | Bodyweight")
    diet_type: Optional[str] = Field(None, description="vegan | vegetarian | keto | paleo | normal")
    allergies: Optional[List[str]] = Field(default_factory=list, description="Daftar alergen")
    notes: Optional[str] = Field(None, max_length=1000, description="Catatan tambahan dari user")

