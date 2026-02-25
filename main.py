import asyncio, httpx, logging
from aiogram import Bot, Dispatcher, types, executor
from supabase import create_client, Client

# --- [ الإعدادات النهائية والمحدثة ] ---
# التوكن الجديد الذي أرسلته
API_TOKEN = "8587471594:AAEDUgePR4dToTkxeJkrhFL3sWo0nFUY1yU"
# آيدي الأدمن الخاص بك للتنبيهات
ADMIN_ID = 7988144062 

# بيانات سوبابيس (Supabase) للربط بالجدول الذي أنشأته
SUPABASE_URL = "https://snlcbtgzdxsacwjipggn.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InNubGNidGd6ZHhzYWN3amlwZ2duIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MDU3NDMzMiwiZXhwIjoyMDg2MTUwMzMyfQ.v3SRkONLNlQw5LWhjo03u0fDce3EvWGBpJ02OGg5DEI"

# القلوب (مفاتيح جوروب) - يمكنك إضافة مفاتيح أخرى هنا مستقبلاً
GROQ_KEYS = [
    "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",
    "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",
    "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"
]

current_key_index = 0
# إنشاء اتصال بسوبابيس
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
bot = Bot(token=API_TOKEN, parse_mode="HTML")
dp = Dispatcher(bot)

# --- [ نظام الذاكرة السحابية ] ---
def get_cached_hint(word):
    try:
        # البحث في الجدول الذي أنشأته يا ياسر
        response = supabase.table("hints").select("hint").eq("word", word).execute()
        if response.data:
            return response.data[0]['hint']
    except Exception as e:
        logging.error(f"Supabase Select Error: {e}")
    return None

def save_to_cache(word, hint):
    try:
        # حفظ الكلمة والتلميح في السحاب
        supabase.table("hints").insert({"word": word, "hint": hint}).execute()
    except Exception as e:
        logging.error(f"Supabase Insert Error: {e}")

# --- [ محرك جوروب (تدوير القلوب) ] ---
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
                elif res.status_code == 429: # في حال تعطل المفتاح
                    await bot.send_message(ADMIN_ID, f"⚠️ <b>تنبيه يا ياسر:</b>\nالمفتاح رقم {current_key_index+1} تعطل، سيتم التحويل للقلب التالي.")
                    current_key_index = (current_key_index + 1) % len(GROQ_KEYS)
        except:
            current_key_index = (current_key_index + 1) % len(GROQ_KEYS)
    return None, None

# --- [ معالج الرسائل الأساسي ] ---
@dp.message_handler()
async def main_logic(m: types.Message):
    word = m.text.strip()
    
    # 1. البحث في سوبابيس أولاً لتوفير المفاتيح
    cached = get_cached_hint(word)
    if cached:
        return await m.answer(f"☁️ <b>تلميح من الذاكرة السحابية:</b>\n\n{cached}")

    # 2. إذا لم تكن موجودة، نطلبها من الذكاء الاصطناعي
    wait_msg = await m.answer("⏳ <i>جاري التفكير واستحضار اللغز...</i>")
    hint, source = await get_groq_hint(word)
    
    if hint:
        save_to_cache(word, hint) # حفظها للمستقبل
        res = f"🌟 <b>تلميح ذكي ({source}):</b>\n\n{hint}"
    else:
        res = f"📝 <b>تلميح عادي:</b>\nهذا الشيء يتعلق بـ ({word})، حاول تخمينه!"

    await wait_msg.delete()
    await m.answer(res)

if __name__ == '__main__':
    print("🚀 البوت انطلق بنجاح مع نظام Supabase والتوكن الجديد!")
    executor.start_polling(dp, skip_updates=True)
