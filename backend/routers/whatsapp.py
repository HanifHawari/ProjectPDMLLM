"""
Router: /api/whatsapp
Endpoints untuk integrasi WhatsApp melalui Fonnte API.
"""
import logging
import httpx
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from config import FONNTE_TOKEN

logger = logging.getLogger(__name__)
router = APIRouter()

class WhatsAppSendRequest(BaseModel):
    phone: str
    plan_type: str
    title: str
    schedule: Optional[List[dict]] = None
    meals: Optional[List[dict]] = None

def format_workout_message(plan: WhatsAppSendRequest) -> str:
    msg = f"🏋️ *FITMIND AI: {plan.title}* 🏋️\n\n"
    if not plan.schedule:
        return msg + "Jadwal kosong."
        
    for s in plan.schedule:
        msg += f"🗓️ *{s.get('day')} - {s.get('focus')}*\n"
        for ex in s.get("exercises", []):
            msg += f"  • {ex.get('name')}: {ex.get('sets')} set x {ex.get('reps')}\n"
        msg += "\n"
    
    msg += "💪 Semangat latihannya!\n_Pesan ini dikirim otomatis oleh FitMind AI._"
    return msg

def format_meal_message(plan: WhatsAppSendRequest) -> str:
    msg = f"🥗 *FITMIND AI: {plan.title}* 🥗\n\n"
    if not plan.meals:
        return msg + "Jadwal kosong."
        
    for m in plan.meals:
        msg += f"⏰ *{m.get('time')} - {m.get('meal_name')}*\n"
        for food in m.get("foods", []):
            msg += f"  • {food.get('name')} ({food.get('portion')}): {food.get('calories')} kkal\n"
        msg += "\n"
    
    msg += "🍎 Ingat minum air yang cukup!\n_Pesan ini dikirim otomatis oleh FitMind AI._"
    return msg

@router.post("/send-plan")
async def send_plan_whatsapp(request: WhatsAppSendRequest):
    """
    Format JSON plan ke teks dan kirim via WhatsApp (Fonnte).
    """
    if not FONNTE_TOKEN or FONNTE_TOKEN == "ISI_TOKEN_FONNTE_ANDA_DISINI":
        raise HTTPException(status_code=400, detail="Fonnte Token belum dikonfigurasi di .env")
        
    # 1. Bersihkan nomor HP (pastikan mulai dari 08 atau 628)
    phone = request.phone.strip()
    if phone.startswith("0"):
        phone = "62" + phone[1:]
    elif phone.startswith("+"):
        phone = phone[1:]

    # 2. Format pesan sesuai tipe
    if request.plan_type == "workout":
        message_text = format_workout_message(request)
    else:
        message_text = format_meal_message(request)

    # 3. Kirim via Fonnte API
    url = "https://api.fonnte.com/send"
    headers = {
        "Authorization": FONNTE_TOKEN
    }
    data = {
        "target": phone,
        "message": message_text,
        "countryCode": "62", # Default Indonesia
    }

    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post(url, headers=headers, data=data, timeout=15.0)
            
            if resp.status_code == 200:
                result = resp.json()
                if result.get("status") is True:
                    return {"success": True, "message": "Pesan berhasil dikirim ke WhatsApp."}
                else:
                    logger.error(f"Fonnte Error: {result}")
                    raise HTTPException(status_code=400, detail=f"Fonnte error: {result.get('reason', 'Unknown')}")
            else:
                logger.error(f"Fonnte HTTP Error: {resp.status_code} {resp.text}")
                raise HTTPException(status_code=resp.status_code, detail="Gagal terhubung ke Fonnte API.")
    except Exception as e:
        logger.error(f"Error sending WA: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
