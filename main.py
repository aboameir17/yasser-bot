import asyncio, os, httpx, logging
from aiogram import Bot, Dispatcher, types, executor
from aiohttp import web

# --- [ الإعدادات ] ---
API_TOKEN = "8587471594:AAEDUgePR4dToTkxeJkrhFL3sWo0nFUY1yU"
OPENROUTER_KEY = "b33a34f2b0da469e854176cc78642ea5"
GROQ_API_KEY = "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"

bot = Bot(token=API_TOKEN, parse_mode="HTML")
dp = Dispatcher(bot)

# --- [ 1. محرك الرابط المباشر (مستوحى من ملفاتك) ] ---
async def get_direct_api(word):
    # نستخدم رابط من الروابط التي وجدناها في ملفاتك لضمان الرد السريع
    url = f"https://www.pyhanzo.com/ChatGPT3.5?prompt=أعطني لغز عن {word} بدون ذكر اسمها"
    try:
        async with httpx.AsyncClient() as client:
            res = await client.get(url, timeout=10.0)
            if res.status_code == 200 and len(res.text) > 5:
                return res.text.strip(), "Direct Link 🔗"
    except:
        return None, None

# --- [ 2. محرك Groq ] ---
async def get_groq_hint(word):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}"}
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [{"role": "user", "content": f"لغز ذكي وقصير جداً عن ({word}) بدون ذكر اسمها."}]
    }
    try:
        async with httpx.AsyncClient() as client:
            res = await client.post(url, json=payload, headers=headers, timeout=10.0)
            return res.json()['choices'][0]['message']['content'].strip(), "Groq 🐺"
    except:
        return None, None

# --- [ 3. محرك OpenRouter ] ---
async def get_openrouter_hint(word):
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {"Authorization": f"Bearer {OPENROUTER_KEY}", "Content-Type": "application/json"}
    payload = {
        "model": "google/gemini-2.0-flash-exp:free",
        "messages": [{"role": "user", "content": f"لغز غامض وذكي عن كلمة ({word}) بدون ذكرها."}]
    }
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, json=payload, timeout=10.0)
            return response.json()['choices'][0]['message']['content'].strip(), "OpenRouter 💎"
    except:
        return None, None

# --- [ النظام الذكي لاختيار المحرك ] ---
async def get_final_hint(word):
    # الترتيب: OpenRouter -> Groq -> Direct Link
    methods = [get_openrouter_hint, get_groq_hint, get_direct_api]
    
    for method in methods:
        text, source = await method(word)
        if text:
            return text, source
            
    return "⚠️ كل المحركات مشغولة، حاول مجدداً بعد ثواني.", "Failed ❌"

@dp.message_handler()
async def handle_game(m: types.Message):
    word = m.text.strip()
    wait_msg = await m.answer(f"⏳ جاري تشغيل المحركات...")
    
    hint, source = await get_final_hint(word)
    
    res = (
        f"💎 <b>〔 تـلـمـيـح الـمـسـابـقـة 〕</b>\n"
        f"━━━━━━━━━━━━━━\n\n"
        f"📜 <b>الوصف:</b>\n"
        f"« <i>{hint}</i> »\n\n"
        f"━━━━━━━━━━━━━━\n"
        f"⚙️ <b>المصدر:</b> {source}"
    )
    await wait_msg.delete()
    await m.answer(res)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
