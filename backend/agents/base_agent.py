import json
import logging
from typing import AsyncGenerator

from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_google_genai import ChatGoogleGenerativeAI

from config import GEMINI_API_KEY, GEMINI_MODEL

logger = logging.getLogger(__name__)

# Inisialisasi LangChain LLM Client
llm = None
if GEMINI_API_KEY and GEMINI_API_KEY != "ISI_API_KEY_KAMU_DISINI":
    llm = ChatGoogleGenerativeAI(
        model=GEMINI_MODEL, 
        google_api_key=GEMINI_API_KEY, 
        temperature=0.7, 
        streaming=True
    )
else:
    logger.warning("GEMINI_API_KEY belum diset!")

class BaseAgent:
    """
    Kelas dasar untuk semua agent FitMind AI.
    Sekarang di-upgrade menggunakan LangChain.
    """
    name: str = "BaseAgent"
    description: str = "Agent dasar"
    system_prompt: str = "Kamu adalah asisten AI."

    def _build_lc_messages(self, message: str, chat_history: list[dict], context: str = ""):
        messages = [SystemMessage(content=self.system_prompt)]
        
        for msg in chat_history[-10:]:
            role = msg.get("role")
            content = msg.get("content", "")
            if role == "user":
                messages.append(HumanMessage(content=content))
            else:
                messages.append(AIMessage(content=content))
                
        final_message = message
        if context:
            final_message = f"{message}\n\n---\n[KONTEKS DATA RELEVAN - Gunakan ini untuk menjawab]\n{context}\n---"
            
        messages.append(HumanMessage(content=final_message))
        return messages

    async def stream(self, message: str, chat_history: list[dict], context: str = "") -> AsyncGenerator[str, None]:
        """Stream respons dari LLM menggunakan LangChain astream."""
        if not llm:
            yield f"[{self.name}] ERROR: LLM tidak terkonfigurasi dengan benar (Periksa API Key)."
            return
            
        try:
            messages = self._build_lc_messages(message, chat_history, context)
            async for chunk in llm.astream(messages):
                if chunk.content:
                    yield chunk.content
        except Exception as e:
            logger.error(f"[{self.name}] LLM error: {e}")
            yield f"\n\nMaaf, terjadi error pada {self.name}: {str(e)}"
            
    async def run(self, message: str, chat_history: list[dict], context: str = "") -> str:
        """Non-streaming version dari stream()."""
        full = ""
        async for chunk in self.stream(message, chat_history, context):
            full += chunk
        return full

    async def generate_structured(
        self, 
        message: str, 
        chat_history: list[dict], 
        context: str = "", 
        response_schema: dict = None, 
        system_prompt_override: str = None
    ) -> dict:
        """Generate structured JSON output menggunakan LangChain."""
        prompt = system_prompt_override or self.system_prompt
        json_prompt = prompt + "\nKamu HARUS membalas dalam format JSON yang valid."
        if response_schema:
            json_prompt += f"\nSchema JSON:\n{json.dumps(response_schema)}"
            
        messages = [SystemMessage(content=json_prompt)]
        for msg in chat_history[-10:]:
            role = msg.get("role")
            content = msg.get("content", "")
            if role == "user":
                messages.append(HumanMessage(content=content))
            else:
                messages.append(AIMessage(content=content))
                
        final_message = message
        if context:
            final_message = f"{message}\n\n---\n[KONTEKS DATA RELEVAN]\n{context}\n---"
        messages.append(HumanMessage(content=final_message))
        
        try:
            resp = await llm.ainvoke(messages)
            content = resp.content
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].strip()
            return json.loads(content)
        except Exception as e:
            logger.error(f"Error parsing JSON dari LLM: {e}")
            return {}
