import asyncio, os, httpx, logging
from aiogram import Bot, Dispatcher, types, executor
from aiohttp import web

# --- [ الإعدادات ] ---
API_TOKEN = "8587471594:AAEDUgePR4dToTkxeJkrhFL3sWo0nFUY1yU"
OPENROUTER_KEY = "b33a34f2b0da469e854176cc78642ea5"
GROQ_API_KEY = "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"

bot = Bot(token=API_TOKEN, parse_mode="HTML")
dp = Dispatcher(bot)
logging.basicConfig(level=logging.INFO)

# --- [ محرك Groq الاحتياطي ] ---
async def get_groq_backup(word):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}"}
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [{"role": "user", "content": f"لغز ذكي وقصير جداً عن ({word}) بدون ذكرها."}],
        "temperature": 0.5
    }
    try:
        async with httpx.AsyncClient() as client:
            res = await client.post(url, json=payload, timeout=10.0)
            return res.json()['choices'][0]['message']['content'].strip(), "Groq 🐺"
    except:
        return None, None

# --- [ محرك OpenRouter الأساسي ] ---
async def get_hint_combined(word):
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {"Authorization": f"Bearer {OPENROUTER_KEY}", "Content-Type": "application/json"}
    payload = {
        "model": "google/gemini-2.0-flash-exp:free",
        "messages": [{"role": "user", "content": f"لغز غامض وذكي عن كلمة ({word}) بدون ذكرها."}]
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, json=payload, timeout=15.0)
            res_data = response.json()
            if 'choices' in res_data:
                return res_data['choices'][0]['message']['content'].strip(), "OpenRouter 💎"
    except:
        pass # إذا فشل ننتقل للاحتياطي

    # إذا وصلنا هنا يعني المحرك الأول فشل، نشغل الاحتياطي فوراً
    backup_text, source = await get_groq_backup(word)
    if backup_text:
        return backup_text, source
    
    return "⚠️ جميع المحركات مشغولة حالياً، جرب كلمة أخرى.", "Error ❌"

@dp.message_handler(commands=['start'])
async def start(m: types.Message):
    await m.answer("🚀 <b>تم تفعيل نظام الحماية المزدوج!</b>\nأرسل أي كلمة وسأستخدم أذكى المحركات المتاحة.")

@dp.message_handler()
async def handle_game(m: types.Message):
    word = m.text.strip()
    wait_msg = await m.answer(f"⏳ جاري البحث في عقول الذكاء الاصطناعي...")
    
    hint, source = await get_hint_combined(word)
    
    res = (
        f"💎 <b>〔 تـلـمـيـح الـمـسـابـقـة 〕</b>\n"
        f"━━━━━━━━━━━━━━\n\n"
        f"📜 <b>الوصف:</b>\n"
        f"« <i>{hint}</i> »\n\n"
        f"━━━━━━━━━━━━━━\n"
        f"⚙️ <b>المحرك المستخدم:</b> {source}"
    )
    await wait_msg.delete()
    await m.answer(res)

# --- [ نظام Render ] ---
async def handle_ping(request): return web.Response(text="Active")
if __name__ == '__main__':
    app = web.Application()
    app.router.add_get('/', handle_ping)
    runner = web.AppRunner(app); loop = asyncio.get_event_loop()
    loop.run_until_complete(runner.setup())
    port = int(os.environ.get("PORT", 10000))
    loop.create_task(web.TCPSite(runner, '0.0.0.0', port).start())
    executor.start_polling(dp, skip_updates=True)
