"""
Router: /api/users
Manajemen user berdasarkan username (tanpa password/auth).

Alur:
  POST /api/users/login  → get-or-create user berdasarkan username
  GET  /api/users/{username}/profile   → ambil profil kebugaran
  PUT  /api/users/{username}/profile   → simpan / update profil kebugaran
  GET  /api/users/{username}/sessions  → daftar sesi chat user
  GET  /api/users/{username}/sessions/{session_id}/messages → riwayat pesan sesi
  DELETE /api/users/{username}/sessions/{session_id}        → hapus sesi
"""
import logging
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database.db_engine import get_db
from database.db_models import User, UserProfile, ChatSession, ChatMessage
from models import (
    APIResponse, UserCreate, UserProfileUpdate,
    UserResponse, SessionResponse, MessageResponse
)

logger = logging.getLogger(__name__)
router = APIRouter()


# ==============================================================
# Helper
# ==============================================================

def _get_user_or_404(username: str, db: Session) -> User:
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail=f"User '{username}' tidak ditemukan")
    return user


def _compute_bmi(weight_kg: Optional[float], height_m: Optional[float]) -> Optional[float]:
    if weight_kg and height_m and height_m > 0:
        return round(weight_kg / (height_m ** 2), 2)
    return None


# ==============================================================
# POST /login — get-or-create user
# ==============================================================
@router.post("/login", response_model=UserResponse)
async def login_or_register(body: UserCreate, db: Session = Depends(get_db)):
    """
    Masuk / daftar berdasarkan username.
    - Jika username sudah ada → kembalikan data user lama (is_new=False)
    - Jika belum ada → buat user baru otomatis (is_new=True)
    Tidak ada password — identifikasi hanya berdasarkan username.
    """
    username = body.username.strip()

    existing = db.query(User).filter(User.username == username).first()
    if existing:
        logger.info(f"User login: '{username}' (id={existing.id})")
        return UserResponse(
            id=existing.id,
            username=existing.username,
            is_new=False,
            has_profile=existing.profile is not None
        )

    # Buat user baru
    new_user = User(username=username)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    logger.info(f"User baru dibuat: '{username}' (id={new_user.id})")

    return UserResponse(
        id=new_user.id,
        username=new_user.username,
        is_new=True,
        has_profile=False
    )


# ==============================================================
# GET /profile — ambil profil kebugaran
# ==============================================================
@router.get("/{username}/profile")
async def get_profile(username: str, db: Session = Depends(get_db)):
    """Ambil profil kebugaran user. 404 jika user belum ada, 204 jika profil belum diisi."""
    user = _get_user_or_404(username, db)

    if not user.profile:
        return APIResponse(success=True, data=None,
                           message="Profil belum diisi. Gunakan PUT untuk mengisinya.")

    profile = user.profile
    return APIResponse(success=True, data={
        "user_id":           user.id,
        "username":          user.username,
        "age":               profile.age,
        "gender":            profile.gender,
        "weight_kg":         profile.weight_kg,
        "height_m":          profile.height_m,
        "bmi":               profile.bmi,
        "goal":              profile.goal,
        "experience_level":  profile.experience_level,
        "workout_frequency": profile.workout_frequency,
        "session_duration":  profile.session_duration,
        "workout_type":      profile.workout_type,
        "equipment":         profile.equipment,
        "diet_type":         profile.diet_type,
        "allergens": {
            "no_gluten": profile.no_gluten,
            "no_dairy":  profile.no_dairy,
            "no_nuts":   profile.no_nuts,
            "no_soy":    profile.no_soy,
            "no_eggs":   profile.no_eggs,
            "no_fish":   profile.no_fish,
        },
        "updated_at": profile.updated_at.isoformat() if profile.updated_at else None,
    })


# ==============================================================
# PUT /profile — simpan / update profil
# ==============================================================
@router.put("/{username}/profile")
async def upsert_profile(
    username: str,
    body: UserProfileUpdate,
    db: Session = Depends(get_db)
):
    """
    Simpan atau update profil kebugaran user.
    Jika profil sudah ada → update kolom yang dikirim saja.
    Jika belum ada → buat profil baru.
    """
    user = _get_user_or_404(username, db)

    profile = user.profile
    if not profile:
        profile = UserProfile(user_id=user.id)
        db.add(profile)

    # Update field yang dikirim (tidak overwrite dengan None jika tidak dikirim)
    data = body.model_dump(exclude_unset=False)
    for field, value in data.items():
        if value is not None or field.startswith("no_"):
            setattr(profile, field, value)

    # Hitung BMI otomatis
    profile.bmi = _compute_bmi(profile.weight_kg, profile.height_m)

    db.commit()
    db.refresh(profile)
    logger.info(f"Profil diupdate: '{username}'")

    return APIResponse(
        success=True,
        message="Profil berhasil disimpan.",
        data={"bmi": profile.bmi}
    )


# ==============================================================
# GET /sessions — daftar sesi chat user
# ==============================================================
@router.get("/{username}/sessions")
async def get_sessions(
    username: str,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """Ambil daftar sesi chat user (terbaru dulu)."""
    user = _get_user_or_404(username, db)

    sessions = (
        db.query(ChatSession)
        .filter(ChatSession.user_id == user.id)
        .order_by(ChatSession.created_at.desc())
        .limit(limit)
        .all()
    )

    return APIResponse(
        success=True,
        total=len(sessions),
        data=[{
            "id":            s.id,
            "title":         s.title or "Sesi tanpa judul",
            "last_intent":   s.last_intent,
            "message_count": s.message_count,
            "created_at":    s.created_at.isoformat() if s.created_at else None,
            "updated_at":    s.updated_at.isoformat() if s.updated_at else None,
        } for s in sessions]
    )


# ==============================================================
# GET /sessions/{session_id}/messages — riwayat pesan
# ==============================================================
@router.get("/{username}/sessions/{session_id}/messages")
async def get_session_messages(
    username: str,
    session_id: int,
    db: Session = Depends(get_db)
):
    """Ambil semua pesan dalam satu sesi chat."""
    user = _get_user_or_404(username, db)

    session = db.query(ChatSession).filter(
        ChatSession.id == session_id,
        ChatSession.user_id == user.id
    ).first()

    if not session:
        raise HTTPException(status_code=404, detail="Sesi tidak ditemukan")

    messages = (
        db.query(ChatMessage)
        .filter(ChatMessage.session_id == session_id)
        .order_by(ChatMessage.created_at)
        .all()
    )

    return APIResponse(
        success=True,
        total=len(messages),
        data={
            "session": {
                "id":    session.id,
                "title": session.title or "Sesi tanpa judul",
            },
            "messages": [{
                "id":         m.id,
                "role":       m.role,
                "content":    m.content,
                "intent":     m.intent,
                "created_at": m.created_at.isoformat() if m.created_at else None,
            } for m in messages]
        }
    )


# ==============================================================
# DELETE /sessions/{session_id} — hapus sesi
# ==============================================================
@router.delete("/{username}/sessions/{session_id}")
async def delete_session(
    username: str,
    session_id: int,
    db: Session = Depends(get_db)
):
    """Hapus sesi chat beserta semua pesannya."""
    user = _get_user_or_404(username, db)

    session = db.query(ChatSession).filter(
        ChatSession.id == session_id,
        ChatSession.user_id == user.id
    ).first()

    if not session:
        raise HTTPException(status_code=404, detail="Sesi tidak ditemukan")

    db.delete(session)
    db.commit()
    logger.info(f"Sesi {session_id} dihapus oleh '{username}'")

    return APIResponse(success=True, message=f"Sesi '{session.title}' berhasil dihapus.")
