"""
Router: /api/calendar
Endpoints untuk integrasi kalender (menghasilkan file .ics).
"""
import logging
from datetime import datetime, timedelta, date
from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel
from typing import List, Optional, Any

# icalendar sudah kita install di sesi sebelumnya
from icalendar import Calendar, Event, Alarm

logger = logging.getLogger(__name__)
router = APIRouter()

class SyncCalendarRequest(BaseModel):
    title: str
    plan_type: str
    schedule: Optional[List[dict]] = None
    meals: Optional[List[dict]] = None

def get_next_weekday(target_weekday: int, hour: int = 7) -> datetime:
    """Mendapatkan datetime untuk hari tertentu di minggu ini/depan.
    target_weekday: 0=Senin, 1=Selasa, dst.
    """
    today = date.today()
    days_ahead = target_weekday - today.weekday()
    if days_ahead <= 0: # Jika hari sudah lewat minggu ini, jadwalkan untuk minggu depan
        days_ahead += 7
    target_date = today + timedelta(days=days_ahead)
    return datetime.combine(target_date, datetime.min.time()).replace(hour=hour)

DAY_MAP = {
    "senin": 0, "selasa": 1, "rabu": 2,
    "kamis": 3, "jumat": 4, "sabtu": 5, "minggu": 6
}

@router.post("/export")
async def export_to_calendar(plan: SyncCalendarRequest):
    """
    Convert workout/meal plan JSON → .ics calendar file.
    Menerima JSON plan dari frontend.
    """
    cal = Calendar()
    cal.add('prodid', '-//FitMind AI//Plan Generator//ID')
    cal.add('version', '2.0')

    # Jika ini WORKOUT plan
    if plan.plan_type == "workout" and plan.schedule:
        for session in plan.schedule:
            event = Event()
            
            # Parsing hari menjadi integer (0-6)
            day_str = session.get("day", "Senin").lower()
            weekday_idx = DAY_MAP.get(day_str, 0)
            
            # Set waktu latihan (default jam 07:00 pagi selama 1 jam)
            dt_start = get_next_weekday(weekday_idx, hour=7)
            dt_end = dt_start + timedelta(hours=1)
            
            event.add('summary', f"🏋️ FitMind: {session.get('focus', 'Workout')}")
            
            # Format deskripsi gerakan
            desc_lines = [f"Program: {plan.title}", f"Fokus: {session.get('focus')}", ""]
            for ex in session.get("exercises", []):
                desc_lines.append(f"• {ex.get('name')} — {ex.get('sets')}x{ex.get('reps')}")
                if "notes" in ex and ex["notes"]:
                    desc_lines.append(f"  Note: {ex['notes']}")
            
            event.add('description', "\n".join(desc_lines))
            event.add('dtstart', dt_start)
            event.add('dtend', dt_end)
            
            # Alarm 1 jam sebelumnya
            alarm = Alarm()
            alarm.add('action', 'DISPLAY')
            alarm.add('description', f"Reminder Latihan: {session.get('focus')}")
            alarm.add('trigger', timedelta(hours=-1))
            event.add_component(alarm)
            
            cal.add_component(event)

    # Jika ini MEAL plan (Opsional: jadwalkan prep meals / sarapan dsb)
    elif plan.plan_type == "meal" and plan.meals:
        # Jadwalkan untuk BESOK
        tomorrow = date.today() + timedelta(days=1)
        for meal in plan.meals:
            event = Event()
            
            # Parse waktu (misal "08:00")
            time_str = meal.get("time", "08:00")
            try:
                hour, minute = map(int, time_str.split(":"))
            except:
                hour, minute = 8, 0
                
            dt_start = datetime.combine(tomorrow, datetime.min.time()).replace(hour=hour, minute=minute)
            dt_end = dt_start + timedelta(minutes=30)
            
            event.add('summary', f"🥗 FitMind: {meal.get('meal_name', 'Meal')}")
            
            desc_lines = [f"Program: {plan.title}", f"Waktu: {time_str}", ""]
            for food in meal.get("foods", []):
                desc_lines.append(f"• {food.get('name')} ({food.get('portion')}) — {food.get('calories')} kkal")
            
            event.add('description', "\n".join(desc_lines))
            event.add('dtstart', dt_start)
            event.add('dtend', dt_end)
            
            cal.add_component(event)
    
    else:
        raise HTTPException(status_code=400, detail="Data plan tidak valid atau tidak memiliki schedule/meals.")

    # Kembalikan sebagai file biner .ics
    return Response(
        content=cal.to_ical(),
        media_type="text/calendar",
        headers={"Content-Disposition": f"attachment; filename=fitmind_{plan.plan_type}.ics"}
    )
