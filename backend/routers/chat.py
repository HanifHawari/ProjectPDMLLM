"""
Router: /api/chat
Endpoints untuk AI chat (streaming & non-streaming).

Endpoint:
  POST /api/chat/stream         → streaming (tanpa DB, untuk testing)
  POST /api/chat                → non-streaming (tanpa DB, untuk testing)
  POST /api/chat/session/stream → streaming + simpan ke DB (production)
  GET  /api/chat/intents        → daftar intent yang didukung
"""
import json
import logging
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from database.db_engine import get_db
from database.db_models import User, ChatSession, ChatMessage
from models import ChatRequest, ChatResponse, ChatRequestDB
from llm_service import chat_stream, chat_simple, detect_intent

logger = logging.getLogger(__name__)
router = APIRouter()


# ==============================================================
# Helper — simpan pesan ke DB
# ==============================================================

def _get_or_create_session(
    db: Session,
    username: str,
    session_id: int | None,
    first_message: str
) -> tuple[ChatSession, bool]:
    """
    Ambil sesi yang ada atau buat sesi baru.
    Returns: (session, is_new)
    """
    # Pastikan user ada
    user = db.query(User).filter(User.username == username).first()
    if not user:
        # Auto-create user jika belum ada (sama seperti /login)
        user = User(username=username)
        db.add(user)
        db.commit()
        db.refresh(user)
        logger.info(f"Auto-create user '{username}' saat chat")

    # Cari sesi yang diminta
    if session_id:
        session = db.query(ChatSession).filter(
            ChatSession.id == session_id,
            ChatSession.user_id == user.id
        ).first()
        if session:
            return session, False

    # Buat sesi baru
    title = first_message[:80].strip()
    new_session = ChatSession(
        user_id=user.id,
        title=title,
        message_count=0,
    )
    db.add(new_session)
    db.commit()
    db.refresh(new_session)
    return new_session, True


def _save_message(db: Session, session_id: int, role: str, content: str, intent: str | None = None):
    """Simpan satu pesan ke tabel chat_messages dan update message_count."""
    msg = ChatMessage(
        session_id=session_id,
        role=role,
        content=content,
        intent=intent,
    )
    db.add(msg)
    # Increment message_count di sesi
    db.query(ChatSession).filter(ChatSession.id == session_id).update(
        {"message_count": ChatSession.message_count + 1}
    )
    db.commit()
    return msg


# ==============================================================
# POST /session/stream — streaming + simpan ke DB
# ==============================================================
@router.post("/session/stream")
async def chat_session_stream(
    request: ChatRequestDB,
    db: Session = Depends(get_db)
):
    """
    Streaming chat dengan Gemini AI yang menyimpan percakapan ke database.

    - username wajib diisi (tanpa password)
    - session_id opsional: jika None → buat sesi baru
    - Pesan user dan jawaban AI disimpan ke chat_messages
    - Response: text/event-stream (SSE)

    SSE events yang dikirim:
      data: {"chunk": "..."} → potongan teks dari AI
      data: {"session_id": 123, "is_new_session": true} → info sesi
      data: [DONE] → selesai
    """
    # Dapatkan / buat sesi
    session, is_new = _get_or_create_session(
        db=db,
        username=request.username,
        session_id=request.session_id,
        first_message=request.message
    )
    session_id = session.id

    # Deteksi intent dari pesan user
    intent, _ = detect_intent(request.message)

    # Simpan pesan user ke DB
    _save_message(db, session_id, role="user", content=request.message, intent=intent)

    # Update last_intent di sesi
    db.query(ChatSession).filter(ChatSession.id == session_id).update(
        {"last_intent": intent}
    )
    db.commit()

    # Siapkan data untuk LLM
    user_profile_dict = request.user_profile.model_dump() if request.user_profile else None
    history_dicts = [{"role": m.role, "content": m.content} for m in request.history]

    async def generate():
        # Kirim info sesi di awal
        yield f"data: {json.dumps({'session_id': session_id, 'is_new_session': is_new, 'intent': intent})}\n\n"

        full_response = ""
        try:
            async for chunk in chat_stream(
                message=request.message,
                chat_history=history_dicts,
                user_profile=user_profile_dict
            ):
                full_response += chunk
                yield f"data: {json.dumps({'chunk': chunk})}\n\n"

            yield "data: [DONE]\n\n"

        except Exception as e:
            logger.error(f"Stream error: {e}")
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
        finally:
            # Simpan jawaban AI ke DB (setelah streaming selesai)
            if full_response:
                try:
                    _save_message(db, session_id, role="assistant", content=full_response, intent=intent)
                except Exception as db_err:
                    logger.error(f"Gagal simpan pesan AI ke DB: {db_err}")

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "Connection": "keep-alive",
        }
    )


