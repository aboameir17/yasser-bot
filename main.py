import asyncio, httpx, logging
from aiogram import Bot, Dispatcher, types, executor
from supabase import create_client, Client

# --- [ الإعدادات النهائية ] ---
API_TOKEN = "8587471594:AAEB0cRP3lrEFfP-vGTRC1B4sHhMCxYF6LM"
ADMIN_ID = 7988144062 

# القلوب (مفاتيح جوروب)
GROQ_KEYS = [
    "g_uiVfQCAABOvhIAyeyIcwWGdyb3FYt4W4O1Xzg4eKLTIe38M9WBf556",
    "g_yVkyOmMFalkLToStSRYqWGdyb3FY5kLK4Hr1KECxdpAawZWd4iV55X",
    "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"
]

# بيانات سوبابيس
SUPABASE_URL = "https://snlcbtgzdxsacwjipggn.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InNubGNidGd6ZHhzYWN3amlwZ2duIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MDU3NDMzMiwiZXhwIjoyMDg2MTUwMzMyfQ.v3SRkONLNlQw5LWhjo03u0fDce3EvWGBpJ02OGg5DEI"

# إعداد الاتصالات
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
bot = Bot(token=API_TOKEN, parse_mode="HTML")
dp = Dispatcher(bot)

current_key_index = 0

# --- [ نظام الذاكرة السحابية - Supabase ] ---
def get_cached_hint(word):
    try:
        res = supabase.table("hints").select("hint").eq("word", word).execute()
        return res.data[0]['hint'] if res.data else None
    except: return None

def save_to_cache(word, hint):
    try:
        supabase.table("hints").insert({"word": word, "hint": hint}).execute()
    except: pass

# --- [ محرك جوروب (Groq) ] ---
async def get_groq_hint(word):
    global current_key_index
    url = "https://api.groq.com/openai/v1/chat/completions"
    
    for _ in range(len(GROQ_KEYS)):
        active_key = GROQ_KEYS[current_key_index]
        headers = {"Authorization": f"Bearer {active_key}"}
        payload = {
            "model": "llama-3.3-70b-versatile",
            "messages": [{"role": "user", "content": f"أعطني لغزاً قصيراً وذكياً عن كلمة ({word}) بدون ذكرها."}]
        }
        try:
            async with httpx.AsyncClient() as client:
                res = await client.post(url, json=payload, headers=headers, timeout=12.0)
                if res.status_code == 200:
                    hint_text = res.json()['choices'][0]['message']['content'].strip()
                    return hint_text, f"القلب {current_key_index+1}"
                
                # تدوير المفتاح في حال الخطأ (مثل 429)
                current_key_index = (current_key_index + 1) % len(GROQ_KEYS)
        except:
            current_key_index = (current_key_index + 1) % len(GROQ_KEYS)
    return None, None

# --- [ المعالج الأساسي ] ---
@dp.message_handler()
async def main_logic(m: types.Message):
    word = m.text.strip()
    
    # 1. البحث في السحاب أولاً لتوفير المفاتيح
    cached = get_cached_hint(word)
    if cached:
        return await m.answer(f"☁️ <b>تلميح مخزن:</b>\n\n{cached}")

    wait_msg = await m.answer("⏳ <i>جاري استحضار اللغز...</i>")
    
    # 2. طلب لغز جديد من جوروب
    hint, source = await get_groq_hint(word)
    
    if hint:
        save_to_cache(word, hint) # حفظه فوراً
        res = f"🌟 <b>تلميح ذكي ({source}):</b>\n\n{hint}"
    else:
        res = f"📝 <b>تلميح عادي:</b>\nهذا الشيء يتعلق بـ ({word})، حاول تخمينه!"

    await wait_msg.delete()
    await m.answer(res)

if __name__ == '__main__':
    print("✅ تم إزالة Gemini.. البوت يعمل الآن بنظام Groq الصافي.")
    executor.start_polling(dp, skip_updates=True)