# ==============================================================
# POST /session — non-streaming + simpan ke DB
# ==============================================================
@router.post("/session")
async def chat_session(
    request: ChatRequestDB,
    db: Session = Depends(get_db)
):
    """
    Non-streaming chat yang menyimpan percakapan ke database.
    Berguna untuk testing atau client yang tidak mendukung SSE.
    """
    session, is_new = _get_or_create_session(
        db=db,
        username=request.username,
        session_id=request.session_id,
        first_message=request.message
    )
    session_id = session.id

    intent, _ = detect_intent(request.message)
    _save_message(db, session_id, role="user", content=request.message, intent=intent)

    db.query(ChatSession).filter(ChatSession.id == session_id).update(
        {"last_intent": intent}
    )
    db.commit()

    user_profile_dict = request.user_profile.model_dump() if request.user_profile else None
    history_dicts = [{"role": m.role, "content": m.content} for m in request.history]

    response_text = await chat_simple(
        message=request.message,
        chat_history=history_dicts,
        user_profile=user_profile_dict
    )

    _save_message(db, session_id, role="assistant", content=response_text, intent=intent)

    return {
        "session_id":     session_id,
        "is_new_session": is_new,
        "intent":         intent,
        "response":       response_text,
    }


# ==============================================================
# POST /stream — streaming tanpa DB (testing / anonymous)
# ==============================================================
@router.post("/stream")
async def chat_endpoint_stream(request: ChatRequest):
    """
    Streaming chat TANPA menyimpan ke database.
    Cocok untuk testing cepat atau mode anonim.
    """
    user_profile_dict = request.user_profile.model_dump() if request.user_profile else None
    history_dicts = [{"role": m.role, "content": m.content} for m in request.history]

    async def generate():
        try:
            async for chunk in chat_stream(
                message=request.message,
                chat_history=history_dicts,
                user_profile=user_profile_dict
            ):
                yield f"data: {json.dumps({'chunk': chunk})}\n\n"
            yield "data: [DONE]\n\n"
        except Exception as e:
            logger.error(f"Stream error: {e}")
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "Connection": "keep-alive",
        }
    )


# ==============================================================
# POST / — non-streaming tanpa DB (testing)
# ==============================================================
@router.post("", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """Non-streaming chat TANPA database (untuk testing)."""
    user_profile_dict = request.user_profile.model_dump() if request.user_profile else None
    history_dicts = [{"role": m.role, "content": m.content} for m in request.history]
    intent, _ = detect_intent(request.message)
    response_text = await chat_simple(
        message=request.message,
        chat_history=history_dicts,
        user_profile=user_profile_dict
    )
    return ChatResponse(response=response_text, intent=intent)


# ==============================================================
# GET /intents — daftar intent
# ==============================================================
@router.get("/intents")
async def get_intents():
    """Daftar intent yang didukung (untuk debugging)."""
    from llm_service import INTENT_PATTERNS
    return {"intents": list(INTENT_PATTERNS.keys())}
